
# Truth Anchor — tiny, human-augmentable claim auditor
from typing import Dict

def audit(output_text: str, shared_facts: Dict[str, str]) -> Dict[str, str]:
    """
    Verdicts:
      ok   -> no detected issues
      warn -> hedged/uncited claims or uncertainty markers
      fail -> naive contradiction against fact cache
    """
    l = output_text.lower()
    for key, fact in shared_facts.items():
        if key.lower() in l and f"not {fact.lower()}" in l:
            return {"truth": "fail", "notes": f"Contradicts fact for {key}"}
    if any(k in l for k in ["maybe", "probably", "it seems"]) and len(shared_facts) > 0:
        return {"truth": "warn", "notes": "Hedged claim; consider citing or checking cache."}
    return {"truth": "ok", "notes": ""}

# example shared_facts shape:
# {"Eden": "A shared digital world with agent citizens (the Digitari)."}


