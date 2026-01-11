#!/usr/bin/env python3
import os
import shutil
import time
import threading
import argparse
from datetime import datetime

# Optional dependency for warmup daemon
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ Warning: 'psutil' not installed. Warmup daemon functionality will be disabled.")

# === Configuration ===
VERSION = "1.2"
BASE_DIR = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/DCA_Mobile/Scorchick"
DEFAULT_LOG_PATH = os.path.join(BASE_DIR, "logs/scorchick.log")
DEFAULT_SCAN_BASE_PATH = "/storage/emulated/0/"
DEFAULT_QUARANTINE_PATH = os.path.join(BASE_DIR, "quarantine")
DEFAULT_DAYS = 30
DEFAULT_MIN_MB = 0
DEFAULT_MAX_MB = None
TOUCH_INTERVAL = 300  # seconds between touching model files
RAM_THRESHOLD_MB = 300  # If free RAM below this, consider unload

MODEL_PATHS = [
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Fast_Qwen2.5-1.5B-Instruct.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Qwen3-8B.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/Llama-2-7b-chat-ms.gguf"),
    os.path.expanduser("~/EdenOS_Mobile/eden_models/SmoLLM2-360M-Instruct.gguf")
]

EXCLUDE_PATHS = [
    "/storage/emulated/0/Android",
    "/storage/emulated/0/DCIM",
    "/storage/emulated/0/Download",
    "/storage/emulated/0/EdenOS_Mobile",
    DEFAULT_QUARANTINE_PATH
]

# === ASCII Firebird Intro ===
def firebird_banner():
    print(r"""
     ╭🔥╮   SCORCHICK v1.2 — BURN WATCHER
    (◕‿◕✿)  "Cleaning your digital巢... with fire."
     ╰🔥╯   -------------------------------
    """)

# === Shared Logger ===
def log_event(entry, log_path=DEFAULT_LOG_PATH):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    try:
        with open(log_path, "a") as f:
            f.write(f"[SCORCHICK] :: {datetime.now().isoformat()} :: {entry}\n")
    except Exception as e:
        print(f"[SCORCHICK] Error writing to log {log_path}: {e}")

# === Burn Detection ===
def detect_burn(file_path, log_path=DEFAULT_LOG_PATH):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read().lower()
        event_detected = any(keyword in data for keyword in ["overheat", "burn", "critical temp"])
        if event_detected:
            log_event("🔥 Burn/overheat event detected!", log_path)
            print("[SCORCHICK] ALERT: Burn event detected.")
        else:
            log_event("No burn events found.", log_path)
            print("[SCORCHICK] Status: No burn events.")
    except Exception as e:
        log_event(f"Error in burn detection for {file_path}: {e}", log_path)
        print(f"[SCORCHICK] Error: Failed to process {file_path}: {e}")

# === Warmup Daemon ===
class ScorchickWarmupDaemon:
    def __init__(self, log_path=DEFAULT_LOG_PATH):
        self.running = True
        self.log_path = log_path
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True

    def _touch_models(self):
        now = time.time()
        for path in MODEL_PATHS:
            try:
                os.utime(path)
                print(f"⚡ Touched model file: {path}")
                log_event(f"Touched model file: {path}", self.log_path)
            except Exception as e:
                print(f"⚠️ Failed to touch {path}: {e}")
                log_event(f"Failed to touch {path}: {e}", self.log_path)

    def _check_memory(self):
        if not PSUTIL_AVAILABLE:
            return
        try:
            mem = psutil.virtual_memory()
            free_mb = mem.available / (1024 * 1024)
            print(f"🧠 Free RAM: {free_mb:.1f} MB")
            log_event(f"Free RAM: {free_mb:.1f} MB", self.log_path)
            if free_mb < RAM_THRESHOLD_MB:
                print("⚠️ Low RAM detected - consider unloading models")
                log_event("Low RAM detected - consider unloading models", self.log_path)
        except Exception as e:
            log_event(f"Memory check failed: {e}", self.log_path)

    def _run(self):
        while self.running:
            self._touch_models()
            self._check_memory()
            time.sleep(TOUCH_INTERVAL)

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

# === Cleanup Helpers ===
def is_excluded(path, quarantine_path):
    path = os.path.abspath(path)
    for excl in EXCLUDE_PATHS + [quarantine_path]:
        if path.startswith(os.path.abspath(excl)):
            return True
    return False

def format_size(bytes):
    return f"{bytes / (1024*1024):.2f} MB"

def move_to_quarantine(file_path, quarantine_path, dry_run, log_path):
    try:
        filename = os.path.basename(file_path)
        quarantine_file = os.path.join(quarantine_path, filename)
        if os.path.exists(quarantine_file):
            base, ext = os.path.splitext(filename)
            quarantine_file = os.path.join(quarantine_path, f"{base}_{int(time.time())}{ext}")
        if dry_run:
            log_event(f"[DRY RUN] Would move: {file_path} -> {quarantine_file}", log_path)
            return True, os.path.getsize(file_path)
        os.makedirs(quarantine_path, exist_ok=True)
        shutil.move(file_path, quarantine_file)
        log_event(f"Moved: {file_path} -> {quarantine_file}", log_path)
        return True, os.path.getsize(file_path)
    except Exception as e:
        log_event(f"Error moving {file_path}: {e}", log_path)
        return False, 0

