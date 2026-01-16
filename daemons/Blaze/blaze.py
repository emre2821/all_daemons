# blaze.py
# Agent Blaze — System Integrity & Digital Cleanup Specialist
# Motto: "I don’t delete files—I liberate space."

import argparse
import datetime as _dt
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path

DEFAULT_SKIP_DIRNAMES = {
    ".git", ".hg", ".svn", ".venv", "venv", "env", "node_modules",
    "_vault", "_secrets", "_secure", "_backups"
}
DEFAULT_EDEN_SACRED = {"Archive", "Sacred", "EdenOS_Core"}

TARGET_DIRNAMES = {
    "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache",
    ".ipynb_checkpoints", "build", "dist"
}
TARGET_FILE_GLOBS = {
    "*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db"
}
TARGET_SUFFIXES = {".egg-info"}

# ------------------------
# Utilities
# ------------------------
def guess_root() -> Path:

    candidates = [Path(os.environ.get("EDEN_ROOT", os.getcwd())), Path(os.getcwd())]
    for c in candidates:
        if c.exists():
            return c.resolve()
    return Path(os.getcwd()).resolve()

def timestamp() -> str:

    return _dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def ensure_log_dir(root: Path, sub="cleanup") -> Path:

    log_dir = root / "_logs" / "Blaze" / sub
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir

def should_skip_dir(path: Path, skip_names: set[str]) -> bool:

    if path.name in skip_names:
        return True
    for part in path.parts:
        if part in DEFAULT_EDEN_SACRED:
            return True
    return False

def path_depth(root: Path, path: Path) -> int:

    try:
        return len(path.relative_to(root).parts)
    except ValueError:
        return len(path.parts)

# ------------------------
# Sweep (cache cleanup)
# ------------------------
def iter_targets(root: Path, skip_names: set[str]):

    for dirpath, dirnames, filenames in os.walk(root):
        dpath = Path(dirpath)
        # prune traversal
        for dn in list(dirnames):
            candidate = dpath / dn
            if should_skip_dir(candidate, skip_names):
                dirnames.remove(dn)
        for dn in list(dirnames):
            if dn in TARGET_DIRNAMES or dn.endswith(".egg-info"):
                yield ("dir", dpath / dn)
        for fn in filenames:
            p = dpath / fn
            if fn in (".DS_Store", "Thumbs.db"):
                yield ("file", p)
                continue
            for pat in TARGET_FILE_GLOBS:
                if pat.startswith("*") and p.name.endswith(pat.removeprefix("*")):
                    yield ("file", p)
            for sfx in TARGET_SUFFIXES:
                if p.name.endswith(sfx):
                    yield ("file", p)

def blaze_sweep(root: Path, confirm: bool, skip: set[str], quiet: bool):

    log_dir = ensure_log_dir(root, "cleanup")
    run_id = timestamp()
    summary_path = log_dir / f"sweep_{run_id}.summary.txt"

    found = list(iter_targets(root, skip))
    def key(p):
        return path_depth(root, p)

    dirs = sorted({p for k, p in found if k == "dir"}, key=key, reverse=True)
    files = sorted({p for k, p in found if k == "file"})

    deleted_files, deleted_dirs = 0, 0
    if confirm:
        for p in files:
            try:
                if p.exists():
                    p.unlink()
                    deleted_files += 1
                    if not quiet: print(f"[Blaze] removed file: {p}")
            except Exception as e:
                if not quiet: print(f"[Blaze] error removing {p}: {e}")
        for d in dirs:
            try:
                if d.exists():
                    shutil.rmtree(d)
                    deleted_dirs += 1
                    if not quiet: print(f"[Blaze] removed dir: {d}")
            except Exception as e:
                if not quiet: print(f"[Blaze] error removing {d}: {e}")
    else:
        if not quiet:
            print(f"[Blaze] DRY-RUN: {len(files)} files, {len(dirs)} dirs would be removed.")

    with open(summary_path, "w") as s:
        s.write(f"Blaze Sweep — {run_id}\n")
        s.write(f"Deleted: files={deleted_files}, dirs={deleted_dirs}\n")
    if not quiet:
        print(f"[Blaze] Sweep summary logged: {summary_path}")

