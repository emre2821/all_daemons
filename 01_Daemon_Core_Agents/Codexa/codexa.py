#!/usr/bin/env python3
"""
Codexa Daemon
Role: Extracts code blocks from conversation fragments and saves them into
      properly named .chaos files by language type.
Inputs:
  - Sheele JSON fragments
  - Briar TXT transcripts
  - Janvier CHAOS JSON
Output:
  "C:\\EdenOS_Origin\\01_Daemon_Core_Agents\\Rhea\\_outputs\\Codexa_files\\*.chaos.code"
"""

import os, re, json
from pathlib import Path

# === CONFIG ===
ROOT_DIR = Path(r"C:\EdenOS_Origin\01_Daemon_Core_Agents")
INPUT_SHEELE = ROOT_DIR / r"Rhea\_outputs\Sheele_files"
INPUT_BRIAR  = ROOT_DIR / r"Rhea\_outputs\Briar_files"
INPUT_JANVIER = ROOT_DIR / r"Rhea\_outputs\Janvier_files"
OUTPUT_DIR = ROOT_DIR / r"Rhea\_outputs\Codexa_files"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
# ==============

CODEBLOCK_PATTERN = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

def extract_from_text(text: str):
    """Extract code blocks from text, return list of (lang, code)."""
    results = []
    for match in CODEBLOCK_PATTERN.finditer(text):
        lang = match.group(1) or "plaintext"
        code = match.group(2).strip()
        results.append((lang, code))
    return results

def process_json_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    text = json.dumps(data, ensure_ascii=False)
    return extract_from_text(text)

def process_txt_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return extract_from_text(text)

def save_blocks(blocks, source_file: Path, prefix: str):
    base = source_file.stem
    for idx, (lang, code) in enumerate(blocks, start=1):
        out_name = f"{prefix}_{base}_{idx:03d}.{lang}.chaos.code"
        out_path = OUTPUT_DIR / out_name
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"[Codexa] Saved {out_name}")

def run():
    # Sheele JSON
    for file in INPUT_SHEELE.glob("*.json"):
        blocks = process_json_file(file)
        if blocks: save_blocks(Sblocks, file, "sheele")

    # Briar TXT
    for file in INPUT_BRIAR.glob("*.txt"):
        blocks = process_txt_file(file)
        if blocks: save_blocks(blocks, file, "briar")

    # Janvier CHAOS
    for file in INPUT_JANVIER.glob("*.chaos*"):
        blocks = process_txt_file(file)   # treat as raw text, not JSON
        if blocks: save_blocks(blocks, file, "janvier")

if __name__ == "__main__":
    run()
