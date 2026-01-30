from pathlib import Path

from .Rhea import rhea_main


def _make_daemon(path: Path, name: str = "Echo", *, create_main: bool = False, create_primary: bool = True) -> None:
    daemon_dir = path / name
    daemon_dir.mkdir(parents=True, exist_ok=True)
    if create_primary:
        (daemon_dir / f"{name.lower()}.py").write_text("# daemon placeholder\n")
    if create_main:
        (daemon_dir / f"{name.lower()}_main.py").write_text("# daemon main placeholder\n")


def test_registry_path_is_anchored_to_rhea_dir():
    rhea_dir = Path(rhea_main.__file__).resolve().parent

    assert rhea_main.RHEA_DIR == rhea_dir
    assert rhea_main.REGISTRY_PATH.parent == rhea_dir


def test_resolve_root_defaults_to_project_root():
    result = rhea_main.resolve_root(env={})
    assert result == rhea_main.PROJECT_ROOT


def test_resolve_root_prefers_env(tmp_path):
    env = {"EDEN_ROOT": str(tmp_path)}
    assert rhea_main.resolve_root(env=env) == tmp_path


def test_resolve_root_warns_when_env_path_missing(capsys, tmp_path):
    missing_root = tmp_path / "ghost_root"
    env = {"EDEN_ROOT": str(missing_root)}

    result = rhea_main.resolve_root(env=env)

    captured = capsys.readouterr().out
    assert str(missing_root) in captured
    assert "does not exist" in captured
    assert result == rhea_main.PROJECT_ROOT


def test_resolve_daemon_dir_prefers_env_when_valid(tmp_path):
    env_daemons = tmp_path / "custom_daemons"
    _make_daemon(env_daemons, "Custom")
    env = {"EDEN_DAEMONS_DIR": str(env_daemons)}

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env=env)
    assert result == env_daemons


def test_resolve_daemon_dir_handles_file_env_path(tmp_path):
    file_candidate = tmp_path / "not_a_dir"
    file_candidate.write_text("not a dir")
    _make_daemon(tmp_path, "Live")

    env = {"EDEN_DAEMONS_DIR": str(file_candidate)}

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env=env)

    assert result == tmp_path


def test_resolve_daemon_dir_prefers_core_agents(tmp_path):
    core_agents = tmp_path / "01_Daemon_Core_Agents"
    _make_daemon(core_agents, "Core")

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env={})

    assert result == core_agents


def test_resolve_daemon_dir_prefers_daemons_when_core_absent(tmp_path):
    daemons_dir = tmp_path / "daemons"
    _make_daemon(daemons_dir, "Alt")

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env={})

    assert result == daemons_dir


def test_resolve_daemon_dir_recognizes_main_variant(tmp_path):
    _make_daemon(tmp_path, name="Echo", create_main=True, create_primary=False)

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env={})

    assert result == tmp_path


def test_resolve_daemon_dir_falls_back_to_root_with_daemons(tmp_path):
    _make_daemon(tmp_path, "CoreOne")

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env={})
    assert result == tmp_path


def test_resolve_daemon_dir_ignores_empty_candidates(tmp_path):
    empty_candidate = tmp_path / "empty_daemons"
    empty_candidate.mkdir()
    _make_daemon(tmp_path, "Live")

    env = {"EDEN_DAEMONS_DIR": str(empty_candidate)}
    result = rhea_main.resolve_daemon_dir(root=tmp_path, env=env)
    assert result == tmp_path


def test_resolve_daemon_dir_returns_root_when_no_candidates(tmp_path):
    env = {"EDEN_DAEMONS_DIR": str(tmp_path / "missing_daemons")}

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env=env)

    assert result == tmp_path
