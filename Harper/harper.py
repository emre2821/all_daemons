import os
import shutil
from datetime import datetime

try:
    import psutil  # optional
import used for real CPU/mem
    _PSUTIL_OK = True
except Exception:
    _PSUTIL_OK = False

try:
    import sys
    sys.path.append(os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "all_daemons", "Daemon_tools", "scripts"))
    from eden_paths import daemon_out_dir  # type: ignore
    _OUT_DIR = daemon_out_dir("Harper")
except Exception:
    _OUT_DIR = os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "all_daemons", "Rhea", "_outbox", "Harper")
    os.makedirs(_OUT_DIR, exist_ok=True)

THRESHOLDS = {
    'cpu': 85.0,  # percentage
    'mem': 85.0,  # percentage
    'chaos_backlog': 10  # number of unprocessed .chaos files
}

WATCH_PATH = os.path.join(_OUT_DIR, "chaos_watch")
ALERT_LOG = os.path.join(_OUT_DIR, "harper_alerts.log")
os.makedirs(WATCH_PATH, exist_ok=True)

def log_alert(reason, value):

    timestamp = datetime.now().isoformat()
    entry = f"[HARPER ALERT] {timestamp} :: {reason} = {value}%\n"
    with open(ALERT_LOG, 'a') as f:
        f.write(entry)
    print(entry.strip())

def check_system_pressure():

    cpu = psutil.cpu_percent(interval=1) if _PSUTIL_OK else 0.0
    mem = psutil.virtual_memory().percent if _PSUTIL_OK else 0.0
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


def describe() -> dict:

    return {
        "name": "Harper",
        "role": "System-pressure watcher",
        "inputs": {"watch_path": WATCH_PATH},
        "outputs": {"alerts": ALERT_LOG},
        "flags": [],
        "safety_level": "normal",
    }


def healthcheck() -> dict:

    status = "ok"; notes = []
    if not _PSUTIL_OK:
        status = "warn"; notes.append("psutil not installed; CPU/mem disabled")
    try:
        os.makedirs(WATCH_PATH, exist_ok=True)
        with open(ALERT_LOG, 'a') as _:
            pass
    except Exception as e:
        if status == "ok": status = "warn"
        notes.append(f"log/write warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
