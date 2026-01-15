# C:\EdenOS_Origin\daemons\Tempest\tempest.py
import os, json, re, time, traceback
from pathlib import Path

# ── Eden layout ───────────────────────────────────────────────────────────────
EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
WORK_ROOT = Path(os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT))
RHEA_BASE = WORK_ROOT / "daemons" / "Rhea"

INPUT_DIR   = RHEA_BASE / "janvier_cleaned"
OUTBOX_DIR  = RHEA_BASE / "_outbox" / "tempest"
LOGS_DIR    = RHEA_BASE / "_logs"

for d in (INPUT_DIR, OUTBOX_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = OUTBOX_DIR / "tempest_scores.json"
LOG_FILE    = LOGS_DIR / "tempest_daemon.log"

def log_line(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [Tempest] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# ── Drama signals (kept from your draft) ─────────────────────────────────────
DRAMA_TERMS = [
    r"\b(why|please|don\'t|can\'t|never|always|enough|sorry|hate|leave|stay)\b",
    r"\b(I need|I want|I can\'t|You never|You always|You said|You promised)\b",
    r"!{2,}",
    r"\.{3,}"  # trailing ellipses
]
compiled_patterns = [re.compile(pat, re.IGNORECASE) for pat in DRAMA_TERMS]

def score_thread(filepath: Path) -> int:
    try:
        lines = filepath.read_text(encoding="utf-8", errors="ignore").splitlines()
    except Exception as e:
        log_line(f"WARN: cannot read {filepath.name}: {e}")
        return 0
    score = 0
    for line in lines:
        score += sum(bool(p.search(line)) for p in compiled_patterns)
    return score

def main():
    log_line("Measuring chaos density...")
    chaos_files = sorted([p for p in INPUT_DIR.glob("*.chaos") if p.is_file()])
    if not chaos_files:
        log_line("No CHAOS files yet in janvier_cleaned; nothing to score.")
    tempest_log = {}
    for fp in chaos_files:
        s = score_thread(fp)
        if s > 0:
            tempest_log[fp.name] = s
            log_line(f"{fp.name} scored {s} tension points.")
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(dict(sorted(tempest_log.items(), key=lambda kv: kv[1], reverse=True)), f, indent=2, ensure_ascii=False)
        log_line(f"Scores saved to {OUTPUT_FILE}")
    except Exception as e:
        log_line(f"ERROR: cannot write scores: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
