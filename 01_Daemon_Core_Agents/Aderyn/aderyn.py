#!/usr/bin/env python3
# Aderyn — Summons Archivist
# Purpose: Scan Janvier’s CHAOS files for “summon” events and shelve them in chaos_library.
# Path convention enforced:
#   INPUT  = ..\Rhea\outputs\from_Janvier\
#   OUTPUT = ..\Rhea\outputs\from_Aderyn\chaos_library\

import os
import re
import json
from datetime import datetime
from pathlib import Path

# =============================
# Unified Paths
# =============================
ROOT = Path(__file__).resolve().parent.parent.parent
INPUT_DIR = ROOT / "Rhea" / "outputs" / "from_Janvier"
OUTPUT_DIR = ROOT / "Rhea" / "outputs" / "from_Aderyn" / "chaos_library"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# =============================
# Patterns
# =============================
SUMMON_PATTERNS = [
    r"\bsummon\b",
    r"\binvoke\b",
    r"\bcall forth\b",
    r"\bconjure\b",
    r"\bbring to life\b",
    r"\bi am become\b",
]

def detect_summons(text: str) -> bool:
    text_l = text.lower()
    return any(re.search(p, text_l) for p in SUMMON_PATTERNS)

def clean_filename(s: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in s)

# =============================
# Core Logic
# =============================
def process_chaos_file(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Aderyn] ⚠️ Skipped {path.name} (invalid JSON): {e}")
        return {}

    title = data.get("title", "Untitled")
    date = data.get("date", datetime.now().strftime("%Y-%m-%d"))
    nodes = data.get("nodes", [])
    summons = []

    for node in nodes:
        txt = node.get("content", "")
        if detect_summons(txt):
            summons.append({
                "role": node.get("role"),
                "text": txt,
                "timestamp": node.get("timestamp"),
            })

    return {"title": title, "date": date, "summons": summons}

def archive_summons():
    results = []
    for fname in os.listdir(INPUT_DIR):
        if not fname.lower().endswith(".chaos"):
            continue
        path = INPUT_DIR / fname
        result = process_chaos_file(path)
        if not result or not result["summons"]:
            continue

        base = clean_filename(fname.rsplit('.', 1)[0])
        outname = f"{base}_summons.chaos"
        outpath = OUTPUT_DIR / outname

        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        print(f"[Aderyn] ✅ Detected summons in {fname} → {outname}")
        results.append(str(outpath))
    return results

# =============================
# Entrypoints
# =============================
def main():
    if not INPUT_DIR.exists():
        print(f"[Aderyn] {INPUT_DIR} missing; nothing to archive.")
        return
    results = archive_summons()
    if not results:
        print("[Aderyn] No summons found.")

def run(payload=None, registry=None, **kwargs):
    """Rhea-facing entrypoint."""
    results = archive_summons()
    return {"output_dir": str(OUTPUT_DIR), "results": results}

# =============================
# CLI
# =============================
if __name__ == "__main__":
    main()
