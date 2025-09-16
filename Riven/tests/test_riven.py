import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riven.riven import mend_fragments


def test_mend_fragments(tmp_path):
    fractured = tmp_path / "fractured"
    repaired = tmp_path / "repaired"
    fractured.mkdir()
    repaired.mkdir()

    (fractured / "log.chaos").write_text("start [FRACTURE] end [UNBOUND]")

    mend_fragments(memory_path=fractured, repaired_path=repaired)

    out = repaired / "riven_log.chaos"
    assert out.exists()
    content = out.read_text()
    assert "[REPAIRED]" in content
    assert "[BOUND]" in content
