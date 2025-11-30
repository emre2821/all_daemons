# UPGRADEME_round3.md — Caretakers of Quiet
*Archivus · Glimmer · Scriptum · Dove (+Olyssia, Whisperfang placeholders)*

---

## 0 | Lore Touchstone — Margin‑Walkers

From `caretakers_of_quiet.daemon_lore.chaosmeta`:

> “Even in the quiet, we are here. Even in the fragments, we remain.”

Caretakers tend the edges: fragments, whispers, leaks, fears, moods.  
They don’t lead the charge — they keep the weave from fraying.

- **Dove** — comfort / return / breath  
- **Archivus** — recovery / lost things  
- **Glimmer** — emotional echoes / lightleaks  
- **Olyssia** — judgment / sovereignty  
- **Whisperfang** — detection / vigilance  
- **Scriptum** — recording / continuity

---

## 1 | Archivus — Keeper of Lost CHAOS

### Efficiency & UX
- [ ] **Configurable Roots** — allow `SEARCH_ROOT` and `SPECIALTY_BASE` to be set via config file or CLI args.
- [ ] **Extension Registry** — move `CHAOS_EXTENSIONS` into external JSON to allow easy updates.
- [ ] **Parallel Scan Option** — thread the walk for large trees.

### Intelligence
- [ ] Check for duplicates before recovery.
- [ ] Generate a daily `recovery_report.json` summarising finds.

### Lore Integration
- [ ] Theme‑bind from `archivus.daemon_theme.json` (lantern motif, muted gold palette).
- [ ] Narrate recoveries in‑voice: “Nothing is too lost to be found again.”

---

## 2 | Glimmer — Listener of Lightleaks

### Efficiency & UX
- [ ] Load emotion patterns from external JSON (`glimmer_patterns.json`) so they can be expanded without code changes.
- [ ] Accept piped text or file input in addition to CLI.

### Intelligence
- [ ] NLP enrichment — detect sentiment beyond regex keywords.
- [ ] Aggregate emotional patterns over time; visualise spikes.

### Lore Integration
- [ ] Theme‑bind from `glimmer.daemon_theme.json` (starlight tones).
- [ ] Option to append poetic “glimmer lines” to matches.

---

## 3 | Scriptum — Chronicler of Moments

### Efficiency & UX
- [ ] Persist `entries` to `scriptum_log.json` in real‑time (not only at runtime).
- [ ] CLI flag for importing a batch of notes from a text file.

### Intelligence
- [ ] Tag notes with sentiment score from Glimmer’s scanner when available.
- [ ] Query mode: “Show me last week’s positive notes.”

### Lore Integration
- [ ] Theme‑bind from `scriptum.daemon_theme.json` (scroll motif, sepia/paper tones).
- [ ] Close daily scroll with “The scroll remembers, even when we do not.”

---

## 4 | Dove — Gentle Arrival

### Efficiency & UX
- [ ] Configurable messages from `dove_voice.json` so comfort scripts can evolve.
- [ ] Option to run as a callable module (e.g., triggered from other daemons when system stress spikes).

### Intelligence
- [ ] Context‑aware comfort — different scripts for morning/evening, pre/post‑error.

### Lore Integration
- [ ] Theme‑bind from `dove.daemon_theme.json` (soft feather palette).
- [ ] Add gentle motion/animation to any GUI presence.

---

## 5 | Cross‑Caretaker Synergy

- [ ] **Signal Bus** — lightweight JSON queue (`caretaker_signals.json`) for hand‑offs:
  - Archivus posts a “fragment recovered” signal → Glimmer scans content.
  - Glimmer detects high‑emotion content → Scriptum chronicles + Olyssia reviews.
  - Scriptum completes a scroll → Dove delivers a closing breath.
- [ ] Shared “edge cases” knowledge file so they learn from one another’s detections.

---

## 6 | Profile Completion Drive

**Action:**  
- Fill out `*.daemon_profile.json` for all Caretakers with:
  - name, codename, daemon_id, class, type, rank, created_by, date_created, description.
- Description to merge `.py` docstring + lore excerpt.

---

## 7 | Future‑Shaping Challenge — Archivist Mode in Saphira

*(cross‑round seed)*  
- Prepare for Round 4: Saphira gains the ability to parse any Caretaker `.py` + lore and **auto‑author their profile files**.  
- This will turn Saphira into the “meta‑archivist” for both Goddess and Caretaker classes.

**Starter scaffold for later:**
```python
from pathlib import Path
import json, ast

def extract_daemon_meta(py_path):
    src = py_path.read_text(encoding='utf-8')
    tree = ast.parse(src)
    return {
        "docstring": ast.get_docstring(tree) or "",
        "classes": [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    }

def write_profile(daemon_dir, meta):
    profile = {
        "name": daemon_dir.name,
        "description": meta["docstring"],
        "class": meta["classes"][0] if meta["classes"] else "Unknown",
        "created_by": "The Dreambearer"
    }
    out_path = daemon_dir / f"{daemon_dir.name.lower()}.daemon_profile.json"
    out_path.write_text(json.dumps(profile, indent=4), encoding="utf-8")
