from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from Daemon_tools.scripts.eden_paths import daemons_root, rhea_root  # noqa: E402

INBOX_DIR = rhea_root() / "outputs" / "Saphira" / "inbox"
AGENTS_DIR = rhea_root() / "outputs" / "Saphira" / "agents"
TEMPLATE_FILE = daemons_root() / "Saphira" / "DCA_template.agent.json"

AGENTS_DIR.mkdir(parents=True, exist_ok=True)


def load_template():
    if TEMPLATE_FILE.exists():
        try:
            return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"type": "DCA", "name": "", "intent": "", "summon_phrase": "", "tags": [], "status": "draft"}


def infer_intent(text: str) -> str:
    lowered = text.lower()
    if "parse" in lowered or "ingest" in lowered:
        return "ingest/parse"
    if "index" in lowered or "embed" in lowered:
        return "index/embed"
    if "watch" in lowered or "daemon" in lowered:
        return "watch/daemonize"
    return "general_utility"


def extract_tags(text: str):
    base = ["daemon", "pipeline", "memory", "index", "embed", "parse", "ingest", "summon"]
    lowered = text.lower()
    return sorted({k for k in base if k in lowered})


def extract_summon_phrase(text: str) -> str:
    for pat in (r".*\bsummon\b.*", r".*\binvoke\b.*", r".*\bcall forth\b.*"):
        match = re.search(pat, text, flags=re.I)
        if match:
            return match.group(0).strip()
    for line in text.splitlines():
        if line.strip():
            return line.strip()[:160]
    return ""


def seed_from_fragment(frag_json: dict) -> dict:
    template = load_template()
    template["created_at"] = datetime.now().isoformat()
    template["name"] = frag_json.get("guess_name") or "Unnamed_DCA"
    frag = (frag_json.get("fragment") or "").strip()
    template["summon_phrase"] = extract_summon_phrase(frag)
    template["intent"] = infer_intent(frag)
    template["tags"] = extract_tags(frag)
    return template


def main():
    if not INBOX_DIR.exists():
        print(f"[Saphira] inbox not found: {INBOX_DIR}")
        return
    count = 0
    for fragment_path in INBOX_DIR.glob("*.fragment.json"):
        try:
            data = json.loads(fragment_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_DCA").replace(" ", "_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent, indent=2), encoding="utf-8")
        count += 1
    print(f"[Saphira] seeded {count} DCA agent(s).")


if __name__ == "__main__":
    main()
