# C:\EdenOS_Origin\all_daemons\Snatch\snatch.py
import os, shutil, time, traceback

# --- Eden path bootstrap ------------------------------------------------------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin")
RHEA_BASE = os.path.join(EDEN_ROOT, "all_daemons", "Rhea")

# Override with env vars if you want:
SOURCE_DIR   = os.environ.get("EDEN_APP_WATCH",    os.path.join(RHEA_BASE, "_inbox", "apps"))
PRESERVE_DIR = os.environ.get("EDEN_APP_PRESERVE", os.path.join(RHEA_BASE, "_archives", "apps"))
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

def main_loop():
    log_line(f"[Snatch] Watching for app folders in: {SOURCE_DIR}")
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

if __name__ == "__main__":
    main_loop()
