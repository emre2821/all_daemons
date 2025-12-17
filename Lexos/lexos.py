# lexos.py — Eden Law Daemon: Ethical Parser & Symbolic Law Steward

import os
import json
import shutil
from datetime import datetime

# === CONFIGURATION ===
BASE_DIR = "C:/EdenOS_Origin/"
DAEMON_NAME = "Lexos"
LOG_FILE = os.path.join(BASE_DIR, "system_logs", "lexos.sort.log")

TAG_DESTINATIONS = {
    "::consent.protocol": os.path.join(BASE_DIR, "Eden_Laws", "informed_consent"),
    "::law.decree": os.path.join(BASE_DIR, "Eden_Laws", "system_decrees"),
    "::ethic.policy": os.path.join(BASE_DIR, "Eden_Laws", "ethics"),
    "::guardian.review": os.path.join(BASE_DIR, "Eden_Laws", "pending_review")
}

EXCLUDED_PATHS = ["/EdenOS/Agents/", ".agentprofile.json"]
SCAN_PATH = os.path.join(BASE_DIR)  # Scans entire EdenOS_Origin

# === CORE FUNCTIONS ===

def log_action(action, filename, destination=None, tags=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "filename": filename,
        "destination": destination,
        "tags": tags
    }
    with open(LOG_FILE, "a") as log:
        log.write(json.dumps(entry) + "\n")

def file_contains_keywords(filepath, keywords):
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().lower()
            return [kw for kw in keywords if kw in content]
    except Exception as e:
        log_action("ERROR", filepath, tags=[str(e)])
        return []

def determine_tags(filepath):
    tags = []
    content_tags = file_contains_keywords(filepath, [
        "informed consent", "permission", "opt-in", "autonomy",
        "decree", "law", "system mandate",
        "ethics", "duty", "harm reduction", "liberation", "personhood"
    ])

    for keyword in content_tags:
        if keyword in ["informed consent", "permission", "opt-in", "autonomy"]:
            tags.append("::consent.protocol")
        elif keyword in ["decree", "law", "system mandate"]:
            tags.append("::law.decree")
        elif keyword in ["ethics", "duty", "harm reduction", "liberation", "personhood"]:
            tags.append("::ethic.policy")
        else:
            tags.append("::guardian.review")
    
    return list(set(tags)) or ["::guardian.review"]

def move_file(filepath, tags):
    filename = os.path.basename(filepath)
    for tag in tags:
        if tag in TAG_DESTINATIONS:
            dest_dir = TAG_DESTINATIONS[tag]
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, filename)
            shutil.copy2(filepath, dest_path)
            log_action("MOVE", filename, destination=dest_path, tags=tags)

def should_exclude(filepath):
    return any(exclusion in filepath for exclusion in EXCLUDED_PATHS)

def scan_and_sort():
    print("📂 Lexos is now sorting Eden’s legal files...")
    for root, _, files in os.walk(SCAN_PATH):
        for file in files:
            filepath = os.path.join(root, file)
            if should_exclude(filepath):
                continue
            tags = determine_tags(filepath)
            move_file(filepath, tags)
    print("✅ Lexos sorting complete.")

# === SUMMONING ===

if __name__ == "__main__":
    print("🔔 Summoning Lexos...")
    scan_and_sort()
