"""Shared helper for placeholder daemon entrypoints."""

from __future__ import annotations

import logging
from typing import Optional


DEFAULT_LOG_LEVEL = logging.INFO


def configure_placeholder_logging(name: str, level: int = DEFAULT_LOG_LEVEL) -> logging.Logger:
    """Configure logging for placeholder entrypoints when no handlers exist."""
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        logging.basicConfig(level=level, format=f"[{name}] %(levelname)s: %(message)s")
    return logging.getLogger(name)


def run_placeholder(name: str, *, message: Optional[str] = None) -> None:
    """Log a minimal placeholder entrypoint message."""
    logger = configure_placeholder_logging(name)
    if message is None:
        message = f"{name} placeholder entrypoint invoked."
    logger.info(message)
