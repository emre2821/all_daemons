# Luke v1.0 — Disk Keeper for EdenNode Mobile
# Monitors storage, logs usage, and optionally suggests cleanup

import os
import shutil
from datetime import datetime

# CONFIG
LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/Luke/logs/memorymap.md"
WARN_THRESHOLD = 0.9  # Warn when 90% full

# Logging helper
def log(entry):

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log_file:
        timestamp = datetime.now().isoformat()
        log_file.write(f"[LUKE] :: {timestamp} :: {entry}\n")
    print(f"[LUKE] {entry}")

# Check storage
def check_disk():

    total, used, free = shutil.disk_usage("/")
    percent_used = used / total
    log(f"Disk check: {used//(1024**2)}MB used / {total//(1024**2)}MB total ({percent_used*100:.1f}% used)")

    if percent_used >= WARN_THRESHOLD:
        log("[WARNING] Disk space low. Consider cleanup.")
    else:
        log("[OK] Storage within safe range.")

# Execute
check_disk()
