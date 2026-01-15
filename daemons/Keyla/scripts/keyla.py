import os
import sys
import shutil
import json
import uuid
from datetime import datetime
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

# Resolve EDEN_ROOT smartly; fallback to CWD
EDEN_ROOT = os.environ.get("EDEN_ROOT", os.getcwd())
WORK_ROOT = os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT)
ALL_DAEMONS = os.path.join(EDEN_ROOT, "daemons")
TOOLS_SCRIPTS = os.path.join(EDEN_ROOT, "shared", "Daemon_tools", "scripts")
try:
    sys.path.append(TOOLS_SCRIPTS)
    from eden_paths import daemon_out_dir  # type: ignore
    DAEMON_ROOT = str(daemon_out_dir("Keyla"))
except Exception:
    RHEA_BASE = os.path.join(ALL_DAEMONS, "Rhea")
    DAEMON_ROOT = os.path.join(WORK_ROOT, "daemons", "Rhea", "_outbox", "Keyla")

# Events bus integration (optional)
try:
    # Package-style import first
    from Daemon_tools.scripts.eden_safety import log_event as _log_event  # type: ignore
except Exception:
    try:
        sys.path.append(TOOLS_SCRIPTS)
        from eden_safety import log_event as _log_event  # type: ignore
    except Exception:
        def _log_event(*_a, **_k):
            pass

def ensure_home(daemon_name):
    home = os.path.join(DAEMON_ROOT, daemon_name)
    os.makedirs(home, exist_ok=True)
    return home

def infer_daemon_name(filename):
    # Use the filename stem to guess
    base = os.path.basename(filename).split('.')[0]
    return base.title()

def should_ignore(path):
    # This function checks if a directory should be ignored
    IGNORE_DIRS = ["C:/Windows", "C:/Program Files", "C:/Program Files (x86)", "C:/Users/All Users", "C:/$Recycle.Bin"]
    return any(path.startswith(ignored) for ignored in IGNORE_DIRS)

def _known_daemons():
    """Return (daemon_names: set[str], script_stems: set[str])."""
    names = set()
    stems = set()
    # Try eden_discovery for accuracy
    try:
        sys.path.append(TOOLS_SCRIPTS)
        import eden_discovery  # type: ignore
        for info in eden_discovery.discover():
            names.add(info.name.lower())
            if info.script:
                stem = os.path.splitext(os.path.basename(info.script))[0]
                stems.add(stem.lower())
    except Exception:
        # Fallback: scan folder names under daemons
        try:
            for entry in os.listdir(ALL_DAEMONS):
                path = os.path.join(ALL_DAEMONS, entry)
                if os.path.isdir(path) and entry not in {"Daemon_tools", "Rhea", "Digitari_v0_1", ".venv", ".vscode", "CODE_REPORTS"}:
                    names.add(entry.lower())
                    scripts = os.path.join(path, "scripts")
                    if os.path.isdir(scripts):
                        for f in os.listdir(scripts):
                            if f.endswith(".py"):
                                stems.add(os.path.splitext(f)[0].lower())
        except Exception:
            pass
    return names, stems


def _looks_like_daemon_file(path: str, names: set[str], stems: set[str]) -> bool:
    """Heuristics to accept only likely daemon-related files.

    - .py: filename stem must match a known daemon name or known script stem
    - .json: filename contains a known daemon name and 'daemon_' substring
    - .chaos: keep conservative; must contain 'daemon' in name or a known daemon name
    """
    basename = os.path.basename(path)
    stem, ext = os.path.splitext(basename)
    ext = ext.lower()
    s = stem.lower()
    b = basename.lower()
    if ext == ".py":
        return s in names or s in stems
    if ext == ".json":
        return ("daemon_" in b) and any(n in b for n in names)
    if ext == ".chaos":
        return ("daemon" in b) or any(n in b for n in names)
    return False


def find_daemon_files(folder_path):
    daemon_names, script_stems = _known_daemons()
    matches = []
    for dirpath, _, filenames in os.walk(folder_path):
        if should_ignore(dirpath):
            continue
        for file in filenames:
            full_path = os.path.join(dirpath, file)
            if file.lower().startswith("keyla"):
                continue
            if _looks_like_daemon_file(full_path, daemon_names, script_stems):
                matches.append(full_path)
    return matches

