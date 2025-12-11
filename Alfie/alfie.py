import os
import hashlib
from datetime import datetime
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

TARGET_DIRS = [d.strip() for d in config.get("Alfie", "scan_directories").split(",")]
FINDINGS_DIR = config.get("Alfie", "output_directory")
TARGET_EXTENSIONS = [ext.strip() for ext in config.get("Alfie", "agent_file_extensions").split(",")]
EXCLUDED_DIRS = [config.get("Alfie", "excluded_directories")]

LOG_FILE = os.path.join(FINDINGS_DIR, config.get("Alfie", "tree_log_filename"))

# Define the file extensions to look for.
TARGET_EXTENSIONS = [".chaos", ".edenkey", ".edenmeta", ".emodare", ".mirror.json"]

# Define where the findings and log file will be stored.
FINDINGS_DIR = r"C:\EdenOS_Origin\all_daemons\_daemon_specialty_folders\alfie_findings"
LOG_FILE = os.path.join(FINDINGS_DIR, "alfie_log.txt")
QUARANTINE_DIR = os.path.join(FINDINGS_DIR, "alfie_quarantined_duplicates")
# --- End of Configuration ---

# --- Helper Functions ---
def is_eden_file(file):
    """Checks if a file has one of the target extensions."""
    return any(file.endswith(ext) for ext in TARGET_EXTENSIONS)

def file_hash(path):
    """Calculates the MD5 hash of a file."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        print(f"Could not hash file {path}: {e}")
        return None

def ensure_log_dir():
    """Ensures the directory for storing findings and quarantine exists."""
    os.makedirs(FINDINGS_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)

def scan_system():
    """
    Scans the folders listed in TARGET_DIRS for files with specified extensions,
    ignoring any __pycache__ directories.
    """
    print(f"[Alfie] Beginning scan of folders: {', '.join(TARGET_DIRS)}")
    found = []
    hashes = {} 

    for target_dir in TARGET_DIRS:
        if not os.path.exists(target_dir):
            print(f"[Alfie] Warning: Directory not found, skipping: {target_dir}")
            continue
            
        for root, dirs, files in os.walk(target_dir, topdown=True):
            dirs[:] = [d for d in dirs if d != '__pycache__']

            for file in files:
                if is_eden_file(file):
                    full_path = os.path.join(root, file)
                    h = file_hash(full_path)
                    
                    if h:
                        if h in hashes:
                            found.append((full_path, h, True))
                        else:
                            hashes[h] = full_path
                            found.append((full_path, h, False))
    return found

def generate_tree_output(node, prefix=""):
    """
    Recursively generates a string representation of the file tree using
    ├──, └──, and │ characters.
    """
    directories = sorted([k for k in node if k != '_files_'])
    files = sorted(node.get('_files_', []))
    
    items = directories + files
    output_lines = []

    for i, item_name in enumerate(items):
        is_last = (i == len(items) - 1)
        connector = "└── " if is_last else "├── "
        
        output_lines.append(f"{prefix}{connector}{item_name}")

        if item_name in directories:
            new_prefix = prefix + ("    " if is_last else "│   ")
            output_lines.append(generate_tree_output(node[item_name], new_prefix))

    return "\n".join(output_lines)

# --- NEW: Scan Summary Function ---
def generate_scan_summary(findings):
    """
    Generates a summary report of the scan findings.
    Returns a formatted string.
    """
    total_files = len(findings)
    unique_files = 0
    duplicate_files = 0
    extension_counts = {}
    
    for path, h, is_dup in findings:
        if h: # Only count files that were successfully hashed
            if not is_dup:
                unique_files += 1
            else:
                duplicate_files += 1

            ext = os.path.splitext(path)[1].lower()
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
        
    summary_lines = [
        "--- Scan Summary ---",
        f"Total Files Found: {total_files}",
        f"Unique Files: {unique_files}",
        f"Duplicate Files (by hash): {duplicate_files}",
        "\nFile Types Breakdown:",
    ]

    if not extension_counts:
        summary_lines.append("  No target files found.")
    else:
        for ext, count in sorted(extension_counts.items()):
            summary_lines.append(f"  {ext}: {count}")

    summary_lines.append("--------------------")
    return "\n".join(summary_lines)

def write_log(entries, event_type="Scan", summary_report=""):
    """
    Builds a tree from the findings and writes it to the log file.
    Added event_type and summary_report parameters.
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    file_tree = {}
    for path, h, is_dup in entries:
        flag = " [DUPLICATE]" if is_dup else ""
        if h is None:
            file_display_string = f"{os.path.basename(path)} :: HASH_FAILED{flag}"
        else:
            file_display_string = f"{os.path.basename(path)} :: {h}{flag}"
        
        parts = os.path.normpath(path).split(os.sep)
        
        current_level = file_tree
        for part in parts[:-1]:
            current_level = current_level.setdefault(part, {})
        
        current_level.setdefault('_files_', []).append(file_display_string)

    tree_string = generate_tree_output(file_tree)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n--- {event_type} at {now} ---\n")
        if summary_report: # Include summary if provided
            f.write(summary_report)
            f.write("\n") # Add a newline after the summary for separation
        f.write(tree_string)
        f.write("\n")

