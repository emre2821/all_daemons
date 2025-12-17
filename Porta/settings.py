"""Configuration helpers for the Porta daemon.

Porta supports overriding its default directories through environment variables:

* ``PORTA_SOURCE_DIR`` - directory to watch for new files
* ``PORTA_DEST_DIR`` - directory where files are moved

If the variables are unset, the Windows-friendly defaults below are used.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_SOURCE_DIR = Path(r"C:\Users\emmar\Desktop\Master_EdenOS\to_be_placed")
DEFAULT_DEST_DIR = Path(r"C:\Users\emmar\Documents\Obsidian Vault\Eden\07_Vas_Saves")
DEFAULT_SUPPORTED_EXTENSIONS = (".asciidoc", ".py", ".md")


@dataclass(frozen=True)
class PortaSettings:
    source_dir: Path
    dest_dir: Path
    supported_extensions: tuple[str, ...]


def _normalize_extensions(extensions: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(ext.lower() for ext in (extensions or DEFAULT_SUPPORTED_EXTENSIONS))


def load_settings(
    *,
    source_dir: str | os.PathLike[str] | None = None,
    dest_dir: str | os.PathLike[str] | None = None,
    supported_extensions: Iterable[str] | None = None,
) -> PortaSettings:
    """Create a :class:`PortaSettings` instance from env vars or overrides."""

    resolved_source = Path(source_dir or os.getenv("PORTA_SOURCE_DIR", DEFAULT_SOURCE_DIR))
    resolved_dest = Path(dest_dir or os.getenv("PORTA_DEST_DIR", DEFAULT_DEST_DIR))

    return PortaSettings(
        source_dir=resolved_source,
        dest_dir=resolved_dest,
        supported_extensions=_normalize_extensions(supported_extensions),
    )