LEDGER = os.path.join(DAEMON_ROOT, "keyla.ledger.jsonl")


def _append_ledger(entry: dict):
    os.makedirs(DAEMON_ROOT, exist_ok=True)
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _next_free_path(base_path: str) -> str:
    if not os.path.exists(base_path):
        return base_path
    root, ext = os.path.splitext(base_path)
    n = 2
    cand = f"{root}_{n}{ext}"
    while os.path.exists(cand):
        n += 1
        cand = f"{root}_{n}{ext}"
    return cand


def create_plan(files):
    batch_id = str(uuid.uuid4())
    plan = []
    for filepath in files:
        filename = os.path.basename(filepath)
        daemon_name = infer_daemon_name(filename)
        target_folder = ensure_home(daemon_name)
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, filename)
        target_path = _next_free_path(target_path)
        rec = {"file": filename, "from": filepath, "to": target_path, "daemon": daemon_name}
        plan.append(rec)
        try:
            _log_event("Keyla", action="plan_move", target=filepath, outcome="planned",
                       extra={"to": target_path, "batch_id": batch_id})
        except Exception:
            pass
    # record plan
    _append_ledger({
        "type": "plan",
        "batch_id": batch_id,
        "entries": plan,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    })
    try:
        _log_event("Keyla", action="plan_batch", target=str(len(plan)), outcome="planned",
                   extra={"batch_id": batch_id})
    except Exception:
        pass
    return plan, batch_id


def execute_plan(plan, batch_id: str):
    moved = []
    try:
        _log_event("Keyla", action="execute_batch", outcome="start", target="", extra={"batch_id": batch_id, "count": len(plan)})
    except Exception:
        pass
    for rec in plan:
        src = rec["from"]
        dst = rec["to"]
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.move(src, dst)
            moved.append(rec)
            print(f"🧳 Moved {rec['file']} → {os.path.dirname(dst)}")
            try:
                _log_event("Keyla", action="move", target=src, outcome="ok", extra={"to": dst, "batch_id": batch_id})
            except Exception:
                pass
        except Exception as e:
            print(f"⚠️ Failed to move {rec['file']}: {e}")
            try:
                _log_event("Keyla", action="move", target=src, outcome="error", extra={"to": dst, "batch_id": batch_id, "error": str(e)})
            except Exception:
                pass
    # Write route + ledger
    route_entry = {
        "batch_id": batch_id,
        "rescued_files": moved,
        "symbolic_timestamp": datetime.now().isoformat(timespec="seconds"),
        "guardian": "Keyla",
    }
    _append_ledger({"type": "move_batch", **route_entry})
    try:
        _log_event("Keyla", action="execute_batch", outcome="done", target="", extra={"batch_id": batch_id, "moved": len(moved)})
    except Exception:
        pass
    return moved

def log_keyla_route(moved):
    route_log = os.path.join(DAEMON_ROOT, "keyla.route.chaosmeta")
    data = {
        "rescued_files": moved,
        "symbolic_timestamp": datetime.now().isoformat(timespec="seconds"),
        "guardian": "Keyla"
    }
    with open(route_log, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _show_plan_dialog(plan, batch_id, allow_execute: bool):
    win = tk.Toplevel(root)
    win.title("Keyla Plan Preview")
    text = tk.Text(win, width=100, height=25)
    text.pack(padx=10, pady=10)
    text.insert(tk.END, f"Batch: {batch_id}\nPlanned moves:\n\n")
    for rec in plan:
        text.insert(tk.END, f"{rec['from']}\n  -> {rec['to']}\n")
    text.config(state=tk.DISABLED)

    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)

    def do_execute():
        execute_plan(plan, batch_id)
        log_keyla_route(plan)
        messagebox.showinfo("Success", "Files have been organized successfully!")
        win.destroy()

    if allow_execute:
        tk.Button(btn_frame, text="Execute Plan", command=do_execute).pack(side=tk.LEFT, padx=6)
    tk.Button(btn_frame, text="Close", command=win.destroy).pack(side=tk.LEFT, padx=6)


