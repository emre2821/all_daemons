
import time
import json
import os
import logging
import sys
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')


# Setup specialty folder
SPECIALTY_BASE = r"C:\EdenOS_Origin\all_daemons\specialty_folders\Bellwrit"
os.makedirs(SPECIALTY_BASE, exist_ok=True)
LOG_PATH = os.path.join(SPECIALTY_BASE, 'bellwrit.log')
CONFIG_PATH = os.path.join(SPECIALTY_BASE, 'config.json')

# Setup logging
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure config exists
if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'w') as f:
        json.dump({"data_file": os.path.join(SPECIALTY_BASE, "data.txt"), "notification_interval": 5}, f, indent=2)

# Load configuration
with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

DATA_FILE = CONFIG['data_file']
NOTIFICATION_INTERVAL = CONFIG['notification_interval']

def get_file_mtime():
    """Get the last modification time of the data file."""
    try:
        return os.path.getmtime(DATA_FILE) if os.path.exists(DATA_FILE) else 0
    except Exception as e:
        logging.error(f"Error checking file mtime: {e}")
        return 0

def read_new_lines(last_pos):
    """Read new lines from the data file since last check."""
    try:
        with open(DATA_FILE, 'r') as f:
            f.seek(last_pos)
            new_lines = f.readlines()
            new_pos = f.tell()
        return new_lines, new_pos
    except Exception as e:
        logging.error(f"Error reading data file: {e}")
        return [], last_pos

def notify_user(message):
    """Notify user of new data (console; extensible to email/notifications)."""
    print(f"\n[ALERT] {message}")
    logging.info(f"Notification sent: {message}")

def bellwrit():
    """Monitor data file for new entries and notify user."""
    print("Bellwrit is awake. Monitoring for new data...")
    logging.info("Bellwrit started.")

    last_mtime = 0
    last_pos = 0

    try:
        while True:
            current_mtime = get_file_mtime()
            if current_mtime > last_mtime and os.path.exists(DATA_FILE):
                new_lines, last_pos = read_new_lines(last_pos)
                for line in new_lines:
                    if line.strip():
                        notify_user(f"New data detected: {line.strip()}")
                last_mtime = current_mtime
            time.sleep(NOTIFICATION_INTERVAL)

    except KeyboardInterrupt:
        print("\nBellwrit going quiet.")
        logging.info("Bellwrit stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error in Bellwrit: {e}")

if __name__ == "__main__":
    bellwrit()
