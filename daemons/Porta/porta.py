"""File mover daemon for Eden OS canvases.

Porta watches a source directory for new canvas-compatible files and moves
them into a destination folder with timestamped filenames. The watcher uses
``watchdog`` as an optional dependency; install it with
``pip install -r requirements.txt`` when you want to run Porta.

The source and destination paths can be overridden with the ``PORTA_SOURCE_DIR``
and ``PORTA_DEST_DIR`` environment variables.
"""

from __future__ import annotations

import shutil
import time
from datetime import datetime
from pathlib import Path

from Porta.settings import PortaSettings
import load_settings

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


def _require_watchdog():

    if not WATCHDOG_AVAILABLE:
        raise ImportError(WATCHDOG_HELP) from _WATCHDOG_IMPORT_ERROR


class CanvasFileHandler(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
    def __init__(self, settings: PortaSettings):

        super().__init__()
        self.settings = settings

    def on_created(self, event):

        if not event.is_directory:
            src_path = Path(event.src_path)
            if src_path.suffix.lower() in self.settings.supported_extensions:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                new_name = f"{timestamp}_{src_path.name}"
                dest_path = self.settings.dest_dir / new_name
                try:
                    shutil.move(str(src_path), str(dest_path))
                    print(f"Moved: {src_path.name} -> {dest_path}")
                except Exception as e:
                    print(f"Failed to move {src_path.name}: {e}")


def start_observer(settings: PortaSettings | None = None):

    _require_watchdog()

    resolved_settings = settings or load_settings()

    print(f"Watching for new files in: {resolved_settings.source_dir}")
    resolved_settings.dest_dir.mkdir(parents=True, exist_ok=True)

    event_handler = CanvasFileHandler(resolved_settings)
    observer = Observer()
    observer.schedule(event_handler, str(resolved_settings.source_dir), recursive=False)
    observer.start()

    return observer


def main(settings: PortaSettings | None = None):

    observer = start_observer(settings)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    main()
