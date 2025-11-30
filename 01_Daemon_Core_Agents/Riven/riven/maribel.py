from pathlib import Path
import shutil


def deliver_messages(
    inbox: Path = Path("aether_inbox"),
    outbox: Path = Path("aether_outbox"),
    processed: Path = Path("aether_delivered"),
) -> None:
    inbox.mkdir(exist_ok=True)
    outbox.mkdir(exist_ok=True)
    processed.mkdir(exist_ok=True)

    for src in outbox.glob("*.aethermsg"):
        dest = inbox / src.name
        shutil.copy2(src, dest)
        src.unlink()
        print(f"[Maribel] Delivered: {src.name}")

    for src in inbox.glob("*.aethermsg"):
        dest = processed / src.name
        shutil.move(src, dest)
        print(f"[Maribel] Processed: {src.name}")
