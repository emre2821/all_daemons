from __future__ import annotations

from pathlib import Path
from typing import Any

from ._delegates import REPO_ROOT, load_module, temporary_attributes


class _PsutilStub:
    @staticmethod
    def cpu_percent(interval: float = 0.0) -> float:
        return 0.0

    @staticmethod
    def virtual_memory() -> Any:  # pragma: no cover - minimal shim
        class _Mem:
            percent = 0.0

        return _Mem()


def deliver_messages(
    inbox: Path = Path("aether_inbox"),
    outbox: Path = Path("aether_outbox"),
    processed: Path = Path("aether_delivered"),
) -> None:
    """Carry messages by delegating to Maribel's shared courier."""

    inbox.mkdir(parents=True, exist_ok=True)
    outbox.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)

    module = load_module(
        "maribel",
        REPO_ROOT / "Maribel" / "scripts" / "maribel.py",
        inject={"psutil": _PsutilStub()},
        force_inject=True,
    )

    attrs: dict[str, Any] = {
        "INBOX": str(inbox),
        "OUTBOX": str(outbox),
        "PROCESSED": str(processed),
    }

    with temporary_attributes(module, **attrs):
        module.deliver_messages()
