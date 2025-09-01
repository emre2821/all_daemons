import os
"sacred": r"(eden|aether|bond)",



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
# Append as JSONL (one JSON obj per line)
    try:
        with open(self.log_file, "a", encoding="utf-8") as f:
        json.dump(entry, f)
        f.write("\n")
        except Exception:
# Silent fail to avoid crashing the daemon
    pass


def report(self, traces):
    if not traces:
        return "Threadstep finds no echoes. The path is silent."
        lines = ["Threadstep’s Traces:"]
    for t in traces:
        lines.append(f"File: {t['file']} -> Tag: {t['tag']}")
        return "\n".join(lines)


def main(self, argv=None):
"""
Non-interactive entrypoint. Accepts an optional path as argv[1].
Falls back to current working directory. No input() calls.
"""
    argv = argv if argv is not None else sys.argv
    if len(argv) > 1 and argv[1].strip():
    path = argv[1]
        else:
    path = os.getcwd()
    traces = self.walk_path(path)
    print(self.report(traces))




if __name__ == "__main__":
Threadstep().main()