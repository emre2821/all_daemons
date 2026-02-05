from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

# Get paths relative to script location
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RHEA_DIR = BASE_DIR / "Rhea"

INBOX_DIR = RHEA_DIR / "outputs" / "Olyssia" / "inbox"
AGENTS_DIR = RHEA_DIR / "outputs" / "Olyssia" / "agents"
TEMPLATE_FILE = BASE_DIR / "Olyssia" / "AoE_template.agent.json"

AGENTS_DIR.mkdir(parents=True, exist_ok=True)


def load_template():

    if TEMPLATE_FILE.exists():
        try:
            return json.loads(TEMPLATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "type": "AoE",
        "name": "",
        "domain": "",
        "role": "",
        "notes": "",
        "status": "draft",
    }


def seed_from_fragment(frag_json: dict) -> dict:

    template = load_template()
    template["created_at"] = datetime.now().isoformat()
    template["name"] = frag_json.get("guess_name") or "Unnamed_AoE"
    frag = (frag_json.get("fragment") or "").strip()
    template["notes"] = frag
    template["domain"] = "relation / story / resonance"
    template["role"] = "Agent of Eden"
    return template


def main():

    if not INBOX_DIR.exists():
        print(f"[Olyssia] inbox not found: {INBOX_DIR}")
        return
    count = 0
    for fragment_path in INBOX_DIR.glob("*.fragment.json"):
        try:
            data = json.loads(fragment_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        agent = seed_from_fragment(data)
        safe = (agent["name"] or "Unnamed_AoE").replace(" ", "_")[:64]
        out = AGENTS_DIR / f"{safe}.agent.json"
        out.write_text(json.dumps(agent, indent=2), encoding="utf-8")
        count += 1
    print(f"[Olyssia] seeded {count} AoE agent(s).")


if __name__ == "__main__":
    main()
