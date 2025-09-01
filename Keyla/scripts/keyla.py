import os
import shutil
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

DAEMON_ROOT = "C:/EdenOS_Origin/daemon_profiles"

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

def find_daemon_files(folder_path):
    matches = []
    for dirpath, _, filenames in os.walk(folder_path):
        if should_ignore(dirpath): continue
        for file in filenames:
            if file.endswith((".py", ".json", ".chaos")) and not file.lower().startswith("keyla"):
                full_path = os.path.join(dirpath, file)
                matches.append(full_path)
    return matches

def sort_and_move(files):
    moved = []
    for filepath in files:
        filename = os.path.basename(filepath)
        daemon_name = infer_daemon_name(filename)
        target_folder = ensure_home(daemon_name)
        target_path = os.path.join(target_folder, filename)

        try:
            shutil.move(filepath, target_path)
            moved.append((filename, target_folder))
            print(f"🧳 Moved {filename} → {target_folder}")
        except Exception as e:
            print(f"⚠️ Failed to move {filename}: {e}")
    return moved

def log_keyla_route(moved):
    route_log = os.path.join(DAEMON_ROOT, "keyla.route.chaosmeta")
    data = {
        "rescued_files": [{"file": f, "to": d} for f, d in moved],
        "symbolic_timestamp": "keyla.fullscan.reclaim",
        "guardian": "Keyla"
    }
    with open(route_log, "w") as f:
        json.dump(data, f, indent=2)

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

    reclaimed = sort_and_move(daemon_files)
    log_keyla_route(reclaimed)
    messagebox.showinfo("Success", "Files have been organized successfully!")

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

# Scan button to start the process
scan_button = tk.Button(root, text="Start Scan and Organize", command=start_keyla_scan)
scan_button.pack(pady=20)

root.mainloop()
