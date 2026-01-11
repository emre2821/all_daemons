import os
import shutil
import datetime
import sys

# === Configuration ===
WHITELIST_KEYWORDS = [
    "Obsidian", "Notion", "ChatGPT", "Eden", "Ghost_in_a_Shell",
    "Music_extended", "PausePet"
]
TO_DELETE_FOLDER = os.path.expanduser("~/EdenOS_Mobile/To_Delete")
LOG_FILE = os.path.expanduser("~/EdenOS_Mobile/emberly_cleanup_log.txt")
DRY_RUN = False
SANDBOX_MODE = False
DELETE_LIST_FILE = os.path.expanduser("~/EdenOS_Mobile/eden_delete_list.txt")

def is_safe(filename):
    filename = filename.lower()
    return any(k.lower() in filename for k in WHITELIST_KEYWORDS)

def log_action(entry, action, status):
    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {action}: {entry} | {status}\n")

def move_to_delete(path):
    if not os.path.exists(path):
        return False, "File does not exist"
    if not os.path.exists(TO_DELETE_FOLDER):
        os.makedirs(TO_DELETE_FOLDER)
    try:
        shutil.move(path, TO_DELETE_FOLDER)
        return True, "Moved to To_Delete"
    except Exception as e:
        return False, f"Move failed: {e}"

def print_summary(moved, skipped, failed):
    print("\n===== Emberly Cleanup Summary =====")
    print(f"Files moved: {moved}")
    print(f"Files skipped (whitelist): {skipped}")
    print(f"Files failed: {failed}")
    print("===================================")

def run_cleanup():
    moved = 0
    skipped = 0
    failed = 0

    if SANDBOX_MODE or DRY_RUN:
        print("[DRY RUN] No files will actually be moved.")

    if not os.path.exists(DELETE_LIST_FILE):
        print(f"Delete list file not found: {DELETE_LIST_FILE}")
        return

    with open(DELETE_LIST_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    for path in lines:
        if is_safe(path):
            print(f"⛔ SKIPPED (whitelist): {path}")
            log_action(path, "SKIPPED", "Whitelisted")
            skipped += 1
            continue

        print(f"🔥 Processing: {path}")
        if SANDBOX_MODE or DRY_RUN:
            print(f"[DRY RUN] Would move: {path}")
            log_action(path, "DRY_RUN", "No action")
            continue

        success, status = move_to_delete(path)
        if success:
            print(f"✅ Moved: {path}")
            log_action(path, "MOVED", status)
            moved += 1
        else:
            print(f"❌ Failed: {path} ({status})")
            log_action(path, "FAILED", status)
            failed += 1

    print_summary(moved, skipped, failed)

def main():
    global DRY_RUN, SANDBOX_MODE
    args = sys.argv[1:]
    if "--dry-run" in args:
        DRY_RUN = True
    if "--sandbox" in args:
        SANDBOX_MODE = True

    print("Emberly Cleanup Daemon started.")
    run_cleanup()

if __name__ == "__main__":
    main()
