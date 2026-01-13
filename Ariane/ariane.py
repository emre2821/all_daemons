#!/usr/bin/env python3
r"""
Ariane :: Pathkeeper & Auditor Daemon
-------------------------------------
Keeps daemons, configs, and registry aligned with canonical layout:

    C:\EdenOS_Origin\01_Daemon_Core_Agents\<Daemon>\<daemon>.py
"""

import os
import json
import shutil
import datetime

try:
    import yaml
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

# === CONFIG ===
BASE = r"C:\EdenOS_Origin\01_Daemon_Core_Agents"
RHEA_DIR = os.path.join(BASE, "Rhea")
REGISTRY = os.path.join(RHEA_DIR, "rhea_registry.json")
DAEMONS_YAML = os.path.join(RHEA_DIR, "daemons.yaml")
TASKS_YAML = os.path.join(RHEA_DIR, "tasks.yaml")
LOG = os.path.join(RHEA_DIR, "outputs", "ariane_corrections.jsonl")

os.makedirs(os.path.dirname(LOG), exist_ok=True)

# === HELPERS ===
def now():

    return datetime.datetime.utcnow().isoformat()

def log_fix(record: dict):

    record["time"] = now()
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")

def canonical_path(name: str):

    return os.path.join(BASE, name, f"{name.lower()}.py")

def safe_backup(path: str):

    if os.path.exists(path):
        bak = f"{path}.{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.bak"
        shutil.copyfile(path, bak)
        print(f"[ARIANE] Backup created: {bak}")

# === REGISTRY AUDIT ===
def audit_registry():

    if not os.path.exists(REGISTRY):
        print(f"[ARIANE] No registry found at {REGISTRY}")
        return

    with open(REGISTRY, "r", encoding="utf-8") as f:
        reg = json.load(f)

    if not isinstance(reg, dict):
        print("[ARIANE] Registry format unexpected (not a dict). Skipping.")
        return

    daemons = reg.get("daemons") or reg.get("Daemons") or {}

    # Normalize into list of dicts with name
    entries = []
    if isinstance(daemons, dict):
        for k, v in daemons.items():
            if isinstance(v, dict):
                v = v.copy()
                v["name"] = k
                entries.append(v)
    elif isinstance(daemons, list):
        entries = daemons
    else:
        print("[ARIANE] Registry 'daemons' neither dict nor list. Skipping.")
        return

    changed = False
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        name = entry.get("name") or entry.get("Name")
        if not name:
            continue

        canon = canonical_path(name)
        current = entry.get("module") or entry.get("path") or entry.get("Path")

        if not os.path.exists(canon):
            log_fix({"daemon": name, "issue": "missing_file", "expected": canon})
            print(f"[WARN] Missing file for {name} (expected {canon})")
            continue

        if not current or os.path.abspath(current) != os.path.abspath(canon):
            log_fix({
                "daemon": name,
                "issue": "path_mismatch",
                "old": current,
                "new": canon
            })
            # Update both dict-backed and list-backed forms
            if isinstance(daemons, dict) and name in daemons:
                daemons[name]["module"] = canon
            else:
                entry["path"] = canon
            changed = True
            print(f"[FIX] Corrected registry path for {name}")

    if changed:
        safe_backup(REGISTRY)
        with open(REGISTRY, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=2)
        print(f"[ARIANE] Registry updated at {REGISTRY}")
    else:
        print("[ARIANE] Registry already consistent.")

# === YAML AUDIT ===
def audit_yaml(path: str, key: str):

    if not HAVE_YAML or not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        print(f"[ARIANE] {path} format unexpected. Skipping.")
        return

    changed = False
    for entry in data.get(key, []):
        if not isinstance(entry, dict):
            continue
        name = entry.get("name")
        if not name:
            continue
        canon = canonical_path(name)
        if os.path.abspath(entry.get("path", "")) != os.path.abspath(canon):
            log_fix({"daemon": name, "issue": f"{os.path.basename(path)}_path_mismatch",
                     "old": entry.get("path"), "new": canon})
            entry["path"] = canon
            changed = True
            print(f"[FIX] Updated {path} entry for {name}")

    if changed:
        safe_backup(path)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f)
        print(f"[ARIANE] {path} updated.")
    else:
        print(f"[ARIANE] {path} already consistent.")

# === FILE NORMALIZATION ===
def normalize_daemon_files():

    for d in os.listdir(BASE):
        ddir = os.path.join(BASE, d)
        if not os.path.isdir(ddir): 
            continue
        py_files = [f for f in os.listdir(ddir) if f.lower().endswith(".py")]
        if not py_files:
            continue
        want = f"{d.lower()}.py"
        for f in py_files:
            if f.lower() != want:
                src = os.path.join(ddir, f)
                dst = os.path.join(ddir, want)
                if os.path.exists(dst):
                    print(f"[WARN] {dst} already exists, leaving {f} untouched")
                    continue
                os.replace(src, dst)
                log_fix({"daemon": d, "issue": "rename", "old": f, "new": want})
                print(f"[RENAME] {f} -> {want}")

# === FULL AUDIT ===
def run_audit():

    print("[ARIANE] Starting full audit...")
    normalize_daemon_files()
    audit_registry()
    audit_yaml(DAEMONS_YAML, "daemons")
    audit_yaml(TASKS_YAML, "tasks")
    print("[ARIANE] Audit complete.")

if __name__ == "__main__":
    run_audit()
