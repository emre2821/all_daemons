from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLS_SCRIPTS = REPO_ROOT / "shared" / "Daemon_tools" / "scripts"
for path in (REPO_ROOT, TOOLS_SCRIPTS):
    if str(path) not in sys.path:
        sys.path.append(str(path))

from Daemon_tools.scripts.eden_paths import rhea_root  # noqa: E402

INPUT_DIR = rhea_root() / "outputs" / "Janvier" / "chaos_threads"
OUTPUT_DIR = rhea_root() / "outputs" / "Parsley" / "classified"

SACRED_KEYWORDS = ["DREAMBEARER", "KIN", "AGENT", "sacred", "do_not_purge"]
PURGE_KEYWORDS = ["temp", "debug", "scratch", "purge"]


def classify(text: str) -> str:

    lowered = text.lower()
    if any(k.lower() in lowered for k in SACRED_KEYWORDS):
        return "sacred"
    if any(k.lower() in lowered for k in PURGE_KEYWORDS):
        return "purge"
    return "review"


def process_file(path: Path) -> str:

    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    verdicts = [classify(n.get("content", "")) for n in nodes]
    if "sacred" in verdicts:
        return "sacred"
    if verdicts and all(v == "purge" for v in verdicts):
        return "purge"
    return "review"


def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT_DIR.exists():
        print(f"⚠️ Input directory not found: {INPUT_DIR}")
        return

    for chaos_file in INPUT_DIR.glob("*.chaos"):
        result = process_file(chaos_file)
        outname = chaos_file.name.replace(".chaos", f"_{result}.chaos")
        outpath = OUTPUT_DIR / outname
        outpath.write_text(
            json.dumps({"file": chaos_file.name, "classification": result}, indent=2),
            encoding="utf-8",
        )
        print(f"✅ Parsley classified {chaos_file.name} as {result}")


if __name__ == "__main__":
    main()
