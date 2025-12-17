"""PattyMae sorts CHAOS files into labeled buckets.

Paths can be configured via CLI flags or environment variables:
- PATTYMAE_SOURCE_DIR: source directory containing CHAOS files
- PATTYMAE_DEST_DIR: destination root for sorted output
If not provided, defaults under the repository root are used.
"""

import argparse
import logging
import os
import shutil
from pathlib import Path

ENV_SOURCE = "PATTYMAE_SOURCE_DIR"
ENV_DEST = "PATTYMAE_DEST_DIR"
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_DIR = REPO_ROOT / "Rhea" / "outputs" / "Janvier" / "chaos_threads"
DEFAULT_DEST_DIR = REPO_ROOT / "Rhea" / "PattyMae" / "organized"


def ensure_dir(path: Path) -> None:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sort CHAOS files into labeled buckets.")
    parser.add_argument(
        "--source",
        help=f"Source directory containing CHAOS files (env: {ENV_SOURCE})",
    )
    parser.add_argument(
        "--dest",
        help=f"Destination root for sorted output (env: {ENV_DEST})",
    )
    return parser.parse_args()


def resolve_paths(args: argparse.Namespace) -> tuple[Path, Path]:
    source = Path(args.source) if args.source else Path(os.environ.get(ENV_SOURCE, DEFAULT_SOURCE_DIR))
    dest = Path(args.dest) if args.dest else Path(os.environ.get(ENV_DEST, DEFAULT_DEST_DIR))
    return source, dest


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[PattyMae] %(levelname)s: %(message)s")
    args = parse_args()
    source_dir, dest_root = resolve_paths(args)

    if not source_dir.exists():
        logging.warning("Source directory %s is missing; nothing to sort.", source_dir)
        return

    ensure_dir(dest_root)

    for fname in os.listdir(source_dir):
        if not fname.endswith(".chaos"):
            continue
        category = categorize(fname)
        dest_dir = dest_root / category
        ensure_dir(dest_dir)
        shutil.copy2(source_dir / fname, dest_dir / fname)
        logging.info("Sorted %s -> %s/", fname, category)


if __name__ == "__main__":
    main()
