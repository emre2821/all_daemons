import os
import re
from datetime import datetime

INPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Briar\split_conversations_txt"
OUTPUT_DIR = r"C:\EdenOS_Origin\all_daemons\Rhea\outputs\Janvier\chaos_threads"

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