
import os
import sys
from datetime import datetime
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

DRY_RUN = True  # Set to False to actually delete
SPECIALTY_BASE = r"C:\EdenOS_Origin\all_daemons\specialty_folders\AshFall"
LOG_PATH = os.path.join(SPECIALTY_BASE, 'ashfall_log.txt')
os.makedirs(SPECIALTY_BASE, exist_ok=True)

def log_action(action, path):
    with open(LOG_PATH, 'a', encoding='utf-8') as log:
        log.write(f"{datetime.now()} | {action}: {path}\n")

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

def main():
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()
    print(f"Scanning for empty folders in: {target_dir}")
    delete_empty_folders(target_dir)

if __name__ == "__main__":
    main() 