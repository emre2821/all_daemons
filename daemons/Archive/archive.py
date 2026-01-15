# C:\EdenOS_Origin\daemons\Archive\archive.py
import os
import sys
import time
import traceback
import argparse

# --- Eden path bootstrap ------------------------------------------------------
EDEN_ROOT = os.environ.get("EDEN_ROOT", os.getcwd())
WORK_ROOT = os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT)
RHEA_BASE = os.path.join(WORK_ROOT, "daemons", "Rhea")
TOOLS_DIR = os.path.join(EDEN_ROOT, "shared", "Daemon_tools")
TOOLS_SCRIPTS = os.path.join(TOOLS_DIR, "scripts")

# Make sure imports can find sibling daemons and your tools
for p in (EDEN_ROOT, os.path.join(EDEN_ROOT, "daemons"), TOOLS_DIR, TOOLS_SCRIPTS):
    if p not in sys.path:
        sys.path.append(p)

# Try to import toolchain (fail soft with clear error)
try:
    from Daemon_tools.vas_converter import convert_vas
    from Daemon_tools.db_utils import init_db
    from Daemon_tools.db_utils import log_to_db
except Exception as e:
    print(f"[Archive] ERROR: could not import Daemon_tools: {e}")
    print(f"[Archive] Searched: {TOOLS_DIR}")
    traceback.print_exc()
    # We don't exit; you can still see the error from Rhea and fix paths
    convert_vas = None

    def init_db():
        return None

    def log_to_db(*a, **k):
        return None


# Logging + safety helpers (optional)
try:
    from eden_paths import eden_root
    from eden_safety import SafetyContext
    import log_event
except Exception:
    try:
        from Daemon_tools.scripts.eden_paths import eden_root
        from Daemon_tools.scripts.eden_safety import SafetyContext
        import log_event
    except Exception:

        def eden_root():
            return os.environ.get("EDEN_ROOT", r"C:\\EdenOS_Origin")

        class SafetyContext:  # type: ignore
            def __init__(
                self, daemon: str, dry_run: bool = True, confirm: bool = False, **_
            ):
                self.daemon, self.dry_run, self.confirm = daemon, dry_run, confirm

            def require_confirm(self):
                if not self.confirm and not self.dry_run:
                    self.dry_run = True

            def log(self, *_a, **_k):
                pass

        def log_event(*_a, **_k):  # type: ignore
            pass


# --- Folders you specified ----------------------------------------------------
INBOX_DIR = os.path.join(RHEA_BASE, "_inbox")  # general inbox (not watched by Archive)
WATCH_DIR = os.path.join(RHEA_BASE, "to_convert")  # <== Archive watches this
try:
    from eden_paths import daemon_out_dir as _daemon_out_dir
except Exception:
    try:
        from Daemon_tools.scripts.eden_paths import daemon_out_dir as _daemon_out_dir
    except Exception:
        _daemon_out_dir = None

OUTPUT_DIR = (
    str(_daemon_out_dir("Archive"))
    if _daemon_out_dir
    else os.path.join(RHEA_BASE, "_outbox", "Archive")
)
ARCHIVES_DIR = os.path.join(
    RHEA_BASE, "_archives"
)  # (not used for writes here, but created)
LOGS_DIR = os.path.join(RHEA_BASE, "_logs")
TMP_DIR = os.path.join(RHEA_BASE, "_tmp")
WORK_DIR = os.path.join(RHEA_BASE, "_work")
GRADED_DIR = os.path.join(
    RHEA_BASE, "graded_enteries"
)  # keeping your spelling for canon :)

# --- Ensure filesystem exists -------------------------------------------------
for d in (
    INBOX_DIR,
    WATCH_DIR,
    OUTPUT_DIR,
    ARCHIVES_DIR,
    LOGS_DIR,
    TMP_DIR,
    WORK_DIR,
    GRADED_DIR,
):
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


def iter_pending(scope_dir: str = None):
    """Yield (fname, in_path, out_path) for pending .chaos files."""
    watch_dir = scope_dir or WATCH_DIR
    if not os.path.isdir(watch_dir):
        return
    for fname in os.listdir(watch_dir):
        if not fname.lower().endswith(".chaos"):
            continue
        if fname.endswith(".part"):
            continue
        in_path = os.path.join(watch_dir, fname)
        if not os.path.isfile(in_path):
            continue
        out_name = fname[:-6] + ".converted.chaos"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        yield (fname, in_path, out_path)


