"""File mover daemon for Eden OS canvases.

Porta watches a source directory for new canvas-compatible files and moves
them into a destination folder with timestamped filenames. The watcher uses
``watchdog`` as an optional dependency; install it with
``pip install -r requirements.txt`` when you want to run Porta.
"""

import time
import shutil
from pathlib import Path
from datetime import datetime

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
    _WATCHDOG_IMPORT_ERROR = None
except ImportError as exc:  # pragma: no cover - runtime dependency check
    WATCHDOG_AVAILABLE = False
    _WATCHDOG_IMPORT_ERROR = exc
    Observer = None  # type: ignore
    FileSystemEventHandler = object  # type: ignore

WATCHDOG_HELP = (
    "Porta needs the optional dependency 'watchdog' to monitor directories. "
    "Install it with `pip install watchdog` or `pip install -r requirements.txt`."
)

# Configuration
SOURCE_DIR = Path(r"C:\Users\emmar\Desktop\Master_EdenOS\to_be_placed")
DEST_DIR = Path(r"C:\Users\emmar\Documents\Obsidian Vault\Eden\07_Vas_Saves")
SUPPORTED_EXTENSIONS = ['.asciidoc', '.py', '.md']


def _require_watchdog():
    if not WATCHDOG_AVAILABLE:
        raise ImportError(WATCHDOG_HELP) from _WATCHDOG_IMPORT_ERROR

class CanvasFileHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
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


def start_observer():
    _require_watchdog()

    print(f"Watching for new files in: {SOURCE_DIR}")
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    event_handler = CanvasFileHandler()
    observer = Observer()
    observer.schedule(event_handler, str(SOURCE_DIR), recursive=False)
    observer.start()

    return observer


def main():
    observer = start_observer()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
