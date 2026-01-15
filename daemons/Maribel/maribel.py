import os
import shutil
import psutil
from datetime import datetime

# Harper - Watcher of Collapse
THRESHOLDS = {
    'cpu': 85.0,  # percentage
    'mem': 85.0,  # percentage
    'chaos_backlog': 10  # number of unprocessed .chaos files
}

WATCH_PATH = "./chaos_watch"
ALERT_LOG = "harper_alerts.log"
os.makedirs(WATCH_PATH, exist_ok=True)

def log_alert(reason, value):
    timestamp = datetime.now().isoformat()
    entry = f"[HARPER ALERT] {timestamp} :: {reason} = {value}%\n"
    with open(ALERT_LOG, 'a') as f:
        f.write(entry)
    print(entry.strip())

def check_system_pressure():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    backlog = len([f for f in os.listdir(WATCH_PATH) if f.endswith('.chaos')])

    if cpu > THRESHOLDS['cpu']:
        log_alert("High CPU", cpu)
    if mem > THRESHOLDS['mem']:
        log_alert("High Memory", mem)
    if backlog > THRESHOLDS['chaos_backlog']:
        log_alert("Backlog CHAOS files", backlog)

# Maribel - The Aether Courier
INBOX = "./aether_inbox"
OUTBOX = "./aether_outbox"
PROCESSED = "./aether_delivered"
os.makedirs(INBOX, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

def deliver_messages():
    for fname in os.listdir(OUTBOX):
        if fname.endswith(".aethermsg"):
            src = os.path.join(OUTBOX, fname)
            dest = os.path.join(INBOX, fname)
            shutil.copy2(src, dest)
            os.remove(src)
            print(f"[Maribel] Delivered: {fname}")

    for fname in os.listdir(INBOX):
        if fname.endswith(".aethermsg"):
            src = os.path.join(INBOX, fname)
            dest = os.path.join(PROCESSED, fname)
            shutil.move(src, dest)
            print(f"[Maribel] Processed: {fname}")

if __name__ == "__main__":
    print("Harper listens for fracture in the weave...")
    check_system_pressure()
    print("Harper rests. No immediate collapse detected.")

    print("\nMaribel walks the memory paths...")
    deliver_messages()
    print("Maribel bows. All messages carried.")
