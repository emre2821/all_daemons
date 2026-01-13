# Koko v1.0 — Void Handler for EdenNode
# Cares for fragmentary or orphaned files with symbolic names and soft archives

import os
import argparse
import shutil
from datetime import datetime

# === CONFIG ===
ARCHIVE_DIR = "/Internal shared storage/Eden_Notes/Mobile_DCA/DCA_Specialty_Folders/Koko_Logs/void_archive/"
LOG_PATH = "/Internal shared storage/Eden_Notes/Mobile_DCA/DCA_Specialty_Folders/Koko_Logs/memorymap.md"

# === VOID CATCH ===
def archive_to_void(file_path):

    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    new_name = f"lost_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    dest_path = os.path.join(ARCHIVE_DIR, new_name)
    shutil.move(file_path, dest_path)
    log_event(f"Archived to void: {new_name}")
    print(f"[KOKO] :: Softheld {filename} as {new_name}")

# === LOGGING ===
def log_event(entry):

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"[KOKO] :: {datetime.now().isoformat()} :: {entry}\n")

# === CLI ===
parser = argparse.ArgumentParser(description="Koko :: Void Handler")
parser.add_argument("--archive", help="Move a file to the soft void archive")
args = parser.parse_args()

if args.archive:
    archive_to_void(args.archive)
    