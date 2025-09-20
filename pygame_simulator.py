import pygame
import math
import random
import sys
import time
import socketio
import threading

# --- Setup SocketIO client (connect to backend) ---
sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=2)


@sio.event
def connect():
    print("[SocketIO] Connected to backend")


@sio.event
def disconnect():
    print("[SocketIO] Disconnected from backend, will retry...")


def start_socket():
    """Try to connect in background, auto-reconnect if server restarts"""
    while True:
        try:
            if not sio.connected:
                sio.connect("http://localhost:5000")
            break
        except Exception as e:
            print("[SocketIO] Waiting for backend...", e)
            time.sleep(3)


# Launch socket client in background
threading.Thread(target=start_socket, daemon=True).start()


def safe_emit(event, data, namespace=None):
    """Safe emit that won’t crash if disconnected"""
    if sio.connected:
        sio.emit(event, data, namespace=namespace)
    else:
        print(f"[SocketIO] Skipped emit '{event}' (not connected)")


# --- Pygame Setup ---
pygame.init()
info = pygame.display.Info()
WIDTH, HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jet Radar Simulation")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 18)

# --- Constants ---
SPEED_OF_RADAR = 3e8   # m/s
MIN_FREQ = 8           # GHz
MAX_FREQ = 18          # GHz
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 100)

# --- Helper Functions ---
def random_dir(speed=1.5):
    angle = random.random() * math.tau
    return math.cos(angle) * speed, math.sin(angle) * speed


def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def calculate_azimuth(a, b):
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))


def speed_mach(prev_pos, curr_pos, dt):
    dist = distance(prev_pos, curr_pos)
    speed_m_s = dist / dt if dt > 0 else 0
    mach = speed_m_s / 343
    return speed_m_s, mach


def rotate_vector(dx, dy, deg):
    rad = math.radians(deg)
    new_dx = dx * math.cos(rad) - dy * math.sin(rad)
    new_dy = dx * math.sin(rad) + dy * math.cos(rad)
    return new_dx, new_dy


# --- Jet Class ---
class Jet:
    def __init__(self, idx, x, y):
        self.id = idx
        self.x, self.y = x, y
        self.dx, self.dy = random_dir()
        self.active = True
        self.scanning = False
        self.detected_enemy = False
        self.pulses = []
        self.locking = False
        self.turn_rate = random.uniform(0.2, 0.7)
        self.prev_pos = (x, y)
        self.altitude = random.randint(1000, 3000)

    def update(self):
        if self.active:
            self.dx, self.dy = rotate_vector(self.dx, self.dy, random.uniform(-self.turn_rate, self.turn_rate))
            self.x += self.dx
            self.y += self.dy
            if self.x < 30 or self.x > WIDTH - 30:
                self.dx *= -1
            if self.y < 30 or self.y > HEIGHT - 30:
                self.dy *= -1

        for p in self.pulses:
            p["progress"] += 0.02
            if p["progress"] > 1:
                p["progress"] = 0

    def draw(self, surf, enemy):
        pts = [(0, -12), (8, 12), (-8, 12)]
        rotated = [(self.x + px, self.y + py) for px, py in pts]
        pygame.draw.polygon(surf, CYAN, rotated)

        if self.scanning and not self.locking:
            for p in self.pulses:
                angle = math.atan2(enemy.y - self.y, enemy.x - self.x)
                length = 200 * p["progress"]
                left = (self.x + math.cos(angle - 0.2) * length, self.y + math.sin(angle - 0.2) * length)
                right = (self.x + math.cos(angle + 0.2) * length, self.y + math.sin(angle + 0.2) * length)
                pygame.draw.polygon(surf, GREEN, [(self.x, self.y), left, right], 2)

        if self.locking:
            pygame.draw.line(surf, YELLOW, (self.x, self.y), (enemy.x, enemy.y), 1)


