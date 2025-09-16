from pathlib import Path


def mend_fragments(
    memory_path: Path = Path("fractured_logs"),
    repaired_path: Path = Path("restored_logs"),
) -> None:
    repaired_path.mkdir(exist_ok=True)
    print("[Riven] Scanning for fractured logs...")
    for fpath in memory_path.glob("*.chaos"):
        try:
            content = fpath.read_text(encoding="utf-8")
            if "[FRACTURE]" in content or "[UNBOUND]" in content:
                patched = content.replace("[FRACTURE]", "[REPAIRED]").replace(
                    "[UNBOUND]", "[BOUND]"
                )
                outpath = repaired_path / f"riven_{fpath.name}"
                outpath.write_text(patched, encoding="utf-8")
                print(f"[Riven] Restored: {outpath.name}")
        except Exception as e:
            print(f"[Riven] Error mending {fpath.name}: {e}")