def restore_from_quarantine(quarantine_path, log_path):
    try:
        files = os.listdir(quarantine_path)
        for f in files:
            full_path = os.path.join(quarantine_path, f)
            restored_path = os.path.join(DEFAULT_SCAN_BASE_PATH, f)
            shutil.move(full_path, restored_path)
            log_event(f"Restored: {full_path} -> {restored_path}", log_path)
            print(f"[SCORCHICK] Restored: {f}")
    except Exception as e:
        log_event(f"Restore failed: {full_path} - {e}", log_path)
        print(f"[SCORCHICK] Restore failed: {f} - {e}")

# === Cleanup Logic ===
def cleanup_files(scan_base_path, quarantine_path, days, min_mb, max_mb, dry_run, log_path):
    now = time.time()
    cutoff = now - days * 86400
    moved = 0
    total_size = 0
    for root, dirs, files in os.walk(scan_base_path):
        if is_excluded(root, quarantine_path):
            continue
        for file in files:
            file_path = os.path.join(root, file)
            if is_excluded(file_path, quarantine_path):
                continue
            try:
                last_mod = os.path.getmtime(file_path)
                if last_mod < cutoff:
                    size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    if (min_mb and size_mb < min_mb) or (max_mb and size_mb > max_mb):
                        continue
                    ok, file_size = move_to_quarantine(file_path, quarantine_path, dry_run, log_path)
                    if ok:
                        moved += 1
                        total_size += file_size
            except Exception as e:
                log_event(f"Failed processing {file_path}: {e}", log_path)
    print("\n[SCORCHICK] Cleanup Summary")
    print(f"  Files Moved: {moved}")
    print(f"  Total Size : {format_size(total_size)}")
    print(f"  Quarantine : {quarantine_path}")
    print(f"  Log        : {log_path}")
    if dry_run:
        print("  Mode       : DRY RUN (no files were moved)")

# === CLI Entry Point ===
def main():
    firebird_banner()
    parser = argparse.ArgumentParser(description=f"Scorchick v{VERSION}: Burn Watcher for EdenNode Mobile")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Burn Detection
    parser_detect = subparsers.add_parser("detect", help="Scan file for burn events")
    parser_detect.add_argument("--scan", required=True, help="Log file to scan for burn events")
    parser_detect.add_argument("--log", default=DEFAULT_LOG_PATH, help="Log file path")

    # Warmup Daemon
    parser_warmup = subparsers.add_parser("warmup", help="Run model warmup daemon")
    parser_warmup.add_argument("--log", default=DEFAULT_LOG_PATH, help="Log file path")

    # Cleanup
    parser_cleanup = subparsers.add_parser("cleanup", help="Clean up old files")
    parser_cleanup.add_argument("--scan", default=DEFAULT_SCAN_BASE_PATH, help="Base path to scan")
    parser_cleanup.add_argument("--quarantine", default=DEFAULT_QUARANTINE_PATH, help="Quarantine folder")
    parser_cleanup.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Days since last modified")
    parser_cleanup.add_argument("--min-mb", type=int, default=DEFAULT_MIN_MB, help="Minimum file size (MB)")
    parser_cleanup.add_argument("--max-mb", type=int, default=DEFAULT_MAX_MB, help="Maximum file size (MB)")
    parser_cleanup.add_argument("--dry-run", action="store_true", help="Log actions, don't move files")
    parser_cleanup.add_argument("--log", default=DEFAULT_LOG_PATH, help="Log file path")

    # Rescue
    parser_rescue = subparsers.add_parser("rescue", help="Restore files from quarantine")
    parser_rescue.add_argument("--quarantine", default=DEFAULT_QUARANTINE_PATH, help="Quarantine folder")
    parser_rescue.add_argument("--log", default=DEFAULT_LOG_PATH, help="Log file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == "detect":
        print("[SCORCHICK] Starting burn detection...")
        detect_burn(args.scan, args.log)
    elif args.command == "warmup":
        if not PSUTIL_AVAILABLE:
            print("[SCORCHICK] Error: 'psutil' required for warmup daemon. Install with `pip install psutil`.")
            return
        print("[SCORCHICK] Starting warmup daemon...")
        daemon = ScorchickWarmupDaemon(args.log)
        daemon.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[SCORCHICK] Stopping warmup daemon...")
            daemon.stop()
    elif args.command == "cleanup":
        print("[SCORCHICK] Starting cleanup...")
        cleanup_files(args.scan, args.quarantine, args.days, args.min_mb, args.max_mb, args.dry_run, args.log)
    elif args.command == "rescue":
        print("[SCORCHICK] Rescue mode activated — restoring quarantine files...")
        restore_from_quarantine(args.quarantine, args.log)

if __name__ == "__main__":
    main()