import pygame
import random
import sys
from collections import deque

# --------------------
# CONFIG
# --------------------
WIDTH, HEIGHT = 1600, 900  # Adjusted for better spacing
FPS = 30
MAX_LOGS = 15
PADDING = 20

# --- UI Enhancement: Slow down the data update rate ---
# Original was 2. Higher number means slower graph updates.
DATA_UPDATE_INTERVAL_FRAMES = 8

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚡ Tactical Dashboard v5 - Enhanced UI")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("consolas", 15)
big_font = pygame.font.SysFont("consolas", 18, bold=True)
title_font = pygame.font.SysFont("consolas", 24, bold=True)

# Colors
WHITE = (240, 240, 240)
GREEN = (50, 255, 120)
RED = (255, 80, 80)
BLUE = (80, 180, 255)
YELLOW = (255, 220, 80)
CYAN = (100, 255, 255)
PURPLE = (200, 120, 255)
DARK_BG = (10, 15, 25)
PANEL_BG = (20, 25, 45)
HEADER_BG = (30, 40, 65)
GRID_LINE = (40, 50, 75)


# --------------------
# DATA STRUCTURES
# --------------------
event_log = deque(maxlen=MAX_LOGS)
enemy_speeds = deque(maxlen=200)
enemy_azimuths = deque(maxlen=200)

jet_distances = {}  # jet_id -> deque
jet_freqs = {}      # jet_id -> deque
hit_events = deque(maxlen=200)  # (frame, jet_id)

# --------------------
# SIM OBJECTS
# --------------------
class Jet:
    def __init__(self, jid, altitude):
        self.id = jid
        self.altitude = altitude
        self.active = True
        self.scanning = True
        self.hits = 0

class Enemy:
    def __init__(self):
        self.speed_m_s = 250 + random.uniform(-20,20)
        self.azimuth = random.uniform(0,360)

enemy = Enemy()
jets = [Jet(jid=i+1, altitude=random.randint(2000,12000)) for i in range(5)]

for j in jets:
    jet_distances[j.id] = deque(maxlen=200)
    jet_freqs[j.id] = deque(maxlen=200)

# --------------------
# HELPERS
# --------------------
def add_event(msg):
    event_log.appendleft(msg)

def draw_panel(x,y,w,h,title,color=CYAN):
    # Main panel body
    rect = pygame.Rect(x,y,w,h)
    pygame.draw.rect(screen, PANEL_BG, rect, border_radius=10)
    
    # --- UI Enhancement: Panel header bar ---
    header_rect = pygame.Rect(x, y, w, 35)
    pygame.draw.rect(screen, HEADER_BG, header_rect, border_top_left_radius=10, border_top_right_radius=10)
    
    # Title and border
    screen.blit(big_font.render(title, True, color), (x+15, y+8))
    pygame.draw.rect(screen, color, rect, 2, border_radius=10)
    return rect

def draw_summary_cards():
    cards = [
        ("Total Jets", f"{len(jets)}", BLUE),
        ("Active Jets", f"{sum(j.active for j in jets)}", GREEN),
        ("Total Hits", f"{sum(j.hits for j in jets)}", RED),
        ("Enemy Speed", f"{enemy.speed_m_s:.1f} m/s", PURPLE),
        ("Enemy Azimuth", f"{enemy.azimuth:.1f}°", YELLOW),
    ]
    card_w, card_h = 240, 80
    x, y = PADDING, PADDING
    
    for title, val, color in cards:
        rect = pygame.Rect(x,y,card_w,card_h)
        pygame.draw.rect(screen, HEADER_BG, rect, border_radius=10)
        pygame.draw.rect(screen, color, rect, 2, border_radius=10)
        screen.blit(big_font.render(title, True, WHITE), (x+15, y+15))
        screen.blit(title_font.render(val, True, color), (x+15, y+40))
        y += card_h + PADDING

