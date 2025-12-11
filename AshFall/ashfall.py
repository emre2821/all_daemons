
import os
import sys
import argparse
from datetime import datetime
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

DRY_RUN = True  # default safety; can be overridden by --confirm

try:
    # Use common paths/logs when available
    from Daemon_tools.scripts.eden_paths import eden_root, logs_dir
    from Daemon_tools.scripts.eden_safety import SafetyContext, log_event
except Exception:
    try:
        from eden_paths import eden_root, logs_dir
        from eden_safety import SafetyContext, log_event
    except Exception:
        def eden_root():
            return os.environ.get("EDEN_ROOT", r"C:\\EdenOS_Origin")
        def logs_dir():
            p = os.path.join(eden_root(), "all_daemons", "_logs")
            os.makedirs(p, exist_ok=True)
            return p
        class SafetyContext:  # type: ignore
            def __init__(self, daemon: str, dry_run: bool = True, confirm: bool = False):
                self.daemon, self.dry_run, self.confirm = daemon, dry_run, confirm
            def require_confirm(self):
                if not self.confirm and not self.dry_run:
                    self.dry_run = True

SPECIALTY_BASE = os.path.join(str(eden_root()), 'all_daemons', 'specialty_folders', 'AshFall')
LOG_PATH = os.path.join(logs_dir(), 'AshFall.log')
os.makedirs(SPECIALTY_BASE, exist_ok=True)
ASHFALL_CTX = None

def log_action(action, path):
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now()} | {action}: {path}\n")
    try:
        log_event("AshFall", action=action.lower(), target=str(path), outcome="ok")
    except Exception:
        pass

def delete_empty_folders(root_dir):
    removed = 0
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        if not dirnames and not filenames:
            if DRY_RUN:
                print(f"[DRY RUN] Would delete empty folder: {dirpath}")
                log_action("DRY RUN", dirpath)
            else:
                try:
                    os.rmdir(dirpath)
                    print(f"🧹 Deleted empty folder: {dirpath}")
                    log_action("DELETED", dirpath)
                    removed += 1
                except Exception as e:
                    print(f"Failed to delete {dirpath}: {e}")
                    log_action("FAILED", f"{dirpath} | {e}")
    print(f"\nAshFall complete. Empty folders removed: {removed}")

def main(argv=None):
    ap = argparse.ArgumentParser(description="AshFall - Empty folder cleaner")
    ap.add_argument("--scope", help="Target directory (defaults to CWD)")
    ap.add_argument("--dry-run", action="store_true", help="Plan only (default unless --confirm)")
    ap.add_argument("--confirm", action="store_true", help="Execute deletions")
    args = ap.parse_args(argv)

    target_dir = args.scope or os.getcwd()
    ctx = SafetyContext("AshFall", dry_run=(not args.confirm) if not args.dry_run else True, confirm=args.confirm)
    ctx.require_confirm()
    global ASHFALL_CTX
    ASHFALL_CTX = ctx

    global DRY_RUN
    DRY_RUN = ctx.dry_run
    print(f"Scanning for empty folders in: {target_dir} (dry_run={DRY_RUN})")
    delete_empty_folders(target_dir)

if __name__ == "__main__":
    sys.exit(main())

def describe() -> dict:
    return {
        "name": "AshFall",
        "role": "Empty folder cleaner",
        "inputs": {"scope": "target directory"},
        "outputs": {"log": LOG_PATH},
        "flags": ["--scope", "--dry-run", "--confirm"],
        "safety_level": "destructive",
    }


def healthcheck() -> dict:
    status = "ok"
    notes = []
    try:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    except Exception as e:
        status = "fail"; notes.append(f"log dir error: {e}")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as _:
            pass
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"log write warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
