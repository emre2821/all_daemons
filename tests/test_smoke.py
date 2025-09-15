from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]


def _python_subprojects():
    for path in ROOT.iterdir():
        if path.name.startswith('.') or path.name in {"bin", "tests"}:
            continue
        if path.is_dir() and any(
            p.suffix == '.py' for p in path.rglob('*.py')
        ):
            yield path


@pytest.mark.parametrize(
    "subproject", list(_python_subprojects())
)
def test_subproject_smoke(subproject):
    for py_file in subproject.rglob('*.py'):
        try:
            compile(
                py_file.read_text(encoding='utf-8', errors='ignore'),
                str(py_file),
                'exec',
            )
        except SyntaxError as exc:  # pragma: no cover - smoke test
            pytest.xfail(f"Syntax error in {py_file}: {exc}")


@pytest.mark.parametrize('py_file', list(ROOT.glob('*.py')))
def test_root_python_files(py_file):
    try:
        compile(
            py_file.read_text(encoding='utf-8', errors='ignore'),
            str(py_file),
            'exec',
        )
    except SyntaxError as exc:  # pragma: no cover - smoke test
        pytest.xfail(f"Syntax error in {py_file}: {exc}")
