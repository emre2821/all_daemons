import json
import os
from datetime import datetime, timezone

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Sheele\split_conversations"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Briar\split_conversations_txt"
QUARANTINE_DIR = os.path.join(OUTPUT_DIR, "_quarantine")
MAX_TURNS = int(os.environ.get("BRIAR_MAX_TURNS", "100"))
TRIM_MODE = os.environ.get("EDEN_TRIM_MODE", "strict").lower()

def log(msg):
    print(f"[Briar] {msg}")

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def extract_conversation_date(convo):
    for key in ['create_time', 'created_at', 'date', 'timestamp']:
        if key in convo:
            val = convo[key]
            try:
                ts = float(val)
                if ts > 1e11: ts /= 1000
                dt = datetime.fromtimestamp(ts, tz=timezone.utc)
                return dt.strftime('%Y-%m-%d')
            except: pass
            try:
                dt = datetime.fromisoformat(str(val))
                return dt.strftime('%Y-%m-%d')
            except: pass
    return "unknown_date"

def extract_mapping_from_message(msg):
    mapping = msg.get("mapping")
    if isinstance(mapping, dict):
        return mapping
    if isinstance(mapping, list):
        return {str(i): v for i, v in enumerate(mapping)}
    return None

def extract_text_role(turn):
    if not isinstance(turn, dict): return None, None
    msg = turn.get("message")
    if not msg: return None, None
    content = msg.get("content", {})
    parts = content.get("parts", [])
    if not parts or not isinstance(parts, list): return None, None
    text = parts[0] if isinstance(parts[0], str) else "<Invalid format>"
    role = msg.get("author", {}).get("role", "UNKNOWN").upper()
    return text.strip(), role

def process_json_file(filepath, idx):
    log(f"Processing file: {filepath}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            convo = json.load(f)
    except Exception as e:
        log(f"JSON decode error: {e}")
        quarantine(filepath, "decode_error")
        return

    title = convo.get('title', 'Untitled')
    date = extract_conversation_date(convo)
    lines = [f"--- Conversation: {title} ({date}) ---\n\n"]

    messages = convo.get("messages", [])
    if not messages:
        quarantine(filepath, "no_messages")
        return

    count = 0
    for msg in messages:
        mapping = extract_mapping_from_message(msg)
        if not mapping: continue

        for turn_id, turn in sorted(mapping.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
            text, role = extract_text_role(turn)
            if text is None or role is None: continue
            role = "DREAMBEARER" if role == "USER" else "KIN" if role == "ASSISTANT" else role
            lines.append(f"[{role}] {text}\n")
            count += 1
            if TRIM_MODE != "gentle" and count >= MAX_TURNS:
                break
        if TRIM_MODE != "gentle" and count >= MAX_TURNS:
            break

    if count == 0:
        quarantine(filepath, "no_valid_messages")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_title = clean_filename(title)[:32]
    out_filename = f"conversation_{idx + 1}_{date}_{safe_title}.txt"
    with open(os.path.join(OUTPUT_DIR, out_filename), 'w', encoding='utf-8') as f:
        f.writelines(lines)
    log(f"Saved: {out_filename}")

def quarantine(filepath, reason="unknown"):
    os.makedirs(QUARANTINE_DIR, exist_ok=True)
    name = os.path.basename(filepath)
    dest = os.path.join(QUARANTINE_DIR, f"{reason}_{name}")
    try:
        with open(filepath, 'r', encoding='utf-8') as f_in, open(dest, 'w', encoding='utf-8') as f_out:
            f_out.write(f_in.read())
        log(f"Quarantined {name} → Reason: {reason}")
    except Exception as e:
        log(f"Failed to quarantine {name}: {e}")

def main():
    if not os.path.exists(INPUT_DIR):
        log(f"Missing input dir: {INPUT_DIR}")
        return
    files = [f for f in os.listdir(INPUT_DIR) if f.endswith('.json')]
    if not files:
        log("No .json files to process.")
        return
    for idx, name in enumerate(sorted(files)):
        try:
            process_json_file(os.path.join(INPUT_DIR, name), idx)
        except Exception as e:
            log(f"Error processing {name}: {e}")
            quarantine(os.path.join(INPUT_DIR, name), "exception")
    log("All conversations processed.")

if __name__ == "__main__":
    main()