import os
import json

WORK_ROOT = os.environ.get("EDEN_WORK_ROOT", os.environ.get("EDEN_ROOT", os.getcwd()))
INPUT_DIR = os.path.join(WORK_ROOT, "daemons", "Rhea", "outputs", "Janvier", "chaos_threads")
OUTPUT_DIR = os.path.join(WORK_ROOT, "daemons", "Rhea", "outputs", "Filigree", "tagged")

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
