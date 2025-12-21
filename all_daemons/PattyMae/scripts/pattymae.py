import os
import shutil

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"
OUTPUT_ROOT = r"C:\EdenOS_Origin\all_daemons\Rhea\PattyMae\organized"

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