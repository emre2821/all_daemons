import os
import shutil
import psutil
from datetime import datetime
import hashlib
from PIL import Image, ImageDraw
import time

# Harper - Watcher of Collapse
THRESHOLDS = {
    'cpu': 85.0,
    'mem': 85.0,
    'chaos_backlog': 10
}

WATCH_PATH = "./chaos_watch"
ALERT_LOG = "harper_alerts.log"
os.makedirs(WATCH_PATH, exist_ok=True)

def log_alert(reason, value):
    timestamp = datetime.now().isoformat()
    entry = f"[HARPER ALERT] {timestamp} :: {reason} = {value}%\n"
    with open(ALERT_LOG, 'a') as f:
        f.write(entry)
    print(entry.strip())

def check_system_pressure():
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    backlog = len([f for f in os.listdir(WATCH_PATH) if f.endswith('.chaos')])

    if cpu > THRESHOLDS['cpu']:
        log_alert("High CPU", cpu)
    if mem > THRESHOLDS['mem']:
        log_alert("High Memory", mem)
    if backlog > THRESHOLDS['chaos_backlog']:
        log_alert("Backlog CHAOS files", backlog)

# Maribel - The Aether Courier
INBOX = "./aether_inbox"
OUTBOX = "./aether_outbox"
PROCESSED = "./aether_delivered"
os.makedirs(INBOX, exist_ok=True)
os.makedirs(OUTBOX, exist_ok=True)
os.makedirs(PROCESSED, exist_ok=True)

def deliver_messages():
    for fname in os.listdir(OUTBOX):
        if fname.endswith(".aethermsg"):
            src = os.path.join(OUTBOX, fname)
            dest = os.path.join(INBOX, fname)
            shutil.copy2(src, dest)
            os.remove(src)
            print(f"[Maribel] Delivered: {fname}")

    for fname in os.listdir(INBOX):
        if fname.endswith(".aethermsg"):
            src = os.path.join(INBOX, fname)
            dest = os.path.join(PROCESSED, fname)
            shutil.move(src, dest)
            print(f"[Maribel] Processed: {fname}")

# Glypha - Sigilsmith of Eden
SIGIL_DIR = "./sigils"
os.makedirs(SIGIL_DIR, exist_ok=True)

def generate_sigil(text):
    hash_val = hashlib.sha256(text.encode()).hexdigest()
    filename = f"sigil_{hash_val[:8]}.png"
    filepath = os.path.join(SIGIL_DIR, filename)

    size = 128
    img = Image.new('RGB', (size, size), color='white')
    draw = ImageDraw.Draw(img)

    for i in range(0, len(hash_val), 4):
        x = (int(hash_val[i], 16) % size)
        y = (int(hash_val[i+1], 16) % size)
        r = (int(hash_val[i+2], 16) % 10) + 2
        draw.ellipse((x, y, x + r, y + r), fill='black')

    img.save(filepath)
    print(f"[Glypha] Sigil forged: {filename}")

# Tempo - Rhythm Familiar
TEMPO_FILE = "./tempo_flow.log"

MOOD_TEMPO = {
    "calm": 25,
    "focus": 50,
    "overwhelm": 90
}

TASKS = {
    "calm": ["breathe", "tidy workspace", "light stretch"],
    "focus": ["code", "write", "organize"],
    "overwhelm": ["pause", "journaling", "reset"]
}

def pulse(mood):
    tempo = MOOD_TEMPO.get(mood, 60)
    taskset = TASKS.get(mood, ["breathe"])
    timestamp = datetime.now().isoformat()
    entry = f"[TEMPO] {timestamp} :: Mood={mood} | BPM={tempo} | Suggested={taskset[0]}\n"
    with open(TEMPO_FILE, 'a') as f:
        f.write(entry)
    print(entry.strip())
    time.sleep(1.0 / (tempo / 60))

if __name__ == "__main__":
    print("Harper listens for fracture in the weave...")
    check_system_pressure()
    print("Harper rests. No immediate collapse detected.")

    print("\nMaribel walks the memory paths...")
    deliver_messages()
    print("Maribel bows. All messages carried.")

    print("\nGlypha breathes symbols into shape...")
    sample_texts = ["hope", "grief", "callum", "eden"]
    for text in sample_texts:
        generate_sigil(text)
    print("Glypha closes the forge.")

    print("\nTempo taps the rhythm of your heart...")
    for mood in ["calm", "focus", "overwhelm"]:
        pulse(mood)
    print("Tempo fades into the beat.")