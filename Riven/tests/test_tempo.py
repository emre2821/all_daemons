import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riven.tempo import pulse


def test_pulse_writes_log(tmp_path):
    log = tmp_path / "tempo.log"

    calls = []

    def fake_sleep(seconds):
        calls.append(seconds)

    pulse("calm", log_file=log, sleep_func=fake_sleep)

    assert log.exists()
    content = log.read_text()
    assert "[TEMPO]" in content
    assert calls  # ensure sleep called
