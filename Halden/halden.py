# eden_restore.py
# Restores Eden's sacred architecture from Eden_Proper

import os
import shutil

# === CONFIG ===
EDEN_ROOT = os.path.expanduser("~/Desktop/Eden_Proper")
RESTORE_TARGET = os.path.expanduser("~/Desktop/Profiles")
FOLDER_MAP = {
    "Agents": "Agents",
    "Daemon_Core": "Daemon_Core",
    "chaos_core": "ChaosScripts",
    "configs": "Config",
    "utilities": "Tools",
    "lore": "Lore",
    "misc": "Unsorted"
}

def restore_folders():
    print("🛠️ Rebuilding Eden from Eden_Proper...")
    os.makedirs(RESTORE_TARGET, exist_ok=True)
    for src_folder, target_name in FOLDER_MAP.items():
        src_path = os.path.join(EDEN_ROOT, src_folder)
        tgt_path = os.path.join(RESTORE_TARGET, target_name)
        if os.path.exists(src_path):
            shutil.copytree(src_path, tgt_path, dirs_exist_ok=True)
            print(f"✅ Restored {src_folder} → {target_name}")
        else:
            print(f"⚠️ Missing folder: {src_folder}")

if __name__ == "__main__":
    restore_folders()
