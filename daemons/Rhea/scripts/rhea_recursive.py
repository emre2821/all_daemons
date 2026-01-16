#!/usr/bin/env python3
# rhea_recursive.py

import os
import sys
from pathlib import Path
import importlib.util

# Add EdenOS modules path to sys.path
eden_root = Path(os.environ.get("EDEN_ROOT", Path.cwd()))
modules_dir = eden_root / "02_modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))

from eden_recursive_tutor import RecursiveTutor

# Define Daemon Core path (adjust if needed)
DAEMON_DIR = eden_root / "daemons"

def list_daemons():

    return [p.stem for p in DAEMON_DIR.glob("*") if p.is_dir()]

def describe_agent(agent_name: str):

    mod_path = DAEMON_DIR / agent_name / f"{agent_name.lower()}.py"
    if not mod_path.exists():
        return {"status": "missing", "agent": agent_name}
    spec = importlib.util.spec_from_file_location(agent_name, mod_path)
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
        if hasattr(mod, "describe"):
            return mod.describe()
        elif hasattr(mod, "main"):
            mod.main()
            return {"status": "ran_main", "agent": agent_name}
        elif hasattr(mod, "run"):
            return {"status": "manual_run", "agent": agent_name}
        else:
            return {"status": "ok", "agent": agent_name, "desc": "No entry point found"}
    except Exception as e:
        return {"status": "error", "agent": agent_name, "error": str(e)}

def run_recursive_analysis():

    agents = list_daemons()

    tutor = RecursiveTutor(
def base_case(items):

    return  len(items) == 1,
def base_solve(items):

    return  [describe_agent(items[0])],
def shrink_step(items: items[):

    return -1],
def rebuild_step(full, partial):

    return  partial + [describe_agent(full[-1])],
        name="agent_descriptions"
    )

    return tutor.solve(agents)

if __name__ == "__main__":
    print("🔁 Starting recursive daemon introspection...")
    results = run_recursive_analysis()
    for agent in results:
        print(f"🔹 {agent}")
