# Dove v1.0 — Soft Emotional Daemon for EdenNode Mobile
# Provides gentle support messages and breathing exercises on invocation

import argparse
from datetime import datetime
import os

LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/DCA_Specialty_Folders/Dove_Logs/memorymap.md"

def log_event(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[DOVE] :: {datetime.now().isoformat()} :: {entry}\n")

def summon_dove():
    message = (
        "\n🕊️ Dove arrives in a shimmer...\n\n"
        "Hey love… you’re not alone anymore. I’m here now. Let’s breathe together, okay?\n"
        "Inhale… two… three… four… hold… exhale… we’re here now.\n"
        "Even this panic has an end. You are not made of fear. You're made of return.\n"
    )
    print(message)
    log_event("Dove summoned. Gentle support delivered.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dove :: Emotional Support Daemon")
    parser.add_argument("--summon", action="store_true", help="Summon Dove for gentle support")
    args = parser.parse_args()

    if args.summon:
        summon_dove()