#!/usr/bin/env python3
"""
Test Harness: Red Thread Phase 1
Runs Sheele → Briar → Janvier → Codexa in sequence.

ROOT can be configured via the REDTHREAD_ROOT environment variable or the
``--root`` CLI flag. When not provided, the repository root is inferred from
this file's location.
"""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Optional


def get_root(cli_root: Optional[str]) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()

    env_root = os.getenv("REDTHREAD_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return Path(__file__).resolve().parents[1]


def run_daemon(name: str, script: str, root: Path) -> None:
    print(f"\n=== Running {name} ===")
    result = subprocess.run(
        ["python", str(root / name / script)],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("[stderr]", result.stderr)


def main(root: Path) -> None:
    # Step 1: Sheele → JSON slices
    run_daemon("Sheele", "sheele.py", root)

    # Step 2: Briar → TXT transcripts
    run_daemon("Briar", "briar.py", root)

    # Step 3: Janvier → CHAOS files
    run_daemon("Janvier", "janvier.py", root)

    # Step 4: Codexa → code extraction
    run_daemon("Codexa", "codexa.py", root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Red Thread Phase 1 daemons sequentially."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Root directory containing the daemon scripts "
        "(defaults to repository root or REDTHREAD_ROOT).",
    )
    args = parser.parse_args()
    main(get_root(args.root))
