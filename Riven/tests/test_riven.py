from types import SimpleNamespace
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

import riven.harper as harper
import riven.maribel as maribel
import riven.glypha as glypha
import riven.tempo as tempo
import riven.riven as riven_mod


def test_harper_alerts_when_threshold_exceeded(tmp_path, monkeypatch, capsys):
    watch = tmp_path / "watch"
    watch.mkdir()
    alert_log = tmp_path / "alerts.log"
    monkeypatch.setattr(harper, "WATCH_PATH", str(watch))
    monkeypatch.setattr(harper, "ALERT_LOG", str(alert_log))
    harper.THRESHOLDS.update({'cpu': 10, 'mem': 10, 'chaos_backlog': 0})
    (watch / "a.chaos").write_text("x")

    monkeypatch.setattr(harper.psutil, "cpu_percent", lambda interval=1: 50)
    monkeypatch.setattr(
        harper.psutil,
        "virtual_memory",
        lambda: SimpleNamespace(percent=50),
    )

    harper.check_system_pressure()
    out = capsys.readouterr().out
    assert "High CPU" in out
    assert "High Memory" in out
    assert "Backlog CHAOS files" in out
    assert alert_log.read_text()


def test_maribel_delivers_messages(tmp_path, monkeypatch):
    inbox = tmp_path / "inbox"
    outbox = tmp_path / "outbox"
    processed = tmp_path / "processed"
    for p in (inbox, outbox, processed):
        p.mkdir()
    monkeypatch.setattr(maribel, "INBOX", str(inbox))
    monkeypatch.setattr(maribel, "OUTBOX", str(outbox))
    monkeypatch.setattr(maribel, "PROCESSED", str(processed))

    (outbox / "msg.aethermsg").write_text("hello")
    maribel.deliver_messages()

    assert not any(outbox.iterdir())
    assert not any(inbox.iterdir())
    files = list(processed.iterdir())
    assert files and files[0].name == "msg.aethermsg"


def test_glypha_generates_sigil(tmp_path, monkeypatch):
    monkeypatch.setattr(glypha, "SIGIL_DIR", str(tmp_path))
    filename = glypha.generate_sigil("hope")
    assert (tmp_path / filename).exists()


def test_tempo_pulse_writes_log(tmp_path, monkeypatch):
    log = tmp_path / "tempo.log"
    monkeypatch.setattr(tempo, "TEMPO_FILE", str(log))
    monkeypatch.setattr(tempo.time, "sleep", lambda x: None)
    tempo.pulse("calm")
    assert "Mood=calm" in log.read_text()


def test_riven_mends_fragments(tmp_path, monkeypatch):
    memory = tmp_path / "mem"
    repaired = tmp_path / "repaired"
    memory.mkdir()
    repaired.mkdir()
    monkeypatch.setattr(riven_mod, "MEMORY_PATH", str(memory))
    monkeypatch.setattr(riven_mod, "REPAIRED_PATH", str(repaired))

    (memory / "frag.chaos").write_text("start [FRACTURE] end")
    riven_mod.mend_fragments()

    files = list(repaired.iterdir())
    assert files and files[0].name == "riven_frag.chaos"
    assert "[REPAIRED]" in files[0].read_text()
