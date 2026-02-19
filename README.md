# all_daemons

Monorepo for Paradigm Eden / Echolace daemon work.

This repository is intentionally broad: it contains the active `daemons/` collection, historical/legacy snapshots, framework experiments, docs, and utility scripts. Different folders are at different maturity levels.

## What is in this repo right now

- `daemons/` — the largest active collection (currently 100+ daemon directories).
- `tests/` — root-level smoke/path tests.
- `scripts/` — utility scripts used across projects.
- `shared/` — shared prompts, lore, and training/reference material.
- `docs/` — project documentation (including a more narrative README variant).
- `all_daemons/` — nested legacy/packaged daemon layout with its own `README.md` and `requirements.txt`.
- `Rhea/` — standalone Rhea module snapshot with `rhea_main.py`.
- `03_Daemon_Framework/`, `02_Life_Simulator_Project/`, `Digitari_v0_1/`, `archived_tools/` — adjacent projects and archived tooling retained in-repo.

## Python and environment

- Recommended: Python 3.10+ (some folders may assume newer versions).
- This repo does **not** currently provide a single authoritative root `requirements.txt`.
- A broad dependency set exists at `all_daemons/requirements.txt` for that subtree.

Example setup from repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install pytest
```

If you are working specifically inside `all_daemons/`:

```bash
pip install -r all_daemons/requirements.txt
```

## Running checks

From repo root:

```bash
pytest tests/test_smoke.py
```

That is the safest baseline check because it syntax-compiles discovered Python files without requiring every optional dependency used by every daemon.

## Working with daemons

Most daemon folders are self-contained. Typical layout patterns include:

- `daemon_name.py` (or `*_main.py`) executable entry script
- `configs/` JSON config set (`*.daemon_role.json`, `*.daemon_voice.json`, etc.)
- `scripts/` helper runner variants

Examples:

```bash
python daemons/Rhea/rhea_main.py
python daemons/Seiros/seiros.py
python daemons/Mila/mila.py
python daemons/Saphira/saphira.py
```

(Exact runtime behavior depends on each daemon's local config/dependency assumptions.)

## Notes on structure

This is a living lab, not a single tightly-coupled package. You will find:

- duplicate daemon names across active and archived areas,
- multiple generations of folder conventions,
- experimental files that are intentionally preserved.

When in doubt, prefer `daemons/` + `tests/` for current root-level work and treat other top-level project folders as specialized contexts.

## License

MIT (see `LICENSE`).
