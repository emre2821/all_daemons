import os, json
from pathlib import Path
from datetime import datetime

INBOX_DIR    = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Olyssia/inbox")
AGENTS_DIR   = Path(r"C:/EdenOS_Origin/all_daemons/Rhea/outputs/Olyssia/agents")
TEMPLATE_FILE= Path(r"C:/EdenOS_Origin/all_daemons/Olyssia/AoE_template.agent.json")

AGENTS_DIR.mkdir(parents=True, exist_ok=True)

def load_template():
    if TEMPLATE_FILE.exists():
        try: return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except: pass
    return {"type":"AoE","name":"","domain":"","role":"","notes":"","status":"draft"}

def seed_from_fragment(frag_json: dict) -> dict:
    t = load_template()
    t["created_at"] = datetime.now().isoformat()
    t["name"] = frag_json.get("guess_name") or "Unnamed_AoE"
    frag = (frag_json.get("fragment") or "").strip()
    t["notes"] = frag
    t["domain"] = "relation / story / resonance"
    t["role"] = "Agent of Eden"
    return t

def main():
    if not INBOX_DIR.exists(): return
    count = 0
    for f in INBOX_DIR.glob("*.fragment.json"):
        try: data = json.loads(f.read_text(encoding="utf-8"))
        except: continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_AoE").replace(" ","_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent,indent=2),encoding="utf-8")
        count += 1
    print(f"[Olyssia] seeded {count} AoE agent(s).")

if __name__ == "__main__":
    main()