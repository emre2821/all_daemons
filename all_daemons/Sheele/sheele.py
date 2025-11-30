import json
import os
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

DEFAULT_RAW = r"C:\EdenOS_Origin\all_daemons\Rhea\inputs\conversations.json"
RAW_FILE = os.environ.get("SHEELE_RAW_FILE", DEFAULT_RAW)
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Sheele\split_conversations"
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

    merged_threads = {}
    for conv_id, entries in threads.items():
        all_messages = []
        for e in entries:
            msgs = e.get("messages") or e.get("conversations") or []
            all_messages.extend(msgs)
        unique_msgs = {json.dumps(m, sort_keys=True): m for m in all_messages}
        merged_threads[conv_id] = list(unique_msgs.values())

    return merged_threads, fractures

def extract_title(messages):
    for m in messages:
        if 'metadata' in m and 'title' in m['metadata']:
            return m['metadata']['title']
        if 'text' in m and isinstance(m['text'], str):
            text = m['text'].strip()
            is_short = len(text) < 100
            contains_apostrophe = "'" in text
            if is_short and not contains_apostrophe:
                return text[:50].replace('\n', ' ')
    return None

def try_assign_fractures(fractures, conversations):
    assigned = []
    unassigned = []
    for f in fractures:
        f_texts = ''.join(m.get('text', '') for m in f.get('messages', []) if isinstance(m, dict))
        best_fit = None
        best_score = 0
        for cid, convo in conversations.items():
            convo_texts = ''.join(m.get('text', '') for m in convo if isinstance(m, dict))
            score = similar(f_texts, convo_texts)
            if score > best_score:
                best_fit = cid
                best_score = score
        if best_score > 0.6:
            conversations[best_fit].extend(f.get('messages', []))
            assigned.append(f)
        else:
            unassigned.append(f)
    return conversations, unassigned

def save_conversations(conversations):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for cid, messages in conversations.items():
        date_str = datetime.now().strftime("%Y-%m-%d")
        title = extract_title(messages) or f"thread_{cid}"
        fname = f"{date_str}_{cid}_{title[:40].replace(' ', '_')}.json"
        outpath = os.path.join(OUTPUT_DIR, fname)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump({
                "id": cid,
                "title": title,
                "create_time": date_str,
                "messages": messages
            }, f, indent=2)

def main():
    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print(f"? Sheele: RAW_FILE not found at {RAW_FILE}. Set SHEELE_RAW_FILE or place conversations.json.")
        return
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    grouped, fractures = group_by_conversation(data)
    grouped, lost = try_assign_fractures(fractures, grouped)
    save_conversations(grouped)

    with open(FRACTURE_LOG, 'w', encoding='utf-8') as f:
        json.dump(lost, f, indent=2)
    print(f"✅ Sheele saved {len(grouped)} threads with {len(lost)} unassigned fragments.")

if __name__ == "__main__":
    main()
