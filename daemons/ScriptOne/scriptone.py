"""Script_one: index and query CHAOS log files.

Features:
- CLI with subcommands: index, query, export
- Robust path handling with pathlib
- Improved parsing for multi-word emotions/contexts
- JSON index persistence and CSV export
- Simple interactive query REPL
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
import re
from typing import Dict, List
from tracing import tracer

DEFAULT_VAULT = Path.home() / "Dropbox" / "CHAOS_Logs"
INDEX_FILENAME = "chaos_index.json"

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def parse_entries(text: str) -> List[Dict[str, str]]:
    """Extract all (emotion, context, snippet) entries from a text.

    Recognizes forms like:
      [EMOTION]: sadness
      EMOTION: "very sad"
      [CONTEXT]: some_context_here
    Returns a list of dicts with keys: emotion, context, snippet
    """
    entries: List[Dict[str, str]] = []
    with tracer.start_as_current_span("parse_entries"):
        # Regex loosely matches label followed by value (supports quoted values,
        # multi-word, and optional brackets). Uses DOTALL when capturing snippets.
        emotion_re = re.compile(r"\[?EMOTION\]?:\s*(?:\"(?P<e_q>[^\"]+)\"|(?P<e>[^\n\r]+))", re.IGNORECASE)
        context_re = re.compile(r"\[?CONTEXT\]?:\s*(?:\"(?P<c_q>[^\"]+)\"|(?P<c>[^\n\r]+))", re.IGNORECASE)
        emotions = [m.group('e_q') or m.group('e') for m in emotion_re.finditer(text)]
        contexts = [m.group('c_q') or m.group('c') for m in context_re.finditer(text)]

        # Create pairings in-order; if counts differ, pair as many as possible.
        for e, c in zip(emotions, contexts):
            snippet = extract_snippet_around(text, e, c)
            entries.append({"emotion": e.strip(), "context": c.strip(), "snippet": snippet})

    return entries


def extract_snippet_around(text: str, emotion: str, context: str, radius: int = 80) -> str:
    """Return a short snippet around the first occurrence of emotion or context."""
    idx = text.lower().find(emotion.lower())
    if idx == -1:
        idx = text.lower().find(context.lower())
    if idx == -1:
        return ""
    start = max(0, idx - radius)
    end = min(len(text), idx + radius)
    return text[start:end].strip().replace('\n', ' ')


def build_index(vault: Path, recursive: bool = False) -> List[Dict]:
    """Walk `vault` and parse files into an index list."""
    with tracer.start_as_current_span("build_index"):
        vault = vault.expanduser()
        if not vault.exists():
            raise FileNotFoundError(f"Vault path not found: {vault}")
        files = vault.rglob('*') if recursive else vault.iterdir()
        index: List[Dict] = []

        for p in files:
            if not p.is_file():
                continue
            try:
                text = p.read_text(encoding='utf-8')
            except Exception:
                logging.debug(f"Skipping unreadable file: {p}")
                continue

            entries = parse_entries(text)
            if not entries:
                continue

            stat = p.stat()
            for ent in entries:
                index.append({
                    "file": str(p),
                    "emotion": ent["emotion"],
                    "context": ent["context"],
                    "snippet": ent.get("snippet", ""),
                    "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                })

        return index


def save_index(index: List[Dict], out: Path) -> None:
    with tracer.start_as_current_span("save_index"):
        out_path = out.expanduser()
        out_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), encoding='utf-8')
        logging.info(f"Index saved to {out_path}")


def load_index(path: Path) -> List[Dict]:
    with tracer.start_as_current_span("load_index"):
        p = path.expanduser()
        if not p.exists():
            return []
        return json.loads(p.read_text(encoding='utf-8'))


def summary_by(index: List[Dict], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for e in index:
        counts[e.get(key, '')] = counts.get(e.get(key, ''), 0) + 1
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


def export_csv(index: List[Dict], out: Path) -> None:
    with tracer.start_as_current_span("export_csv"):
        outp = out.expanduser()
        with outp.open('w', newline='', encoding='utf-8') as fh:
            writer = csv.DictWriter(fh, fieldnames=["file", "emotion", "context", "snippet", "mtime"])
            writer.writeheader()
            for row in index:
                writer.writerow(row)
        logging.info(f"Exported CSV to {outp}")


def repl_query(index: List[Dict]) -> None:
    print("Enter simple queries. Examples: emotion=sadness, context=work. 'exit' to quit.")
    while True:
        try:
            q = input('> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not q or q.lower() in ('exit', 'quit'):
            break
        with tracer.start_as_current_span("repl_query"):
            parts = dict(s.split('=', 1) for s in q.split() if '=' in s)
            results = index
            for k, v in parts.items():
                results = [r for r in results if v.lower() in (r.get(k, '') or '').lower()]
            print(f"{len(results)} entries")
            for r in results[:20]:
                print(f"- {r['emotion']} / {r['context']} — {Path(r['file']).name} — {r['mtime']}")


def main(argv=None):
    p = argparse.ArgumentParser(description='Index and query CHAOS logs')
    sub = p.add_subparsers(dest='cmd')

    # index
    si = sub.add_parser('index', help='Scan vault and build index')
    si.add_argument('--vault', '-v', type=Path, default=DEFAULT_VAULT, help='Vault directory')
    si.add_argument('--out', '-o', type=Path, default=Path.home() / INDEX_FILENAME, help='Index output JSON')
    si.add_argument('--recursive', action='store_true', help='Recurse into subdirectories')

    # query
    sq = sub.add_parser('query', help='Query an existing index')
    sq.add_argument('--index', '-i', type=Path, default=Path.home() / INDEX_FILENAME, help='Index JSON to load')
    sq.add_argument('--emotion', '-e', help='Filter by emotion (substring)')
    sq.add_argument('--context', '-c', help='Filter by context (substring)')

    # export
    se = sub.add_parser('export', help='Export index to CSV')
    se.add_argument('--index', '-i', type=Path, default=Path.home() / INDEX_FILENAME, help='Index JSON to load')
    se.add_argument('--out', '-o', type=Path, required=True, help='CSV output path')

    args = p.parse_args(argv)

    if args.cmd == 'index':
        idx = build_index(args.vault, recursive=args.recursive)
        save_index(idx, args.out)
        # Print short report
        logging.info(f"Indexed {len(idx)} entries")
        emo = summary_by(idx, 'emotion')
        ctx = summary_by(idx, 'context')
        print("Top emotions:")
        for k, v in list(emo.items())[:10]:
            print(f"  {k}: {v}")
        print("Top contexts:")
        for k, v in list(ctx.items())[:10]:
            print(f"  {k}: {v}")

    elif args.cmd == 'query':
        idx = load_index(args.index)
        if args.emotion:
            idx = [r for r in idx if args.emotion.lower() in r.get('emotion', '').lower()]
        if args.context:
            idx = [r for r in idx if args.context.lower() in r.get('context', '').lower()]
        print(f"Matches: {len(idx)} entries")
        for r in idx[:50]:
            print(f"{r['emotion']} / {r['context']} — {Path(r['file']).name} — {r['mtime']}")

    elif args.cmd == 'export':
        idx = load_index(args.index)
        export_csv(idx, Path(args.out))

    else:
        # No command — start interactive REPL using the default index if present
        idx = load_index(Path.home() / INDEX_FILENAME)
        if not idx:
            print("No index found. Run 'index' first, e.g. 'script_one.py index --vault ~/Dropbox/CHAOS_Logs'")
            return
        repl_query(idx)


if __name__ == '__main__':
    main()
