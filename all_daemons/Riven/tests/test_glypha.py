import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import pytest

from riven.glypha import generate_sigil


def test_generate_sigil(tmp_path):
    pytest.importorskip("PIL")
    path = generate_sigil("test", sigil_dir=tmp_path)
    assert path.exists()
