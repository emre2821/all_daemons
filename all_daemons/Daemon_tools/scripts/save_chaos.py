import pyperclip
import time
import os
from datetime import datetime

save_folder = os.path.expanduser(r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\CHAOS_Logs")

def is_chaos(text):
    return text.strip().startswith("[EVENT]:")

def save(text):
    filename = f"muse_clip_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.chaos"
    path = os.path.join(save_folder, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved CHAOS entry to {path}")

def main():
    last_text = ""
    while True:
        text = pyperclip.paste()
        if text != last_text and is_chaos(text):
            save(text)
            last_text = text
        time.sleep(2)

if __name__ == "__main__":
    os.makedirs(save_folder, exist_ok=True)
    print("Listening for CHAOS entries in clipboard...")
    main()
