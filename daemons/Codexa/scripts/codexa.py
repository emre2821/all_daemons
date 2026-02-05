# Eden-aware Codexa: harvests code blocks from split transcripts → *.codeblock.chaos
import os
import re
import time
from pathlib import Path

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
WORK_ROOT = Path(os.environ.get("EDEN_WORK_ROOT", EDEN_ROOT))
RHEA_BASE = WORK_ROOT / "daemons" / "Rhea"

SRC_DIR   = RHEA_BASE / "_archives" / "split_conversations"
OUT_DIR   = RHEA_BASE / "_outbox" / "codexa"
LOGS_DIR  = RHEA_BASE / "_logs"

for d in (SRC_DIR, OUT_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOGS_DIR / "codexa_daemon.log"
CODEBLOCK = re.compile(r"```([a-zA-Z0-9_\-+.]*)\s*\n(.*?)\n```", re.DOTALL)

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} [Codexa] {msg}"
    print(line)
    try:
        LOG_FILE.write_text((LOG_FILE.read_text(encoding="utf-8") if LOG_FILE.exists() else "") + line + "\n", encoding="utf-8")
    except Exception:
        pass

def extract_blocks(text: str):
    # returns list of (lang, code)
    return [(m.group(1) or "plain", m.group(2)) for m in CODEBLOCK.finditer(text)]

def write_chaos(chatname: str, lang: str, idx: int, code: str):
    # filename: ChatName.blockN.codeblock.chaos
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", chatname).strip("_")
    fname = f"{safe}.block{idx}.{lang}.codeblock.chaos"
    path = OUT_DIR / fname
    payload = (
        f"# source: {chatname}\n"
        f"# lang: {lang}\n"
        f"# extracted_by: Codexa\n\n"
        f"{code}\n"
    )
    path.write_text(payload, encoding="utf-8")
    return path

def main():
    if not SRC_DIR.exists():
        log(f"{SRC_DIR} missing; nothing to harvest.")
        return

    total_blocks = 0
    for fp in sorted(SRC_DIR.glob("*.txt")) + sorted(SRC_DIR.glob("*.md")) + sorted(SRC_DIR.glob("*.json")):
        try:
            text = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            log(f"WARN cannot read {fp.name}: {e}")
            continue
        blocks = extract_blocks(text)
        if not blocks:
            continue
        for i, (lang, code) in enumerate(blocks, start=1):
            out = write_chaos(fp.stem, lang, i, code)
            log(f"Wrote {out.name}")
            total_blocks += 1

    if total_blocks == 0:
        log("No code blocks found.")
    else:
        log(f"Done. Wrote {total_blocks} codeblock .chaos files.")

if __name__ == "__main__":
    main()
