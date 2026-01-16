import os

MEMORY_PATH = "./fractured_logs"
REPAIRED_PATH = "./restored_logs"

os.makedirs(REPAIRED_PATH, exist_ok=True)


def mend_fragments() -> None:

    print("[Riven] Scanning for fractured logs...")
    for fname in os.listdir(MEMORY_PATH):
        if fname.endswith('.chaos'):
            fpath = os.path.join(MEMORY_PATH, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if '[FRACTURE]' in content or '[UNBOUND]' in content:
                    patched = (
                        content.replace('[FRACTURE]', '[REPAIRED]')
                        .replace('[UNBOUND]', '[BOUND]')
                    )
                    outname = f"riven_{fname}"
                    outpath = os.path.join(REPAIRED_PATH, outname)
                    with open(outpath, 'w', encoding='utf-8') as out:
                        out.write(patched)
                    print(f"[Riven] Restored: {outname}")
            except Exception as e:
                print(f"[Riven] Error mending {fname}: {e}")
