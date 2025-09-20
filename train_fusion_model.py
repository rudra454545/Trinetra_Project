# backend/app.py

import time
import random
import threading
import os
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS

# NOTE: For a real project, you would load your TensorFlow models here
# import tensorflow as tf
# strategic_model = tf.keras.models.load_model('model/strategic_model.h5')
# print("AI models loaded.")

# --- FLASK APP & WEBSOCKET SETUP ---
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CENTRAL GAME STATE (Single Source of Truth) ---
game_state = {
    "mission_status": "PATROL",
    "active_threats": 3,
    "system_health": 100.0,
    "network_health": 100.0,
    "ai_confidence": 0.0,
    "signal_history": [-55, -60, -58, -62, -59], # Start with some initial data
    "squadron": [
        {"id": i + 1, "name": f"TRN-0{i+1}", "status": "PATROL", "fuel": 100, "weapons": 4, "position": {"x": 22.30 + random.uniform(-0.05, 0.05), "y": 84.80 + random.uniform(-0.05, 0.05)}} for i in range(5)
    ],
    "threats": [
        {"id": 1, "x": 22.25, "y": 84.85},
        {"id": 2, "x": 22.28, "y": 84.79},
        {"id": 3, "x": 22.32, "y": 84.88},
    ],
    "events": []
}

# --- SIMULATION ENGINE (Background Thread) ---
def simulation_thread():
    """Continuously updates and emits the game state."""
    # (Your simulation logic remains unchanged)
    while True:
        try:
            # Update System Vitals, Squadron, Threats, AI Events etc.
            game_state["system_health"] = max(90, game_state["system_health"] - random.uniform(0.01, 0.05))
            game_state["network_health"] = max(95, game_state["network_health"] - random.uniform(0.01, 0.02))
            for jet in game_state["squadron"]:
                jet["position"]["x"] += random.uniform(-0.001, 0.001)
                jet["position"]["y"] += random.uniform(-0.001, 0.001)
                jet["fuel"] = max(0, jet["fuel"] - 0.1)
            # ... and so on for other simulation logic ...

            # Emit the state to all connected dashboards via WebSocket
            socketio.emit('dashboard_update', game_state)
            time.sleep(2)
        except Exception as e:
            print(f"Error in simulation thread: {e}")
            time.sleep(5)

# --- NEW API ENDPOINTS FOR POLLING ---
# These endpoints serve specific slices of the game_state for your components.

@app.route('/api/system_status')
def get_system_status():
    """Endpoint for the Header and Sidebar components."""
    return jsonify({
        "mission_status": game_state["mission_status"],
        "active_threats": game_state["active_threats"],
        "system_health": game_state["system_health"],
        "network_health": game_state["network_health"],
        "signal_history": game_state["signal_history"]
    })

@app.route('/api/squadron_status')
def get_squadron_status():
    """Endpoint for the JetStatusPanel component."""
    return jsonify({"jets": game_state["squadron"]})

@app.route('/api/threat_coordinates')
def get_threat_coordinates():
    """Endpoint for the MilitaryMap component."""
    return jsonify({"coordinates": game_state["threats"]})

@app.route('/api/signal_intelligence')
def get_signal_intelligence():
    """Endpoint for the RealTimeData component."""
    # Simulate a new signal detection
    new_signal = {
        "signal_strength_db": -40 - random.random() * 20,
        "frequency_ghz": random.uniform(2, 18),
        "is_known_threat": 1 if random.random() > 0.8 else 0,
        "threat_priority_level": random.randint(1, 3),
        "timestamp": time.time() * 1000 # JS expects milliseconds
    }
    return jsonify([new_signal])


# --- CONTROL AND PREDICTION ENDPOINTS ---

@app.route('/api/control', methods=['POST'])
def control_system():
    # (This function remains unchanged)
    command = request.json.get('command')
    print(f"Received command from dashboard: {command}")
    # ... logic to change game_state based on command ...
    socketio.emit('dashboard_update', game_state) # Push update immediately
    return jsonify({"status": "success", "command_received": command})

# Placeholder for your AI prediction endpoint
@app.route('/predict/ping_decision', methods=['POST'])
def predict_ping():
    """Endpoint for Pygame simulators to call for AI decisions."""
    # data = request.json
    # Here you would preprocess the data, use your loaded model to predict,
    # and return the AI's decision.
    # prediction = strategic_model.predict(...)
    decision = {"decision": "PING BACK", "confidence": random.random()}
    return jsonify(decision)


# --- WEBSOCKET HANDLERS (Unchanged) ---
@socketio.on('connect')
def handle_connect():
    print('Dashboard client connected')
    emit('dashboard_update', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    print('Dashboard client disconnected')


# --- MAIN EXECUTION BLOCK ---
if __name__ == '__main__':
    print("Starting Trinetra AI Backend...")
    sim_thread = threading.Thread(target=simulation_thread, daemon=True)
    sim_thread.start()
    socketio.run(app, host='0.0.0.0', port=5000)