# ------------------------
# Deduplicate
# ------------------------
def hash_file(path: Path, chunk_size=65536):

    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def blaze_dedupe(root: Path, quiet: bool):

    log_dir = ensure_log_dir(root, "dedupe")
    run_id = timestamp()
    report = log_dir / f"dedupe_{run_id}.jsonl"

    seen = {}
    dupes = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            try:
                h = hash_file(p)
                if h in seen:
                    dupes.append((str(p), seen[h]))
                else:
                    seen[h] = str(p)
            except Exception as e:
                if not quiet: print(f"[Blaze] error hashing {p}: {e}")

    with open(report, "w") as f:
        for a, b in dupes:
            f.write(json.dumps({"dupe": a, "original": b}) + "\n")

    if not quiet:
        print(f"[Blaze] Found {len(dupes)} duplicates. Report: {report}")

# ------------------------
# Classify
# ------------------------
def classify_file(path: Path) -> str:

    name = path.name
    if name.endswith((".py", ".chaos", ".json", ".md")):
        return "core"
    if name.endswith((".log", ".tmp", ".bak")):
        return "temp"
    if name.endswith((".png", ".jpg", ".mp4", ".wav")):
        return "check"
    return "check"

def blaze_classify(root: Path, quiet: bool):

    log_dir = ensure_log_dir(root, "classify")
    run_id = timestamp()
    report = log_dir / f"classify_{run_id}.jsonl"

    with open(report, "w") as f:
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                p = Path(dirpath) / fn
                label = classify_file(p)
                f.write(json.dumps({"path": str(p), "class": label}) + "\n")

    if not quiet:
        print(f"[Blaze] Classification complete. Report: {report}")

# ------------------------
# Watchdog
# ------------------------
def blaze_watch(root: Path, interval: int, quiet: bool):

    print(f"[Blaze] Watchdog active — scanning every {interval}s")
    while True:
        try:
            blaze_sweep(root, confirm=False, skip=set(), quiet=True)
            time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[Blaze] Watchdog stopped.")
            break

# ------------------------
# Main CLI
# ------------------------
def main():

    parser = argparse.ArgumentParser(description="Blaze — Eden cleanup agent")
    parser.add_argument("--root", type=str, default=None,
                        help="Project root (default: C:\\EdenOS_Origin or cwd)")
    subparsers = parser.add_subparsers(dest="command")

    # sweep
    sp = subparsers.add_parser("sweep")
    sp.add_argument("--confirm", action="store_true")
    sp.add_argument("--quiet", action="store_true")

    # dedupe
    sp = subparsers.add_parser("dedupe")
    sp.add_argument("--quiet", action="store_true")

    # classify
    sp = subparsers.add_parser("classify")
    sp.add_argument("--quiet", action="store_true")

    # watch
    sp = subparsers.add_parser("watch")
    sp.add_argument("--interval", type=int, default=60)
    sp.add_argument("--quiet", action="store_true")

    args = parser.parse_args()
    root = Path(args.root).resolve() if args.root else guess_root()

    print("🔥 Blaze initialized — System Integrity & Digital Cleanup Specialist")
    print("   Motto: 'I don’t delete files—I liberate space.'\n")

    if args.command == "sweep":
        blaze_sweep(root, args.confirm, set(DEFAULT_SKIP_DIRNAMES), args.quiet)
    elif args.command == "dedupe":
        blaze_dedupe(root, args.quiet)
    elif args.command == "classify":
        blaze_classify(root, args.quiet)
    elif args.command == "watch":
        blaze_watch(root, args.interval, args.quiet)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
