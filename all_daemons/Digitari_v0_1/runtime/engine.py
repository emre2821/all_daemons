# runtime/engine.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Any
import json, time

@dataclass
class Affect:
    valence: float
    arousal: float
    tags: List[str] = field(default_factory=list)

@dataclass
class Episode:
    episode_id: str
    t: str
    what: str
    who: List[str]
    affect: Affect
    salience: float
    consequences: str
    audit: Dict[str, Any] = field(default_factory=dict)

def should_refuse(task: Dict[str, Any], values: Dict[str, float], budgets: Dict[str, Any]) -> bool:
    """Refuse when rest is below threshold, or when task conflicts with strongest values."""
    if budgets.get("energy_points", 0) < budgets.get("rest_required_per_cycle", 0):
        return True
    consent = budgets.get("consent_prefs", {})
    if not consent.get("allow_override", False) and task.get("force", False):
        return True
    # simple value conflict demo: if task says "harm" and Care is high -> refuse
    harmful = any(k in str(task).lower() for k in ["harm","exploit","deceive"])
    if harmful and values.get("Care", 0.0) >= 0.6:
        return True
    return False

def audit(output_text: str, shared_facts: Dict[str, Any]) -> Dict[str, str]:
    """Toy auditor: flags claims that contradict a small fact cache; otherwise ok."""
    verdict = "ok"
    notes = ""
    for key, fact in shared_facts.items():
        if isinstance(fact, str) and key.lower() in output_text.lower():
            # naive contradiction check: user can expand this later
            if "not " in output_text.lower() and fact.lower() in output_text.lower():
                verdict = "fail"; notes = f"Contradicts fact for {key}"
                break
    if verdict == "ok" and "maybe" in output_text.lower():
        verdict = "warn"; notes = "Hedged claim; consider citing."
    return {"truth": verdict, "notes": notes}

def reinterpret(episodes: List[Episode]) -> List[Dict[str, Any]]:
    """Nightly reflective pass: lower salience of stale negative episodes slightly."""
    diffs = []
    now = time.time()
    for ep in episodes:
        try:
            # crude "staleness": older than ~7 days (604800s)
            ts = time.mktime(time.strptime(ep.t, "%Y-%m-%dT%H:%M:%S"))
        except Exception:
            continue
        if now - ts > 604800 and ep.affect.valence < 0:
            old = ep.salience
            ep.salience = max(0.0, ep.salience - 0.05)
            diffs.append({"episode_id": ep.episode_id, "salience": [old, ep.salience]})
    return diffs
