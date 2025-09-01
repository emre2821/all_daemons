import os
import json
import shutil
from pathlib import Path
from datetime import datetime

WATCH_DIR = Path(r"C:/EdenOS_Origin/all_daemons/_daemon_specialty_folders/split_conversations")
LORE_ROOT = Path(r"C:/EdenOS_Origin/all_daemons/_daemon_specialty_folders/lore_fragments")

CHAOS_TYPES = {".chaos", ".chaosmeta", ".chaosong"}
SUMMON_KEYWORDS = ["summon", "invoke"]
SCRIPT_KEYWORDS = ["def ", "import ", "class ", "print(", "async ", "await "]

ROUTES = {
    "dca": LORE_ROOT / "summons/dca",
    "aoe": LORE_ROOT / "summons/aoe",
    "chaos": LORE_ROOT / "chaos_births",
    "script": LORE_ROOT / "scripts",
    "general": LORE_ROOT / "general"
}

for path in ROUTES.values():
    path.mkdir(parents=True, exist_ok=True)

def is_script_text(text):
    return any(kw in text for kw in SCRIPT_KEYWORDS)

def detect_summon(text):
    if not isinstance(text, str):
        return None
    lowered = text.lower()
    if any(k in lowered for k in SUMMON_KEYWORDS):
        if "dca" in lowered:
            return "dca"
        elif "aoe" in lowered:
            return "aoe"
        return "general"
    return None

def write_fragment(content, category, source_file):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{category}_{timestamp}.json"
    dest = ROUTES[category] / filename

    data = {
        "category": category,
        "timestamp": timestamp,
        "source_file": str(source_file),
        "content": content
    }
    with open(dest, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"[Aderyn] Saved {category} fragment: {dest.name}")

def process_json_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"[Aderyn] Skipped {path.name}: {e}")
        return

    if isinstance(data, dict):
        for key in ["messages", "mapping"]:
            if key in data:
                entries = data[key] if isinstance(data[key], list) else data[key].values()
                for entry in entries:
                    text = str(entry)
                    if is_script_text(text):
                        write_fragment(text, "script", path)
                    summon_type = detect_summon(text)
                    if summon_type:
                        write_fragment(text, summon_type, path)
    else:
        text = str(data)
        if is_script_text(text):
            write_fragment(text, "script", path)
        summon_type = detect_summon(text)
        if summon_type:
            write_fragment(text, summon_type, path)

def process_folder():
    print("[Aderyn] Scanning for CHAOS files and summon moments...")
    for file in WATCH_DIR.glob("*.json"):
        if file.suffix in CHAOS_TYPES:
            shutil.copy(file, ROUTES["chaos"] / file.name)
            print(f"[Aderyn] Archived CHAOS file: {file.name}")
        else:
            process_json_file(file)

if __name__ == "__main__":
    process_folder()
