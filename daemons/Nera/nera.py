"""Placeholder entrypoint for Nera.

Created to normalize daemon folder structure.
"""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from placeholder_daemon import run_placeholder


if __name__ == "__main__":
    run_placeholder("Nera")
