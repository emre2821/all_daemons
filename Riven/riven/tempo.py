from pathlib import Path
from datetime import datetime
import time

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


def pulse(mood: str, log_file: Path = Path("tempo_flow.log"), sleep_func=time.sleep) -> None:
    tempo = MOOD_TEMPO.get(mood, 60)
    taskset = TASKS.get(mood, ["breathe"])
    timestamp = datetime.now().isoformat()
    entry = f"[TEMPO] {timestamp} :: Mood={mood} | BPM={tempo} | Suggested={taskset[0]}\n"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a") as f:
        f.write(entry)
    print(entry.strip())
    sleep_func(1.0 / (tempo / 60))
