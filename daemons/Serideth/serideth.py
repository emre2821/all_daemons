import json
import re
from pathlib import Path
from datetime import datetime

# Get paths relative to script location
SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
RHEA_DIR = BASE_DIR / "Rhea"

ADERYN_OUT = RHEA_DIR / "outputs" / "Aderyn" / "summons"
OLYSSIA_IN = RHEA_DIR / "outputs" / "Olyssia" / "inbox"
SAPHIRA_IN = RHEA_DIR / "outputs" / "Saphira" / "inbox"
SERIDETH_OUT = RHEA_DIR / "outputs" / "Serideth"

for p in (OLYSSIA_IN, SAPHIRA_IN, SERIDETH_OUT):
    p.mkdir(parents=True, exist_ok=True)

DISPATCH_LOG = SERIDETH_OUT / "dispatch_log.json"

DCA_HINTS = ["daemon", "pipeline", "parse", "embed", "index", "memory", "daemon core"]
AOE_HINTS = ["agent", "voice", "story", "lore", "aesthetic", "eden", "front of house"]


def guess_bucket(text: str) -> str:

    t = text.lower()
    if any(k in t for k in DCA_HINTS):
        return "DCA"
    if any(k in t for k in AOE_HINTS):
        return "AOE"
    if re.search(r"\bsummon\b|\binvoke\b", t):
        return "DCA"
    return "AOE"


def guess_name(text: str, prefix: str) -> str:

    m = re.search(r"(agent|name)\s*[:=]\s*([A-Za-z0-9_\-]{3,64})", text, flags=re.I)
    if m:
        return m.group(2)
    m = re.search(r"\b([A-Z][a-zA-Z0-9_\-]{2,32})\b", text)
    if m:
        return m.group(1)
    return f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def main():

    log = {"dispatched": [], "skipped": []}
    if not ADERYN_OUT.exists():
        print("[Serideth] No Aderyn output found.")
        return
    for f in ADERYN_OUT.glob("*.chaos"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except:
            log["skipped"].append({"file": f.name, "reason": "bad_json"})
            continue
        fragments = []
        if isinstance(data.get("summons"), list):
            fragments = [s.get("text", "") for s in data["summons"]]
        elif isinstance(data.get("nodes"), list):
            fragments = [n.get("content", "") for n in data["nodes"]]
        for frag in fragments:
            bucket = guess_bucket(frag)
            if bucket == "DCA":
                agent_name = guess_name(frag, "Unnamed_DCA")
                outpath = SAPHIRA_IN / f"{agent_name}.fragment.json"
                outpath.write_text(
                    json.dumps({"fragment": frag, "guess_name": agent_name}, indent=2),
                    encoding="utf-8",
                )
                log["dispatched"].append({"to": "Saphira", "file": outpath.name})
            else:
                agent_name = guess_name(frag, "Unnamed_AoE")
                outpath = OLYSSIA_IN / f"{agent_name}.fragment.json"
                outpath.write_text(
                    json.dumps({"fragment": frag, "guess_name": agent_name}, indent=2),
                    encoding="utf-8",
                )
                log["dispatched"].append({"to": "Olyssia", "file": outpath.name})
    (DISPATCH_LOG).write_text(json.dumps(log, indent=2), encoding="utf-8")
    print(f"[Serideth] dispatched {len(log['dispatched'])} fragment(s).")


if __name__ == "__main__":
    main()
