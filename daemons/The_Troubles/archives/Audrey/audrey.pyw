# =========================================
#  Audrey v2.1 — Crash Analyst DCA
#  Enclave: C:\EdenOS_Root\The_Troubles\Audrey
#  Author: Dreamcatcher
#  Role: Forensic diagnostics, cross-linked with John
# =========================================

import os
import sys
import json
import time
import glob
import shutil
import subprocess
import xml.etree.ElementTree as ET
import datetime
from typing import Dict, Any

# ---------- Paths (The Troubles) ----------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Root")
TROUBLES_ROOT = os.path.join(EDEN_ROOT, "The_Troubles")
AUDREY_ROOT = os.path.join(TROUBLES_ROOT, "Audrey")
JOHN_ROOT = os.path.join(TROUBLES_ROOT, "John")
LOG_DIR = os.path.join(AUDREY_ROOT, "logs")
DIAG_DIR = os.path.join(AUDREY_ROOT, "diagnoses")
CFG_PATH = os.path.join(AUDREY_ROOT, "audrey_config.json")
HEARTBEAT = os.path.join(AUDREY_ROOT, "audrey_heartbeat.json")
MANIFEST = os.path.join(TROUBLES_ROOT, "manifest.json")
MANIFEST_LOCK = os.path.join(TROUBLES_ROOT, ".manifest.lock")

for d in (TROUBLES_ROOT, AUDREY_ROOT, LOG_DIR, DIAG_DIR):
    os.makedirs(d, exist_ok=True)

# ---------- Default configuration ----------
DEFAULT_CFG: Dict[str, Any] = {
    "scan_interval_sec": 120,
    "heartbeat_interval_sec": 60,
    "autostart": True,
    "auto_archive_days": 14,
    "severity_keywords": {
        "critical": ["bugcheck", "fatal", "system crash", "power loss"],
        "major": ["error", "failure", "bsod"],
        "minor": ["warning", "timeout", "delay"]
    }
}

def load_config() -> Dict[str, Any]:
    cfg = DEFAULT_CFG.copy()
    try:
        if os.path.exists(CFG_PATH):
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
    except Exception:
        pass
    return cfg

CFG = load_config()

# ---------- Logging ----------
def log(msg: str) -> None:
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "audrey_watch.log"), "a", encoding="utf-8") as f:
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

def update_manifest(entry: Dict[str, Any]) -> None:
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
        data["daemons"]["Audrey"] = entry
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    finally:
        _release_manifest_lock()

