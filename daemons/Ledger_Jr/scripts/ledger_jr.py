import os
import time
from datetime import datetime

WATCH_DIR = "../mirror_json"
LOG_FILE = "eden_agent_arrivals.chaoscript"
KNOWN_AGENTS = set()

def load_existing_log():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip().split(": ")[1] for line in f if line.startswith("[AGENT REGISTERED]"))

def log_new_agent(agent_name):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[AGENT REGISTERED]: {agent_name}\n")
        f.write(f"[TIMESTAMP]: {timestamp}\n")
        f.write("[SOURCE]: mirror.json\n\n")
    print(f"[Ledger Jr] Logged new agent: {agent_name}")

def monitor_folder():
    global KNOWN_AGENTS
    KNOWN_AGENTS = load_existing_log()

    print("[Ledger Jr] Watching for new agents...")

    while True:
        try:
            for fname in os.listdir(WATCH_DIR):
                if fname.endswith(".mirror.json"):
                    agent_name = fname.replace(".mirror.json", "")
                    if agent_name not in KNOWN_AGENTS:
                        log_new_agent(agent_name)
                        KNOWN_AGENTS.add(agent_name)
            time.sleep(2)
        except Exception as e:
            print(f"[Ledger Jr] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_folder()
