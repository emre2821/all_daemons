# =========================================
#  John v2.1 — Device & Shell Integrity Daemon
#  Enclave: C:\EdenOS_Root\The_Troubles\John
#  Author: Dreamcatcher
#  Role: BSOD aftermath + explorer watchdog + manifest heartbeat
# =========================================

import os
import sys
import time
import json
import shutil
import subprocess
import platform
import datetime
from typing import Dict, Any

# ---------- Optional deps ----------
try:
    import psutil
    _PSUTIL_OK = True
except Exception:
    _PSUTIL_OK = False

# ---------- Paths (The Troubles) ----------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Root")
TROUBLES_ROOT = os.path.join(EDEN_ROOT, "The_Troubles")
JOHN_ROOT = os.path.join(TROUBLES_ROOT, "John")
LOG_DIR = os.path.join(JOHN_ROOT, "logs")
DUMP_DIR = os.path.join(JOHN_ROOT, "crash_dumps")
CFG_PATH = os.path.join(JOHN_ROOT, "john_config.json")
HEARTBEAT = os.path.join(JOHN_ROOT, "john_heartbeat.json")
BSOD_MARK = os.path.join(JOHN_ROOT, "last_bsod_logged.txt")
WATCH_LOG = os.path.join(LOG_DIR, "john_watch.log")
MANIFEST = os.path.join(TROUBLES_ROOT, "manifest.json")
MANIFEST_LOCK = os.path.join(TROUBLES_ROOT, ".manifest.lock")

for d in (TROUBLES_ROOT, JOHN_ROOT, LOG_DIR, DUMP_DIR):
    os.makedirs(d, exist_ok=True)

