#!/usr/bin/env python3
"""
Enhanced Phone Auto Organizer (cindy.py)
- Watches a folder and automatically organizes files
- Features intelligent file sorting, error handling, and statistics
- Supports concurrent processing and graceful shutdown
- Includes comprehensive logging and configuration management
"""

import os
import re
import time
import shutil
import signal
import logging
import sys
import yaml
import magic
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# === Default Configuration (can be overridden by config.yaml) ===
DEFAULT_CONFIG = {
    "watch_path": "/storage/emulated/0",
    "dest_root": "/storage/emulated/0",
    "interval": 10,
    "max_file_size": 104857600,  # 100MB
    "max_workers": 4,
    "categories": {
        "docs": [".pdf", ".docx", ".txt", ".md"],
        "images": [".jpg", ".jpeg", ".png", ".gif", ".webp"],
        "videos": [".mp4", ".mov", ".avi", ".mkv"],
        "audio": [".mp3", ".wav", ".flac", ".m4a"],
        "code": [".py", ".js", ".ts", ".html", ".css", ".json"],
        "chaos": [".chaos", ".sn", ".ritual"]
    },
    "ignore_patterns": [
        ".DS_Store",
        "Thumbs.db",
        "*.tmp",
        "*.temp",
        "~*"
    ]
}

class FileOrganizerStats:
    """Tracks statistics for file organization operations."""
    def __init__(self):
        self.files_processed: int = 0
        self.total_size: int = 0
        self.errors: int = 0
        self.start_time: float = time.time()

    def update(self, file_size: int) -> None:
        """Update statistics with processed file information."""
        self.files_processed += 1
        self.total_size += file_size

    def increment_errors(self) -> None:
        """Increment the error counter."""
        self.errors += 1

    def get_summary(self) -> str:
        """Return a formatted summary of statistics."""
        duration = time.time() - self.start_time
        return (
            f"Files processed: {self.files_processed}\n"
            f"Total size: {self.total_size/1024/1024:.2f} MB\n"
            f"Errors: {self.errors}\n"
            f"Running time: {duration:.2f} seconds"
        )

class FileOrganizer:
    """Main file organizer class handling all file operations."""
    
    def __init__(self):
        self.config = self._load_config()
        self.stats = FileOrganizerStats()
        self.watch_path = Path(self.config["watch_path"])
        self.dest_root = Path(self.config["dest_root"])
        self.setup_logging()
        self.bad_patterns = re.compile(r"(final.*|copy.*|backup.*|\(\d+\))", re.IGNORECASE)
        
        # Ensure destination directory exists
        self.dest_root.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """Load configuration from YAML file or use defaults."""
        try:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
                return {**DEFAULT_CONFIG, **(config or {})}
        except FileNotFoundError:
            logging.warning("Config file not found, using defaults")
            return DEFAULT_CONFIG

    def setup_logging(self) -> None:
        """Configure logging settings."""
        log_file = self.dest_root / "organizer.log"
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        # Also log to console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(console_handler)

    def clean_name(self, name: str) -> str:
        """Clean up filename by removing unwanted patterns."""
        base, ext = os.path.splitext(name)
        base = self.bad_patterns.sub("", base).strip("_- .")
        return f"{base}{ext}" if base else f"file_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"

    def categorize(self, file: Path) -> Path:
        """Determine appropriate category for file."""
        try:
            mime_type = magic.from_file(str(file), mime=True)
            # First try to categorize by MIME type
            mime_category = mime_type.split('/')[0]
            if mime_category in self.config["categories"]:
                return self.dest_root / mime_category
            
            # Fall back to extension-based categorization
            for cat, exts in self.config["categories"].items():
                if file.suffix.lower() in exts:
                    return self.dest_root / cat
            
            return self.dest_root / "other"
        except Exception as e:
            logging.error(f"Error categorizing {file}: {e}")
            return self.dest_root / "other"

    def should_process(self, file: Path) -> bool:
        """Determine if file should be processed based on filters."""
        if not file.is_file():
            return False
        if file.stat().st_size > self.config["max_file_size"]:
            logging.warning(f"File too large: {file}")
            return False
        if any(file.match(pattern) for pattern in self.config["ignore_patterns"]):
            return False
        return True

    def move_file(self, file: Path) -> None:
        """Safely move file to its destination directory."""
        try:
            if not self.should_process(file):
                return

            dest_dir = self.categorize(file)
            dest_dir.mkdir(parents=True, exist_ok=True)
            new_name = self.clean_name(file.name)
            dest_path = dest_dir / new_name

            # Handle filename conflicts
            counter = 1
            while dest_path.exists():
                stem = dest_path.stem.rsplit('_', 1)[0]
                dest_path = dest_dir / f"{stem}_{counter}{file.suffix}"
                counter += 1

            shutil.move(str(file), str(dest_path))
            self.stats.update(file.stat().st_size)
            logging.info(f"Moved: {file} → {dest_path}")
            
        except PermissionError:
            self.stats.increment_errors()
            logging.error(f"Permission denied: {file}")
        except Exception as e:
            self.stats.increment_errors()
            logging.error(f"Error processing {file}: {e}")

    def process_directory(self) -> None:
        """Process all files in watch directory using thread pool."""
        try:
            files = [f for f in self.watch_path.iterdir() if self.should_process(f)]
            with ThreadPoolExecutor(max_workers=self.config["max_workers"]) as executor:
                executor.map(self.move_file, files)
        except Exception as e:
            logging.error(f"Error processing directory: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    logging.info("Shutting down gracefully...")
    sys.exit(0)

def main():
    """Main execution function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    organizer = FileOrganizer()
    logging.info(f"Starting file organizer watching {organizer.watch_path}")

    try:
        while True:
            organizer.process_directory()
            logging.info(organizer.stats.get_summary())
            time.sleep(organizer.config["interval"])
    except KeyboardInterrupt:
        logging.info("Organizer stopped by user")
        logging.info(organizer.stats.get_summary())
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        raise

if __name__ == "__main__":
    main()