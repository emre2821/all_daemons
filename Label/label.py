import os
import json

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Label\labeled"

WORD_BANK_FILE = r"C:\EdenOS_Origin\all_daemons\Label\LabelWordBank.chaos"

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