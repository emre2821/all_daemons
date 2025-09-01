# C:\EdenOS_Origin\all_daemons\Archive\archive.py
import os, sys, time, traceback

# --- Eden path bootstrap ------------------------------------------------------
EDEN_ROOT = os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin")
RHEA_BASE = os.path.join(EDEN_ROOT, "all_daemons", "Rhea")
TOOLS_DIR = os.path.join(EDEN_ROOT, "all_daemons", "Daemon_tools")

# Make sure imports can find sibling daemons and your tools
for p in (EDEN_ROOT,
          os.path.join(EDEN_ROOT, "all_daemons"),
          TOOLS_DIR):
    if p not in sys.path:
        sys.path.append(p)

# Try to import toolchain (fail soft with clear error)
try:
    from Daemon_tools.vas_converter import convert_vas
    from Daemon_tools.db_utils import init_db, log_to_db
except Exception as e:
    print(f"[Archive] ERROR: could not import Daemon_tools: {e}")
    print(f"[Archive] Searched: {TOOLS_DIR}")
    traceback.print_exc()
    # We don't exit; you can still see the error from Rhea and fix paths
    convert_vas = None
    init_db = lambda: None
    log_to_db = lambda *a, **k: None

# --- Folders you specified ----------------------------------------------------
INBOX_DIR     = os.path.join(RHEA_BASE, "_inbox")           # general inbox (not watched by Archive)
WATCH_DIR     = os.path.join(RHEA_BASE, "to_convert")       # <== Archive watches this
OUTPUT_DIR    = os.path.join(RHEA_BASE, "_outbox", "converted")
ARCHIVES_DIR  = os.path.join(RHEA_BASE, "_archives")        # (not used for writes here, but created)
LOGS_DIR      = os.path.join(RHEA_BASE, "_logs")
TMP_DIR       = os.path.join(RHEA_BASE, "_tmp")
WORK_DIR      = os.path.join(RHEA_BASE, "_work")
GRADED_DIR    = os.path.join(RHEA_BASE, "graded_enteries")  # keeping your spelling for canon :)

# --- Ensure filesystem exists -------------------------------------------------
for d in (INBOX_DIR, WATCH_DIR, OUTPUT_DIR, ARCHIVES_DIR, LOGS_DIR, TMP_DIR, WORK_DIR, GRADED_DIR):
    try:
        os.makedirs(d, exist_ok=True)
    except Exception as e:
        print(f"[Archive] WARN: could not create {d}: {e}")

LOG_FILE = os.path.join(LOGS_DIR, "archive_daemon.log")

def log_line(msg: str):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        # don’t crash on logging problems
        pass

# --- DB init (optional if tools missing) -------------------------------------
try:
    init_db()
except Exception as e:
    log_line(f"[Archive] WARN: init_db failed: {e}")

def safe_convert(in_path: str, out_path: str):
    """
    Convert .chaos using convert_vas into OUTPUT_DIR.
    Write via a temp file first, then atomically rename.
    """
    if convert_vas is None:
        raise RuntimeError("Daemon_tools not available; convert_vas is None")

    tmp_path = os.path.join(TMP_DIR, os.path.basename(out_path) + ".part")
    # Ensure temp dir exists
    os.makedirs(os.path.dirname(tmp_path), exist_ok=True)

    # Convert into temp first
    convert_vas(in_path, tmp_path)

    # Ensure output folder exists
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Atomic-ish replace on Windows (best effort)
    if os.path.exists(out_path):
        try:
            os.remove(out_path)
        except Exception:
            pass
    os.replace(tmp_path, out_path)

def main_loop(poll_seconds: float = 2.0):
    log_line("[Archive] Daemon online. Watching for CHAOS files in 'to_convert'...")
    while True:
        try:
            # listdir can throw if path disappears; we re-create it just in case
            if not os.path.isdir(WATCH_DIR):
                os.makedirs(WATCH_DIR, exist_ok=True)

            for fname in os.listdir(WATCH_DIR):
                # Only process plain .chaos files; skip temp/partial
                if not fname.lower().endswith(".chaos"):
                    continue
                if fname.endswith(".part"):
                    continue

                in_path = os.path.join(WATCH_DIR, fname)
                # skip directories or vanished files
                if not os.path.isfile(in_path):
                    continue

                try:
                    out_name = fname[:-6] + ".converted.chaos"  # replace .chaos
                    out_path = os.path.join(OUTPUT_DIR, out_name)

                    log_line(f"[Archive] Converting: {fname}")
                    safe_convert(in_path, out_path)

                    # Guess an agent from filename; harmless if Unknown
                    agent_guess = "Handel" if "handel" in fname.lower() else "Unknown"
                    try:
                        log_to_db(fname, out_name, agent=agent_guess)
                    except Exception as e_db:
                        log_line(f"[Archive] DB log warning for {fname}: {e_db}")

                    # Remove only after successful conversion
                    try:
                        os.remove(in_path)
                    except Exception as e_rm:
                        log_line(f"[Archive] WARN: could not remove {in_path}: {e_rm}")

                    log_line(f"[Archive] Logged and converted: {fname} -> {out_name}")

                except Exception as e:
                    log_line(f"[Archive] Error converting {fname}: {e}")
                    traceback.print_exc()

        except Exception as outer:
            log_line(f"[Archive] Outer loop error: {outer}")
            traceback.print_exc()

        time.sleep(poll_seconds)

if __name__ == "__main__":
    main_loop()
