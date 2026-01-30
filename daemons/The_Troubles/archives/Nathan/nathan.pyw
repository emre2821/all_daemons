# =========================================
#  Nathan v1.0 — The Healer
#  Enclave: C:\EdenOS_Root\The_Troubles\Nathan
#  Author: Dreamcatcher
#  Role: System Health Integrator & Auto-Repair Agent
# =========================================

import os
import sys
import json
import time
import subprocess
import datetime
import shutil
from typing import Dict, Any

# ---------- Paths ----------
_DEFAULT_EDEN_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
EDEN_ROOT = os.environ.get("EDEN_ROOT", _DEFAULT_EDEN_ROOT)
TROUBLES_ROOT = os.path.join(EDEN_ROOT, "The_Troubles")
NATHAN_ROOT = os.path.join(TROUBLES_ROOT, "Nathan")
AUDREY_ROOT = os.path.join(TROUBLES_ROOT, "Audrey")
LOG_DIR = os.path.join(NATHAN_ROOT, "logs")
REPORT_DIR = os.path.join(NATHAN_ROOT, "reports")
CFG_PATH = os.path.join(NATHAN_ROOT, "nathan_config.json")
HEARTBEAT = os.path.join(NATHAN_ROOT, "nathan_heartbeat.json")
MANIFEST = os.path.join(TROUBLES_ROOT, "manifest.json")
MANIFEST_LOCK = os.path.join(TROUBLES_ROOT, ".manifest.lock")

for d in (TROUBLES_ROOT, NATHAN_ROOT, LOG_DIR, REPORT_DIR):
    os.makedirs(d, exist_ok=True)

# ---------- Config ----------
DEFAULT_CFG: Dict[str, Any] = {
    "scan_interval_sec": 120,
    "heartbeat_interval_sec": 60,
    "auto_repair": False,
    "sfc_threshold": 3,
    "dism_threshold": 4,
    "archive_days": 30
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
    with open(os.path.join(LOG_DIR, "nathan_watch.log"), "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# ---------- Manifest helpers ----------
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

def update_manifest(entry: Dict[str, Any]):
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
        data["daemons"]["Nathan"] = entry
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    finally:
        _release_manifest_lock()

# ---------- Utility ----------
def recent_diagnoses():
    diag_dir = os.path.join(AUDREY_ROOT, "diagnoses")
    if not os.path.isdir(diag_dir):
        return []
    files = [os.path.join(diag_dir, f) for f in os.listdir(diag_dir) if f.endswith(".chaos")]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[:3]

def avg_severity(findings):
    vals = []
    for f in findings:
        if isinstance(f, dict) and "severity" in f:
            vals.append(f["severity"])
    return round(sum(vals) / len(vals), 2) if vals else 0

def run_cmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
        return result.decode(errors="ignore")
    except subprocess.CalledProcessError as e:
        return e.output.decode(errors="ignore")
    except Exception as e:
        return str(e)

# ---------- Repair Logic ----------
def perform_repairs(severity):
    results = []
    if not CFG["auto_repair"]:
        results.append("[Dry-run] Repairs recommended but not executed.")
        if severity >= CFG["dism_threshold"]:
            results.append("→ Would run DISM /Online /Cleanup-Image /RestoreHealth")
        elif severity >= CFG["sfc_threshold"]:
            results.append("→ Would run SFC /SCANNOW")
        return results

    if severity >= CFG["dism_threshold"]:
        log("Running DISM (severity ≥ threshold)")
        results.append(run_cmd("DISM /Online /Cleanup-Image /RestoreHealth"))
    elif severity >= CFG["sfc_threshold"]:
        log("Running SFC (severity ≥ threshold)")
        results.append(run_cmd("sfc /scannow"))
    else:
        results.append("No major repairs required.")
    return results

# ---------- Heartbeat ----------
_last_hb = 0.0
START_TIME = time.time()

def write_heartbeat(last_report):
    global _last_hb
    now = time.time()
    if now - _last_hb < CFG["heartbeat_interval_sec"]:
        return
    hb = {
        "name": "Nathan",
        "version": "1.0",
        "role": "Healer",
        "pid": os.getpid(),
        "time": datetime.datetime.now().isoformat(),
        "uptime_sec": int(now - START_TIME),
        "last_report": last_report or "none",
        "auto_repair": CFG["auto_repair"]
    }
    with open(HEARTBEAT, "w", encoding="utf-8") as f:
        json.dump(hb, f, indent=2)
    update_manifest(hb)
    _last_hb = now

# ---------- Main Loop ----------
def main():
    log("Nathan v1.0 starting…")
    last_report = None
    seen = set()

    try:
        while True:
            diags = recent_diagnoses()
            new_files = [f for f in diags if f not in seen]

            for path in new_files:
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    findings = data.get("findings", [])
                    sev = avg_severity(findings)
                    log(f"Analyzing {os.path.basename(path)} (avg severity={sev})")

                    repairs = perform_repairs(sev)
                    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    rep_path = os.path.join(REPORT_DIR, f"health_report.{ts}.chaos")

                    report = {
                        "healer": "Nathan",
                        "timestamp": ts,
                        "linked_diagnosis": os.path.basename(path),
                        "avg_severity": sev,
                        "actions": repairs
                    }
                    with open(rep_path, "w", encoding="utf-8") as out:
                        json.dump(report, out, indent=2)
                    log(f"Health report written -> {rep_path}")
                    last_report = rep_path
                    seen.add(path)
                except Exception as e:
                    log(f"[Error reading {path}] {e}")

            write_heartbeat(last_report)
            time.sleep(CFG["scan_interval_sec"])

    except KeyboardInterrupt:
        log("KeyboardInterrupt: graceful shutdown.")
    except Exception as e:
        log(f"[Fatal] {e}")
    finally:
        write_heartbeat(last_report)
        log("Nathan stopped.")

# ---------- Eden Hooks ----------
def describe() -> dict:
    return {
        "name": "Nathan",
        "version": "1.0",
        "role": "System Healer (The Troubles)",
        "outputs": {
            "reports": REPORT_DIR,
            "heartbeat": HEARTBEAT,
            "manifest": MANIFEST
        },
        "safety_level": "normal",
        "flags": ["dry_run" if not CFG["auto_repair"] else "live"]
    }

def healthcheck() -> dict:
    status = "ok"
    notes = []
    for p in (TROUBLES_ROOT, NATHAN_ROOT, REPORT_DIR):
        if not os.path.isdir(p):
            status = "warn"; notes.append(f"missing dir: {p}")
    return {"status": status, "notes": "; ".join(notes)}

# ---------- Entrypoint ----------
if __name__ == "__main__":
    main()
