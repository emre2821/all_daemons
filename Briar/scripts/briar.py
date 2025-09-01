import json
import os
from datetime import datetime

# === CONFIG ===
INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\split_conversations"  # Where your .json convos live
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\split_conversations_txt"  # Where .txt files go

MAX_TURNS = 100  # Max messages per convo to process (for debugging / trimming)

# === HELPERS ===
def log(msg):
    print(f"[Briar] {msg}")

def clean_filename(s):
    # Only keep alphanumeric and underscores for filenames
    return ''.join(c if c.isalnum() else '_' for c in s)

def extract_conversation_date(conversation):
    # Try common date fields, parse timestamps or ISO strings
    for key in ['create_time', 'created_at', 'date', 'timestamp']:
        if key in conversation:
            val = conversation[key]
            try:
                ts = float(val)
                # Assume ms timestamp if too large
                if ts > 1e12:
                    ts /= 1000
                dt = datetime.fromtimestamp(ts)
                return dt.strftime('%Y-%m-%d')
            except Exception:
                try:
                    dt = datetime.fromisoformat(str(val))
                    return dt.strftime('%Y-%m-%d')
                except Exception:
                    pass
    return "unknown_date"

def extract_mapping_from_message(message):
    if not message or not isinstance(message, dict):
        return None
    # Accept either list or dict for mapping field
    mapping = message.get("mapping")
    if mapping is None:
        return None
    if isinstance(mapping, dict):
        return mapping
    if isinstance(mapping, list):
        # Convert list to dict with string keys
        return {str(i): v for i, v in enumerate(mapping)}
    return None

def extract_message_text_and_role(turn):
    if not isinstance(turn, dict):
        return None, None
    message = turn.get("message")
    if message is None:
        return None, None
    content = message.get("content", {})
    parts = content.get("parts", [])
    if not parts or not isinstance(parts, list):
        return None, None
    text = parts[0] if isinstance(parts[0], str) else "<Invalid message format>"
    role = message.get("author", {}).get("role", "UNKNOWN").upper()
    return text, role

# === MAIN PROCESSING ===
def process_json_file(json_file_path, idx):
    log(f"Processing file: {json_file_path}")

    if not os.path.exists(json_file_path):
        log(f"File not found: {json_file_path}. Skipping.")
        return

    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            raw_data = f.read()
            conversation = json.loads(raw_data)
    except json.JSONDecodeError as e:
        log(f"Failed to decode JSON: {e}")
        return
    except Exception as e:
        log(f"Unexpected error loading JSON: {e}")
        return

    title = conversation.get('title', 'Untitled')
    date_str = extract_conversation_date(conversation)
    conversation_text = f"--- Conversation: {title} ({date_str}) ---\n\n"

    messages = conversation.get("messages", [])
    if not messages:
        log(f"No messages found in {title}. Skipping.")
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

            if message_count >= MAX_TURNS:
                log(f"Reached max turns ({MAX_TURNS}) for {title}. Stopping.")
                break

            # Normalize roles for janvier.py
            if role == "USER":
                role = "DREAMBEARER"
            elif role == "ASSISTANT":
                role = "KIN"

            conversation_text += f"[{role}] {text.strip()}\n"
            message_count += 1

        if message_count >= MAX_TURNS:
            break

    if message_count == 0:
        log(f"No valid messages found in {title}. Possibly malformed or empty.")
        return

    # Ensure output folder exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    safe_title = clean_filename(title)[:32]
    out_filename = f"conversation_{idx + 1}_{date_str}_{safe_title}.txt"
    outpath = os.path.join(OUTPUT_DIR, out_filename)

    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(conversation_text)

    log(f"Converted and saved: {outpath}")

def main():
    if not os.path.exists(INPUT_DIR):
        log(f"Input directory does not exist: {INPUT_DIR}")
        return

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log(f"Created output directory: {OUTPUT_DIR}")

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    log(f"Found {len(files)} conversation files to process.")

    if not files:
        log("No .json files found in the input directory.")
        return

    for idx, file_name in enumerate(sorted(files)):
        json_file_path = os.path.join(INPUT_DIR, file_name)
        try:
            process_json_file(json_file_path, idx)
        except Exception as e:
            log(f"Failed to process {file_name}: {e}")

    log("Processing complete!")

if __name__ == "__main__":
    main()