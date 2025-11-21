from __future__ import annotations
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

try:
    from .eden_paths import daemons_root, daemon_dir
except Exception:
    # Allow usage as a plain script
    import sys as _sys
    from pathlib import Path as _Path
    _HERE = _Path(__file__).resolve().parent
    if str(_HERE) not in _sys.path:
        _sys.path.append(str(_HERE))
    from eden_paths import daemons_root, daemon_dir  # type: ignore


SKIP_FOLDERS = {
    ".git", ".venv", ".vscode", "Daemon_tools", "CODE_REPORTS", "Digitari_v0_1",
    "Rhea", "specialty_folders", "_logs", "_template", "bin", "tools",
    # Archived / app-like, not daemons
    "Aethercore", "Cradle", "archived_tools", "RitualGUI"
}


KNOWN_SAFETY: Dict[str, str] = {
    # destructive = may delete or move user files aggressively
    "Scorchick": "destructive",
    "AshFall": "destructive",
    "Snatch": "destructive",
    # mutating = converts or rewrites files
    "Archive": "mutating",
    "Handel": "mutating",
}


@dataclass
class DaemonInfo:
    name: str
    role: str
    safety_level: str
    status: str
    folder: str
    script: Optional[str] = None
    manifest: Optional[Dict[str, str]] = None

    def to_dict(self):
        return asdict(self)


def _read_json(path: Path) -> Optional[dict]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _manifest_for(name: str, base: Path) -> Dict[str, str]:
    # Saphira naming pattern: <name>.<daemon_*.json>
    out: Dict[str, str] = {}
    for suffix in ("daemon_role.json", "daemon_function.json", "daemon_mirror.json", "daemon_voice.json"):
        p = base / f"{name.lower()}.{suffix}"
        if p.exists():
            out[suffix] = str(p)
    return out


def discover() -> List[DaemonInfo]:
    root = daemons_root()
    infos: List[DaemonInfo] = []

    for child in sorted([p for p in root.iterdir() if p.is_dir()], key=lambda x: x.name.lower()):
        if child.name.startswith(".") or child.name == "__pycache__":
            continue
        if child.name in SKIP_FOLDERS:
            continue

        script_dir = child / "scripts"
        primary_script = script_dir / f"{child.name.lower()}.py"
        script_path: Optional[Path] = None
        if primary_script.exists():
            script_path = primary_script
        else:
            # fallback: any .py under scripts
            cands = list(script_dir.glob("*.py")) if script_dir.exists() else []
            if cands:
                script_path = cands[0]

        manifest = _manifest_for(child.name, child)
        role = "Unknown"
        if "daemon_role.json" in "|".join(manifest.keys()):
            # try to extract role/description
            for k, v in manifest.items():
                if k.endswith("daemon_role.json"):
                    data = _read_json(Path(v))
                    if isinstance(data, dict):
                        role = data.get("role") or data.get("name") or role
        # else try mirror/profile
        if role == "Unknown":
            for k, v in manifest.items():
                data = _read_json(Path(v))
                if isinstance(data, dict):
                    role = data.get("description") or data.get("name") or role

        safety = KNOWN_SAFETY.get(child.name, "normal")
        status = "ready" if script_path else ("meta-only" if manifest else "missing")

        infos.append(
            DaemonInfo(
                name=child.name,
                role=role,
                safety_level=safety,
                status=status,
                folder=str(child),
                script=str(script_path) if script_path else None,
                manifest=manifest or None,
            )
        )

    return infos


def describe(name: str) -> Optional[Dict]:
    folder = daemon_dir(name)
    if not folder.exists():
        return None
    info = [d for d in discover() if d.name.lower() == name.lower()]
    return info[0].to_dict() if info else None
