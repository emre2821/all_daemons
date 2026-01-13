# mila.py — Storage Allocation Daemon
# Role: ensures daemons have space and organized shelves.
# Think of her as Eden’s quiet librarian, arranging drawers so nothing is lost.

import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Mila:
    daemon_id = "mila_allocator"
    class_name = "Mila"
    type = "storage.core.mila"
    role = "Storage Allocation Daemon"
    quote = "Every shelf has its keeper; every keeper, her place."
    description = "Scans daemon directories, creates missing folders, and allocates files into order."
    symbolic_traits = {
        "sigil": "≋",
        "element": "earth",
        "alignment": "grounded"
    }

    def __init__(self, root=None):

        if root is None:
            # Try to use eden_paths helper for cross-platform support
            try:
                import sys
                from pathlib import Path as P
                sys.path.insert(0, str(P(__file__).resolve().parents[1]))
                from Daemon_tools.scripts.eden_paths import daemons_root
                self.root = daemons_root()
            except ImportError:
                # Fallback to environment variable or current directory
                self.root = Path(os.environ.get("EDEN_ROOT", Path.cwd())) / "all_daemons"
        else:
            self.root = Path(root)
        self.rules = {
            "logs": ["*.log"],
            "configs": ["*.yaml", "*.json"],
            "scripts": ["*.py"],
            "archives": ["*.zip", "*.tar", "*.gz"],
            "tmp": ["*.tmp", "*.bak"],
        }

    def _ensure_dirs(self, base: Path):

        for key in self.rules:
            (base / key).mkdir(exist_ok=True)

    def allocate(self, daemon_name: str):

        """Sort files in a daemon folder into proper shelves."""
        folder = self.root / daemon_name
        if not folder.exists():
            logging.warning(f"Daemon folder {daemon_name} not found.")
            return
        self._ensure_dirs(folder)
        for f in folder.glob("*.*"):
            for cat, patterns in self.rules.items():
                if any(f.match(pat) for pat in patterns):
                    dest = folder / cat / f.name
                    if not dest.exists():
                        shutil.move(str(f), dest)
                        logging.info(f"{self.symbolic_traits['sigil']} Mila filed {f.name} → {cat}")
                    break

    def allocate_all(self):

        for daemon_folder in self.root.iterdir():
            if daemon_folder.is_dir():
                self.allocate(daemon_folder.name)


if __name__ == "__main__":
    mila = Mila()
    mila.allocate_all()
    logging.info("≋ Mila completed allocation pass.")