def draw_jet_table():
    # --- UI Enhancement: Repositioned and resized for better fit ---
    table_x = 2 * PADDING + 240
    table_w = WIDTH - table_x - PADDING
    rect = draw_panel(table_x, PADDING, table_w, 200, "Jet Status Table")

    x, y = rect.x + 20, rect.y + 45
    headers = ["Jet ID", "Altitude", "State", "Last Dist (km)", "Last Freq (GHz)", "Total Hits"]
    col_widths = [100, 150, 150, 180, 180, 120]
    
    # Draw headers
    col_x = x
    for i, h in enumerate(headers):
        screen.blit(big_font.render(h, True, WHITE), (col_x, y))
        col_x += col_widths[i]

    y += 30
    
    # Draw jet rows
    for j in jets:
        dist = f"{jet_distances[j.id][-1]:.1f}" if jet_distances[j.id] else "N/A"
        freq = f"{jet_freqs[j.id][-1]:.2f}" if jet_freqs[j.id] else "N/A"
        state = ("ACTIVE" if j.active else "OFFLINE") + " / " + ("SCAN" if j.scanning else "IDLE")
        
        vals = [str(j.id), str(j.altitude), state, dist, freq, str(j.hits)]
        row_col = GREEN if j.scanning and j.active else (RED if not j.active else WHITE)
        
        col_x = x
        for i, v in enumerate(vals):
            # --- UI Enhancement: Right-align numerical values ---
            text_surface = font.render(v, True, row_col)
            text_x = col_x
            # Align right for columns 3, 4, 5
            if i in [3, 4, 5]:
                text_x = col_x + col_widths[i] - text_surface.get_width() - 20
            
            screen.blit(text_surface, (text_x, y))
            col_x += col_widths[i]
        y += 22

def draw_event_log():
    # --- UI Enhancement: Repositioned log to fill bottom-left column ---
    log_y = 5 * (80 + PADDING) + PADDING
    log_h = HEIGHT - log_y - PADDING
    rect = draw_panel(PADDING, log_y, 240, log_h, "Event Log", YELLOW)
    
    log_y_start = rect.y + 40
    for i, e in enumerate(list(event_log)):
        screen.blit(font.render(e, True, WHITE), (rect.x+15, log_y_start + i*18))

def gradient_color(value, min_val, max_val):
    if max_val == min_val: return GREEN
    ratio = max(0, min(1, (value - min_val) / (max_val - min_val)))
    r = int(50 + ratio * 205)
    g = int(255 - ratio * 175)
    b = int(120 - ratio * 80)
    return (max(0,min(255,r)), max(0,min(255,g)), max(0,min(255,b)))

def draw_graph(data, title, rect, base_color):
    draw_panel(rect.x, rect.y, rect.w, rect.h, title, base_color)
    graph_area = rect.inflate(-20, -45) # Padding inside the panel

    if len(data) > 1:
        dmin, dmax = min(data), max(data)
        rng = dmax - dmin if dmax != dmin else 1
        points = [
            (graph_area.left + i * (graph_area.width / (len(data)-1)),
             graph_area.bottom - ((d - dmin) / rng) * graph_area.height)
            for i, d in enumerate(data)
        ]
        if len(points) > 1:
            pygame.draw.aalines(screen, base_color, False, points, 2)
        
        # Stats text
        avg = sum(data)/len(data)
        txt = f"Avg: {avg:.1f} | Min: {dmin:.1f} | Max: {dmax:.1f}"
        screen.blit(font.render(txt, True, WHITE), (rect.x+15, rect.bottom-25))

        # Trend arrow
        if len(data) > 2:
            trend_val = data[-1] - data[-5] if len(data) > 5 else data[-1] - data[-2]
            if trend_val > 0.1: arrow, col = "▲", GREEN
            elif trend_val < -0.1: arrow, col = "▼", RED
            else: arrow, col = "–", WHITE
            trend_surf = big_font.render(arrow, True, col)
            screen.blit(trend_surf, (rect.right - 30, rect.top + 8))

