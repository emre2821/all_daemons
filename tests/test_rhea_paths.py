from pathlib import Path

from Rhea import rhea_main


def _make_daemon(path: Path, name: str = "Echo") -> None:
    daemon_dir = path / name
    daemon_dir.mkdir(parents=True, exist_ok=True)
    (daemon_dir / f"{name.lower()}.py").write_text("# daemon placeholder\n")


def test_resolve_root_defaults_to_project_root():
    result = rhea_main.resolve_root(env={})
    assert result == rhea_main.PROJECT_ROOT


def test_resolve_root_prefers_env(tmp_path):
    env = {"EDEN_ROOT": str(tmp_path)}
    assert rhea_main.resolve_root(env=env) == tmp_path


def test_resolve_daemon_dir_prefers_env_when_valid(tmp_path):
    env_daemons = tmp_path / "custom_daemons"
    _make_daemon(env_daemons, "Custom")
    env = {"EDEN_DAEMONS_DIR": str(env_daemons)}

    result = rhea_main.resolve_daemon_dir(root=tmp_path, env=env)
    assert result == env_daemons


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
