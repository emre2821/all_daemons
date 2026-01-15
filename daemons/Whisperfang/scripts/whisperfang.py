import time
import json
import os
import logging
from filelock import FileLock

# Setup logging
logging.basicConfig(filename='whisperfang.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

COMMUNICATION_FILE = CONFIG['communication_file']
CHECK_INTERVAL = CONFIG['check_interval']
KEYWORDS = CONFIG['keywords']

def check_text_for_keywords(text, keywords):
    """Scan text for keywords (case-insensitive)."""
    found = []
    if not text or not keywords:
        return found
    normalized_text = text.lower()
    for keyword in keywords:
        if keyword.lower() in normalized_text:
            found.append(keyword)
    return list(set(found))

def write_to_communication_file(data):
    """Write data to communication file with locking."""
    lock = FileLock(f"{COMMUNICATION_FILE}.lock")
    try:
        with lock:
            with open(COMMUNICATION_FILE, 'a') as f:
                f.write(data + "\n")
        logging.info(f"Wrote to communication file: {data}")
    except Exception as e:
        logging.error(f"Error writing to communication file: {e}")

def update_keywords():
    """Allow user to update keywords during runtime."""
    custom_input = input("Enter new keywords (comma-separated) or press Enter to keep current: ")
    if custom_input.strip():
        new_keywords = [kw.strip() for kw in custom_input.split(',') if kw.strip()]
        CONFIG['keywords'] = new_keywords
        with open('config.json', 'w') as f:
            json.dump(CONFIG, f, indent=2)
        logging.info(f"Keywords updated: {new_keywords}")
        return new_keywords
    return CONFIG['keywords']

def whisperfang():
    """Monitor text for keywords and communicate detections."""
    print("Whisperfang activated.")
    print(f"Listening for keywords: {KEYWORDS}")
    print(f"Interval: {CHECK_INTERVAL} seconds. Press Ctrl+C to stop.")
    logging.info("Whisperfang started.")

    try:
        while True:
            print("\nPaste text to scan (or leave blank to skip):")
            text = input("> ")
            if not text.strip():
                print(f"No input. Waiting {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
                continue

            if text.lower() == "update keywords":
                KEYWORDS[:] = update_keywords()
                print(f"Updated keywords: {KEYWORDS}")
                continue

            detected = check_text_for_keywords(text, KEYWORDS)
            if detected:
                print("\n!!! KEYWORDS DETECTED !!!")
                for kw in detected:
                    print(f"  - {kw}")
                    data = f"Detected: {kw} at {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    write_to_communication_file(data)
                print("!!!!!!!!!!!!!!!!!!!!!!!\n")
                logging.info(f"Detected keywords: {detected}")
            else:
                print("No keywords found.")
                logging.info("No keywords found in input.")

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nWhisperfang stopped.")
        logging.info("Whisperfang stopped by user.")
    except Exception as e:
        print(f"Error: {e}")
        logging.error(f"Error in Whisperfang: {e}")

if __name__ == "__main__":
    if not KEYWORDS:
        print("No keywords in config. Please add keywords to config.json.")
        KEYWORDS.extend(update_keywords())
    if KEYWORDS:
        whisperfang()
    else:
        print("No keywords provided. Exiting.")
        logging.error("No keywords configured. Exiting.")
