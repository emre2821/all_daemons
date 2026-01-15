import argparse
import json
from pathlib import Path

"""Label chaos threads with tags from a word bank.

Usage examples:
    # Use defaults relative to the repository root
    python Label/label.py

    # Supply custom locations relative to the base directory
    python Label/label.py --base-dir /data/daemons \ --input-dir Rhea/outputs/Janvier/chaos_threads \ --output-dir Rhea/outputs/Label/labeled \ --word-bank Label/LabelWordBank.chaos

    # Override with absolute paths
    python Label/label.py --input-dir /tmp/in --output-dir /tmp/out
"""

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT_DIR = Path("Rhea/outputs/Janvier/chaos_threads")
DEFAULT_OUTPUT_DIR = Path("Rhea/outputs/Label/labeled")
DEFAULT_WORD_BANK_FILE = Path("Label/LabelWordBank.chaos")


def resolve_path(path_value: Path, base_dir: Path) -> Path:

    """Return an absolute path, resolving relative paths against a base directory.

    The input path supports tilde expansion (e.g., ~/data).
    """

    # Expand user home (~, ~user) before resolving relative paths
    path_value = path_value.expanduser()

    return path_value if path_value.is_absolute() else base_dir / path_value


def resolve_path(path_value: Path, base_dir: Path) -> Path:

    """Return an absolute path, resolving relative paths against a base directory."""

    return path_value if path_value.is_absolute() else base_dir / path_value


def load_wordbank(word_bank_file: Path):

    if not word_bank_file.exists():
        print(f"⚠️ Word bank not found at {word_bank_file}; continuing without labels.")
        return {}
    with word_bank_file.open("r", encoding="utf-8") as f:
        return json.load(f)

def match_labels(text, wordbank):

    tags = []
    text_l = text.lower()
    for label, words in wordbank.items():
        for w in words:
            if w.lower() in text_l:
                tags.append(label)
                break
    return tags

def process_file(path, wordbank):

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    title = data.get("title", "Untitled")
    date = data.get("date", "unknown_date")
    nodes = data.get("nodes", [])
    labels = set()
    for node in nodes:
        labels.update(match_labels(node.get("content", ""), wordbank))
    return {"title": title, "date": date, "labels": list(labels)}


def parse_args():

    parser = argparse.ArgumentParser(description="Label chaos threads using a word bank.")
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=REPO_ROOT,
        help="Base directory used to resolve relative paths (defaults to repository root).",
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=DEFAULT_INPUT_DIR,
        help="Directory containing .chaos files to label (relative paths resolve from --base-dir).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination for labeled files (relative paths resolve from --base-dir).",
    )
    parser.add_argument(
        "--word-bank",
        type=Path,
        default=DEFAULT_WORD_BANK_FILE,
        help="Path to the LabelWordBank.chaos file (relative paths resolve from --base-dir).",
    )
    args = parser.parse_args()

    base_dir = args.base_dir.resolve()
    args.input_dir = resolve_path(args.input_dir, base_dir).resolve()
    args.output_dir = resolve_path(args.output_dir, base_dir).resolve()
    args.word_bank = resolve_path(args.word_bank, base_dir).resolve()
    return args

def main():

    args = parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    if not args.input_dir.exists():
        print(f"⚠️ Input directory {args.input_dir} does not exist; nothing to process.")
        return

    wordbank = load_wordbank(args.word_bank)

    for path in sorted(args.input_dir.glob("*.chaos")):
        if not path.is_file():
            continue
        result = process_file(path, wordbank)
        outname = f"{path.stem}_labels.chaos"
        outpath = args.output_dir / outname
        with outpath.open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"✅ Label tagged {path.name} -> {outname}")

if __name__ == "__main__":
    main()
