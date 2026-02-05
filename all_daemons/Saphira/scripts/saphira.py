import json
import re
from pathlib import Path
from datetime import datetime

INBOX_DIR    = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Saphira/inbox")
AGENTS_DIR   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Saphira/agents")
TEMPLATE_FILE= Path(r"C:/EdenOS_Origin/all_daemons/Saphira/DCA_template.agent.json")

AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def load_template():
    if TEMPLATE_FILE.exists():
        try: return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"type":"DCA","name":"","intent":"","summon_phrase":"","tags":[],"status":"draft"}

def infer_intent(text: str) -> str:
    t = text.lower()
    if "parse" in t or "ingest" in t: return "ingest/parse"
    if "index" in t or "embed" in t: return "index/embed"
    if "watch" in t or "daemon" in t: return "watch/daemonize"
    return "general_utility"

def extract_tags(text: str):
    base = ["daemon","pipeline","memory","index","embed","parse","ingest","summon"]
    t = text.lower()
    return sorted({k for k in base if k in t})

def extract_summon_phrase(text: str) -> str:
    for pat in (r".*\bsummon\b.*", r".*\binvoke\b.*", r".*\bcall forth\b.*"):
        m = re.search(pat, text, flags=re.I)
        if m: return m.group(0).strip()
    for line in text.splitlines():
        if line.strip(): return line.strip()[:160]
    return ""

def seed_from_fragment(frag_json: dict) -> dict:
    t = load_template()
    t["created_at"] = datetime.now().isoformat()
    t["name"] = frag_json.get("guess_name") or "Unnamed_DCA"
    frag = (frag_json.get("fragment") or "").strip()
    t["summon_phrase"] = extract_summon_phrase(frag)
    t["intent"] = infer_intent(frag)
    t["tags"] = extract_tags(frag)
    return t

def main():
    if not INBOX_DIR.exists(): return
    count = 0
    for f in INBOX_DIR.glob("*.fragment.json"):
        try: data = json.loads(f.read_text(encoding="utf-8"))
        except: continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_DCA").replace(" ","_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent,indent=2),encoding="utf-8")
        count += 1
    print(f"[Saphira] seeded {count} DCA agent(s).")

if __name__ == "__main__":
    main()