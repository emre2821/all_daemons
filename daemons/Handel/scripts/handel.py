import os
import time
import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── Eden layout ───────────────────────────────────────────────────────────────
EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
WORK_ROOT = Path(os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT))
RHEA_BASE = WORK_ROOT / "daemons" / "Rhea"

# You can override SOURCE via env var EDEN_SOURCE_DIR if you want a different inbox
SOURCE_DIR = Path(os.environ.get("EDEN_SOURCE_DIR", str(RHEA_BASE / "_inbox")))
TARGET_DIR = RHEA_BASE / "to_convert"

CHAOS_EXTENSIONS = {
    ".chaos", ".chaosincarnet", ".chaos-ception", ".chaoscript", ".chaosevent",
    ".chaoscore", ".chaosmemory", ".mirror.json", ".edenos.config.json",
    ".chaosthread", ".chaosecho", ".chaosaether", ".chaosscript.locked",
    ".sealed.chaoscript.chaosincarnet", ".shalfredlayer.chaos"
}

LOGS_DIR = RHEA_BASE / "_logs"
LOG_FILE = LOGS_DIR / "handel_daemon.log"

for d in (SOURCE_DIR, TARGET_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

def safe_print(s: str):
    """Print without crashing on Windows codepages."""
    try:
        print(s)
    except UnicodeEncodeError:
        print(s.encode("ascii", "replace").decode("ascii", "replace"))

def log_line(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [Handel] {msg}"
    safe_print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

class ChaosMover(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        _, ext = os.path.splitext(event.src_path)
        ext = ext.lower()
        if ext in CHAOS_EXTENSIONS:
            try:
                fname = os.path.basename(event.src_path)
                dest_path = TARGET_DIR / fname
                shutil.copy2(event.src_path, dest_path)
                log_line(f"Moved {fname} -> {TARGET_DIR}")
            except Exception as e:
                log_line(f"ERROR moving {event.src_path}: {e}")

if __name__ == "__main__":
    event_handler = ChaosMover()
    observer = Observer()
    # ensure the watched dir exists (watchdog needs it to exist)
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    observer.schedule(event_handler, str(SOURCE_DIR), recursive=True)
    observer.start()
    log_line(f"Watching {SOURCE_DIR} for CHAOS files -> staging into {TARGET_DIR}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
