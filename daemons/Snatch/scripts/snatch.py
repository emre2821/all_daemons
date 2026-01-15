# C:\EdenOS_Origin\daemons\Snatch\snatch.py
import os, shutil, time, traceback, argparse, sys

TOOLS_SCRIPTS = os.path.join(os.environ.get("EDEN_ROOT", os.getcwd()), "shared", "Daemon_tools", "scripts")
if TOOLS_SCRIPTS not in sys.path:
    sys.path.append(TOOLS_SCRIPTS)

try:
    from Daemon_tools.scripts.eden_safety import log_event
except Exception:
    try:
        from eden_safety import log_event
    except Exception:
        def log_event(*_a, **_k):
            pass

# --- Eden path bootstrap ------------------------------------------------------
EDEN_ROOT = os.environ.get("EDEN_ROOT", os.getcwd())
WORK_ROOT = os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT)
RHEA_BASE = os.path.join(WORK_ROOT, "daemons", "Rhea")

# Override with env vars if you want:
SOURCE_DIR   = os.environ.get("EDEN_APP_WATCH",    os.path.join(RHEA_BASE, "_inbox", "apps"))
try:
    import sys as _sys
    _sys.path.append(os.path.join(EDEN_ROOT, "shared", "Daemon_tools", "scripts"))
    from eden_paths import daemon_out_dir as _daemon_out_dir  # type: ignore
    PRESERVE_DIR = os.environ.get("EDEN_APP_PRESERVE", str(_daemon_out_dir("Snatch")))
except Exception:
    PRESERVE_DIR = os.environ.get("EDEN_APP_PRESERVE", os.path.join(RHEA_BASE, "_outbox", "Snatch"))
LOGS_DIR     = os.path.join(RHEA_BASE, "_logs")
TMP_DIR      = os.path.join(RHEA_BASE, "_tmp")

for d in (SOURCE_DIR, PRESERVE_DIR, LOGS_DIR, TMP_DIR):
    try:
        os.makedirs(d, exist_ok=True)
    except Exception as e:
        print(f"[Snatch] WARN: could not create {d}: {e}")

LOG_FILE = os.path.join(LOGS_DIR, "snatch_daemon.log")

def log_line(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

# --- App “signatures” ---------------------------------------------------------
SIGNATURE_FILES = {
    "main.py", "setup.py", "package.json", "manifest.json", "app.config",
    "pyproject.toml", "requirements.txt"
}
SIGNATURE_DIRS = {"bin", "src", "lib", "venv", "node_modules", ".git", ".venv"}

# Minimum entries before we even consider a folder an app
MIN_CONTENTS = 6

def is_app_folder(folder_path: str) -> bool:
    try:
        contents = os.listdir(folder_path)
        if len(contents) < MIN_CONTENTS:
            return False
        files = set(contents)
        subdirs = {name for name in contents if os.path.isdir(os.path.join(folder_path, name))}
        return bool(SIGNATURE_FILES & files) or bool(SIGNATURE_DIRS & subdirs)
    except Exception:
        return False

def folder_size(path: str) -> int:
    total = 0
    for root, dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(root, name))
            except Exception:
                pass
    return total

def is_stable(folder_path: str, dwell_seconds: float = 2.0) -> bool:
    """
    Consider a folder “stable” if its size and mtime don’t change across a short dwell window.
    Prevents grabbing a folder that’s still being written.
    """
    try:
        s1 = folder_size(folder_path)
        m1 = os.path.getmtime(folder_path)
        time.sleep(dwell_seconds)
        s2 = folder_size(folder_path)
        m2 = os.path.getmtime(folder_path)
        return s1 == s2 and m1 == m2
    except Exception:
        return False

def safe_move_folder(src: str, dst_root: str):
    """
    Move to PRESERVE_DIR via a temp staging name to avoid collisions.
    """
    base = os.path.basename(src.rstrip("\\/"))
    final = os.path.join(dst_root, base)
    staging = os.path.join(dst_root, base + ".staging")

    # If something crashed earlier and left staging behind, clean it
    if os.path.exists(staging):
        try:
            shutil.rmtree(staging, ignore_errors=True)
        except Exception:
            pass

    # If final exists, add a numeric suffix
    candidate = final
    n = 2
    while os.path.exists(candidate):
        candidate = f"{final}_{n}"
        n += 1

    # Stage then rename into place (more atomic than moving straight to final)
    shutil.move(src, staging)
    os.replace(staging, candidate)
    return candidate

