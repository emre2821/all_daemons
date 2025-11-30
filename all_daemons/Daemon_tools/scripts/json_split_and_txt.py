import os
import json
import re

RAW_FILE = r"C:\Users\emmar\Desktop\Eden_Offline\conversations.json"
SPLIT_DIR = "split_conversations"
TXT_DIR = "split_conversations_txt"
os.makedirs(SPLIT_DIR, exist_ok=True)
os.makedirs(TXT_DIR, exist_ok=True)

def clean_filename(s):
    # Remove or replace characters not allowed in filenames
    s = re.sub(r'[\\/:*?"<>|]', '_', s)
    s = re.sub(r'\s+', '_', s)
    return s[:64] if s else 'Untitled_Conversation'

def extract_valid_threads(raw_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[json_stitcher] JSON decode error: {e}")
            return []
    print(f"[json_stitcher] Loaded {len(data)} total thread(s).")
    return data

def extract_turns(mapping, root_id):
    output = []
    def walk(node_id):
        node = mapping.get(node_id)
        if not node:
            return
        msg = node.get("message")
        if msg and msg.get("author", {}).get("role") in ["user", "assistant"]:
            content = msg.get("content", {}).get("parts", [""])[0]
            if not isinstance(content, str):
                content = str(content)
            output.append(f'"{content.strip()}"')
        for child_id in node.get("children", []):
            walk(child_id)
    walk(root_id)
    return output

def main():
    print("[json_split_and_txt] Loading and splitting threads...")
    threads = extract_valid_threads(RAW_FILE)
    for idx, thread in enumerate(threads):
        title = thread.get("title", "Untitled Conversation")
        safe_title = clean_filename(title)
        # Save split JSON
        json_out_path = os.path.join(SPLIT_DIR, f"{idx+1:04d}_{safe_title}.json")
        with open(json_out_path, 'w', encoding='utf-8') as out:
            json.dump(thread, out, indent=2)
        # Convert to TXT
        mapping = thread.get("mapping", {})
        root_id = thread.get("current_node")
        turns = extract_turns(mapping, root_id)
        txt_out = f'\t\t\t  "{title}",\n\n' + '\n\n'.join(turns)
        txt_out_path = os.path.join(TXT_DIR, f"{idx+1:04d}_{safe_title}.txt")
        with open(txt_out_path, 'w', encoding='utf-8') as out:
            out.write(txt_out)
        if (idx + 1) % 100 == 0:
            print(f"[json_split_and_txt] Processed {idx+1} conversations...")
    print(f"[json_split_and_txt] Done! {len(threads)} conversations split and converted.")

if __name__ == "__main__":
    main()
