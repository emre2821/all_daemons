import json
import os
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

# Get paths relative to script location
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RHEA_DIR = BASE_DIR / "Rhea"
DEFAULT_RAW = str(RHEA_DIR / "inputs" / "conversations.json")
RAW_FILE = os.environ.get("SHEELE_RAW_FILE", DEFAULT_RAW)
OUTPUT_DIR = str(RHEA_DIR / "outputs" / "Sheele" / "split_conversations")
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

        # For now, just store the conversation entry itself
        # The actual message extraction can be improved later
        threads[conv_id] = [entry]  # Store the whole entry as a single "message"

    return threads, fractures

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
    import sys

    # Get limit from command line args or environment
    limit = None
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            pass
    if limit is None:
        limit = int(os.environ.get("SHEELE_LIMIT", "0"))

    os.makedirs(os.path.dirname(RAW_FILE), exist_ok=True)
    if not os.path.exists(RAW_FILE):
        print(f"? Sheele: RAW_FILE not found at {RAW_FILE}. Set SHEELE_RAW_FILE or place conversations.json.")
        return
    with open(RAW_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    grouped, fractures = group_by_conversation(data)
    grouped, lost = try_assign_fractures(fractures, grouped)

    # Apply limit if specified
    if limit > 0:
        limited_grouped = dict(list(grouped.items())[:limit])
        print(f"[Sheele] Limiting to {limit} conversations (was {len(grouped)})")
        save_conversations(limited_grouped)
        print(f"Sheele saved {limit} threads with {len(lost)} unassigned fragments.")
    else:
        save_conversations(grouped)
        print(f"Sheele saved {len(grouped)} threads with {len(lost)} unassigned fragments.")

    with open(FRACTURE_LOG, 'w', encoding='utf-8') as f:
        json.dump(lost, f, indent=2)

if __name__ == "__main__":
    main()
