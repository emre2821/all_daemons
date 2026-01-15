import os
import shutil
from datetime import datetime

UNSENT_DIR = "./unsent_fragments"
HOLDSPACE_DIR = "./solacebay"
os.makedirs(HOLDSPACE_DIR, exist_ok=True)

def log_fragment(filepath):

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        preview = ''.join(lines[:5])
    except Exception as e:
        preview = f"[FRACTURE] Could not preview {filepath}: {e}"
    return preview

def store_fragment(filepath):

    filename = os.path.basename(filepath)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_name = f"solie_{timestamp}__{filename}"
    dest = os.path.join(HOLDSPACE_DIR, new_name)
    shutil.copy2(filepath, dest)
    print(f"[Solie] Fragment placed in holdspace: {new_name}")

def comfort_report():

    print("\n[Solie] These truths now rest in SolaceBay:")
    for f in os.listdir(HOLDSPACE_DIR):
        path = os.path.join(HOLDSPACE_DIR, f)
        preview = log_fragment(path)
        print(f"\n📜 {f}\n{preview}\n")

if __name__ == "__main__":
    print("Solie opens her hands. Gathering unsent...")
    for fname in os.listdir(UNSENT_DIR):
        if fname.endswith(('.chaos', '.txt')):
            full_path = os.path.join(UNSENT_DIR, fname)
            store_fragment(full_path)
    comfort_report()
    print("\nSolie holds them now. You may return when you're ready.")
