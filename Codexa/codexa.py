import re
import time
from pathlib import Path

# === PATHS ===
SRC_DIR = Path(r"C:\EdenOS_Origin\data\exports\openai_exports\conversations_text")
OUT_DIR = Path(r"C:\EdenOS_Origin\data\exports\openai_exports\codeblocks")
LOG_FILE = Path(r"C:\EdenOS_Origin\data\exports\openai_exports\codexa_v3.log")

# === REGEX ===
CODEBLOCK = re.compile(r"```([a-zA-Z0-9_\-+.]*)\s*\n(.*?)\n```", re.DOTALL)


# === UTILITIES ===
def log(msg: str):

    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [CodexaV3] {msg}"
    print(line)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def extract_blocks(text: str):
    """Return list of (language, code) from code fences."""
    return [(m.group(1) or "plain", m.group(2)) for m in CODEBLOCK.finditer(text)]


def sanitize_name(name: str):

    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name)
    return name.strip("_")[:120]


def write_codeblock(chatname: str, lang: str, idx: int, code: str):
    """Write each code block as a .chaos file."""
    safe = sanitize_name(chatname)
    lang_safe = lang if lang else "plain"
    out_folder = OUT_DIR / lang_safe
    out_folder.mkdir(parents=True, exist_ok=True)

    fname = f"{safe}.block{idx}.{lang_safe}.codeblock.chaos"
    path = out_folder / fname

    payload = (
        f"# source: {chatname}\n"
        f"# lang: {lang_safe}\n"
        f"# extracted_by: CodexaV3\n\n"
        f"{code}\n"
    )
    path.write_text(payload, encoding="utf-8")
    return path


# === MAIN ===
def main():

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not SRC_DIR.exists():
        log(f"Source folder missing: {SRC_DIR}")
        return

    total_blocks = 0
    for fp in sorted(SRC_DIR.glob("*.txt")):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log(f"WARN: Cannot read {fp.name}: {e}")
            continue

        blocks = extract_blocks(text)
        if not blocks:
            continue

        for i, (lang, code) in enumerate(blocks, start=1):
            out = write_codeblock(fp.stem, lang, i, code)
            log(f"Wrote {out.name}")
            total_blocks += 1

    if total_blocks == 0:
        log("No code blocks found.")
    else:
        log(
            f"✅ Done. Wrote {total_blocks} .codeblock.chaos files across all languages."
        )


if __name__ == "__main__":
    main()
