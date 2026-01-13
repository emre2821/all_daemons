# Emberly v1.0 — Heat Sentinel for EdenNode Mobile
# Monitors system temperature logs and flags overheat risks

import os
import argparse
from datetime import datetime
from pathlib import Path


def setup_paths(log_path=None):
    """Setup paths based on provided log_path or detection"""

    if log_path is None:
        # Try to detect log path relative to current script
        current_dir = Path(__file__).parent
        possible_paths = [
            current_dir / "logs" / "memorymap.md",
            current_dir.parent / "logs" / "memorymap.md",
            Path("/Internal shared storage/Eden_Notes/Mobile_DCA/Emberly/logs/memorymap.md"),
            Path.cwd() / "logs" / "memorymap.md",
        ]

        for path in possible_paths:
            if path.exists():
                log_path = str(path)
                break

        # Fallback to original hardcoded path
        if log_path is None:
            log_path = "/Internal shared storage/Eden_Notes/Mobile_DCA/Emberly/logs/memorymap.md"

    return Path(log_path)


# === CONFIG ===
LOG_PATH = setup_paths()

# === CORE MONITOR ===
def monitor_temp(file_path):

    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read().lower()

    state = "normal"
    if "temp: high" in data or "overheat" in data:
        state = "overheat risk"
    elif "temp: low" in data or "cool" in data:
        state = "cooling"

    log_event(f"Temperature state: {state}")
    print(f"[EMBERLY] Temp Status: {state}")

# === LOGGING ===
def log_event(entry):

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[EMBERLY] :: {datetime.now().isoformat()} :: {entry}\n")

# === CLI ===
parser = argparse.ArgumentParser(description="Emberly :: Heat Sentinel")
parser.add_argument("--scan", help="Parse a temperature log file")
args = parser.parse_args()

if args.scan:
    monitor_temp(args.scan)