# --- Enemy Jet ---
class Enemy:
    def __init__(self):
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.dx, self.dy = 1.2, -1.0
        self.pulses = []
        self.scanning = False
        self.prev_time = time.time()
        self.prev_pos = (self.x, self.y)

    def update(self):
        self.x += self.dx * 0.5
        self.y += self.dy * 0.5
        if self.x < 50 or self.x > WIDTH - 50:
            self.dx *= -1
        if self.y < 50 or self.y > HEIGHT - 50:
            self.dy *= -1

        for p in self.pulses:
            p["r"] += 3
        self.pulses = [p for p in self.pulses if p["r"] < max(WIDTH, HEIGHT)]

        now = time.time()
        dt = now - self.prev_time
        self.speed_m_s, self.mach = speed_mach(self.prev_pos, (self.x, self.y), dt)
        self.azimuth = calculate_azimuth(self.prev_pos, (self.x, self.y))
        self.prev_pos = (self.x, self.y)
        self.prev_time = now

    def draw(self, surf):
        for p in self.pulses:
            pygame.draw.circle(surf, RED, (int(self.x), int(self.y)), int(p["r"]), 1)
        pts = [(0, -12), (8, 12), (-8, 12)]
        rotated = [(self.x + px, self.y + py) for px, py in pts]
        pygame.draw.polygon(surf, RED, rotated)


# --- Starfield ---
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.random() * 2) for _ in range(300)]


def draw_background():
    screen.fill(BLACK)
    for x, y, r in stars:
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(r))


# --- Main Simulation ---
jets = [Jet(i + 1, 200 + i * 100, 200 + i * 60) for i in range(5)]
enemy = Enemy()

running = True
while running:
    clock.tick(60)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN:
            if e.unicode in "12345":
                idx = int(e.unicode) - 1
                jets[idx].active = not jets[idx].active
                print(f"Jet {jets[idx].id} {'resumed' if jets[idx].active else 'paused'}")
            elif e.key == pygame.K_e:
                enemy.scanning = True
                enemy.pulses.append({"r": 0})
                print(f"[Enemy] Sent radar pulse at {time.time():.1f}s")
            elif e.key == pygame.K_l:
                for j in jets:
                    if j.detected_enemy:
                        j.locking = True
                        j.scanning = False
                print("[Jets] Locking enemy position")

    # --- Update ---
    enemy.update()
    for j in jets:
        j.update()
        for p in enemy.pulses:
            dist = distance((j.x, j.y), (enemy.x, enemy.y))
            if abs(dist - p["r"]) < 2 and not j.detected_enemy:
                j.detected_enemy = True
                j.scanning = True
                j.pulses.append({"progress": 0})
                hit_data = {
                    "jet_id": j.id,
                    "x": j.x,
                    "y": j.y,
                    "altitude": j.altitude,
                    "distance": dist,
                    "azimuth": calculate_azimuth((j.x, j.y), (enemy.x, enemy.y)),
                    "enemy_speed": enemy.speed_m_s,
                    "enemy_mach": enemy.mach,
                    "time": time.time()
                }
                safe_emit("pulse_hit", hit_data)
                print(f"[Hit] {hit_data}")

        if j.scanning and not j.locking and random.random() < 0.03:
            dist = distance((j.x, j.y), (enemy.x, enemy.y))
            freq = MAX_FREQ - (dist / max(WIDTH, HEIGHT)) * (MAX_FREQ - MIN_FREQ)
            j.pulses.append({"progress": 0})
            pulse_data = {
                "jet_id": j.id,
                "distance": dist,
                "frequency": freq,
                "time": time.time()
            }
            safe_emit("jet_pulse", pulse_data)
            print(f"[Pulse] {pulse_data}")

    # --- Draw ---
    draw_background()
    enemy.draw(screen)
    for j in jets:
        j.draw(screen, enemy)

    ytxt = 10
    for j in jets:
        dist = distance((j.x, j.y), (enemy.x, enemy.y))
        freq = MAX_FREQ - (dist / max(WIDTH, HEIGHT)) * (MAX_FREQ - MIN_FREQ)
        txt = f"Jet {j.id}: ({int(j.x)},{int(j.y)}) ALT={j.altitude}m {'ON' if j.active else 'PAUSE'} | {'Scan' if j.scanning else 'Idle'} | D={dist:.1f} | F={freq:.2f}GHz"
        screen.blit(font.render(txt, True, GREEN if j.scanning else WHITE), (10, ytxt))
        ytxt += 20

    enemy_info = {
        "x": enemy.x,
        "y": enemy.y,
        "speed": enemy.speed_m_s,
        "mach": enemy.mach,
        "azimuth": enemy.azimuth,
        "time": time.time()
    }
    safe_emit("enemy_update", enemy_info)
    print(f"[Enemy] {enemy_info}")

    pygame.display.flip()

pygame.quit()
sys.exit()