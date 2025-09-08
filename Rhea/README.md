# Rhea — Self-Managing Daemon System

**Features**
- Watch `all_daemons/` for new/changed `.py` files with YAML docstrings → auto‑register
- JSON Schema validation + backups + diff preview
- Self‑correction: disables missing files, syncs team memberships, updates metadata
- CLI to scan/list/start/stop teams/daemons; GUI to edit registry safely
- Custom palettes baked in (Eden Dream, Velvet Division, Rootfire)

**Install (with uv)**
```bash
# Create venv and install all deps (core + daemons)
uv venv .venv
uv pip install -r requirements.eden.txt

# Initialize and scan
uv run Rhea/scripts/full_rhea.complete_build.py init
uv run Rhea/scripts/full_rhea.complete_build.py scan
uv run Rhea/scripts/full_rhea.complete_build.py watch

Add a daemon

1. Create all_daemons/Name/name.py
2. Paste the YAML docstring template and tweak
3. python full_rhea.complete_build.py scan (or just keep watch running)

Open the GUI

uv run Rhea/scripts/full_rhea.complete_build.py gui

---

## UPGRADEME.md
```md
# How to make Rhea even sharper

1. **Process Supervision** — wrap daemons with a supervisor (auto‑restart on crash, exponential backoff, health pings).
2. **Sandboxed Tasks** — run tasks through a small job runner (queue + logs + per‑task env/timeout).
3. **Schema Migration** — add `version`ed migrations to evolve the registry.
4. **Pair Semantics** — encode allowed/forbidden pairs and relationship types with checks.
5. **HTTP Control Plane** — tiny FastAPI to query registry, start/stop, and stream logs.
6. **Credential Broker** — move sensitive env keys into OS keyring and reference them by alias.
7. **Rule Engine** — declarative `rules/` folder; each rule returns (ok, message, patch) for auto‑repair.
8. **Unit Tests** — pytest suite for discovery, reconciliation, and GUI merge semantics.
9. **Windows niceties** — optional `start /B` wrappers and elevation for specific tasks when needed.
10. **Dreammode** — palette‑animated GUI themes that reflect agent mood/state.
