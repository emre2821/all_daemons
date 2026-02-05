# rhea.py (scaffolded)
from pathlib import Path

class Rhea:
    def __init__(self, eden_root: Path):
        self.eden_root = Path(eden_root)
        self.logs_dir = self.eden_root / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        # simple placeholders; your real impl may differ
        self.teams = {}
        self.pairs = {}
        self.procs = {}

    def reload(self):
        # load configs here (scaffold placeholder)
        return True

    def status_rows(self):
        # (tier, name, state, path)
        return []

    def start_daemon(self, name: str):
        return

    def stop_daemon(self, name: str):
        return
