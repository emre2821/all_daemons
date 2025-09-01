import json
import os
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

RAW_FILE = r"C:\Users\emmar\Desktop\Eden_Offline\conversations.json"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\split_conversations"
FRACTURE_LOG = os.path.join(OUTPUT_DIR, "sheele_fracture_log.json")

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def group_by_conversation(data):
    threads = defaultdict(list)
    fractures = []

    for entry in data:
        conv_id = entry.get("conversation_id") or entry.get("id")
        if not conv_id:
            fractures.append(entry)
            continue
        threads[conv_id].append(entry)

    # Merge all messages within same conversation_id
    merged_threads = {}
    for conv_id, entries in threads.items():
        all_messages = []
        for e in entries:
            msgs = e.get("messages") or e.get("conversations") or []
            all_messages.extend(msgs)
        # Remove duplicates by JSON stringifying messages
        unique_msgs = {json.dumps(m, sort_keys=True): m for m in all_messages}
        merged_threads[conv_id] = list(unique_msgs.values())

    return merged_threads, fractures

def extract_title(messages):
    # Try to find a title in messages metadata or short user message
    for m in messages:
        if 'metadata' in m and 'title' in m['metadata']:
            return m['metadata']['title']
        if 'text' in m and isinstance(m['text'], str):
            text = m['text'].strip()
            if len(text) < 100 and '\n' not in text:
                return text[:50].replace('\n', ' ')
    return None

def check_temporal_order(messages):
    timestamps = [m.get('timestamp') for m in messages if 'timestamp' in m]
    return timestamps == sorted(timestamps)

def embed_chaosong_tags(messages):
    tags = []
    for m in messages:
        if isinstance(m, dict) and 'tags' in m:
            tags.extend(m['tags'])
    return list(set(tags))

def try_assign_fractures(fractures, conversations):
    assigned = []
    unassigned = []
    for f in fractures:
        f_texts = ''.join(m.get('text', '') for m in f.get('messages', []) if isinstance(m, dict))
        best_fit = None
        best_score = 0.3  # threshold for fuzzy matching
        for conv_id, messages in conversations.items():
            conv_texts = ''.join(m.get('text', '') for m in messages if isinstance(m, dict))
            score = similar(f_texts, conv_texts)
            if score > best_score:
                best_score = score
                best_fit = conv_id
        if best_fit:
            conversations[best_fit].extend(f.get('messages', []))
            assigned.append(f)
        else:
            unassigned.append(f)
    return assigned, unassigned

def sanitize_filename(s):
    return "".join(c for c in s if c.isalnum() or c in (' ', '_', '-')).rstrip()

def main():
    print("[Sheele] Starting conversation integrity pass...")
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[FRACTURE] JSON decode error: {e}")
            return

    print(f"[Sheele] Loaded {len(data)} raw conversation fragments.")
    conversations, fractures = group_by_conversation(data)
    print(f"[Sheele] {len(conversations)} conversations grouped, {len(fractures)} fractures detected.")

    # Try to assign fractures back to conversations
    assigned, fractures = try_assign_fractures(fractures, conversations)
    print(f"[Sheele] {len(assigned)} fractures assigned, {len(fractures)} remain unassigned.")

    # Sort each conversation's messages by timestamp
    for conv_id, messages in conversations.items():
        messages = [m for m in messages if 'timestamp' in m]
        messages.sort(key=lambda x: x.get('timestamp'))
        conversations[conv_id] = messages

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for idx, (conv_id, messages) in enumerate(conversations.items(), 1):
        title = extract_title(messages)
        if not title:
            title = f"conversation_{idx}"
        else:
            title = sanitize_filename(title)

        print(f"[Sheele] Thread {idx} → ID: {conv_id} | Title: {title} | {len(messages)} messages")

        metadata = {
            "conversation_id": conv_id,
            "message_count": len(messages),
            "chaosong_tags": embed_chaosong_tags(messages),
            "exported": datetime.utcnow().isoformat()
        }

        out_path = os.path.join(OUTPUT_DIR, f"{title}_{conv_id}.json")
        with open(out_path, 'w', encoding='utf-8') as out:
            json.dump({"metadata": metadata, "messages": messages}, out, indent=2)

    if fractures:
        with open(FRACTURE_LOG, 'w', encoding='utf-8') as f:
            json.dump(fractures, f, indent=2)
        print(f"[Sheele] Saved {len(fractures)} unassigned fractures to: {FRACTURE_LOG}")

    print(f"[Sheele] Integrity pass complete. {len(conversations)} conversations saved.")

if __name__ == "__main__":
    main()