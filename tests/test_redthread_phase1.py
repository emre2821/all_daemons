#!/usr/bin/env python3
"""
Test Harness: Red Thread Phase 1
Runs Sheele → Briar → Janvier → Codexa in sequence.

ROOT can be configured via the REDTHREAD_ROOT environment variable or the
``--root`` CLI flag. When not provided, the repository root is inferred from
this file's location.
"""

import argparse
import os
import subprocess
from pathlib import Path
from typing import Optional, Sequence

import pytest

EXPECTED_DAEMONS: Sequence[str] = ("Sheele", "Briar", "Janvier", "Codexa")


def get_root(cli_root: Optional[str]) -> Path:
    if cli_root:
        return Path(cli_root).expanduser().resolve()

    env_root = os.getenv("REDTHREAD_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()

    return infer_repository_root()


def infer_repository_root() -> Path:
    """Infer the repository root by walking parents and locating a .git marker."""

    for candidate in Path(__file__).resolve().parents:
        if (candidate / ".git").is_dir():
            return candidate

    raise RuntimeError(
        "Unable to infer repository root: no .git directory found in parent paths."
    )


def validate_root(root: Path, expected_daemons: Sequence[str]) -> Path:
    if not root.exists():
        raise ValueError(f"Configured root {root} does not exist.")
    if not root.is_dir():
        raise ValueError(f"Configured root {root} is not a directory.")

    missing_daemons = [daemon for daemon in expected_daemons if not (root / daemon).is_dir()]
    if missing_daemons:
        missing_list = ", ".join(sorted(missing_daemons))
        raise ValueError(
            "Configured root is missing expected daemon directories: "
            f"{missing_list}"
        )

    return root


def run_daemon(name: str, script: str, root: Path) -> None:
    print(f"\n=== Running {name} ===")
    result = subprocess.run(
        ["python", str(root / name / script)],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.stderr:
        print("[stderr]", result.stderr)

    if result.returncode != 0:
        raise AssertionError(
            f"Daemon {name} failed with non-zero exit code {result.returncode}.\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def main(root: Path) -> None:
    # Step 1: Sheele → JSON slices
    run_daemon("Sheele", "sheele.py", root)

    # Step 2: Briar → TXT transcripts
    run_daemon("Briar", "briar.py", root)

    # Step 3: Janvier → CHAOS files
    run_daemon("Janvier", "janvier.py", root)

    # Step 4: Codexa → code extraction
    run_daemon("Codexa", "codexa.py", root)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the Red Thread Phase 1 daemons sequentially."
    )
    parser.add_argument(
        "--root",
        type=str,
        default=None,
        help="Root directory containing the daemon scripts "
        "(defaults to repository root or REDTHREAD_ROOT).",
    )
    args = parser.parse_args()
    main(validate_root(get_root(args.root), EXPECTED_DAEMONS))


# --- Tests ------------------------------------------------------------------


def test_get_root_prefers_cli_root_over_env_and_default(monkeypatch, tmp_path):
    cli_root = tmp_path / "cli_root"
    env_root = tmp_path / "env_root"
    monkeypatch.setenv("REDTHREAD_ROOT", str(env_root))

    result = get_root(str(cli_root))

    assert result == cli_root.expanduser().resolve()


def test_get_root_uses_env_when_cli_is_none(monkeypatch, tmp_path):
    cli_root = None
    env_root = tmp_path / "env_root"
    monkeypatch.setenv("REDTHREAD_ROOT", str(env_root))

    result = get_root(cli_root)

    assert result == env_root.expanduser().resolve()


def test_get_root_uses_default_when_cli_and_env_missing(monkeypatch):
    cli_root = None
    monkeypatch.delenv("REDTHREAD_ROOT", raising=False)

    result = get_root(cli_root)
    expected = infer_repository_root()

    assert result == expected


def test_get_root_expands_user_in_cli_root(tmp_path, monkeypatch):
    monkeypatch.delenv("REDTHREAD_ROOT", raising=False)

    home = Path("~").expanduser()
    cli_root = Path("~") / "redthread_cli_root"

    result = get_root(str(cli_root))

    assert result == (home / "redthread_cli_root").resolve()


def test_get_root_expands_user_in_env_root(monkeypatch):
    monkeypatch.delenv("REDTHREAD_ROOT", raising=False)

    home = Path("~").expanduser()
    env_root = Path("~") / "redthread_env_root"
    monkeypatch.setenv("REDTHREAD_ROOT", str(env_root))

    result = get_root(None)

    assert result == (home / "redthread_env_root").resolve()


def test_validate_root_raises_for_missing_directory(tmp_path):
    nonexistent = tmp_path / "does_not_exist"

    with pytest.raises(ValueError) as excinfo:
        validate_root(nonexistent, EXPECTED_DAEMONS)

    assert "does not exist" in str(excinfo.value)


def test_validate_root_requires_expected_daemons(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    (root / "Sheele").mkdir()

    with pytest.raises(ValueError) as excinfo:
        validate_root(root, EXPECTED_DAEMONS)

    message = str(excinfo.value)
    for daemon in ("Briar", "Janvier", "Codexa"):
        assert daemon in message


def test_run_daemon_success(monkeypatch, tmp_path):
    called = {}

    def fake_run(cmd, capture_output, text):
        called["cmd"] = cmd

        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)
    run_daemon("TestDaemon", "script.py", tmp_path)

    assert called["cmd"] == ["python", str(tmp_path / "TestDaemon" / "script.py")]


def test_run_daemon_failure(monkeypatch, tmp_path):
    def fake_run(cmd, capture_output, text):
        class Result:
            returncode = 1
            stdout = "some stdout"
            stderr = "some stderr"

        return Result()

    monkeypatch.setattr(subprocess, "run", fake_run)

    with pytest.raises(AssertionError) as excinfo:
        run_daemon("FailingDaemon", "script.py", tmp_path)

    msg = str(excinfo.value)
    assert "non-zero exit code" in msg
    assert "FailingDaemon" in msg
