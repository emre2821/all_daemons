import time
import shutil
import os
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
SOURCE_DIR = Path(r"C:\Users\emmar\Desktop\Master_EdenOS\to_be_placed")
DEST_DIR = Path(r"C:\Users\emmar\Documents\Obsidian Vault\Eden\07_Vas_Saves")
SUPPORTED_EXTENSIONS = ['.asciidoc', '.py', '.md']

class CanvasFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            src_path = Path(event.src_path)
            if src_path.suffix in SUPPORTED_EXTENSIONS:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{timestamp}_{src_path.name}"
                dest_path = DEST_DIR / new_name
                try:
                    shutil.move(str(src_path), str(dest_path))
                    print(f"Moved: {src_path.name} -> {dest_path}")
                except Exception as e:
                    print(f"Failed to move {src_path.name}: {e}")

if __name__ == "__main__":
    print(f"Watching for new files in: {SOURCE_DIR}")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = CanvasFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(SOURCE_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
