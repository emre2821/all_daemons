import os
import re
import hashlib
import json

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Codexa\codeblocks"
NEWLINE = "\n"

def clean_filename(s):
    return ''.join(c if c.isalnum() else '_' for c in s)

def extract_code_blocks(text):
    pattern = r"```(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    blocks = []
    for m in matches:
        parts = m.split(NEWLINE, 1)
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
