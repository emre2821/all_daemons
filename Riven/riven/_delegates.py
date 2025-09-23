"""Helpers for loading companion daemon scripts lazily."""

from __future__ import annotations

from contextlib import contextmanager
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import ModuleType
from typing import Iterator, Mapping
import sys

_MISSING = object()
_MODULE_CACHE: dict[tuple[str, Path], ModuleType] = {}

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_with_injections(label: str, path: Path, inject: Mapping[str, object] | None) -> ModuleType:
    spec = spec_from_file_location(f"riven.delegates.{label}", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {path}")
    module = module_from_spec(spec)

    injected: list[tuple[str, object]] = []
    if inject:
        for name, stub in inject.items():
            if name not in sys.modules:
                sys.modules[name] = stub  # type: ignore[assignment]
                injected.append((name, _MISSING))
            else:
                injected.append((name, sys.modules[name]))
                sys.modules[name] = stub  # type: ignore[assignment]
    try:
        spec.loader.exec_module(module)
    finally:
        for name, original in reversed(injected):
            if original is _MISSING:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = original
    return module


def load_module(
    label: str,
    path: Path,
    inject: Mapping[str, object] | None = None,
    *,
    force_inject: bool = False,
) -> ModuleType:
    """Load a daemon script from ``path`` and cache the resulting module."""

    key = (label, path)
    if key in _MODULE_CACHE and not force_inject:
        return _MODULE_CACHE[key]

    try:
        if force_inject:
            if not inject:
                raise ValueError("force_inject requires an inject mapping")
            module = _load_with_injections(label, path, inject)
        else:
            module = _load_with_injections(label, path, None)
    except ModuleNotFoundError as exc:
        if not inject or exc.name not in inject:  # type: ignore[arg-type]
            raise
        module = _load_with_injections(label, path, inject)

    _MODULE_CACHE[key] = module
    return module


@contextmanager
def temporary_attributes(module: ModuleType, **attrs) -> Iterator[ModuleType]:
    """Temporarily assign attributes on ``module`` inside the context."""

    sentinel = object()
    originals: dict[str, object] = {}
    for name, value in attrs.items():
        originals[name] = getattr(module, name, sentinel)
        setattr(module, name, value)
    try:
        yield module
    finally:
        for name, original in originals.items():
            if original is sentinel:
                delattr(module, name)
            else:
                setattr(module, name, original)
