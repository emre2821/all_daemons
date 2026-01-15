import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from riven.maribel import deliver_messages


def test_deliver_messages(tmp_path):
    inbox = tmp_path / "inbox"
    outbox = tmp_path / "outbox"
    processed = tmp_path / "processed"
    outbox.mkdir()
    inbox.mkdir()
    processed.mkdir()
    (outbox / "note.aethermsg").write_text("hi")

    deliver_messages(inbox=inbox, outbox=outbox, processed=processed)

    assert not (outbox / "note.aethermsg").exists()
    assert not (inbox / "note.aethermsg").exists()
    assert (processed / "note.aethermsg").exists()
