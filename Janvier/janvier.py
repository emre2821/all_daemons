from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from Daemon_tools.scripts.eden_paths import rhea_root  # noqa: E402

INPUT_DIR = rhea_root() / "outputs" / "Briar" / "split_conversations_txt"
OUTPUT_DIR = rhea_root() / "outputs" / "Janvier" / "chaos_threads"


def clean_filename(raw: str) -> str:
    return "".join(c if c.isalnum() else "_" for c in raw)


def parse_txt_file(txt_file_path: Path):
    content = txt_file_path.read_text(encoding="utf-8")

    lines = content.splitlines()
    if not lines:
        return None, None, None

    title_line = lines[0] if lines[0].startswith("--- Conversation:") else None
    title = "Untitled"
    date = "unknown_date"

    if title_line:
        try:
            title = title_line.split("Conversation:")[1].split("(")[0].strip()
            date = title_line.split("(")[1].split(")")[0]
        except Exception:
            pass
        lines = lines[2:]

    conversation = []
    for line in lines:
        if line.startswith("[DREAMBEARER]"):
            role = "DREAMBEARER"
            text = line[len("[DREAMBEARER]") :].strip()
        elif line.startswith("[KIN]"):
            role = "KIN"
            text = line[len("[KIN]") :].strip()
        else:
            role = "UNKNOWN"
            text = line.strip()
        if text:
            conversation.append({"role": role, "text": text})

    return title, date, conversation


def convert_to_chaos(title, date, conversation):
    nodes = []
    for i, turn in enumerate(conversation):
        nodes.append(
            {
                "id": f"node_{i+1}",
                "role": turn["role"],
                "content": turn["text"],
                "timestamp": datetime.now().isoformat(),
            }
        )
    return {"title": title, "date": date, "nodes": nodes}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_DIR.exists():
        print(f"⚠️ Input directory not found: {INPUT_DIR}")
        return

    for txt_path in INPUT_DIR.glob("*.txt"):
        title, date, convo = parse_txt_file(txt_path)
        if not convo:
            continue
        chaos_data = convert_to_chaos(title, date, convo)
        safe_title = clean_filename(title)[:32]
        outname = f"{date}_{safe_title}.chaos"
        outpath = OUTPUT_DIR / outname
        outpath.write_text(json.dumps(chaos_data, indent=2), encoding="utf-8")
        print(f"✅ Janvier converted {txt_path.name} -> {outname}")


if __name__ == "__main__":
    main()