# --- Watchdog Event Handler Class ---
class AlfieEventHandler(FileSystemEventHandler):
    _known_hashes = set() 

    def __init__(self, initial_findings_hashes):
        super().__init__()
        for _, h, _ in initial_findings_hashes:
            if h:
                self._known_hashes.add(h)

    def _process_file_event(self, src_path, event_name):
        if not os.path.exists(src_path) or os.path.isdir(src_path):
            return 

        if is_eden_file(src_path):
            print(f"[Alfie] Detected {event_name.upper()} file: {src_path}")
            h = file_hash(src_path)
            if h:
                is_duplicate = h in self._known_hashes
                if not is_duplicate:
                    self._known_hashes.add(h)
                
                # For real-time events, we'll log them individually without a full tree summary
                # because the event is for a single file.
                # However, we'll now ensure a basic summary is still passed to write_log.
                # Here, the "findings" for write_log is just this single file event.
                write_log([(src_path, h, is_duplicate)], event_type=f"File {event_name}")
                
                if is_duplicate:
                    quarantine_file(src_path, h)

    def on_created(self, event):
        self._process_file_event(event.src_path, "Created")

    def on_modified(self, event):
        self._process_file_event(event.src_path, "Modified")

    def on_deleted(self, event):
        if not event.is_directory and is_eden_file(event.src_path):
            print(f"[Alfie] Detected DELETED file: {event.src_path}")
            # For deleted files, we don't hash, just log the event.
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n--- File Deleted at {now} ---\n")
                f.write(f"{os.path.basename(event.src_path)} :: {event.src_path}\n")
                f.write("\n")


# --- Duplicate Management Function ---
def quarantine_file(file_path, file_hashing, event_type="Quarantined Duplicate"):
    """Moves a given file to the quarantine directory."""
    ensure_log_dir() 
    
    file_name = os.path.basename(file_path)
    quarantined_name = f"{file_name}.{file_hashing}.quarantined"
    destination_path = os.path.join(QUARANTINE_DIR, quarantined_name)

    try:
        shutil.move(file_path, destination_path)
        log_message = f"Moved '{file_path}' to '{destination_path}'"
        print(f"[Alfie] {log_message}")
        
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n--- {event_type} at {now} ---\n")
            f.write(f"Original: {file_path}\n")
            f.write(f"Quarantined To: {destination_path}\n")
            f.write(f"Hash: {file_hashing}\n")
            f.write("\n")

    except FileNotFoundError:
        print(f"[Alfie] Error: File not found for quarantine: {file_path}")
    except Exception as e:
        print(f"[Alfie] Error quarantining file {file_path}: {e}")


# --- Main Function ---
def main():
    """Main function to run the scanner and start the real-time observer."""
    ensure_log_dir()

    # Initial scan
    print("[Alfie] Running initial scan...")
    initial_findings = scan_system()
    
    # Generate and print summary for the initial scan
    initial_summary = generate_scan_summary(initial_findings)
    print(initial_summary)
    
    # Write initial scan findings and summary to log
    write_log(initial_findings, event_type="Initial Scan", summary_report=initial_summary)
    print(f"[Alfie] Initial scan complete. {len(initial_findings)} files logged.")

    # Process duplicates found during the initial scan
    print("[Alfie] Checking for and quarantining initial duplicates...")
    for path, h, is_dup in initial_findings:
        if is_dup:
            quarantine_file(path, h, event_type="Initial Scan Duplicate Quarantined")
    print("[Alfie] Initial duplicate check complete.")

    # Set up the observer for real-time watching
    event_handler = AlfieEventHandler(initial_findings)
    observer = Observer()

    for target_dir in TARGET_DIRS:
        if os.path.exists(target_dir):
            observer.schedule(event_handler, target_dir, recursive=True)
            print(f"[Alfie] Now watching: {target_dir}")
        else:
            print(f"[Alfie] Warning: Cannot watch non-existent directory: {target_dir}")

    print("[Alfie] Starting real-time file watcher. Press Ctrl+C to stop.")
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n[Alfie] File watcher stopped.")
    finally:
        observer.join()


if __name__ == "__main__":
    main()