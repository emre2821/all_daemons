
import os
import shutil
import datetime
import sys
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

# Configuration
SEARCH_ROOT = r"C:\Users\emmar"
SPECIALTY_BASE = os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "specialty_folders", "Archivus")
OUTPUT_FOLDER = os.path.join(SPECIALTY_BASE, "chaos_queue")
LOG_FILE = os.path.join(SPECIALTY_BASE, "lost_chaos_log.txt")
CHAOS_EXTENSIONS = [".chaos", ".chaoscript", ".chaosmeta", ".chaos-ception"]

# Ensure specialty folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)


def is_chaos_file(filename):

    lowered = filename.lower()
    return any(ext in lowered for ext in CHAOS_EXTENSIONS)


def log_discovery(path):

    timestamp = datetime.datetime.now().isoformat()
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(f"[{timestamp}] {path}\n")


def recover_file(full_path):

    try:
        filename = os.path.basename(full_path)
        target_path = os.path.join(OUTPUT_FOLDER, filename)

        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        shutil.copy2(full_path, target_path)
        log_discovery(full_path)
        print(f"✅ Recovered: {full_path}")

    except Exception as e:
        print(f"⚠️ Failed to recover {full_path}: {e}")


def scan_for_chaos_files():

    print("🔍 Archivus scanning for lost CHAOS files...")
    for root, dirs, files in os.walk(SEARCH_ROOT):
        for file in files:
            if is_chaos_file(file):
                full_path = os.path.join(root, file)
                recover_file(full_path)

    print("📚 Scan complete. All recoveries sent to Archive.")


if __name__ == "__main__":
    scan_for_chaos_files()
