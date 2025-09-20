# app.py
# Trinetra AI Backend (final updated with pulse system & eco-system sharing)

import time
import random
import threading
import math
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# --- FLASK APP & SOCKET SETUP ---
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")  # threading mode for safety

# --- CENTRAL GAME STATE ---
game_state = {
    "is_paused": False,
    "mission_status": "AWAITING COMMANDS",
    "events": ["System Initialized. Awaiting operator input."],
    "squadron": [
        {
            "id": i + 1,
            "name": f"{i + 1}",
            "status": "PATROL",
            "position": {"x": 22.30 + random.uniform(-0.1, 0.1), "y": 84.80 + random.uniform(-0.1, 0.1)},
            "angle": random.uniform(0, 360),
            "speed": 0.001,
            "fuel": 100,
            "weapons": 4,
            "signal_history": [],
            "locked_enemy": None,
        } for i in range(5)
    ],
    "threats": [
        {"id": 1, "x": 22.25, "y": 84.85, "is_scanning": False, "angle": random.uniform(0, 360), "speed": 0.0005},
        {"id": 2, "x": 22.35, "y": 84.83, "is_scanning": False, "angle": random.uniform(0, 360), "speed": 0.0005},
    ],
    "pulse_history": []
}

# --- HELPER FUNCTIONS ---
def broadcast_state():
    socketio.emit("dashboard_update", game_state)

def calculate_angle_and_range(jet_pos, enemy_pos):
    dx = enemy_pos["x"] - jet_pos["x"]
    dy = enemy_pos["y"] - jet_pos["y"]
    angle = math.degrees(math.atan2(dy, dx)) % 360
    distance = math.sqrt(dx**2 + dy**2) * 111  # approximate km conversion
    if distance < 5:
        rng = "NEAR"
    elif distance < 15:
        rng = "MID"
    else:
        rng = "FAR"
    return angle, rng, distance

def simulate_pulse_hits():
    """Simulate enemy pulses toward jets with locking logic."""
    while True:
        try:
            if not game_state["is_paused"]:
                for enemy in game_state["threats"]:
                    for jet in game_state["squadron"]:
                        if jet.get("locked_enemy") == enemy["id"]:
                            continue
                        angle, rng, distance = calculate_angle_and_range(jet["position"], {"x": enemy["x"], "y": enemy["y"]})
                        strength = max(0, 100 - distance * 2)
                        timestamp = time.strftime("%H:%M:%S")

                        pulse_event = {
                            "fromEnemyId": enemy["id"],
                            "toJetId": jet["id"],
                            "strength": strength,
                            "timestamp": timestamp,
                            "angle_deg": angle,
                            "range": rng,
                            "enemy_pos": {"x": enemy["x"], "y": enemy["y"]}
                        }

                        game_state["pulse_history"].append(pulse_event)
                        if len(game_state["pulse_history"]) > 100:
                            game_state["pulse_history"].pop(0)

                        if strength > 30:
                            jet["signal_history"].append({
                                "timestamp": timestamp,
                                "frequency_ghz": random.uniform(8, 18),
                                "strength_db": -strength,
                                "angle_deg": angle,
                                "range": rng
                            })
                            if jet.get("locked_enemy") is None:
                                jet["locked_enemy"] = enemy["id"]
                                game_state["events"].insert(0, f"[{timestamp}] Jet {jet['name']} locked enemy {enemy['id']} (range {rng}, angle {angle:.1f}°)")
                                if len(game_state["events"]) > 50:
                                    game_state["events"] = game_state["events"][:50]
            broadcast_state()
            time.sleep(1)
        except Exception as e:
            print("Pulse simulation error:", e)
            time.sleep(1)

def simulation_thread():
    while True:
        try:
            if not game_state["is_paused"]:
                for jet in game_state["squadron"]:
                    rad = math.radians(jet["angle"])
                    jet["position"]["x"] += math.cos(rad) * jet["speed"]
                    jet["position"]["y"] += math.sin(rad) * jet["speed"]
                    jet["angle"] += random.uniform(-5, 5)
                    jet["fuel"] = max(0, jet["fuel"] - 0.05)

                for threat in game_state["threats"]:
                    rad = math.radians(threat["angle"])
                    threat["x"] += math.cos(rad) * threat["speed"]
                    threat["y"] += math.sin(rad) * threat["speed"]
                    threat["angle"] += random.uniform(-2, 2)
            broadcast_state()
            time.sleep(0.5)
        except Exception as e:
            print("Simulation error:", e)
            time.sleep(1)

# --- SOCKET HANDLERS ---
@socketio.on("connect")
def handle_connect():
    emit("dashboard_update", game_state)
    print("Client connected")

@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

@socketio.on("toggle_pause")
def handle_toggle_pause():
    game_state["is_paused"] = not game_state["is_paused"]
    status = "PAUSED" if game_state["is_paused"] else "RESUMED"
    game_state["mission_status"] = f"SIMULATION {status}"
    socketio.emit("dashboard_update", game_state)

@socketio.on("trigger_scan")
def handle_trigger_scan(data):
    enemy_id = data.get("enemy_id")
    for threat in game_state["threats"]:
        if threat["id"] == enemy_id:
            threat["is_scanning"] = True
            print(f"[{time.strftime('%H:%M:%S')}] Enemy {enemy_id} started scanning")
    socketio.emit("dashboard_update", game_state)

# --- API ENDPOINTS ---
@app.route("/api/squadron_status", methods=["GET"])
def api_squadron_status():
    return jsonify({"jets": game_state["squadron"]})

@app.route("/api/signal_intelligence", methods=["GET"])
def api_signal_intelligence():
    signals = []
    for jet in game_state["squadron"]:
        for s in jet.get("signal_history", []):
            signals.append({
                "jet_id": jet["id"],
                "timestamp": s["timestamp"],
                "frequency_ghz": s["frequency_ghz"],
                "strength_db": s["strength_db"],
                "angle_deg": s["angle_deg"],
                "range": s["range"]
            })
    signals = sorted(signals, key=lambda x: x["timestamp"], reverse=True)
    return jsonify(signals)

@app.route("/api/control", methods=["POST"])
def api_control():
    cmd = request.json.get("command")
    if cmd == "reset_simulation":
        for i, jet in enumerate(game_state["squadron"]):
            jet["position"] = {"x": 22.30 + random.uniform(-0.05, 0.05), "y": 84.80 + random.uniform(-0.05, 0.05)}
            jet["angle"] = random.uniform(0, 360)
            jet["fuel"] = 100
            jet["signal_history"] = []
            jet["locked_enemy"] = None
        for t in game_state["threats"]:
            t["x"] = 22.25 + random.uniform(-0.05, 0.05)
            t["y"] = 84.85 + random.uniform(-0.05, 0.05)
            t["is_scanning"] = False
        game_state["mission_status"] = "SIMULATION RESET"
        game_state["events"].insert(0, f"[{time.strftime('%H:%M:%S')}] Simulation reset.")
        socketio.emit("dashboard_update", game_state)
    return jsonify({"status": "success", "command_received": cmd})

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    print("Starting Trinetra AI Backend (final updated)...")
    # Start threads
    threading.Thread(target=simulation_thread, daemon=True).start()
    threading.Thread(target=simulate_pulse_hits, daemon=True).start()
    # Run Flask-SocketIO server
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)