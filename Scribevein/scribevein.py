import time
import json
import os
import logging
from filelock import FileLock

# Setup logging
logging.basicConfig(filename='scribevein.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

COMMUNICATION_FILE = CONFIG['communication_file']
DATA_FILE = CONFIG['data_file']
CHECK_INTERVAL = CONFIG['check_interval']

def read_communication_file():
    """Read and clear communication file with locking."""
    lock = FileLock(f"{COMMUNICATION_FILE}.lock")
    try:
        with lock:
            if os.path.exists(COMMUNICATION_FILE):
                with open(COMMUNICATION_FILE, 'r') as f:
                    data = f.read().strip()
                with open(COMMUNICATION_FILE, 'w') as f:
                    f.write("")
                return data if data else None
    except Exception as e:
        logging.error(f"Error reading communication file: {e}")
    return None

def write_to_data_file(data):
    """Append data to data file with locking."""
    lock = FileLock(f"{DATA_FILE}.lock")
    try:
        with lock:
            with open(DATA_FILE, 'a') as f:
                f.write(data + "\n")
        logging.info(f"Archived data: {data}")
    except Exception as e:
        logging.error(f"Error writing to data file: {e}")

def scribevein():
    """Collect and store data from communication file."""
    print("Scribevein listening. Waiting for messages...")
    logging.info("Scribevein started.")

    try:
        while True:
            data = read_communication_file()
            if data:
                print(f"Archived: {data}")
                write_to_data_file(data)
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nScribevein stopped.")
        logging.info("Scribevein stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error in Scribevein: {e}")

if __name__ == "__main__":
    scribevein()
