#!/usr/bin/env python3
# Aderyn — Summons Archivist
# Purpose: Scan Janvier's CHAOS files for "summon" events and shelve them in chaos_library.
# Path convention enforced:
#   INPUT = ../Rhea/outputs/from_Janvier/
#   OUTPUT = ../Rhea/outputs/from_Aderyn/chaos_library/

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

def clean_filename(s: str, max_length: int = 50) -> str:
    # Remove or replace invalid characters
    cleaned = re.sub(r'[<>:"/\\|?*]', '_', s)
    # Replace multiple underscores with single
    cleaned = re.sub(r'_+', '_', cleaned)
    # Strip leading/trailing underscores
    cleaned = cleaned.strip('_')
    # Limit length but keep meaningful part
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length].rstrip('_')
    return cleaned if cleaned else 'untitled'

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for fname in sorted(os.listdir(INPUT_DIR)):
        if not fname.lower().endswith(".chaos"):
            continue
        path = INPUT_DIR / fname
        result = process_chaos_file(path)
        if not result or not result["summons"]:
            continue

        # Better filename construction
        base_name = fname.rsplit('.', 1)[0]
        safe_base = clean_filename(base_name)
        title_part = clean_filename(result.get("title", "untitled"), 20)

        # Include date and timestamp for uniqueness
        outname = f"{result['date']}_{timestamp}_{safe_base}_{title_part}_summons.chaos"
        outpath = OUTPUT_DIR / outname

        # Ensure unique filename
        counter = 1
        while outpath.exists():
            name_parts = outname.rsplit('_', 1)
            if len(name_parts) > 1 and name_parts[1].startswith('summons'):
                outname = f"{result['date']}_{timestamp}_{safe_base}_{title_part}_{counter}_summons.chaos"
            else:
                outname = f"{result['date']}_{timestamp}_{safe_base}_{title_part}_{counter}.chaos"
            outpath = OUTPUT_DIR / outname
            counter += 1

        with open(outpath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

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
