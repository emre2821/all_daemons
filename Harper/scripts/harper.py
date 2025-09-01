import os
import shutil
import psutil
from datetime import datetime

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

if __name__ == "__main__":
    print("Harper listens for fracture in the weave...")
    check_system_pressure()
    print("Harper rests. No immediate collapse detected.")
