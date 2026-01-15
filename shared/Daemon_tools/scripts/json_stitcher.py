import json
import os

try:
    from .eden_paths import eden_work_root
except Exception:
    from eden_paths import eden_work_root  # type: ignore

RAW_FILE = os.environ.get("EDEN_JSON_STITCHER_INPUT", "conversations.json")
OUTPUT_DIR = eden_work_root() / "daemons" / "_daemon_specialty_folders" / "split_conversations"


def extract_valid_threads(raw_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[json_stitcher] JSON decode error: {e}")
            return []
    print(f"[json_stitcher] Loaded {len(data)} total thread(s).")
    return data


def main():
    print("[json_stitcher] Loading and splitting threads...")
    threads = extract_valid_threads(RAW_FILE)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for idx, thread in enumerate(threads):
        out_path = OUTPUT_DIR / f"conversation_{idx+1}.json"
        with open(out_path, "w", encoding="utf-8") as out:
            json.dump(thread, out, indent=2)
        if (idx + 1) % 100 == 0:
            print(f"[json_stitcher] Saved {idx+1} conversations...")
    print(f"[json_stitcher] Done! {len(threads)} conversations saved to '{OUTPUT_DIR}' folder.")


if __name__ == "__main__":
    main()
