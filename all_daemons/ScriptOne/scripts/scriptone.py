import os
import re

vault = os.path.expanduser("~/Dropbox/CHAOS_Logs")
index = {}

for fname in os.listdir(vault):
    with open(os.path.join(vault, fname), "r", encoding="utf-8") as f:
        text = f.read()
        emotion = re.search(r"\[EMOTION\]:\s*(\w+)", text)
        context = re.search(r"\[CONTEXT\]:\s*(\S+)", text)
        if emotion and context:
            key = (emotion.group(1), context.group(1))
            index.setdefault(key, []).append(fname)

for (e, c), files in index.items():
    print(f"{e} / {c} → {len(files)} entries")