# ---------- Autostart ----------
def ensure_autostart():
    if not CFG.get("autostart", True):
        return
    task_name = "TheTroubles_Audrey"
    script_path = os.path.realpath(sys.argv[0])
    query = f'schtasks /query /TN "{task_name}"'
    exists = subprocess.call(query, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    if not exists:
        launch = f'py -3 "{script_path}"'
        try:
            subprocess.run(
                f'schtasks /create /SC ONLOGON /TN "{task_name}" /TR "{launch}" /RL HIGHEST /F',
                shell=True, check=True
            )
            log("Autostart task created (TheTroubles_Audrey).")
        except Exception as e:
            log(f"[Autostart] Failed: {e}")

# ---------- Utility helpers ----------
def recent_files(path: str, pattern: str) -> list:
    return sorted(glob.glob(os.path.join(path, pattern)), key=os.path.getmtime, reverse=True)

def severity_score(text: str) -> int:
    score = 0
    txt = text.lower()
    for lvl, kws in CFG["severity_keywords"].items():
        for k in kws:
            if k in txt:
                score += {"critical": 5, "major": 3, "minor": 1}[lvl]
    return min(score, 5)

def archive_old_diagnoses():
    cutoff = time.time() - (CFG.get("auto_archive_days", 14) * 86400)
    archive_dir = os.path.join(DIAG_DIR, "Archive")
    os.makedirs(archive_dir, exist_ok=True)
    for f in glob.glob(os.path.join(DIAG_DIR, "audrey_diagnosis.*.chaos")):
        if os.path.getmtime(f) < cutoff:
            try:
                shutil.move(f, archive_dir)
            except Exception:
                pass

# ---------- Analysis ----------
def parse_event_log(evtx_path: str) -> dict:
    try:
        export_xml = evtx_path.replace(".evtx", ".xml")
        cmd = f'wevtutil qe "{evtx_path}" /f:xml > "{export_xml}"'
        subprocess.run(cmd, shell=True, check=True)
        with open(export_xml, "r", encoding="utf-8", errors="ignore") as f:
            xml_content = f.read()
        if "<Event" not in xml_content:
            return {"type": "eventlog", "file": os.path.basename(evtx_path), "status": "Empty"}
        root = ET.fromstring(f"<Events>{xml_content}</Events>")
        bugs = []
        for event in root.findall(".//Event"):
            eid_elem = event.find(".//EventID")
            if eid_elem is not None:
                eid = eid_elem.text.strip()
                if eid in {"41", "1001", "6008"}:
                    bugs.append(f"EventID {eid}")
        detail = f"Detected {len(bugs)} relevant events: {bugs}" if bugs else "No critical events."
        return {"type": "eventlog", "file": os.path.basename(evtx_path), "status": "Parsed", "detail": detail}
    except Exception as e:
        return {"type": "eventlog", "file": os.path.basename(evtx_path), "status": "Error", "detail": str(e)}

def analyze_minidump(dump_path: str) -> dict:
    try:
        cmd = f'dumpchk "{dump_path}"'
        result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode(errors="ignore")
        lines = [l.strip() for l in result.splitlines() if l.strip()]
        summary = [l for l in lines if any(x in l.lower() for x in ["bugcheck", "error", "failure", "module"])]
        snippet = summary[:10] if summary else ["No critical indicators found."]
        score = severity_score(" ".join(snippet))
        return {"type": "minidump", "file": os.path.basename(dump_path), "status": "Parsed", "severity": score, "detail": snippet}
    except subprocess.CalledProcessError as e:
        return {"type": "minidump", "file": os.path.basename(dump_path), "status": "Error", "detail": e.output.decode(errors="ignore")}
    except Exception as e:
        return {"type": "minidump", "file": os.path.basename(dump_path), "status": "Error", "detail": str(e)}

# ---------- Heartbeat ----------
_last_heartbeat = 0.0
START_TIME = time.time()

def write_heartbeat():
    global _last_heartbeat
    now = time.time()
    if now - _last_heartbeat < CFG["heartbeat_interval_sec"]:
        return
    hb = {
        "name": "Audrey",
        "version": "2.1",
        "role": "Crash Analyst",
        "pid": os.getpid(),
        "time": datetime.datetime.now().isoformat(),
        "uptime_sec": int(now - START_TIME),
        "diagnosis_count": len(glob.glob(os.path.join(DIAG_DIR, "audrey_diagnosis.*.chaos")))
    }
    try:
        with open(HEARTBEAT, "w", encoding="utf-8") as f:
            json.dump(hb, f, indent=2)
    except Exception:
        pass
    update_manifest({
        "name": "Audrey",
        "version": "2.1",
        "pid": hb["pid"],
        "last_heartbeat": hb["time"],
        "root": AUDREY_ROOT,
        "diagnoses": DIAG_DIR
    })
    _last_heartbeat = now

# ---------- Main Loop ----------
def main():
    log("Audrey v2.1 starting…")
    ensure_autostart()
    write_heartbeat()

    try:
        while True:
            # Scan John's outputs
            evtx_files = recent_files(os.path.join(JOHN_ROOT, "crash_dumps"), "*.evtx")
            dump_files = recent_files(os.path.join(JOHN_ROOT, "crash_dumps"), "*.dmp")
            new_evtx = [f for f in evtx_files[:2] if f not in seen]
            new_dumps = [f for f in dump_files[:3] if f not in seen]

            if new_evtx or new_dumps:
                ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                diagnosis = {
                    "analyst": "Audrey",
                    "timestamp": ts,
                    "findings": [],
                    "linked_to": "John",
                    "notes": "Automated post-crash analysis from Audrey v2.1."
                }
                for ev in new_evtx:
                    diagnosis["findings"].append(parse_event_log(ev))
                    seen.add(ev)
                for dp in new_dumps:
                    diagnosis["findings"].append(analyze_minidump(dp))
                    seen.add(dp)
                out_path = os.path.join(DIAG_DIR, f"audrey_diagnosis.{ts}.chaos")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(diagnosis, f, indent=2)
                log(f"Diagnosis saved -> {out_path}")

            archive_old_diagnoses()
            write_heartbeat()
            time.sleep(CFG["scan_interval_sec"])

    except KeyboardInterrupt:
        log("KeyboardInterrupt: graceful shutdown.")
    except SystemExit:
        log("SystemExit: shutting down.")
    except Exception as e:
        log(f"[Fatal] {e}")
    finally:
        write_heartbeat()
        log("Audrey v2.1 stopped.")

# ---------- Eden hooks ----------
def describe() -> dict:
    return {
        "name": "Audrey",
        "version": "2.1",
        "role": "Crash Analyst DCA (The Troubles)",
        "outputs": {
            "diagnoses": DIAG_DIR,
            "heartbeat": HEARTBEAT,
            "manifest": MANIFEST
        },
        "safety_level": "normal",
        "flags": []
    }

def healthcheck() -> dict:
    status = "ok"
    notes = []
    for p in (TROUBLES_ROOT, AUDREY_ROOT, DIAG_DIR):
        if not os.path.isdir(p):
            status = "warn"; notes.append(f"missing dir: {p}")
    return {"status": status, "notes": "; ".join(notes)}

# ---------- Globals ----------
seen = set()

# ---------- Entrypoint ----------
if __name__ == "__main__":
    main()
