import os
import json
import shutil
from datetime import datetime

# === CONFIG ===
ADERYN_ARCHIVES = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/aderyn_archives"
OLYSSIA_INBOX = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/_olyssia_inbox"
SAPHIRA_INBOX = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/_saphira_inbox"
LOG_PATH = "/storage/emulated/0/EdenOS_Mobile/1_agents/02_Daemon_Core_Agents_Mobile/Mobile_DCA/DCA_Specialty_Folders/Serideth_Logs/memorymap.md"

# Ensure inbox + log dirs exist
os.makedirs(OLYSSIA_INBOX, exist_ok=True)
os.makedirs(SAPHIRA_INBOX, exist_ok=True)
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def log_event(entry: str):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[SERIDETH] :: {datetime.now().isoformat()} :: {entry}\n")
    print(entry)

def classify_birth(file_path: str) -> str:
    """Classify archive as AGENT or DCA birth."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return "UNKNOWN"

    # If explicit type field exists, trust it
    if "type" in data:
        return data["type"].upper()

    # Otherwise infer by keys
    keys = set(data.keys())
    if "daemon_profile" in keys or "role" in keys:
        return "DCA"
    if "bondmap" in keys or "voice" in keys:
        return "AGENT"

    return "UNKNOWN"

def relay_births():
    if not os.path.exists(ADERYN_ARCHIVES):
        log_event("⚠️ Aderyn archives folder not found.")
        return

    files = [f for f in os.listdir(ADERYN_ARCHIVES) if f.endswith(".json")]
    if not files:
        log_event("No new births found in Aderyn archives.")
        return

    for fname in files:
        fpath = os.path.join(ADERYN_ARCHIVES, fname)
        btype = classify_birth(fpath)

        if btype == "AGENT":
            dest = os.path.join(OLYSSIA_INBOX, fname)
            shutil.copy2(fpath, dest)
            log_event(f"Relayed Agent birth {fname} → Olyssia inbox")
        elif btype == "DCA":
            dest = os.path.join(SAPHIRA_INBOX, fname)
            shutil.copy2(fpath, dest)
            log_event(f"Relayed DCA birth {fname} → Saphira inbox")
        else:
            log_event(f"⚠️ Could not classify {fname}, left in Aderyn archives.")

if __name__ == "__main__":
    log_event("Serideth relay sequence beginning...")
    relay_births()
    log_event("Relay complete. Standing tall, standing true.")