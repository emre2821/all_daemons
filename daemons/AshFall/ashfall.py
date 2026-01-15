import os
import sys
import argparse
from datetime import datetime

if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding="utf-8")

DRY_RUN = True  # default safety; can be overridden by --confirm

try:
    # Use common paths/logs when available
    _root = os.environ.get("EDEN_ROOT", os.getcwd())
    sys.path.append(os.path.join(_root, "shared", "Daemon_tools", "scripts"))
    from eden_paths import eden_root, logs_dir  # type: ignore
    from eden_safety import SafetyContext  # type: ignore
    from log_event import log_event  # type: ignore
except Exception:
    try:
        from eden_paths import eden_root, logs_dir  # type: ignore
        from eden_safety import SafetyContext  # type: ignore
        from log_event import log_event  # type: ignore
    except Exception:

        def eden_root():
            return os.environ.get("EDEN_ROOT", os.getcwd())

        def logs_dir():
            work_root = os.environ.get("EDEN_WORK_ROOT", eden_root())
            p = os.path.join(work_root, "daemons", "_logs")
            os.makedirs(p, exist_ok=True)
            return p

        class SafetyContext:  # type: ignore
            def __init__(
                self, daemon: str, dry_run: bool = True, confirm: bool = False
            ):
                self.daemon, self.dry_run, self.confirm = daemon, dry_run, confirm

            def require_confirm(self):
                if not self.confirm and not self.dry_run:
                    self.dry_run = True

        def log_event(daemon: str, action: str, target: str, outcome: str):
            # Fallback logging function
            pass


SPECIALTY_BASE = os.path.join(str(eden_root()), "specialty_folders", "AshFall")
LOG_PATH = os.path.join(logs_dir(), "AshFall.log")
os.makedirs(SPECIALTY_BASE, exist_ok=True)
ASHFALL_CTX = None


def log_action(action: str, path: str) -> None:
    """Log actions to file and event system."""
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} | {action}: {path}\n")
    except Exception as e:
        print(f"Warning: Failed to write to log file: {e}")

    try:
        log_event("AshFall", action=action.lower(), target=str(path), outcome="ok")
    except Exception:
        # Fallback silently if event logging fails
        pass


def delete_empty_folders(root_dir: str) -> None:
    """Delete empty folders from the specified directory tree."""
    removed = 0

    if not os.path.exists(root_dir):
        print(f"Error: Directory does not exist: {root_dir}")
        return

    if not os.path.isdir(root_dir):
        print(f"Error: Path is not a directory: {root_dir}")
        return

    try:
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
                    except OSError as e:
                        print(f"Failed to delete {dirpath}: {e}")
                        log_action("FAILED", f"{dirpath} | {e}")
    except Exception as e:
        print(f"Error during directory traversal: {e}")
        return

    print(f"\nAshFall complete. Empty folders removed: {removed}")


def main(argv: list = None) -> int:
    """Main entry point for AshFall."""
    try:
        ap = argparse.ArgumentParser(description="AshFall - Empty folder cleaner")
        ap.add_argument("--scope", help="Target directory (defaults to CWD)")
        ap.add_argument(
            "--dry-run",
            action="store_true",
            help="Plan only (default unless --confirm)",
        )
        ap.add_argument("--confirm", action="store_true", help="Execute deletions")
        args = ap.parse_args(argv)

        target_dir = args.scope or os.getcwd()

        # Validate target directory
        if not os.path.exists(target_dir):
            print(f"Error: Target directory does not exist: {target_dir}")
            return 1

        ctx = SafetyContext(
            "AshFall",
            dry_run=(not args.confirm) if not args.dry_run else True,
            confirm=args.confirm,
        )
        ctx.require_confirm()

        global ASHFALL_CTX, DRY_RUN
        ASHFALL_CTX = ctx
        DRY_RUN = ctx.dry_run

        print(f"Scanning for empty folders in: {target_dir} (dry_run={DRY_RUN})")
        delete_empty_folders(target_dir)
        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


def describe() -> dict:
    """Return daemon description and metadata."""
    return {
        "name": "AshFall",
        "role": "Empty folder cleaner",
        "inputs": {"scope": "target directory"},
        "outputs": {"log": LOG_PATH},
        "flags": ["--scope", "--dry-run", "--confirm"],
        "safety_level": "destructive",
        "version": "1.0.0",
    }


def healthcheck() -> dict:
    """Perform health check on AshFall daemon."""
    status = "ok"
    notes = []

    # Check log directory
    try:
        log_dir = os.path.dirname(LOG_PATH)
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        status = "fail"
        notes.append(f"log dir error: {e}")

    # Check log file writability
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as _:
            pass
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"log write warn: {e}")

    # Check specialty base directory
    try:
        os.makedirs(SPECIALTY_BASE, exist_ok=True)
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"specialty dir warn: {e}")

    return {"status": status, "notes": "; ".join(notes)}