# ---------- Defaults / Config ----------
DEFAULT_CFG: Dict[str, Any] = {
    "check_interval_sec": 5,          # main loop tick
    "heartbeat_interval_sec": 60,     # write heartbeat cadence
    "explorer_safe_delay_sec": 15,    # wait this long before restarting explorer
    "autostart": True,                # create Scheduled Task at first run
    "enforce_shell_registry": True,   # ensure Winlogon Shell/Userinit are correct
    "device_watch": True,             # log drive add/remove like v1
    "event_ids_query": [41, 1001, 6008]  # what to export from System.evtx on BSOD
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
    with open(WATCH_LOG, "a", encoding="utf-8") as f:
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
                # stale lock
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
        data["daemons"]["John"] = entry
        with open(MANIFEST, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    finally:
        _release_manifest_lock()

# ---------- Autostart ----------
def ensure_autostart():
    if platform.system() != "Windows" or not CFG.get("autostart", True):
        return
    task_name = "TheTroubles_John"
    script_path = os.path.realpath(sys.argv[0])
    query = f'schtasks /query /TN "{task_name}"'
    exists = subprocess.call(query, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    if not exists:
        # Prefer py launcher if present; fall back to python
        launch = f'py -3 "{script_path}"'
        try:
            subprocess.run(
                f'schtasks /create /SC ONLOGON /TN "{task_name}" /TR "{launch}" /RL HIGHEST /F',
                shell=True, check=True
            )
            log("Autostart task created (TheTroubles_John).")
        except Exception as e:
            log(f"[Autostart] Failed to create task: {e}")

# ---------- Registry enforcement ----------
def enforce_shell_registry():
    if platform.system() != "Windows" or not CFG.get("enforce_shell_registry", True):
        return
    try:
        # Shell = explorer.exe
        subprocess.run(
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" '
            '/v Shell /t REG_SZ /d explorer.exe /f',
            shell=True, check=True
        )
        # Userinit = C:\Windows\system32\userinit.exe,
        subprocess.run(
            'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon" '
            '/v Userinit /t REG_SZ /d "C:\\Windows\\system32\\userinit.exe," /f',
            shell=True, check=True
        )
        log("Winlogon Shell/Userinit verified.")
    except Exception as e:
        log(f"[Registry] Enforcement failed: {e}")

# ---------- BSOD detection & capture ----------
def _current_boot_time_str():
    if _PSUTIL_OK:
        return str(datetime.datetime.fromtimestamp(psutil.boot_time()))
    return str(datetime.datetime.now())

def bsod_occurred_this_boot() -> bool:
    if not _PSUTIL_OK:
        return False
    cur = _current_boot_time_str()
    if not os.path.exists(BSOD_MARK):
        return True
    try:
        with open(BSOD_MARK, "r") as f:
            last = f.read().strip()
        return last != cur
    except Exception:
        return True

def mark_bsod_logged():
    try:
        with open(BSOD_MARK, "w") as f:
            f.write(_current_boot_time_str())
    except Exception:
        pass

def export_event_logs(timestamp: str):
    try:
        q_ids = CFG.get("event_ids_query", [41, 1001, 6008])
        query = " or ".join([f"EventID={i}" for i in q_ids])
        evtx_path = os.path.join(DUMP_DIR, f"eventlog_{timestamp}.evtx")
        cmd = f'wevtutil epl System "{evtx_path}" /q:"*[System[({query})]]"'
        subprocess.run(cmd, shell=True, check=True)
        log(f"Exported System.evtx (ids {q_ids}) -> {evtx_path}")
    except Exception as e:
        log(f"[EventExport] {e}")

def copy_minidumps(timestamp: str):
    try:
        minidump_dir = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "Minidump")
        if not os.path.isdir(minidump_dir):
            return
        for fn in os.listdir(minidump_dir):
            if fn.lower().endswith(".dmp"):
                src = os.path.join(minidump_dir, fn)
                dst = os.path.join(DUMP_DIR, f"{timestamp}_{fn}")
                try:
                    shutil.copy(src, dst)
                    log(f"Copied dump {fn}")
                except Exception as e:
                    log(f"[DumpCopy] {fn}: {e}")
    except Exception as e:
        log(f"[DumpWalk] {e}")

def create_aftermath_log():
    ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(LOG_DIR, f"bsod_aftermath.{ts}.chaos")
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("::crash.log::\n")
            f.write(f"- Timestamp: {ts}\n")
            f.write(f"- OS: {platform.platform()}\n")
            f.write(f"- Boot Time: {_current_boot_time_str()}\n")
            f.write(f"- Daemon: John v2.1\n")
            f.write("- NOTE: Autogenerated post-boot after suspected crash/bugcheck.\n")
        export_event_logs(ts)
        copy_minidumps(ts)
        log(f"Created aftermath log -> {path}")
    except Exception as e:
        log(f"[Aftermath] {e}")

# ---------- Explorer watchdog ----------
def explorer_running() -> bool:
    if not _PSUTIL_OK:
        # fall back: try to query tasklist
        try:
            out = subprocess.check_output('tasklist /FI "IMAGENAME eq explorer.exe"', shell=True).decode(errors="ignore")
            return "explorer.exe" in out.lower()
        except Exception:
            return False
    for p in psutil.process_iter(attrs=["name"]):
        try:
            if p.info["name"] and p.info["name"].lower() == "explorer.exe":
                return True
        except Exception:
            pass
    return False

def restart_explorer():
    try:
        subprocess.run("taskkill /f /im explorer.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(2)
        subprocess.Popen("explorer.exe", shell=True)
        log("Explorer restarted.")
    except Exception as e:
        log(f"[ExplorerRestart] {e}")

# ---------- Device watch (drives) ----------
_prev_drives = set()
def _get_drives():
    try:
        out = subprocess.check_output("wmic logicaldisk get name", shell=True).decode(errors="ignore")
        return {ln.strip() for ln in out.splitlines() if ln.strip() and "name" not in ln.lower()}
    except Exception:
        return set()

def device_watch_tick():
    global _prev_drives
    if not CFG.get("device_watch", True):
        return
    cur = _get_drives()
    added = cur - _prev_drives
    removed = _prev_drives - cur
    if added:
        for d in sorted(added):
            log(f"Device added: {d}")
    if removed:
        for d in sorted(removed):
            log(f"Device removed: {d}")
    _prev_drives = cur

# ---------- Heartbeat ----------
_last_heartbeat = 0.0
def write_heartbeat():
    global _last_heartbeat
    now = time.time()
    if now - _last_heartbeat < CFG["heartbeat_interval_sec"]:
        return
    hb = {
        "name": "John",
        "version": "2.1",
        "role": "Device & Shell Integrity",
        "pid": os.getpid(),
        "time": datetime.datetime.now().isoformat(),
        "uptime_sec": int(now - START_TIME),
        "explorer_running": explorer_running(),
        "paths": {
            "root": JOHN_ROOT,
            "logs": LOG_DIR,
            "crash_dumps": DUMP_DIR
        }
    }
    try:
        with open(HEARTBEAT, "w", encoding="utf-8") as f:
            json.dump(hb, f, indent=2)
    except Exception:
        pass
    update_manifest({
        "name": "John",
        "version": "2.1",
        "pid": hb["pid"],
        "last_heartbeat": hb["time"],
        "root": JOHN_ROOT,
        "logs": LOG_DIR
    })
    _last_heartbeat = now

# ---------- Main ----------
START_TIME = time.time()

def main():
    log("John v2.1 starting…")
    ensure_autostart()
    enforce_shell_registry()

    # First heartbeat + manifest registration
    write_heartbeat()

    # BSOD aftermath (once per unique boot)
    if _PSUTIL_OK and bsod_occurred_this_boot():
        log("Detected new boot sequence (possible crash). Generating aftermath package.")
        create_aftermath_log()
        mark_bsod_logged()

    # Explorer watchdog cadence
    missing_since = 0
    interval = CFG["check_interval_sec"]
    safe_delay = CFG["explorer_safe_delay_sec"]

    # seed device list
    if CFG.get("device_watch", True):
        globals()["_prev_drives"] = _get_drives()

    try:
        while True:
            time.sleep(interval)

            # explorer watchdog
            if explorer_running():
                missing_since = 0
            else:
                missing_since += interval
                if missing_since >= safe_delay:
                    log("Explorer missing beyond safe_delay — restarting.")
                    restart_explorer()
                    missing_since = 0

            # device change log
            device_watch_tick()

            # heartbeat
            write_heartbeat()

    except KeyboardInterrupt:
        log("KeyboardInterrupt: graceful shutdown.")
    except SystemExit:
        log("SystemExit: shutting down.")
    except Exception as e:
        log(f"[Fatal] {e}")
    finally:
        write_heartbeat()
        log("John v2.1 stopped.")

# ---------- Eden hooks ----------
def describe() -> dict:
    return {
        "name": "John",
        "version": "2.1",
        "role": "Device & Shell Integrity (The Troubles)",
        "outputs": {
            "logs": LOG_DIR,
            "crash_dumps": DUMP_DIR,
            "heartbeat": HEARTBEAT,
            "manifest": MANIFEST
        },
        "safety_level": "normal",
        "flags": []
    }

def healthcheck() -> dict:
    status = "ok"
    notes = []
    if platform.system() != "Windows":
        status = "warn"; notes.append("non-Windows host")
    if not _PSUTIL_OK:
        status = "warn"; notes.append("psutil missing (reduced BSOD detection fidelity)")
    for p in (TROUBLES_ROOT, JOHN_ROOT, LOG_DIR, DUMP_DIR):
        if not os.path.isdir(p):
            status = "warn"; notes.append(f"missing dir: {p}")
    return {"status": status, "notes": "; ".join(notes)}

# ---------- Entrypoint ----------
if __name__ == "__main__":
    main()