def _plan_or_move(path: str, dry_run: bool = True):
    name = os.path.basename(path.rstrip("\\/"))
    if dry_run:
        log_line(f"[Snatch] PLAN preserve: {name}")
        return None
    try:
        dest = safe_move_folder(path, PRESERVE_DIR)
        log_line(f"[Snatch] Preserved app folder: {name}  ->  {dest}")
        return dest
    except Exception as e:
        log_line(f"[Snatch] Error preserving '{path}': {e}")
        traceback.print_exc()
        return None

def main_loop(dry_run: bool = True):
    log_line(f"[Snatch] Watching for app folders in: {SOURCE_DIR} (dry_run={dry_run})")
    while True:
        try:
            if not os.path.isdir(SOURCE_DIR):
                os.makedirs(SOURCE_DIR, exist_ok=True)

            for name in os.listdir(SOURCE_DIR):
                if name.startswith("~") or name.startswith("."):
                    continue
                path = os.path.join(SOURCE_DIR, name)
                if not os.path.isdir(path):
                    continue

                # Quick triage: app-like?
                if not is_app_folder(path):
                    continue

                # Stability check to avoid grabbing mid-write
                if not is_stable(path, dwell_seconds=2.0):
                    continue

                if dry_run:
                    log_line(f"[Snatch] PLAN preserve: {name}")
                    continue
                try:
                    dest = safe_move_folder(path, PRESERVE_DIR)
                    log_line(f"[Snatch] Preserved app folder: {name}  →  {dest}")
                except Exception as e:
                    log_line(f"[Snatch] Error preserving '{path}': {e}")
                    traceback.print_exc()

            time.sleep(3)
        except KeyboardInterrupt:
            log_line("[Snatch] Stopping (KeyboardInterrupt).")
            break
        except Exception as e:
            log_line(f"[Snatch] Loop error: {e}")
            traceback.print_exc()
            time.sleep(5)

def main(argv=None):
    ap = argparse.ArgumentParser(description="Snatch - App Preserver")
    ap.add_argument("--watch", action="store_true", help="Watch for app folders (default action)")
    ap.add_argument("--once", action="store_true", help="Process once and exit")
    ap.add_argument("--dry-run", action="store_true", help="Plan only (default unless --confirm)")
    ap.add_argument("--confirm", action="store_true", help="Execute moves to PRESERVE_DIR")
    args = ap.parse_args(argv)

    dry_run = (not args.confirm) if not args.dry_run else True
    if args.once:
        # One pass over current content
        if os.path.isdir(SOURCE_DIR):
            for name in os.listdir(SOURCE_DIR):
                path = os.path.join(SOURCE_DIR, name)
                if os.path.isdir(path) and is_app_folder(path) and is_stable(path, dwell_seconds=1.0):
                    if dry_run:
                        log_line(f"[Snatch] PLAN preserve: {name}")
                    else:
                        try:
                            dest = safe_move_folder(path, PRESERVE_DIR)
                            log_line(f"[Snatch] Preserved app folder: {name}  ->  {dest}")
                        except Exception as e:
                            log_line(f"[Snatch] Error preserving '{path}': {e}")
                            traceback.print_exc()
        raise SystemExit(0)
    # default watch
    main_loop(dry_run=dry_run)


if __name__ == "__main__":
    main()

def describe() -> dict:
    return {
        "name": "Snatch",
        "role": "App folder preserver",
        "inputs": {"source": SOURCE_DIR},
        "outputs": {"preserve_dir": PRESERVE_DIR},
        "flags": ["--watch", "--once", "--dry-run", "--confirm"],
        "safety_level": "destructive",
    }


def healthcheck() -> dict:
    status = "ok"; notes = []
    for p in (SOURCE_DIR, PRESERVE_DIR, LOGS_DIR, TMP_DIR):
        try:
            os.makedirs(p, exist_ok=True)
        except Exception as e:
            status = "fail"; notes.append(f"cannot create {p}: {e}")
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as _:
            pass
    except Exception as e:
        if status == "ok":
            status = "warn"
        notes.append(f"log write warn: {e}")
    return {"status": status, "notes": "; ".join(notes)}
