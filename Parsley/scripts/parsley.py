# Eden-aware Parsley
import os
import argparse
from pathlib import Path
import time

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin"))
RHEA_BASE = EDEN_ROOT / "all_daemons" / "Rhea"

try:
    import sys
    sys.path.append(str((EDEN_ROOT / "all_daemons" / "Daemon_tools" / "scripts").resolve()))
    from eden_paths import daemon_out_dir  # type: ignore
    OUT_DIR = Path(daemon_out_dir("Parsley"))
except Exception:
    OUT_DIR = RHEA_BASE / "_outbox" / "Parsley"

WORK_DIR   = RHEA_BASE / "_work"
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

def main(argv=None):
    ap = argparse.ArgumentParser(description="Parsley - File classifier")
    ap.add_argument("--input", help="Path to input list file (one path per line)")
    ap.add_argument("--dry-run", action="store_true", help="Plan only; do not write outputs")
    ap.add_argument("--confirm", action="store_true", help="Write output lists to OUT_DIR")
    args = ap.parse_args(argv)

    input_file = Path(args.input) if args.input else INPUT_FILE
    if not input_file.exists():
        log(f"Missing {input_file}; nothing to do.")
        return 0

    keep, purge, review = [], [], []
    for line in input_file.read_text(encoding="utf-8", errors="ignore").splitlines():
        path = line.strip()
        if not path: continue
        bucket = classify_file(path)
        if bucket == "keep":   keep.append(path)
        elif bucket == "purge": purge.append(path)
        else:                  review.append(path)

    if args.confirm and not args.dry_run:
        KEEP_FILE.write_text("\n".join(keep), encoding="utf-8")
        PURGE_FILE.write_text("\n".join(purge), encoding="utf-8")
        REVIEW_FILE.write_text("\n".join(review), encoding="utf-8")
        log(f"Classification written. keep={len(keep)} purge={len(purge)} review={len(review)}")
    else:
        log(f"[DRY RUN] keep={len(keep)} purge={len(purge)} review={len(review)} (no files written)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

def describe() -> dict:
    return {
        "name": "Parsley",
        "role": "File classifier (keep/purge/review)",
        "inputs": {"input": str(INPUT_FILE)},
        "outputs": {"out_dir": str(OUT_DIR)},
        "flags": ["--input", "--dry-run", "--confirm"],
        "safety_level": "normal",
    }


def healthcheck() -> dict:
    status = "ok"; notes = []
    for d in (WORK_DIR, OUT_DIR, LOGS_DIR):
        try:
            d.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            status = "fail"; notes.append(f"cannot create {d}: {e}")
    try:
        (LOGS_DIR / "parsley_daemon.log").touch()
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"log write warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
