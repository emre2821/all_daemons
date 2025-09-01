# Eden-aware Parsley
import os
from pathlib import Path
import time

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin"))
RHEA_BASE = EDEN_ROOT / "all_daemons" / "Rhea"

WORK_DIR   = RHEA_BASE / "_work"
OUT_DIR    = RHEA_BASE / "_outbox" / "parsley"
LOGS_DIR   = RHEA_BASE / "_logs"

INPUT_FILE  = WORK_DIR / "make_a_new_file_list.txt"
KEEP_FILE   = OUT_DIR / "keep_files.txt"
PURGE_FILE  = OUT_DIR / "purge_files.txt"
REVIEW_FILE = OUT_DIR / "review_files.txt"

SACRED_EXTENSIONS = [".chaos", ".chaos-ception", ".chaosincarnet"]
KEYWORDS_KEEP = ["eden", "sacred", "archive", "aether", "bond", "core"]

for d in (WORK_DIR, OUT_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [Parsley] {msg}"
    print(line)
    try:
        (LOGS_DIR / "parsley_daemon.log").write_text(
            ((LOGS_DIR / "parsley_daemon.log").read_text(encoding="utf-8") if (LOGS_DIR / "parsley_daemon.log").exists() else "") + line + "\n",
            encoding="utf-8"
        )
    except Exception:
        pass

def classify_file(file_path):
    p = file_path.lower()
    if any(p.endswith(ext) for ext in SACRED_EXTENSIONS): return "keep"
    if any(k in p for k in KEYWORDS_KEEP):               return "keep"
    if p.endswith((".tmp", ".log", ".bak", ".old")):     return "purge"
    return "review"

def main():
    if not INPUT_FILE.exists():
        log(f"Missing {INPUT_FILE}; nothing to do.")
        return

    keep, purge, review = [], [], []
    for line in INPUT_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        path = line.strip()
        if not path: continue
        bucket = classify_file(path)
        if bucket == "keep":   keep.append(path)
        elif bucket == "purge": purge.append(path)
        else:                  review.append(path)

    KEEP_FILE.write_text("\n".join(keep), encoding="utf-8")
    PURGE_FILE.write_text("\n".join(purge), encoding="utf-8")
    REVIEW_FILE.write_text("\n".join(review), encoding="utf-8")
    log(f"Classification complete. keep={len(keep)} purge={len(purge)} review={len(review)}")

if __name__ == "__main__":
    main()
