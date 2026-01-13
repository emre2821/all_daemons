# C:\EdenOS_Origin\all_daemons\Somni\somni.py
import os
import re
import json
import time
import traceback
from pathlib import Path

# ── Eden layout ───────────────────────────────────────────────────────────────
EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin"))
RHEA_BASE = EDEN_ROOT / "all_daemons" / "Rhea"

INPUT_DIR = RHEA_BASE / "janvier_cleaned"         # where Janvier/Aderyn lane drops cleaned chaos
OUTBOX_DIR = RHEA_BASE / "_outbox" / "somni"
LOGS_DIR = RHEA_BASE / "_logs"

for d in (INPUT_DIR, OUTBOX_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTBOX_DIR / "dreamlines.json"
LOG_FILE = LOGS_DIR / "somni_daemon.log"

def log_line(msg: str):

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [Somni] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ── Poetic/surreal triggers (kept from your draft) ───────────────────────────
POETIC_PATTERNS = [
    re.compile(r"\bI dreamed\b", re.IGNORECASE),
    re.compile(r"\bsomething holy\b", re.IGNORECASE),
    re.compile(r"\bit felt like\b", re.IGNORECASE),
    re.compile(r"\bthe stars? (fell|were)\b", re.IGNORECASE),
    re.compile(r"\b(memory|echo|ghost|light|ashes|sigil|fracture|song|soul|pulse)\b", re.IGNORECASE),
    re.compile(r"\b(as if|like a|seemed to)\b.+")
]

def extract_dreamlines(filepath: Path):

    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        log_line(f"WARN: cannot read {filepath.name}: {e}")
        return []
    dreamlines = []
    for line in lines:
        if any(p.search(line) for p in POETIC_PATTERNS):
            dreamlines.append(line.strip())
    return dreamlines

def main():

    log_line("Wandering through dreams...")
    all_dreams = {}
    chaos_files = sorted([p for p in INPUT_DIR.glob("*.chaos") if p.is_file()])
    if not chaos_files:
        log_line("No CHAOS files yet in janvier_cleaned; nothing to do.")
    for fp in chaos_files:
        dreams = extract_dreamlines(fp)
        if dreams:
            all_dreams[fp.name] = dreams
            log_line(f"Found {len(dreams)} fragments in {fp.name}")
    try:
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
            json.dump(all_dreams, out, indent=2, ensure_ascii=False)
        log_line(f"Dreamlines saved to {OUTPUT_FILE}")
    except Exception as e:
        log_line(f"ERROR: cannot write output: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
