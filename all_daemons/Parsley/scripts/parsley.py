import os
import json

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Parsley\classified"

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