def process_once(ctx: "SafetyContext", scope_dir: str = None) -> int:

    count = 0
    for fname, in_path, out_path in iter_pending(scope_dir):
        count += 1
        if ctx.dry_run or not ctx.confirm:
            print(f"[DRY RUN] Would convert: {fname} -> {os.path.basename(out_path)}")
            log_event("Archive", "plan_convert", target=fname, outcome="planned")
            continue
        try:
            log_line(f"[Archive] Converting: {fname}")
            safe_convert(in_path, out_path)
            agent_guess = "Handel" if "handel" in fname.lower() else "Unknown"
            try:
                log_to_db(fname, os.path.basename(out_path), agent=agent_guess)
            except Exception as e_db:
                log_line(f"[Archive] DB log warning for {fname}: {e_db}")
            try:
                os.remove(in_path)
            except Exception as e_rm:
                log_line(f"[Archive] WARN: could not remove {in_path}: {e_rm}")
            log_event("Archive", "convert", target=fname, outcome="ok")
            log_line(
                f"[Archive] Logged and converted: {fname} -> {os.path.basename(out_path)}"
            )
        except Exception as e:
            log_line(f"[Archive] Error converting {fname}: {e}")
            traceback.print_exc()
            log_event("Archive", "convert", target=fname, outcome="error", error=str(e))
    return count


def main_loop(
    poll_seconds: float = 2.0, ctx: "SafetyContext" = None, scope_dir: str = None
):

    log_line("[Archive] Daemon online. Watching for CHAOS files in 'to_convert'...")
    while True:
        try:
            if not os.path.isdir(scope_dir or WATCH_DIR):
                os.makedirs(scope_dir or WATCH_DIR, exist_ok=True)
            process_once(ctx or SafetyContext("Archive", dry_run=True), scope_dir)

        except Exception as outer:
            log_line(f"[Archive] Outer loop error: {outer}")
            traceback.print_exc()

        time.sleep(poll_seconds)


def _build_parser():

    ap = argparse.ArgumentParser(description="Archive daemon")
    ap.add_argument(
        "--watch", action="store_true", help="Watch directory and process continuously"
    )
    ap.add_argument("--scope", help="Override watch directory for one-shot processing")
    ap.add_argument("--dry-run", action="store_true", help="Plan only")
    ap.add_argument(
        "--confirm", action="store_true", help="Execute conversions and removals"
    )
    ap.add_argument("--log-dir", help="Custom log directory")
    return ap


def main(argv=None):

    args = _build_parser().parse_args(argv)
    ctx = SafetyContext(
        "Archive",
        dry_run=(not args.confirm) if not args.dry_run else True,
        confirm=args.confirm,
    )
    ctx.require_confirm()
    if args.watch:
        main_loop(ctx=ctx, scope_dir=args.scope)
        return 0
    processed = process_once(ctx, scope_dir=args.scope)
    print(f"Archive processed {processed} item(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


def describe() -> dict:

    return {
        "name": "Archive",
        "role": ".chaos converter (to converted.chaos)",
        "inputs": {"scope": WATCH_DIR},
        "outputs": {"outbox": OUTPUT_DIR},
        "flags": ["--watch", "--scope", "--dry-run", "--confirm", "--log-dir"],
        "safety_level": "mutating",
    }


def healthcheck() -> dict:

    status = "ok"
    notes = []
    # Check tool import
    try:
        ok = convert_vas is not None  # type: ignore[name-defined]
    except Exception:
        ok = False
    if not ok:
        status = "warn"
        notes.append("convert_vas unavailable; conversions will be skipped")
    # Check dirs
    for p in [WATCH_DIR, OUTPUT_DIR, TMP_DIR]:
        try:
            os.makedirs(p, exist_ok=True)
        except Exception as e:
            status = "fail"
            notes.append(f"cannot create dir {p}: {e}")
    return {"status": status, "notes": "; ".join(notes)}
