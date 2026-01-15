import json
import os
from datetime import datetime, timezone

# === CONFIG ===
WORK_ROOT = os.environ.get("EDEN_WORK_ROOT", os.environ.get("EDEN_ROOT", os.getcwd()))
INPUT_DIR = os.path.join(WORK_ROOT, "daemons", "_daemon_specialty_folders", "split_conversations")
OUTPUT_DIR = os.path.join(WORK_ROOT, "daemons", "_daemon_specialty_folders", "split_conversations_txt")
QUARANTINE_DIR = os.path.join(OUTPUT_DIR, "_quarantine")
MAX_TURNS = int(os.environ.get("BRIAR_MAX_TURNS", "100"))
TRIM_MODE = os.environ.get("EDEN_TRIM_MODE", "strict").lower()

# === HELPERS ===
def log(msg):
    print(f"[Briar] {msg}")

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def extract_conversation_date(conversation):
    for key in ['create_time', 'created_at', 'date', 'timestamp']:
        if key in conversation:
            val = conversation[key]
            try:
                ts = float(val)
                if ts > 1e11:
                    ts /= 1000
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                return dt.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                pass
            try:
                dt = datetime.fromisoformat(str(val))
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                pass
    return "unknown_date"

def extract_mapping_from_message(message):
    mapping = message.get("mapping")
    if isinstance(mapping, dict):
        return mapping
    if isinstance(mapping, list):
        return {str(i): v for i, v in enumerate(mapping)}
    return None

def extract_message_text_and_role(turn):
    if not isinstance(turn, dict):
        return None, None
    message = turn.get("message")
    if not message:
        return None, None
    content = message.get("content", {})
    parts = content.get("parts", [])
    if not parts or not isinstance(parts, list):
        return None, None
    text = parts[0] if isinstance(parts[0], str) else "<Invalid format>"
    role = message.get("author", {}).get("role", "UNKNOWN").upper()
    return text.strip(), role

def process_json_file(json_file_path, idx):
    log(f"Processing file: {json_file_path}")
    safe_title = f"unknown_{idx + 1}"
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            conversation = json.load(f)
    except json.JSONDecodeError as e:
        log(f"JSON decode error in {json_file_path}: {e}")
        quarantine(json_file_path, reason="decode_error")
        return

    title = conversation.get('title', 'Untitled')
    date_str = extract_conversation_date(conversation)
    output_lines = [f"--- Conversation: {title} ({date_str}) ---\n\n"]

    messages = conversation.get("messages", [])
    if not messages:
        log(f"No messages in {title}")
        quarantine(json_file_path, reason="no_messages")
        return

    message_count = 0
    for message_obj in messages:
        mapping = extract_mapping_from_message(message_obj)
        if not mapping:
            continue

        for turn_id, turn in sorted(mapping.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
            text, role = extract_message_text_and_role(turn)
            if text is None or role is None:
                continue

            if role == "USER":
                role = "DREAMBEARER"
            elif role == "ASSISTANT":
                role = "KIN"

            output_lines.append(f"[{role}] {text}\n")
            message_count += 1
            if TRIM_MODE != "gentle" and message_count >= MAX_TURNS:
                break

        if TRIM_MODE != "gentle" and message_count >= MAX_TURNS:
            break

    if message_count == 0:
        log(f"No valid messages in {title}")
        quarantine(json_file_path, reason="no_valid_messages")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_title = clean_filename(title)[:32]
    out_filename = f"conversation_{idx + 1}_{date_str}_{safe_title}.txt"
    outpath = os.path.join(OUTPUT_DIR, out_filename)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.writelines(output_lines)
    log(f"Saved: {outpath}")

def quarantine(json_file_path, reason="unknown"):
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    filename = os.path.basename(json_file_path)
    dest = os.path.join(QUARANTINE_DIR, f"{reason}_{filename}")
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f_in, open(dest, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        log(f"Quarantined {filename} → Reason: {reason}")
    except Exception as e:
        log(f"Failed to quarantine {filename}: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        log(f"Missing input dir: {INPUT_DIR}")
        return

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    if not files:
        log("No .json files to process.")
        return

    for idx, file_name in enumerate(sorted(files)):
        try:
            process_json_file(os.path.join(INPUT_DIR, file_name), idx)
        except Exception as e:
            log(f"Error processing {file_name}: {e}")
            quarantine(os.path.join(INPUT_DIR, file_name), reason="exception")

    log("All conversations processed.")

if __name__ == "__main__":
    main()
