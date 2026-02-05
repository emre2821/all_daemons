# === Daemon Core Member: Scorchick (Rewritten for Safety) ===

import os
import shutil
import argparse
from datetime import datetime
import sys

# === CONFIGURATION ===
SAFE_KEYWORDS = [
    "Obsidian", "Notion", "ChatGPT", "Eden", "Ghost_in_a_Shell", "Music_extended", "PausePet"
]
DRY_RUN = True
try:
    _root = os.environ.get("EDEN_ROOT", os.getcwd())
    sys.path.append(os.path.join(_root, "shared", "Daemon_tools", "scripts"))
    from eden_paths import logs_dir as _logs_dir  # type: ignore
    from eden_paths import eden_root as _eden_root  # type: ignore
    from eden_paths import daemon_out_dir as _daemon_out_dir  # type: ignore
except Exception:
    def _eden_root():
        return os.environ.get("EDEN_ROOT", os.getcwd())

    def _logs_dir():
        work_root = os.environ.get("EDEN_WORK_ROOT", _eden_root())
        p = os.path.join(work_root, "daemons", "_logs")
        os.makedirs(p, exist_ok=True)
        return p

    def _daemon_out_dir(name: str):
        work_root = os.environ.get("EDEN_WORK_ROOT", _eden_root())
        p = os.path.join(work_root, "daemons", "Rhea", "_outbox", name)
        os.makedirs(p, exist_ok=True)
        return p
LOG_PATH = os.path.join(_logs_dir(), "Scorchick.log")
TO_DELETE_FOLDER = _daemon_out_dir("Scorchick")

FILES_MOVED = 0
SURVIVORS = 0
SANDBOX_MODE = False
FAKE_PATHS = [f"C:/FakePath/File_{i}.txt" for i in range(1, 21)]

def is_safe(entry):

    return any(keyword.lower() in entry.lower() for keyword in SAFE_KEYWORDS)

def move_to_delete(path):

    try:
        if not os.path.exists(TO_DELETE_FOLDER):
            os.makedirs(TO_DELETE_FOLDER)
        basename = os.path.basename(path)
        shutil.move(path, os.path.join(TO_DELETE_FOLDER, basename))
        return True, "Moved to To_Delete"
    except Exception as e:
        return False, f"Move failed: {e}"

def log_action(entry, action, status):

    with open(LOG_PATH, "a", encoding="utf-8") as log:
        log.write(f"{datetime.now()} | {action}: {entry} | {status}\n")

def print_burn_summary():

    print("\n===== BURN SUMMARY =====")
    print(f"Files moved: {FILES_MOVED}")
    print(f"Survivors: {SURVIVORS}")
    print("========================\n")

def main_menu():

    print("\nScorchick Cleanup Utility")
    print("1. Run Safe Cleanup")
    print("2. Enable Sandbox Mode")
    print("3. Exit")
    return input("Select an option: ").strip()

def interactive_main():

    global SANDBOX_MODE, FILES_MOVED, SURVIVORS
    while True:
        choice = main_menu()
        if choice == '1':
            entries = FAKE_PATHS if SANDBOX_MODE else open('eden_delete_list.txt', 'r', encoding='utf-8').read().splitlines()
            for entry in entries:
                if is_safe(entry):
                    print(f"⛔ SKIPPED: {entry}")
                    log_action(entry, "SKIPPED", "Protected")
                    SURVIVORS += 1
                    continue
                print(f"\n🔥 Processing: {entry}")
                if DRY_RUN or SANDBOX_MODE:
                    print(f"[DRY RUN] Would move: {entry}")
                    log_action(entry, "DRY RUN", "No action")
                    continue
                moved, status = move_to_delete(entry)
                if moved:
                    print(f"✅ Moved: {entry}")
                    log_action(entry, "MOVED", status)
                    FILES_MOVED += 1
                else:
                    print(f"❓ Failed: {entry}")
                    log_action(entry, "FAILED", status)
                    SURVIVORS += 1
            print_burn_summary()
        elif choice == '2':
            SANDBOX_MODE = True
            print("Sandbox Mode ENABLED.")
        elif choice == '3':
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

def run_noninteractive(list_file: str, dry_run: bool = True) -> int:

    global FILES_MOVED, SURVIVORS
    try:
        entries = [l.strip() for l in open(list_file, 'r', encoding='utf-8').read().splitlines() if l.strip()]
    except FileNotFoundError:
        print(f"List file not found: {list_file}")
        return 1
    for entry in entries:
        if is_safe(entry):
            print(f"? SKIPPED: {entry}")
            log_action(entry, "SKIPPED", "Protected")
            SURVIVORS += 1
            continue
        print(f"\n?? Processing: {entry}")
        if dry_run:
            print(f"[DRY RUN] Would move: {entry}")
            log_action(entry, "DRY RUN", "No action")
            try:
                from Daemon_tools.scripts.eden_safety import log_event as _le
            except Exception:
                _le = None
            if _le:
                _le("Scorchick", action="plan_move", target=entry, outcome="planned")
            continue
        moved, status = move_to_delete(entry)
        if moved:
            print(f"? Moved: {entry}")
            log_action(entry, "MOVED", status)
            try:
                from Daemon_tools.scripts.eden_safety import log_event as _le
            except Exception:
                _le = None
            if _le:
                _le("Scorchick", action="move", target=entry, outcome="ok")
            FILES_MOVED += 1
        else:
            print(f"? Failed: {entry}")
            log_action(entry, "FAILED", status)
            SURVIVORS += 1
    print_burn_summary()
    return 0


def main(argv=None):

    parser = argparse.ArgumentParser(description="Scorchick - Risky file mover (To_Delete)")
    parser.add_argument("--list-file", default="eden_delete_list.txt", help="Path to file list")
    parser.add_argument("--dry-run", action="store_true", help="Plan only (default unless --confirm)")
    parser.add_argument("--confirm", action="store_true", help="Execute moves to To_Delete")
    args = parser.parse_args(argv)

    dry_run = (not args.confirm) if not args.dry_run else True
    return run_noninteractive(args.list_file, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())

def describe() -> dict:

    return {
        "name": "Scorchick",
        "role": "Risky file mover (To_Delete)",
        "inputs": {"list_file": "eden_delete_list.txt"},
        "outputs": {"to_delete": TO_DELETE_FOLDER},
        "flags": ["--list-file", "--dry-run", "--confirm"],
        "safety_level": "destructive",
    }


def healthcheck() -> dict:

    status = "ok"; notes = []
    try:
        os.makedirs(TO_DELETE_FOLDER, exist_ok=True)
    except Exception as e:
        status = "fail"; notes.append(f"to_delete folder error: {e}")
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as _:
            pass
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"log write warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
