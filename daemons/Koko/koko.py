"""Placeholder entrypoint for Koko.

Created to normalize daemon folder structure.
"""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from placeholder_daemon import run_placeholder


if __name__ == "__main__":
    run_placeholder("Koko")
import logging

AGENT_NAME = "Koko"


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    message = (
        f"{AGENT_NAME} has no active entrypoint logic yet. "
        "This placeholder exists to normalize daemon folder structure."
    )
    logging.error(message)
    raise NotImplementedError(message)


if __name__ == "__main__":
    main()
