import os
import json
from pathlib import Path
from datetime import datetime

WORK_ROOT = Path(os.environ.get("EDEN_WORK_ROOT", os.environ.get("EDEN_ROOT", Path.cwd())))
DCA_DIR = WORK_ROOT / "daemons" / "_daemon_specialty_folders" / "lore_fragments" / "summons" / "dca"
AOE_DIR = WORK_ROOT / "daemons" / "_daemon_specialty_folders" / "lore_fragments" / "summons" / "aoe"

ARCHIVE_DIR = {
    "dca": WORK_ROOT / "daemons" / "Serideth" / "received_logs",
    "aoe": WORK_ROOT / "daemons" / "AoE_Profile_Manager" / "received_logs",
}

for folder in ARCHIVE_DIR.values():
    folder.mkdir(parents=True, exist_ok=True)

def clean_and_route(source_dir, archive_dir, label):
    for file in source_dir.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            cleaned = {
                "agent_name": extract_agent_name(data.get("content", "")),
                "timestamp": data.get("timestamp"),
                "origin": data.get("source_file"),
                "raw_content": data.get("content")
            }

            outname = f"{cleaned['agent_name'] or 'unknown'}_{datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')}.json"
            outpath = archive_dir / outname
            with open(outpath, 'w', encoding='utf-8') as out:
                json.dump(cleaned, out, indent=2)
            print(f"[{label}] Archived summon: {outname}")

            file.unlink()  # Remove original after processing
        except Exception as e:
            print(f"[{label}] Error processing {file.name}: {e}")

def extract_agent_name(text):
    if not isinstance(text, str):
        return None
    for token in text.replace('"', "'" ).split():
        if token.startswith("'") and token.endswith("'"):
            return token.strip("'").capitalize()
    return None

def main():
    clean_and_route(DCA_DIR, ARCHIVE_DIR["dca"], "Serideth")
    clean_and_route(AOE_DIR, ARCHIVE_DIR["aoe"], "AoE")

if __name__ == "__main__":
    main()
