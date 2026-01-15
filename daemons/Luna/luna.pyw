# =========================================
#  Luna v1.0 — The Voice of the Troubles
#  Enclave: C:\EdenOS_Root\The_Troubles\Luna
#  Author: Dreamcatcher
#  Role: Night-watch, summary-keeper, and gentle alarm bell
# =========================================

import os
import sys
import json
import time
import datetime
from typing import Dict, Any

try:
    from TTS.api import TTS          # coqui-tts
    _TTS_OK = True
except Exception:
    _TTS_OK = False

# ---------- Directories ----------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Root")
TROUBLES_ROOT = os.path.join(EDEN_ROOT, "The_Troubles")
LUNA_ROOT = os.path.join(TROUBLES_ROOT, "Luna")
LOG_DIR = os.path.join(LUNA_ROOT, "logs")
REPORT_DIR = os.path.join(LUNA_ROOT, "reports")
CFG_PATH = os.path.join(LUNA_ROOT, "luna_config.json")
HEARTBEAT = os.path.join(LUNA_ROOT, "luna_heartbeat.json")
MANIFEST = os.path.join(TROUBLES_ROOT, "manifest.json")
for d in (LUNA_ROOT, LOG_DIR, REPORT_DIR):
    os.makedirs(d, exist_ok=True)

# ---------- Config ----------
DEFAULT_CFG: Dict[str, Any] = {
    "scan_interval_sec": 180,
    "heartbeat_interval_sec": 60,
    "speak_on_issue": True,
    "model_name": "tts_models/en/ljspeech/tacotron2-DDC",
    "voice_gain": 1.0
}

def load_cfg():
    cfg = DEFAULT_CFG.copy()
    if os.path.exists(CFG_PATH):
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                cfg.update(json.load(f))
        except Exception:
            pass
    return cfg

CFG = load_cfg()

# ---------- Logging ----------
def log(msg: str):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "luna_watch.log"), "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {msg}\n")

# ---------- Speaking ----------
def say(text: str):
    if not CFG.get("speak_on_issue", True) or not _TTS_OK:
        log(f"[Silent] {text}")
        return
    try:
        tts = TTS(model_name=CFG["model_name"])
        tts.tts_to_file(text=text, file_path=os.path.join(LOG_DIR, "alert.wav"))
        os.system(f'start "" "{os.path.join(LOG_DIR, "alert.wav")}"')
        log(f"[Voice] {text}")
    except Exception as e:
        log(f"[VoiceError] {e}")

# ---------- Heartbeat Summaries ----------
def gather_heartbeats():
    hb_paths = {
        "John": os.path.join(TROUBLES_ROOT, "John", "john_heartbeat.json"),
        "Audrey": os.path.join(TROUBLES_ROOT, "Audrey", "audrey_heartbeat.json"),
        "Nathan": os.path.join(TROUBLES_ROOT, "Nathan", "nathan_heartbeat.json"),
        "Duke": os.path.join(TROUBLES_ROOT, "Duke", "duke_heartbeat.json")
    }
    data = {}
    for name, path in hb_paths.items():
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data[name] = json.load(f)
            except Exception as e:
                data[name] = {"error": str(e)}
        else:
            data[name] = {"status": "missing"}
    return data

def check_for_issues(heartbeats):
    issues = []
    for name, hb in heartbeats.items():
        if "error" in hb or hb.get("status") == "missing":
            issues.append(f"{name} is missing or corrupted.")
        elif "summary" in hb and not hb["summary"].get("ok", True):
            issues.append(f"{name} reports warnings ({hb['summary'].get('warnings', '?')} issues).")
    return issues

# ---------- Heartbeat Writer ----------
_last_hb = 0.0
START_TIME = time.time()

def write_heartbeat(summary):
    global _last_hb
    now = time.time()
    if now - _last_hb < CFG["heartbeat_interval_sec"]:
        return
    hb = {
        "name": "Luna",
        "version": "1.0",
        "role": "Voice & Summary",
        "pid": os.getpid(),
        "time": datetime.datetime.now().isoformat(),
        "uptime_sec": int(now - START_TIME),
        "last_summary": summary
    }
    with open(HEARTBEAT, "w", encoding="utf-8") as f:
        json.dump(hb, f, indent=2)
    _last_hb = now

# ---------- Main ----------
def main():
    log("Luna v1.0 online — watching quietly.")
    try:
        while True:
            hbs = gather_heartbeats()
            issues = check_for_issues(hbs)
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            summary_path = os.path.join(REPORT_DIR, f"luna_summary.{ts}.chaos")
            with open(summary_path, "w", encoding="utf-8") as f:
                json.dump({"timestamp": ts, "issues": issues, "heartbeats": hbs}, f, indent=2)
            log(f"Summary written -> {summary_path}")

            if issues:
                msg = f"I detected {len(issues)} issue(s): " + "; ".join(issues)
                log(msg)
                say("Something’s wrong in The Troubles.")
                say(msg)
            else:
                log("All is calm. The Troubles rest easy.")

            write_heartbeat(summary_path)
            time.sleep(CFG["scan_interval_sec"])

    except KeyboardInterrupt:
        log("Shutdown request — Luna resting.")
    except Exception as e:
        log(f"[Fatal] {e}")
        say("A fatal error occurred in Luna.")
    finally:
        write_heartbeat("final")
        log("Luna stopped.")

# ---------- Entrypoint ----------
if __name__ == "__main__":
    main()
