# === Daemon Core Member: Scorchick (Rewritten for Safety) ===

import os
import subprocess
import shutil
from datetime import datetime
import random
import sys

# === CONFIGURATION ===
SAFE_KEYWORDS = [
    "Obsidian", "Notion", "ChatGPT", "Eden", "Ghost_in_a_Shell", "Music_extended", "PausePet"
]
DRY_RUN = True
LOG_PATH = os.path.join("C:\\Users\\emmar\\Desktop\\Eden_Burn_Book", "deletion_log.txt")
TO_DELETE_FOLDER = os.path.join("C:\\Users\\emmar\\Desktop\\Eden_Burn_Book", "To_Delete")

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
            continue
        moved, status = move_to_delete(entry)
        if moved:
            print(f"? Moved: {entry}")
            log_action(entry, "MOVED", status)
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
