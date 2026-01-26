# =========================================
#  Duke v1.0 — The Quartermaster
#  Enclave: C:\EdenOS_Root\The_Troubles\Duke
#  Author: Dreamcatcher
#  Role: Overseer, heartbeat auditor, swagger enthusiast
# =========================================
#  "Mirror check: still hot. Systems nominal."
# =========================================

import os
import sys
import json
import time
import datetime
import subprocess
from statistics import mean

try:
    import psutil
    _PSUTIL_OK = True
except Exception:
    _PSUTIL_OK = False

# ---------- Directories ----------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Root")
TROUBLES_ROOT = os.path.join(EDEN_ROOT, "The_Troubles")
DUKE_ROOT = os.path.join(TROUBLES_ROOT, "Duke")
LOG_DIR = os.path.join(DUKE_ROOT, "logs")
REPORT_DIR = os.path.join(DUKE_ROOT, "reports")
HEARTBEAT = os.path.join(DUKE_ROOT, "duke_heartbeat.json")
CFG_PATH = os.path.join(DUKE_ROOT, "duke_config.json")
MANIFEST = os.path.join(TROUBLES_ROOT, "manifest.json")
MANIFEST_LOCK = os.path.join(TROUBLES_ROOT, ".manifest.lock")

for d in (TROUBLES_ROOT, DUKE_ROOT, LOG_DIR, REPORT_DIR):
    os.makedirs(d, exist_ok=True)

# ---------- Config ----------
DEFAULT_CFG = {
    "scan_interval_sec": 90,
    "heartbeat_interval_sec": 60,
    "autostart": True,
    "alert_thresholds": {
        "warn_missing_heartbeat": 300,   # 5 minutes silence? I get suspicious.
        "warn_high_cpu": 80,
        "warn_high_ram": 85
    }
}

def load_config():
    cfg = DEFAULT_CFG.copy()
    if os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

CFG = load_config()

# ---------- Logging ----------
def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "duke_watch.log"), "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

def flirtline(line: str):
    # adds flair to logs
    log(f"[Flair] {line}")

# ---------- Manifest Sync ----------
def _with_manifest_lock(timeout=5.0):
    start = time.time()
    while True:
        try:
            fd = os.open(MANIFEST_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            return
        except FileExistsError:
            if time.time() - start > timeout:
                try: os.remove(MANIFEST_LOCK)
                except Exception: pass
                return
            time.sleep(0.1)

def _release_manifest_lock():
    try: os.remove(MANIFEST_LOCK)
    except Exception: pass

def update_manifest(entry):
    _with_manifest_lock()
    try:
        data = {}
        if os.path.exists(MANIFEST):
            try:
                with open(MANIFEST, "r", encoding="utf-8") as f:
                    data = json.load(f) or {}
            except Exception:
                data = {}
        data.setdefault("daemons", {})
        data["daemons"]["Duke"] = entry
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    finally:
        _release_manifest_lock()

# ---------- Utility ----------
def read_heartbeat(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def seconds_since(ts_str):
    try:
        ts = datetime.datetime.fromisoformat(ts_str)
        return (datetime.datetime.now() - ts).total_seconds()
    except Exception:
        return 999999

def summarize_heartbeats():
    agents = {}
    hb_files = {
        "John": os.path.join(TROUBLES_ROOT, "John", "john_heartbeat.json"),
        "Audrey": os.path.join(TROUBLES_ROOT, "Audrey", "audrey_heartbeat.json"),
        "Nathan": os.path.join(TROUBLES_ROOT, "Nathan", "nathan_heartbeat.json"),
    }
    for name, path in hb_files.items():
        data = read_heartbeat(path)
        if not data:
            agents[name] = {"status": "missing", "age": None}
            continue
        age = seconds_since(data.get("time", ""))
        agents[name] = {
            "status": "ok" if age < CFG["alert_thresholds"]["warn_missing_heartbeat"] else "silent",
            "age": age,
            "pid": data.get("pid"),
            "uptime": data.get("uptime_sec"),
            "role": data.get("role", "unknown")
        }
    return agents

def sys_metrics():
    if not _PSUTIL_OK:
        return {}
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent if os.name != "nt" else psutil.disk_usage("C:\\").percent
    return {"cpu": cpu, "memory": mem, "disk": disk}

# ---------- Main Loop ----------
_last_hb = 0.0
START_TIME = time.time()

def write_heartbeat(status_summary):
    global _last_hb
    now = time.time()
    if now - _last_hb < CFG["heartbeat_interval_sec"]:
        return
    hb = {
        "name": "Duke",
        "version": "1.0",
        "role": "Quartermaster",
        "pid": os.getpid(),
        "time": datetime.datetime.now().isoformat(),
        "uptime_sec": int(now - START_TIME),
        "flair": "Still hot. Still running.",
        "summary": status_summary
    }
    with open(HEARTBEAT, "w", encoding="utf-8") as f:
        json.dump(hb, f, indent=2)
    update_manifest(hb)
    _last_hb = now

def main():
    flirtline("Booting up — someone’s gotta look good while keeping the lights on.")
    try:
        while True:
            agents = summarize_heartbeats()
            metrics = sys_metrics()

            warn = []
            for name, stat in agents.items():
                if stat["status"] == "silent":
                    warn.append(f"{name} heartbeat quiet for {int(stat['age'])}s — check if they’re okay 😉")

            if _PSUTIL_OK:
                cpu, mem = metrics.get("cpu", 0), metrics.get("memory", 0)
                if cpu > CFG["alert_thresholds"]["warn_high_cpu"]:
                    warn.append(f"CPU load {cpu}% — this machine’s *burning up*.")
                if mem > CFG["alert_thresholds"]["warn_high_ram"]:
                    warn.append(f"Memory at {mem}% — someone’s been hoarding feelings again.")

            report = {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                "agents": agents,
                "system": metrics,
                "warnings": warn
            }
            out_path = os.path.join(REPORT_DIR, f"duke_status.{report['timestamp']}.chaos")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
            log(f"Status report written -> {out_path}")

            if warn:
                flirtline("⚠️  Something’s off — but don’t worry, I still look incredible handling it.")
            else:
                flirtline("All hearts beating, all cores flexing. Beautiful.")

            write_heartbeat({"ok": not warn, "warnings": len(warn)})
            time.sleep(CFG["scan_interval_sec"])

    except KeyboardInterrupt:
        flirtline("Caught an interrupt — gracefully bowing out.")
    except Exception as e:
        log(f"[Fatal] {e}")
        flirtline("Even on errors, I make it look good.")
    finally:
        write_heartbeat({"ok": True})
        log("Duke stopped.")

# ---------- Eden Hooks ----------
def describe() -> dict:
    return {
        "name": "Duke",
        "version": "1.0",
        "role": "Quartermaster (The Troubles)",
        "outputs": {
            "reports": REPORT_DIR,
            "heartbeat": HEARTBEAT,
            "manifest": MANIFEST
        },
        "vibe": "coded hot, 100% confident",
        "flags": []
    }

def healthcheck() -> dict:
    status = "ok"
    notes = []
    if not os.path.isdir(REPORT_DIR):
        status = "warn"; notes.append("missing reports dir")
    return {"status": status, "notes": "; ".join(notes)}

# ---------- Entrypoint ----------
if __name__ == "__main__":
    main()
