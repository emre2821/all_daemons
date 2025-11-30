import os
import shutil

INBOX = "./aether_inbox"
OUTBOX = "./aether_outbox"
PROCESSED = "./aether_delivered"

for path in (INBOX, OUTBOX, PROCESSED):
    os.makedirs(path, exist_ok=True)


def deliver_messages() -> None:
    for fname in os.listdir(OUTBOX):
        if fname.endswith('.aethermsg'):
            src = os.path.join(OUTBOX, fname)
            dest = os.path.join(INBOX, fname)
            shutil.copy2(src, dest)
            os.remove(src)
            print(f"[Maribel] Delivered: {fname}")

    for fname in os.listdir(INBOX):
        if fname.endswith('.aethermsg'):
            src = os.path.join(INBOX, fname)
            dest = os.path.join(PROCESSED, fname)
            shutil.move(src, dest)
            print(f"[Maribel] Processed: {fname}")