def undo_last_batch():
    if not os.path.exists(LEDGER):
        messagebox.showinfo("Undo", "No ledger found to undo.")
        return
    # Read all entries; pop last move_batch
    with open(LEDGER, "r", encoding="utf-8") as f:
        lines = [json.loads(line) for line in f if line.strip()]
    for i in range(len(lines) - 1, -1, -1):
        entry = lines[i]
        if entry.get("type") == "move_batch":
            batch = entry
            break
    else:
        messagebox.showinfo("Undo", "No move batch to undo.")
        return
    errors = []
    batch_id = batch.get("batch_id")
    try:
        _log_event("Keyla", action="undo_batch", outcome="start", target="", extra={"batch_id": batch_id})
    except Exception:
        pass
    for rec in batch.get("rescued_files", []):
        src = rec.get("to")
        dst = rec.get("from")
        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # If destination exists, append suffix to avoid overwrite
            final_dst = dst
            n = 2
            while os.path.exists(final_dst):
                base, ext = os.path.splitext(dst)
                final_dst = f"{base}_{n}{ext}"
                n += 1
            if os.path.exists(src):
                shutil.move(src, final_dst)
                try:
                    _log_event("Keyla", action="undo_move", target=src, outcome="ok", extra={"to": final_dst, "batch_id": batch_id})
                except Exception:
                    pass
            else:
                errors.append(f"Missing: {src}")
        except Exception as e:
            errors.append(f"{src} -> {dst}: {e}")
    # Mark undo in ledger
    _append_ledger({
        "type": "undo_batch",
        "undo_of": batch.get("batch_id"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "errors": errors,
    })
    try:
        _log_event("Keyla", action="undo_batch", outcome="done", target="", extra={"batch_id": batch_id, "errors": len(errors)})
    except Exception:
        pass
    if errors:
        messagebox.showwarning("Undo completed with issues", "\n".join(errors))
    else:
        messagebox.showinfo("Undo", "Last batch reverted.")

def start_keyla_scan():
    folder_path = folder_path_entry.get()
    if not folder_path:
        messagebox.showerror("Error", "Please select a folder to scan.")
        return

    print(f"🔍 Keyla is scanning the folder: {folder_path}")
    daemon_files = find_daemon_files(folder_path)
    if not daemon_files:
        messagebox.showinfo("Info", "No orphaned daemon files found.")
        return

    plan, batch_id = create_plan(daemon_files)
    # Always show plan. If dry-run, don't execute; if not, allow confirm+execute.
    allow_exec = not plan_only_var.get()
    _show_plan_dialog(plan, batch_id, allow_exec)

def browse_folder():
    folder_selected = filedialog.askdirectory(initialdir=DAEMON_ROOT, title="Select Folder to Scan")
    if folder_selected:
        folder_path_entry.delete(0, tk.END)  # Clear current entry
        folder_path_entry.insert(0, folder_selected)  # Insert new path

# GUI setup using Tkinter
root = tk.Tk()
root.title("Keyla Daemon File Organizer")

# Folder selection
folder_label = tk.Label(root, text="Select folder to scan:")
folder_label.pack(pady=10)

folder_path_entry = tk.Entry(root, width=50)
folder_path_entry.pack(pady=10)

browse_button = tk.Button(root, text="Browse...", command=browse_folder)
browse_button.pack(pady=10)

# Plan only (dry-run) toggle
plan_only_var = tk.BooleanVar(value=True)
plan_check = tk.Checkbutton(root, text="Plan Only (Dry Run)", variable=plan_only_var)
plan_check.pack(pady=4)

# Scan button to start the process
scan_button = tk.Button(root, text="Start Scan and Organize", command=start_keyla_scan)
scan_button.pack(pady=20)

# Undo button
undo_button = tk.Button(root, text="Undo Last Batch", command=undo_last_batch)
undo_button.pack(pady=10)

root.mainloop()
