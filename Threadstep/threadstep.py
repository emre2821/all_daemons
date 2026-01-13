from __future__ import annotations
import os
import re
import json
import argparse
from datetime import datetime
from pathlib import Path


class Threadstep:
    def __init__(self, log_file: Path | None = None):

        self.patterns = {
            "sacred": r"(eden|aether|bond)",
            "code": r"(daemon|script|digitari)",
        }
        root = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
        logs = root / "all_daemons" / "_logs"
        logs.mkdir(parents=True, exist_ok=True)
        self.log_file = log_file or (logs / "Threadstep.log")

    def walk_path(self, path: str):

        traces = []
        for root, _, files in os.walk(path):
            for file in files:
                filepath = os.path.join(root, file)
                for tag, pattern in self.patterns.items():
                    if re.search(pattern, filepath, re.IGNORECASE):
                        traces.append({"file": filepath, "tag": tag})
                        self._log_trace(filepath, tag)
        return traces

    def _log_trace(self, filepath: str, tag: str):

        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "file": filepath,
            "tag": tag,
        }
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                json.dump(entry, f)
                f.write("\n")
        except Exception:
            pass

    def report(self, traces):

        if not traces:
            return "Threadstep finds no echoes. The path is silent."
        lines = ["Threadstep's Traces:"]
        for t in traces:
            lines.append(f"File: {t['file']} -> Tag: {t['tag']}")
        return "\n".join(lines)

    @staticmethod
    def describe() -> dict:

        return {
            "name": "Threadstep",
            "role": "Path tracer (pattern-based)",
            "inputs": {"scope": "Directory to scan"},
            "outputs": {"log": "_logs/Threadstep.log (JSONL)"},
            "flags": ["--scope"],
        }

    @staticmethod
    def healthcheck() -> dict:

        try:
            root = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
            logs = root / "all_daemons" / "_logs"
            logs.mkdir(parents=True, exist_ok=True)
            (logs / "Threadstep.log").touch()
            return {"status": "ok", "notes": "log writable"}
        except Exception as e:
            return {"status": "warn", "notes": f"log write warn: {e}"}

    def main(self, argv=None):

        parser = argparse.ArgumentParser(description="Threadstep - Path tracer")
        parser.add_argument("--scope", help="Directory to scan (defaults to CWD)")
        args = parser.parse_args(argv)
        path = args.scope or os.getcwd()
        traces = self.walk_path(path)
        print(self.report(traces))


if __name__ == "__main__":
    Threadstep().main()
