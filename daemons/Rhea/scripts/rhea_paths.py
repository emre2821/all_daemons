from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RheaPaths:
    rhea_dir: Path
    config_dir: Path
    registry_path: Path
    scripts_configs_dir: Path
    daemon_lists_dir: Path


def resolve_rhea_paths(script_file: Path) -> RheaPaths:
    script_dir = script_file.resolve().parent
    scripts_dir = (
        script_dir
        if script_dir.name == "scripts"
        else next((parent for parent in script_dir.parents if parent.name == "scripts"), None)
    )
    rhea_dir = scripts_dir.parent if scripts_dir is not None else script_dir
    config_dir = rhea_dir / "config"
    return RheaPaths(
        rhea_dir=rhea_dir,
        config_dir=config_dir,
        registry_path=config_dir / "rhea_registry.json",
        scripts_configs_dir=(scripts_dir or rhea_dir / "scripts") / "configs",
        daemon_lists_dir=config_dir / "daemon_lists",
    )


def ensure_rhea_dirs(paths: RheaPaths) -> None:
    paths.config_dir.mkdir(parents=True, exist_ok=True)
    paths.scripts_configs_dir.mkdir(parents=True, exist_ok=True)
    paths.daemon_lists_dir.mkdir(parents=True, exist_ok=True)
