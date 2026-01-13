import json
import os
from datetime import datetime
from datetime import timezone
from pathlib import Path
import re

# Get paths relative to script location
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RHEA_DIR = BASE_DIR / "Rhea"
INPUT_DIR = RHEA_DIR / "outputs" / "Sheele" / "split_conversations"
OUTPUT_DIR = RHEA_DIR / "outputs" / "Briar" / "split_conversations_txt"
QUARANTINE_DIR = OUTPUT_DIR / "_quarantine"
MAX_TURNS = int(os.environ.get("BRIAR_MAX_TURNS", "100"))
TRIM_MODE = os.environ.get("EDEN_TRIM_MODE", "strict").lower()

def log(msg):
    print(f"[Briar] {msg}")

def clean_filename(s: str, max_length: int = 50) -> str:
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', s)
    # Replace multiple underscores with single
    cleaned = re.sub(r'_+', '_', cleaned)
    # Strip leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Limit length but keep meaningful part
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('_')
    return cleaned if cleaned else 'untitled'

def extract_conversation_date(convo):
    for key in ["create_time", "created_at", "date", "timestamp"]:
        if key in convo:
            val = convo[key]
            try:
                ts = float(val)
                if ts > 1e11:
                    ts /= 1000
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                return dt.strftime("%Y-%m-%d")
            except:
                pass
            try:
                dt = datetime.fromisoformat(str(val))
                return dt.strftime("%Y-%m-%d")
            except:
                pass
    return datetime.now().strftime("%Y-%m-%d")

def extract_mapping_from_message(msg):
    mapping = msg.get("mapping")
    if isinstance(mapping, dict):
        return mapping
    if isinstance(mapping, list):
        return {str(i): v for i, v in enumerate(mapping)}
    return None

def extract_text_role(turn):
    if not isinstance(turn, dict):
        return None, None
    msg = turn.get("message")
    if not msg:
        return None, None
    content = msg.get("content", {})
    parts = content.get("parts", [])
    if not parts or not isinstance(parts, list):
        return None, None
    text = parts[0] if isinstance(parts[0], str) else "<Invalid format>"
    role = msg.get("author", {}).get("role", "UNKNOWN").upper()
    return text.strip(), role

def process_json_file(filepath, idx):
    log(f"Processing file: {filepath.name}")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            convo = json.load(f)
    except Exception as e:
        log(f"JSON decode error: {e}")
        quarantine(filepath, "decode_error")
        return

    title = convo.get("title", "Untitled")
    date = extract_conversation_date(convo)

    # Create proper header
    lines = [f"--- Conversation: {title} ({date}) ---\n\n"]

    messages = convo.get("messages", [])
    if not messages:
        quarantine(filepath, "no_messages")
        return

    count = 0
    for msg in messages:
        mapping = extract_mapping_from_message(msg)
        if not mapping:
            continue

        for turn_id, turn in sorted(
            mapping.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]
        ):
            text, role = extract_text_role(turn)
            if text is None or role is None:
                continue
            role = (
                "DREAMBEARER"
                if role == "USER"
                else "KIN" if role == "ASSISTANT" else role
            )
            lines.append(f"[{role}] {text}\n")
            count += 1
            if TRIM_MODE != "gentle" and count >= MAX_TURNS:
                lines.append("\n[Conversation trimmed due to length limit]\n")
                break
        if TRIM_MODE != "gentle" and count >= MAX_TURNS:
            break

    if count == 0:
        quarantine(filepath, "no_valid_messages")
        return

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Better filename construction
    safe_title = clean_filename(title)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    out_filename = f"{date}_{idx + 1:04d}_{safe_title}.txt"

    # Ensure unique filename
    outpath = OUTPUT_DIR / out_filename
    counter = 1
    while outpath.exists():
        out_filename = f"{date}_{idx + 1:04d}_{safe_title}_{counter}.txt"
        outpath = OUTPUT_DIR / out_filename
        counter += 1

    with open(outpath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    log(f"Saved: {outpath.name}")

def quarantine(filepath, reason="unknown"):
    QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)
    name = filepath.name
    dest = QUARANTINE_DIR / f"{reason}_{name}"
    try:
        # Ensure source file exists before trying to copy
        if filepath.exists():
            dest.write_text(filepath.read_text(encoding="utf-8"), encoding="utf-8")
            log(f"Quarantined {name} → Reason: {reason}")
        else:
            log(f"Source file not found for quarantine: {filepath}")
    except Exception as e:
        log(f"Failed to quarantine {name}: {e}")

def main():
    import sys

    # Get limit from command line args or environment
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    if limit is None:
        limit = int(os.environ.get("BRIAR_LIMIT", "0"))

    if not INPUT_DIR.exists():
        log(f"Missing input dir: {INPUT_DIR}")
        return

    files = [f for f in INPUT_DIR.iterdir() if f.suffix == ".json"]
    if not files:
        log("No .json files to process.")
        return

    # Sort files by modification time or name
    files.sort(key=lambda x: x.stat().st_mtime if x.exists() else 0)

    # Apply limit if specified
    if limit > 0:
        files = files[:limit]
        log(f"Limiting to {limit} files (was {len(files)})")

    for idx, file_path in enumerate(files):
        try:
            process_json_file(file_path, idx)
        except Exception as e:
            log(f"Error processing {file_path.name}: {e}")

    log("All conversations processed.")

if __name__ == "__main__":
    main()
