import os
import sys
import json
from datetime import datetime

if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

SPECIALTY_BASE = r"C:\EdenOS_Origin\all_daemons\specialty_folders\Dagr"
os.makedirs(SPECIALTY_BASE, exist_ok=True)

PROFILE_PATH = os.path.join(os.path.dirname(__file__), 'dagr_cyclekeeper.json')


def load_profile():

    with open(PROFILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def log_event(event):

    log_path = os.path.join(SPECIALTY_BASE, 'dagr.log')
    with open(log_path, 'a', encoding='utf-8') as log:
        log.write(f"[{datetime.now()}] {event}\n")


def discover_daemons():

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    daemons = []
    for name in os.listdir(base_dir):
        daemon_path = os.path.join(base_dir, name)
        if os.path.isdir(daemon_path) and not name.startswith('_'):
            py_file = os.path.join(daemon_path, f"{name}.py")
            if os.path.isfile(py_file) and name.lower() != "dagr":
                daemons.append((name, py_file))
    return daemons

def activate():

    profile = load_profile()
    print(f"{profile['symbolic_traits']['sigil']}  {profile['class_name']} (ID: {profile['daemon_id']}) is now active!")
    print(f"Role: {profile['role']}")
    print(f"Description: {profile['description']}")
    print(f"Quote: {profile['quote']}")
    print(f"Status: {profile['status']}")
    log_event("Dagr activated.")

    # Synchronize and trigger other daemons
    daemons = discover_daemons()
    print(f"\nSynchronizing {len(daemons)} daemons...")
    for name, script in daemons:
        print(f"Triggering {name}...")
        log_event(f"Triggering {name}")
        try:
            result = os.system(f'"{sys.executable}" "{script}"')
            log_event(f"{name} exited with code {result}")
        except Exception as e:
            print(f"[ERROR] Could not trigger {name}: {e}")
            log_event(f"[ERROR] Could not trigger {name}: {e}")

if __name__ == "__main__":
    activate()
