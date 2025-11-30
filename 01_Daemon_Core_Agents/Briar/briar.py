#!/usr/bin/env python3
"""
Briar Daemon
Role: Converts Sheele's .json conversation fragments into plain .txt transcripts.
Input:  C:\EdenOS_Origin\01_Daemon_Core_Agents\Rhea\_outputs\Sheele_files\*.json
Output: C:\EdenOS_Origin\01_Daemon_Core_Agents\Rhea\_outputs\Briar_files\*.txt
"""

import os, json
from pathlib import Path

# === CONFIG ===
ROOT_DIR = Path(r"C:\EdenOS_Origin\01_Daemon_Core_Agents")
INPUT_DIR = ROOT_DIR / r"Rhea\_outputs\Sheele_files"
OUTPUT_DIR = ROOT_DIR / r"Rhea\_outputs\Briar_files"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ==============

def extract_messages(convo):
    """
    Normalize a conversation JSON fragment into a list of (speaker, text).
    Supports multiple schema shapes.
    """
    messages = []

    # Case 1: OpenAI-like {"role":"user","content":"..."}
    if isinstance(convo, list):
        for msg in convo:
            if isinstance(msg, dict):
                role = msg.get("role") or msg.get("speaker") or "Unknown"
                content = msg.get("content") or msg.get("text") or str(msg)
                messages.append((role, content))
    # Case 2: Dict with "messages"
    elif isinstance(convo, dict) and "messages" in convo:
        for msg in convo["messages"]:
            role = msg.get("role") or msg.get("speaker") or "Unknown"
            content = msg.get("content") or msg.get("text") or str(msg)
            messages.append((role, content))
    else:
        # Fallback: dump whole thing
        messages.append(("Unknown", str(convo)))

    return messages

def convert_to_txt(json_file: Path, out_file: Path):
    """Convert one JSON fragment to a plain .txt transcript."""
    with open(json_file, "r", encoding="utf-8") as f:
        convo = json.load(f)

    messages = extract_messages(convo)

    with open(out_file, "w", encoding="utf-8") as f:
        for role, content in messages:
            f.write(f"{role}: {content}\n")

    print(f"[Briar] Converted {json_file.name} -> {out_file.name}")


def run():
    if not INPUT_DIR.exists():
        raise FileNotFoundError(f"[Briar] Cannot find input folder {INPUT_DIR}")
    files = list(INPUT_DIR.glob("*.json"))
    if not files:
        print(f"[Briar] No input files in {INPUT_DIR}")
        return

    for json_file in files:
        out_file = OUTPUT_DIR / f"{json_file.stem}.txt"
        convert_to_txt(json_file, out_file)

if __name__ == "__main__":
    run()
