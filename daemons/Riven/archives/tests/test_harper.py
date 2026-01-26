import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riven.harper import check_system_pressure


class DummyPsutil:
    def cpu_percent(self, interval=1):
        return 90.0

    class VM:
        percent = 90.0

    def virtual_memory(self):
        return self.VM()


def test_check_system_pressure(tmp_path, monkeypatch):
    watch = tmp_path / "watch"
    watch.mkdir()
    for i in range(12):
        (watch / f"{i}.chaos").write_text("x")
    alert_log = tmp_path / "alerts.log"
    check_system_pressure(
        watch_path=watch,
        alert_log=alert_log,
        thresholds={"cpu": 50, "mem": 50, "chaos_backlog": 10},
        psutil_module=DummyPsutil(),
    )
    content = alert_log.read_text()
    assert "High CPU" in content
    assert "High Memory" in content
    assert "Backlog CHAOS files" in content
