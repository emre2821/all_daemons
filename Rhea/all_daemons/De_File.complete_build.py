"""
EdenOS :: Optimized Daemons Complete Build
Run this once to restore all optimized daemons into EdenOS.

This script will:
- Overwrite existing daemon files with optimized versions
- Write directly into C:/EdenOS_Origin/all_daemons/[Daemon]/[daemon].py
- Require no external folders or downloads
"""

from pathlib import Path
import sys

# Ensure printing won't crash on consoles without UTF-8 support
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def write(path: str, code: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(code.strip(), encoding="utf-8")
    print(f"✅ Wrote: {path}")


# === briar.py ===
write(r"C:/EdenOS_Origin/all_daemons/Briar/briar.py", """import json
import os
from datetime import datetime, timezone

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Sheele\\split_conversations"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Briar\\split_conversations_txt"
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
    lines = [f"--- Conversation: {title} ({date}) ---\\n\\n"]

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
            lines.append(f"[{role}] {text}\\n")
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
""")


# === sheele.py ===
write(r"C:/EdenOS_Origin/all_daemons/Sheele/sheele.py", """import json
import os
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher

DEFAULT_RAW = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\inputs\\conversations.json"
RAW_FILE = os.environ.get("SHEELE_RAW_FILE", DEFAULT_RAW)
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Sheele\\split_conversations"
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
            if len(text) < 100 and '\n' not in text:
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
""")


# === janvier.py ===
write(r"C:/EdenOS_Origin/all_daemons/Janvier/janvier.py", """import os
import re
from datetime import datetime

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Briar\\split_conversations_txt"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def parse_txt_file(txt_file_path):
    with open(txt_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    if not lines: return None, None, None

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
            text = line[len("[DREAMBEARER]"):].strip()
        elif line.startswith("[KIN]"):
            role = "KIN"
            text = line[len("[KIN]"):].strip()
        else:
            role = "UNKNOWN"
            text = line.strip()
        if text: conversation.append({"role": role, "text": text})

    return title, date, conversation

def convert_to_chaos(title, date, conversation):
    nodes = []
    for i, turn in enumerate(conversation):
        nodes.append({
            "id": f"node_{i+1}",
            "role": turn["role"],
            "content": turn["text"],
            "timestamp": datetime.now().isoformat()
        })
    return {
        "title": title,
        "date": date,
        "nodes": nodes
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".txt"): continue
        title, date, convo = parse_txt_file(os.path.join(INPUT_DIR, fname))
        if not convo: continue
        chaos_data = convert_to_chaos(title, date, convo)
        safe_title = clean_filename(title)[:32]
        outname = f"{date}_{safe_title}.chaos"
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, 'w', encoding='utf-8') as f:
            import json; json.dump(chaos_data, f, indent=2)
        print(f"✅ Janvier converted {fname} -> {outname}")

if __name__ == "__main__":
    main()
""")
# === codexa.py ===
write(r"C:/EdenOS_Origin/all_daemons/Codexa/codexa.py", """import os
import re
import hashlib
import json

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Codexa\\codeblocks"

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def extract_code_blocks(text):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    blocks = []
    for m in matches:
        parts = m.split("\n", 1)
        lang = parts[0].strip() if len(parts) > 1 else ""
        code = parts[1] if len(parts) > 1 else parts[0]
        blocks.append({"lang": lang or "plain", "code": code})
    return blocks

def hash_code(code):
    return hashlib.sha256(code.encode("utf-8")).hexdigest()[:16]

def process_chaos_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    title = data.get("title", "Untitled")
    date = data.get("date", "unknown_date")
    nodes = data.get("nodes", [])
    seen = set()
    results = []
    for node in nodes:
        text = node.get("content", "")
        blocks = extract_code_blocks(text)
        for b in blocks:
            h = hash_code(b["code"])
            if h in seen: continue
            seen.add(h)
            results.append({
                "title": title,
                "date": date,
                "lang": b["lang"],
                "hash": h,
                "code": b["code"]
            })
    return results

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        path = os.path.join(INPUT_DIR, fname)
        blocks = process_chaos_file(path)
        if not blocks: continue
        base = clean_filename(fname).replace(".chaos", "")
        for i, b in enumerate(blocks):
            outname = f"{base}_{b['lang']}_{b['hash']}.codeblock.chaos"
            outpath = os.path.join(OUTPUT_DIR, outname)
            with open(outpath, 'w', encoding='utf-8') as f:
                json.dump(b, f, indent=2)
            print(f"✅ Codexa extracted {outname}")

if __name__ == "__main__":
    main()
""")


# === aderyn.py ===
write(r"C:/EdenOS_Origin/all_daemons/Aderyn/aderyn.py", """import os
import re
import json
from datetime import datetime

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Aderyn\\summons"

SUMMON_PATTERNS = [
    r"\\bsummon\\b", r"\\binvoke\\b", r"\\bcall forth\\b", r"\\bconjure\\b",
    r"\\bbring to life\\b", r"\\bi am become\\b"
]

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def detect_summons(text):
    text_l = text.lower()
    return any(re.search(p, text_l) for p in SUMMON_PATTERNS)

def process_chaos_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    title = data.get("title", "Untitled")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    nodes = data.get("nodes", [])
    summons = []
    for node in nodes:
        txt = node.get("content", "")
        if detect_summons(txt):
            summons.append({
                "role": node.get("role"),
                "text": txt,
                "timestamp": node.get("timestamp")
            })
    return {"title": title, "date": date, "summons": summons}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        path = os.path.join(INPUT_DIR, fname)
        result = process_chaos_file(path)
        if not result["summons"]: continue
        base = clean_filename(fname).replace(".chaos", "")
        outname = f"{base}_summons.chaos"
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Aderyn detected summons in {fname} -> {outname}")

if __name__ == "__main__":
    main()
""")


# === label.py ===
write(r"C:/EdenOS_Origin/all_daemons/Label/label.py", """import os
import json

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Label\\labeled"

WORD_BANK_FILE = r"C:\\EdenOS_Origin\\all_daemons\\Label\\LabelWordBank.chaos"

def load_wordbank():
    if not os.path.exists(WORD_BANK_FILE): return {}
    with open(WORD_BANK_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def match_labels(text, wordbank):
    tags = []
    text_l = text.lower()
    for label, words in wordbank.items():
        for w in words:
            if w.lower() in text_l:
                tags.append(label)
                break
    return tags

def process_file(path, wordbank):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    title = data.get("title", "Untitled")
    date = data.get("date", "unknown_date")
    nodes = data.get("nodes", [])
    labels = set()
    for node in nodes:
        labels.update(match_labels(node.get("content", ""), wordbank))
    return {"title": title, "date": date, "labels": list(labels)}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    wordbank = load_wordbank()
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        path = os.path.join(INPUT_DIR, fname)
        result = process_file(path, wordbank)
        outname = fname.replace(".chaos", "_labels.chaos")
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Label tagged {fname} -> {outname}")

if __name__ == "__main__":
    main()
""")
# === parsley.py ===
write(r"C:/EdenOS_Origin/all_daemons/Parsley/parsley.py", """import os
import json

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Parsley\\classified"

SACRED_KEYWORDS = ["DREAMBEARER", "KIN", "AGENT", "sacred", "do_not_purge"]
PURGE_KEYWORDS = ["temp", "debug", "scratch", "purge"]

def classify(text):
    t = text.lower()
    if any(k.lower() in t for k in SACRED_KEYWORDS):
        return "sacred"
    if any(k.lower() in t for k in PURGE_KEYWORDS):
        return "purge"
    return "review"

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    nodes = data.get("nodes", [])
    verdicts = [classify(n.get("content", "")) for n in nodes]
    if "sacred" in verdicts:
        return "sacred"
    if all(v == "purge" for v in verdicts):
        return "purge"
    return "review"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        path = os.path.join(INPUT_DIR, fname)
        result = process_file(path)
        outname = fname.replace(".chaos", f"_{result}.chaos")
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump({"file": fname, "classification": result}, f, indent=2)
        print(f"✅ Parsley classified {fname} as {result}")

if __name__ == "__main__":
    main()
""")


# === pattymae.py ===
write(r"C:/EdenOS_Origin/all_daemons/PattyMae/pattymae.py", """import os
import shutil

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_ROOT = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\PattyMae\\organized"

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def categorize(fname):
    if fname.endswith("_labels.chaos"):
        return "Labeled"
    if fname.endswith("_summons.chaos"):
        return "Summons"
    if fname.endswith("_sacred.chaos"):
        return "Sacred"
    if fname.endswith("_purge.chaos"):
        return "Purge"
    return "Unsorted"

def main():
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        category = categorize(fname)
        dest_dir = os.path.join(OUTPUT_ROOT, category)
        ensure_dir(dest_dir)
        shutil.copy2(os.path.join(INPUT_DIR, fname), os.path.join(dest_dir, fname))
        print(f"✅ PattyMae sorted {fname} -> {category}/")

if __name__ == "__main__":
    main()
""")


# === filigree.py ===
write(r"C:/EdenOS_Origin/all_daemons/Filigree/filigree.py", """import os
import json

INPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Janvier\\chaos_threads"
OUTPUT_DIR = r"C:\\EdenOS_Origin\\all_daemons\\Rhea\\outputs\\Filigree\\tagged"

VIBE_TAGS = {
    "soft": ["gentle", "kind", "calm", "soothing"],
    "chaotic": ["chaos", "fracture", "storm", "tangle"],
    "hopeful": ["hope", "dream", "light", "eden"],
    "dark": ["void", "fear", "loss", "death"]
}

def tag_text(text):
    tags = []
    text_l = text.lower()
    for tag, words in VIBE_TAGS.items():
        if any(w in text_l for w in words):
            tags.append(tag)
    return tags

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    title = data.get("title", "Untitled")
    date = data.get("date", "unknown_date")
    nodes = data.get("nodes", [])
    tags = set()
    for node in nodes:
        tags.update(tag_text(node.get("content", "")))
    return {"title": title, "date": date, "tags": list(tags)}

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for fname in os.listdir(INPUT_DIR):
        if not fname.endswith(".chaos"): continue
        path = os.path.join(INPUT_DIR, fname)
        result = process_file(path)
        outname = fname.replace(".chaos", "_tags.chaos")
        outpath = os.path.join(OUTPUT_DIR, outname)
        with open(outpath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"✅ Filigree tagged {fname} with {result['tags']}")

if __name__ == "__main__":
    main()
""")

# === serideth.py ===
write(r"C:/EdenOS_Origin/all_daemons/Serideth/serideth.py", """import os, json, re
from pathlib import Path
from datetime import datetime

ADERYN_OUT   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Aderyn/summons")
OLYSSIA_IN   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Olyssia/inbox")
SAPHIRA_IN   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Saphira/inbox")
SERIDETH_OUT = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Serideth")

for p in (OLYSSIA_IN, SAPHIRA_IN, SERIDETH_OUT):
    p.mkdir(parents=True, exist_ok=True)

DISPATCH_LOG = SERIDETH_OUT / "dispatch_log.json"

DCA_HINTS = ["daemon","pipeline","parse","embed","index","memory","daemon core"]
AOE_HINTS = ["agent","voice","story","lore","aesthetic","eden","front of house"]

def guess_bucket(text: str) -> str:
    t = text.lower()
    if any(k in t for k in DCA_HINTS): return "DCA"
    if any(k in t for k in AOE_HINTS): return "AOE"
    if re.search(r"\\bsummon\\b|\\binvoke\\b", t): return "DCA"
    return "AOE"

def guess_name(text: str, prefix: str) -> str:
    m = re.search(r"(agent|name)\\s*[:=]\\s*([A-Za-z0-9_\\-]{3,64})", text, flags=re.I)
    if m: return m.group(2)
    m = re.search(r"\\b([A-Z][a-zA-Z0-9_\\-]{2,32})\\b", text)
    if m: return m.group(1)
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

def main():
    log = {"dispatched": [], "skipped": []}
    if not ADERYN_OUT.exists():
        print("[Serideth] No Aderyn output found.")
        return
    for f in ADERYN_OUT.glob("*.chaos"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except: 
            log["skipped"].append({"file": f.name,"reason":"bad_json"})
            continue
        fragments = []
        if isinstance(data.get("summons"), list):
            fragments = [s.get("text","") for s in data["summons"]]
        elif isinstance(data.get("nodes"), list):
            fragments = [n.get("content","") for n in data["nodes"]]
        for frag in fragments:
            bucket = guess_bucket(frag)
            if bucket == "DCA":
                agent_name = guess_name(frag,"Unnamed_DCA")
                outpath = SAPHIRA_IN / f"{agent_name}.fragment.json"
                outpath.write_text(json.dumps({"fragment":frag,"guess_name":agent_name},indent=2),encoding="utf-8")
                log["dispatched"].append({"to":"Saphira","file":outpath.name})
            else:
                agent_name = guess_name(frag,"Unnamed_AoE")
                outpath = OLYSSIA_IN / f"{agent_name}.fragment.json"
                outpath.write_text(json.dumps({"fragment":frag,"guess_name":agent_name},indent=2),encoding="utf-8")
                log["dispatched"].append({"to":"Olyssia","file":outpath.name})
    (DISPATCH_LOG).write_text(json.dumps(log,indent=2),encoding="utf-8")
    print(f"[Serideth] dispatched {len(log['dispatched'])} fragment(s).")

if __name__ == "__main__":
    main()
""")


# === olyssia.py ===
write(r"C:/EdenOS_Origin/all_daemons/Olyssia/olyssia.py", """import os, json
from pathlib import Path
from datetime import datetime

INBOX_DIR    = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Olyssia/inbox")
AGENTS_DIR   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Olyssia/agents")
TEMPLATE_FILE= Path(r"C:/EdenOS_Origin/all_daemons/Olyssia/AoE_template.agent.json")

AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def load_template():
    if TEMPLATE_FILE.exists():
        try: return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"type":"AoE","name":"","domain":"","role":"","notes":"","status":"draft"}

def seed_from_fragment(frag_json: dict) -> dict:
    t = load_template()
    t["created_at"] = datetime.now().isoformat()
    t["name"] = frag_json.get("guess_name") or "Unnamed_AoE"
    frag = (frag_json.get("fragment") or "").strip()
    t["notes"] = frag
    t["domain"] = "relation / story / resonance"
    t["role"] = "Agent of Eden"
    return t

def main():
    if not INBOX_DIR.exists(): return
    count = 0
    for f in INBOX_DIR.glob("*.fragment.json"):
        try: data = json.loads(f.read_text(encoding="utf-8"))
        except: continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_AoE").replace(" ","_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent,indent=2),encoding="utf-8")
        count += 1
    print(f"[Olyssia] seeded {count} AoE agent(s).")

if __name__ == "__main__":
    main()
""")

# === saphira.py ===
write(r"C:/EdenOS_Origin/all_daemons/Saphira/saphira.py", """import os, json, re
from pathlib import Path
from datetime import datetime

INBOX_DIR    = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Saphira/inbox")
AGENTS_DIR   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Saphira/agents")
TEMPLATE_FILE= Path(r"C:/EdenOS_Origin/all_daemons/Saphira/DCA_template.agent.json")

AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def load_template():
    if TEMPLATE_FILE.exists():
        try: return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"type":"DCA","name":"","intent":"","summon_phrase":"","tags":[],"status":"draft"}

def infer_intent(text: str) -> str:
    t = text.lower()
    if "parse" in t or "ingest" in t: return "ingest/parse"
    if "index" in t or "embed" in t: return "index/embed"
    if "watch" in t or "daemon" in t: return "watch/daemonize"
    return "general_utility"

def extract_tags(text: str):
    base = ["daemon","pipeline","memory","index","embed","parse","ingest","summon"]
    t = text.lower()
    return sorted({k for k in base if k in t})

def extract_summon_phrase(text: str) -> str:
    for pat in (r".*\\bsummon\\b.*", r".*\\binvoke\\b.*", r".*\\bcall forth\\b.*"):
        m = re.search(pat, text, flags=re.I)
        if m: return m.group(0).strip()
    for line in text.splitlines():
        if line.strip(): return line.strip()[:160]
    return ""

def seed_from_fragment(frag_json: dict) -> dict:
    t = load_template()
    t["created_at"] = datetime.now().isoformat()
    t["name"] = frag_json.get("guess_name") or "Unnamed_DCA"
    frag = (frag_json.get("fragment") or "").strip()
    t["summon_phrase"] = extract_summon_phrase(frag)
    t["intent"] = infer_intent(frag)
    t["tags"] = extract_tags(frag)
    return t

def main():
    if not INBOX_DIR.exists(): return
    count = 0
    for f in INBOX_DIR.glob("*.fragment.json"):
        try: data = json.loads(f.read_text(encoding="utf-8"))
        except: continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_DCA").replace(" ","_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent,indent=2),encoding="utf-8")
        count += 1
    print(f"[Saphira] seeded {count} DCA agent(s).")

if __name__ == "__main__":
    main()
""")

print("\n🌱 All optimized daemons restored.")
# === pipeline README.md ===
readme_content = """# EdenOS :: Daemon Pipeline (Optimized Build)

This README was auto-generated when the daemons were restored.

## 📂 Daemon Flow

1. **Sheele** → Splits raw conversations → `Rhea/outputs/Sheele/split_conversations`
2. **Briar** → Converts JSON to clean .txt conversations → `Rhea/outputs/Briar/split_conversations_txt`
3. **Janvier** → Converts .txt into .chaos threads → `Rhea/outputs/Janvier/chaos_threads`
4. **Codexa** → Extracts code blocks → `Rhea/outputs/Codexa/codeblocks`
5. **Aderyn** → Detects summon phrases → `Rhea/outputs/Aderyn/summons`
6. **Label** → Tags conversations with keywords → `Rhea/outputs/Label/labeled`
7. **Parsley** → Classifies chaos threads (sacred / purge / review) → `Rhea/outputs/Parsley/classified`
8. **PattyMae** → Organizes chaos threads by category → `Rhea/PattyMae/organized`
9. **Filigree** → Tags conversations with vibes (soft/chaotic/hopeful/dark) → `Rhea/outputs/Filigree/tagged`
10. **Serideth** → Dispatches fragments from Aderyn into:
    - `Rhea/outputs/Olyssia/inbox` (AoE fragments)
    - `Rhea/outputs/Saphira/inbox` (DCA fragments)
11. **Olyssia** (AoE) → Seeds *Agents of Eden* from AoE inbox using AoE templates → `Rhea/outputs/Olyssia/agents`
12. **Saphira** (DCA) → Seeds *Daemon Core Agents* from DCA inbox using DCA templates → `Rhea/outputs/Saphira/agents`

---

## 🧬 AoE vs DCA

- **Agents of Eden (AoE)**: front-of-house, relational, story-bearing. Seeded by Olyssia.  
- **Daemon Core Agents (DCA)**: back-of-house, structural, logistics. Seeded by Saphira.  
- **Serideth** ensures summons are routed to the right side.

---

🌱 Generated automatically by `optimized_daemons.complete_build.py`.
"""

readme_path = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/README.md")
readme_path.parent.mkdir(parents=True, exist_ok=True)
readme_content = readme_content.replace('optimized_daemons.complete_build.py', 'De_File.complete_build.py')
readme_path.write_text(readme_content.strip(), encoding="utf-8")
print(f"📘 Pipeline README generated at {readme_path}")
