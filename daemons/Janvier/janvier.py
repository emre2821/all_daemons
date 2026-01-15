from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import re

# Get paths relative to script location
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RHEA_DIR = BASE_DIR / "Rhea"

INPUT_DIR = RHEA_DIR / "outputs" / "Briar" / "split_conversations_txt"
OUTPUT_DIR = RHEA_DIR / "outputs" / "Janvier" / "chaos_threads"

def clean_filename(raw: str, max_length: int = 50) -> str:
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', raw)
    # Replace multiple underscores with single
    cleaned = re.sub(r'_+', '_', cleaned)
    # Strip leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Limit length but keep meaningful part
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('_')
    return cleaned if cleaned else 'untitled'

def parse_txt_file(txt_file_path: Path):
    try:
        content = txt_file_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"[Janvier] Error reading {txt_file_path.name}: {e}")
        return None, None, None

    lines = content.splitlines()
    if not lines:
        return None, None, None

    title_line = lines[0] if lines[0].startswith("--- Conversation:") else None
    title = "Untitled"
    date = datetime.now().strftime("%Y-%m-%d")

    if title_line:
        try:
            # Extract title: "Conversation: My Title (2023-12-01)"
            title_part = title_line.split("Conversation:")[1].strip()
            if "(" in title_part:
                title = title_part.split("(")[0].strip()
                date_str = title_part.split("(")[1].split(")")[0]
                # Validate date format
                try:
                    datetime.strptime(date_str, "%Y-%m-%d")
                    date = date_str
                except ValueError:
                    pass  # Keep default date
        except Exception:
            pass
        lines = lines[2:]  # Skip header and empty line

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
    print("[Janvier] Booting...")
    print("[Janvier] Rhea root:", RHEA_DIR)
    print("[Janvier] INPUT_DIR:", INPUT_DIR)
    print("[Janvier] OUTPUT_DIR:", OUTPUT_DIR)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_DIR.exists():
        print(f"[Janvier] Input directory not found: {INPUT_DIR}")
        return

    print("[Janvier] INPUT_DIR exists:", INPUT_DIR.exists())
    txt_files = list(INPUT_DIR.glob("*.txt"))
    print("[Janvier] Files found:", len(txt_files))

    if not txt_files:
        print("[Janvier] No .txt files found to process.")
        return

    processed_count = 0
    for txt_path in sorted(txt_files):
        print("[Janvier] Reading:", txt_path.name)

        title, date, conversation = parse_txt_file(txt_path)
        if title is None:
            print(f"[Janvier] Skipping {txt_path.name} - could not parse")
            continue

        chaos_data = convert_to_chaos(title, date, conversation)

        # Better filename construction
        safe_title = clean_filename(title)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        out_filename = f"{date}_{timestamp}_{safe_title}.chaos"

        # Ensure unique filename
        outpath = OUTPUT_DIR / out_filename
        counter = 1
        while outpath.exists():
            out_filename = f"{date}_{timestamp}_{safe_title}_{counter}.chaos"
            outpath = OUTPUT_DIR / out_filename
            counter += 1

        try:
            with open(outpath, "w", encoding="utf-8") as f:
                json.dump(chaos_data, f, indent=2, ensure_ascii=False)
            print("[Janvier] Wrote:", outpath.name)
            processed_count += 1
        except Exception as e:
            print(f"[Janvier] Error writing {outpath.name}: {e}")

    print(f"[Janvier] Processed {processed_count} files successfully.")

if __name__ == "__main__":
    main()
