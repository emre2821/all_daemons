from datetime import datetime
import time

TEMPO_FILE = "./tempo_flow.log"

MOOD_TEMPO = {
    "calm": 25,
    "focus": 50,
    "overwhelm": 90,
}

TASKS = {
    "calm": ["breathe", "tidy workspace", "light stretch"],
    "focus": ["code", "write", "organize"],
    "overwhelm": ["pause", "journaling", "reset"],
}


def pulse(mood: str) -> None:
    tempo = MOOD_TEMPO.get(mood, 60)
    taskset = TASKS.get(mood, ["breathe"])
    timestamp = datetime.now().isoformat()
    entry = (
        f"[TEMPO] {timestamp} :: Mood={mood} | BPM={tempo} | "
        f"Suggested={taskset[0]}\n"
    )
    with open(TEMPO_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())
    time.sleep(1.0 / (tempo / 60))