def draw_hit_timeline(rect):
    draw_panel(rect.x, rect.y, rect.w, rect.h, "Hit Timeline", YELLOW)
    timeline_area = rect.inflate(-40, -50)
    
    if not hit_events: return

    # --- UI Enhancement: Draw horizontal lanes for each jet ---
    for i, jet in enumerate(jets):
        lane_y = timeline_area.top + (i + 0.5) * (timeline_area.height / len(jets))
        pygame.draw.line(screen, GRID_LINE, (timeline_area.left, lane_y), (timeline_area.right, lane_y), 1)
        jet_label = font.render(f"J-{jet.id}", True, WHITE)
        screen.blit(jet_label, (rect.x + 15, lane_y - 8))
    
    first_frame = hit_events[0][0]
    last_frame = frame
    frame_range = last_frame - first_frame if last_frame > first_frame else 1
    
    for f, jid in hit_events:
        px = timeline_area.left + int(((f-first_frame) / frame_range) * timeline_area.width)
        lane_index = jid - 1
        py = timeline_area.top + (lane_index + 0.5) * (timeline_area.height / len(jets))
        
        pygame.draw.circle(screen, GREEN, (px, py), 5)
        pygame.draw.circle(screen, WHITE, (px, py), 5, 1)

# --------------------
# MAIN LOOP
# --------------------
running = True
frame = 0
while running:
    dt = clock.tick(FPS)
    frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    # --- Simulation update: Slowed down ---
    if frame % DATA_UPDATE_INTERVAL_FRAMES == 0:
        enemy.speed_m_s += random.uniform(-2,2) * 2
        enemy.azimuth = (enemy.azimuth + random.uniform(-1,1) * 2) % 360
        enemy_speeds.append(enemy.speed_m_s)
        enemy_azimuths.append(enemy.azimuth)

        for j in jets:
            if j.active and j.scanning:
                dist = random.uniform(50,500) + j.altitude / 100
                freq = random.uniform(8,12) + (500/dist if dist>0 else 0)
                jet_distances[j.id].append(dist)
                jet_freqs[j.id].append(freq)
                if random.random() < 0.05:
                    add_event(f"J-{j.id} target lock")
                    hit_events.append((frame, j.id))
                    j.hits += 1

    # --- Draw ---
    screen.fill(DARK_BG)

    # --- Column 1: Vitals & Logs ---
    draw_summary_cards()
    draw_event_log()
    
    # --- Column 2: Jet Status & Trends ---
    draw_jet_table()
    
    jg_x = 2 * PADDING + 240
    jg_y = PADDING + 200 + PADDING
    jg_w = 280
    jg_h = 130
    jg_gap = 20

    for idx, j in enumerate(jets):
        row = idx // 3
        col = idx % 3
        dx = jg_x + col * (jg_w + jg_gap)
        dy = jg_y + row * (jg_h * 2 + jg_gap * 2)
        draw_graph(jet_distances[j.id], f"Jet {j.id} Distance", pygame.Rect(dx, dy, jg_w, jg_h), GREEN)
        draw_graph(jet_freqs[j.id], f"Jet {j.id} Frequency", pygame.Rect(dx, dy + jg_h + jg_gap, jg_w, jg_h), BLUE)

    # --- Column 3: Enemy Trends & History ---
    eg_x = jg_x + 3 * (jg_w + jg_gap) - jg_gap
    eg_w = WIDTH - eg_x - PADDING
    draw_graph(enemy_speeds, "Enemy Speed Trend", pygame.Rect(eg_x, PADDING, eg_w, 200), PURPLE)
    draw_graph(enemy_azimuths, "Enemy Azimuth Trend", pygame.Rect(eg_x, PADDING + 200 + PADDING, eg_w, 200), CYAN)

    timeline_y = PADDING + 200 + PADDING + 200 + PADDING
    timeline_h = HEIGHT - timeline_y - PADDING
    draw_hit_timeline(pygame.Rect(eg_x, timeline_y, eg_w, timeline_h))

    pygame.display.flip()

pygame.quit()
sys.exit()
