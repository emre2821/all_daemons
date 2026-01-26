# tidbit.sn — Live duplicate bouncer (Python, “snek” edition 🐍)
# Requires: pip install watchdog
# Purpose: Watch folders, hash new/changed files, and move duplicates to a dump folder.
#          Keeps a SQLite index so it survives restarts and doesn’t rehash forever.

import os
import sys
import time
import hashlib
import sqlite3
import shutil
import logging
import threading
import signal
from pathlib import Path
from queue import Queue, Empty

# ========= USER SETTINGS =========
WATCH_FOLDERS = [
    r"C:\Path\To\Folder1",
    r"C:\Path\To\Folder2",
]
DUMP_FOLDER = r"C:\Path\To\waste_of_my_goddamned_time_and_space"
LOG_FILE = r"C:\Path\To\dedupe_watchdog.log"

# File types to ignore (extensions lowercased, incl. the dot)
IGNORE_EXTS = {".tmp", ".part", ".crdownload", ".bak", ".lnk"}

# Directory names to ignore anywhere in the path (case-insensitive)
IGNORE_DIR_NAMES = {".git", "__pycache__", "node_modules"}

# Max file size to consider (in bytes). None = no limit.
MAX_SIZE_BYTES = None  # e.g. 50 * 1024 * 1024 for 50MB

# Debounce time: wait this long after a file event before processing (ms)
DEBOUNCE_MS = 1500

# DRY RUN: if True, do not move files—just log what would happen
DRY_RUN = False

# (Optional) per-folder policy: "move" | "report" | "ignore"
FOLDER_POLICY = {
    # r"C:\Path\Sensitive": "report",
    # r"C:\Path\NeverTouch": "ignore",
}
# =================================

# Ensure paths exist
for p in WATCH_FOLDERS:
    Path(p).mkdir(parents=True, exist_ok=True)
Path(DUMP_FOLDER).mkdir(parents=True, exist_ok=True)
Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("tidbit")

# SQLite index (hash -> canonical path)
DB_PATH = str(Path(LOG_FILE).with_suffix(".sqlite3"))
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute(
    """
CREATE TABLE IF NOT EXISTS files(
    hash TEXT PRIMARY KEY,
    path TEXT NOT NULL
)
"""
)
# Cache: (size, head_hash) -> full_hash to avoid rehashing identical patterns
conn.execute(
    """
CREATE TABLE IF NOT EXISTS quick_cache(
    size INTEGER NOT NULL,
    head_hash TEXT NOT NULL,
    full_hash TEXT NOT NULL,
    PRIMARY KEY (size, head_hash)
)
"""
)
conn.commit()


# -------- Helpers --------
def norm(p: str) -> str:
    """Normalize path for stable comparisons on Windows."""
    return os.path.normcase(os.path.abspath(p))


def is_ignored_dir(path: str) -> bool:
    parts = [seg.lower() for seg in Path(path).parts]
    return any(seg in IGNORE_DIR_NAMES for seg in parts)


def wait_until_readable(path: str, tries=5, delay=0.6) -> bool:
    """Retry opening a file briefly to avoid hashing partial writes/locks."""
    for _ in range(tries):
        try:
            with open(path, "rb"):
                return True
        except Exception:
            time.sleep(delay)
    return False


