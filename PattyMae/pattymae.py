from __future__ import annotations

import shutil
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from Daemon_tools.scripts.eden_paths import rhea_root  # noqa: E402

INPUT_DIR = rhea_root() / "outputs" / "Janvier" / "chaos_threads"
OUTPUT_ROOT = rhea_root() / "PattyMae" / "organized"


def ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def categorize(fname: str) -> str:
    if fname.endswith("_labels.chaos"):
        return "Labeled"
    if fname.endswith("_summons.chaos"):
        return "Summons"
    if fname.endswith("_sacred.chaos"):
        return "Sacred"
    if fname.endswith("_purge.chaos"):
        return "Purge"
    return "Unsorted"


def main():
    if not INPUT_DIR.exists():
        print(f"⚠️ Input directory not found: {INPUT_DIR}")
        return

    for chaos_file in INPUT_DIR.glob("*.chaos"):
        category = categorize(chaos_file.name)
        dest_dir = OUTPUT_ROOT / category
        ensure_dir(dest_dir)
        shutil.copy2(chaos_file, dest_dir / chaos_file.name)
        print(f"✅ PattyMae sorted {chaos_file.name} -> {category}/")


if __name__ == "__main__":
    main()
