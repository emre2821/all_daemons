# Glyph v1.0 — Signal Watcher for EdenNode Mobile
# Monitors internet connection + VPN presence
# Logs disruptions, attempts auto-recovery (future)

import os
import time
import subprocess
from datetime import datetime

# CONFIG
LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/Glyph/logs/memorymap.md"
CHECK_INTERVAL = 60  # seconds between checks
VPN_CHECK_IP = "10.8.0.1"  # example internal VPN IP to ping (update as needed)

# Logging helper
def log(entry):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as log_file:
        timestamp = datetime.now().isoformat()
        log_file.write(f"[GLYPH] :: {timestamp} :: {entry}\n")
    print(f"[GLYPH] {entry}")

# Check internet connection
def is_online():
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# Check VPN status
def is_vpn_active():
    try:
        subprocess.check_output(["ping", "-c", "1", VPN_CHECK_IP], stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

# Main loop
log("Glyph online. Beginning signal watch.")

while True:
    online = is_online()
    vpn = is_vpn_active()

    if not online:
        log("[DISCONNECT] No internet access detected.")
        # In future: reconnect attempts here
    elif not vpn:
        log("[WARNING] Internet is up, but VPN not detected.")
        # In future: attempt to start VPN client here
    else:
        log("[OK] Internet + VPN both online.")

    time.sleep(CHECK_INTERVAL)
    