def sha256_file(path: str, block=1024 * 1024) -> str:
    """Full SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(block), b""):
            h.update(b)
    return h.hexdigest()


def quick_fingerprint(path: str, head_bytes=1024 * 1024):
    """Return (size, head_sha256) for quick pre-check to avoid full hashing repeats."""
    size = os.path.getsize(path)
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(head_bytes))
    return (size, h.hexdigest())


def get_or_compute_full_hash(path: str) -> str:
    """Use quick_cache to avoid re-hashing identical files repeatedly."""
    size, head = quick_fingerprint(path)
    cur = conn.execute(
        "SELECT full_hash FROM quick_cache WHERE size=? AND head_hash=?",
        (size, head),
    )
    row = cur.fetchone()
    if row:
        # Still compute to verify; if it matches, trust cache next time
        try:
            full = sha256_file(path)
            if full == row[0]:
                return full
        except Exception:
            pass
    # Compute and store
    full = sha256_file(path)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO quick_cache(size, head_hash, full_hash) VALUES(?,?,?)",
            (size, head, full),
        )
        conn.commit()
    except Exception:
        pass
    return full


def policy_for(path: str) -> str:
    ap = norm(path)
    for base, pol in FOLDER_POLICY.items():
        if ap.startswith(norm(base) + os.sep):
            return pol
    return "move"


def move_duplicate(src_path: str, dump_dir: str, keeper: str):
    base = os.path.basename(src_path)
    target = os.path.join(dump_dir, base)
    root, ext = os.path.splitext(base)
    n = 1
    while os.path.exists(target):
        target = os.path.join(dump_dir, f"{root}_{n}{ext}")
        n += 1
    if DRY_RUN:
        log.info(f"[DRY-RUN DUPE] {src_path} dup-of {keeper} -> {target}")
        return
    shutil.move(src_path, target)
    log.info(f"[DUPE→DUMP] {src_path} dup-of {keeper} -> {target}")


# -------- Work queue & debounce --------
q = Queue()
pending = {}  # path -> last_event_time
pending_lock = threading.Lock()


def enqueue(path: str):
    try:
        if not os.path.isfile(path):
            return
        if is_ignored_dir(path):
            return
        if Path(path).suffix.lower() in IGNORE_EXTS:
            return
        if MAX_SIZE_BYTES is not None and os.path.getsize(path) > MAX_SIZE_BYTES:
            return
        with pending_lock:
            pending[path] = time.time()
    except FileNotFoundError:
        return


def debouncer():
    while True:
        now = time.time()
        to_process = []
        with pending_lock:
            for p, t0 in list(pending.items()):
                if (now - t0) * 1000 >= DEBOUNCE_MS:
                    to_process.append(p)
                    del pending[p]
        for p in to_process:
            q.put(p)
        time.sleep(0.5)


# -------- Watchdog setup --------
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            enqueue(event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            enqueue(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            # only need to hash the new destination
            enqueue(event.dest_path)


def scanner_worker():
    while True:
        try:
            path = q.get(timeout=1)
        except Empty:
            continue

        try:
            if not os.path.isfile(path):
                q.task_done()
                continue
            if is_ignored_dir(path) or Path(path).suffix.lower() in IGNORE_EXTS:
                q.task_done()
                continue
            if MAX_SIZE_BYTES is not None and os.path.getsize(path) > MAX_SIZE_BYTES:
                q.task_done()
                continue
            if not wait_until_readable(path):
                log.warning(f"[SKIP-LOCKED] {path}")
                q.task_done()
                continue
        except FileNotFoundError:
            q.task_done()
            continue

        try:
            full_hash = get_or_compute_full_hash(path)
        except Exception as e:
            log.warning(f"[SKIP] Hash failed for {path}: {e}")
            q.task_done()
            continue

        cur = conn.execute("SELECT path FROM files WHERE hash=?", (full_hash,))
        row = cur.fetchone()
        if row:
            keeper = row[0]
            if norm(keeper) == norm(path):
                log.debug(f"[SEEN] {path}")
            else:
                pol = policy_for(path)
                if pol == "ignore":
                    log.info(f"[IGNORE-POLICY] {path} dup-of {keeper}")
                elif pol == "report":
                    log.info(f"[DUPLICATE REPORT] {path} == {keeper}")
                else:
                    try:
                        move_duplicate(path, DUMP_FOLDER, keeper)
                    except Exception as e:
                        log.error(f"[FAIL MOVE] {path}: {e}")
        else:
            try:
                conn.execute(
                    "INSERT INTO files(hash, path) VALUES(?,?)",
                    (full_hash, norm(path)),
                )
                conn.commit()
                log.info(f"[KEEP] {path}")
            except Exception as e:
                log.error(f"[DB] Failed to remember {path}: {e}")

        q.task_done()


def initial_walk():
    """Seed the DB and catch existing dupes on startup."""
    log.info("[STARTUP] Initial crawl…")
    for root_folder in WATCH_FOLDERS:
        for root, dirs, files in os.walk(root_folder):
            # prune ignored dirs
            dirs[:] = [d for d in dirs if d.lower() not in {s.lower() for s in IGNORE_DIR_NAMES}]
            for name in files:
                fpath = os.path.join(root, name)
                enqueue(fpath)
    # Let debouncer feed queue and drain
    time.sleep((DEBOUNCE_MS / 1000) + 0.5)
    q.join()
    log.info("[STARTUP] Initial crawl complete.")


def main():
    # Start threads
    threading.Thread(target=debouncer, daemon=True).start()
    threading.Thread(target=scanner_worker, daemon=True).start()

    # Seed existing files
    initial_walk()

    # Observe
    obs = Observer()
    handler = Handler()
    for folder in WATCH_FOLDERS:
        obs.schedule(handler, folder, recursive=True)
    obs.start()
    log.info("[WATCHING] " + " | ".join(WATCH_FOLDERS))

    # Handle Ctrl+C / SIGTERM gracefully
    def shutdown(signum=None, frame=None):
        log.info("[SHUTDOWN] Stopping observer and closing DB…")
        try:
            obs.stop()
            obs.join()
        finally:
            try:
                conn.close()
            except Exception:
                pass
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    log.info("=== tidbit (dedupe watchdog) starting ===")
    main()
