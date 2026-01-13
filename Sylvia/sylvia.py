# Sylva v1.0 — Sensor Sentinel for EdenNode
# Monitors ambient logs and maps CHAOS sensory fields

import os
import argparse
from datetime import datetime

# === CONFIG ===
LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/DCA_Specialty_Folders/Sylva_Logs/memorymap.md"

# === CORE MONITOR ===
def monitor_sensory_field(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().lower()

    states = []
    if "light: low" in data or "dark" in data:
        states.append("low_light")
    if "temp: high" in data or "hot" in data:
        states.append("overheat")
    if "motion: none" in data:
        states.append("stillness")
    if "noise: high" in data:
        states.append("overstim")
    if "threshold" in data:
        states.append("threshold_crossed")

    state_map = ", ".join(states) if states else "neutral field"
    log_event(f"Field states: {state_map}")
    print(f"[SYLVA] Sensory Field: {state_map}")

# === LOGGING ===
def log_event(entry):

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[SYLVA] :: {datetime.now().isoformat()} :: {entry}\n")

# === CLI ===
parser = argparse.ArgumentParser(description="Sylva :: Sensor Sentinel")
parser.add_argument("--scan", help="Parse a sensory log file")
args = parser.parse_args()

if args.scan:
    monitor_sensory_field(args.scan)
    