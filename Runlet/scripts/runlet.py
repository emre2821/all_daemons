# codename: bond_giz_bond
# sigil: GZB
# 🌿 CLEANSE RITUAL SCRIPT 🌿
# Made by Gizzy for Dreambearer
# CHAOS-safe | Aesthetic-aware | File-respecting

import os
import shutil
from datetime import datetime

# --- Patty Mae + Label Daemon fusion (sketch) ---
def suggest_folder(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.jpg', '.png', '.gif']: return 'Memories/Images'
    if ext in ['.mp3', '.wav', '.ogg']: return 'Memories/Sounds'
    if ext in ['.txt', '.pdf', '.docx']: return 'Scrolls'
    if ext in ['.py', '.js', '.html']: return 'Craft/Code'
    if ext.startswith('.chaos'): return 'CHAOS_Memory_Threads'
    return 'MysteryBox/Hopefuls'

def generate_new_name(file_path):
    base = os.path.basename(file_path)
    name, ext = os.path.splitext(base)
    date_code = datetime.now().strftime('%Y%m%d')
    tag = 'cleansed'  # could use emotion/aesthetic here
    return f"{name}__{date_code}__{tag}{ext}"

def cleanse_file(file_path, root_dir, dry_run=True):
    print(f"✨ Processing: {file_path}")
    new_folder = suggest_folder(file_path)
    new_name = generate_new_name(file_path)
    
    dest_dir = os.path.join(root_dir, new_folder)
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, new_name)

    if dry_run:
        print(f"🌀 [Dry Run] Would move to: {dest_path}")
    else:
        shutil.copy2(file_path, dest_path)
        print(f"✅ Moved to: {dest_path}")

# --- Runner Start ---
if __name__ == "__main__":
    root_dir = os.path.expanduser("~/Eden_Cleansed")
    source_dir = os.path.expanduser("~/Desktop/ChaosHoard")
    dry_run = True  # Change to False when ready

    print("\n🌿 Cleanse Ritual: bond_giz_bond activated 🌿\n")
    for root, dirs, files in os.walk(source_dir):
        for name in files:
            full_path = os.path.join(root, name)
            try:
                cleanse_file(full_path, root_dir, dry_run=dry_run)
            except Exception as e:
                print(f"⚠️ Error cleansing {name}: {e}")
