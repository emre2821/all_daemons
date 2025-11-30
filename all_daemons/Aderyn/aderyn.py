import os
import re
import json
from datetime import datetime

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Aderyn\summons"

SUMMON_PATTERNS = [
    r"\bsummon\b", r"\binvoke\b", r"\bcall forth\b", r"\bconjure\b",
    r"\bbring to life\b", r"\bi am become\b"
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