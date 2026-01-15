import os
import json
from datetime import datetime
from configparser import ConfigParser
from difflib import SequenceMatcher
from typing import List
import Tuple, Dict, Any

# ----------------------------
# Savvy Daemon – A Sweet Southern Belle with a Sassy Bite
#
# This script compares agent files (e.g. ".mirror.json") in paired directories.
# It reads configuration from the [Savvy] section in config.ini and logs
# reflective observations to a designated journal file.
#
# Signature: “Just because they match doesn't mean they align. 🌸”
# ----------------------------

# ------------- Config Handling -------------
def get_config() -> ConfigParser:

    config = ConfigParser()
    config.read("config.ini")
    return config

def get_directory_pairs() -> List[List[str]]:

    """
    Reads all keys starting with "pair_" from the [Savvy] section
    and returns a list of directory pairs (2+ entries allowed for N-way scans).
    """
    config = get_config()
    pairs: List[List[str]] = []
    if "Savvy" in config.sections():
        for key in sorted(config["Savvy"].keys()):
            if key.startswith("pair_"):
                pair_str = config["Savvy"][key]
                dirs = [d.strip() for d in pair_str.split(",") if d.strip()]
                if len(dirs) >= 2:
                    pairs.append(dirs)
    return pairs

def get_savvy_settings() -> Dict[str, Any]:

    config = get_config()
    if "Savvy" not in config:
        raise Exception("Missing [Savvy] section in config.ini")
    settings = config["Savvy"]
    fuzzy = settings.get("fuzzy_match", "no").lower() in ["yes", "true", "1", "y", "on"]
    journal = settings.get("journal_path", "savvy_journal.txt")
    chaosdiff = settings.get("chaosdiff_output", "no").lower() in ["yes", "true", "1", "y", "on"]
    verbosity = settings.get("verbosity", "observant").lower()
    threshold = float(settings.get("fuzzy_threshold", "0.82"))
    fields = [f.strip() for f in settings.get("fields", "").split(",") if f.strip()]
    return {
        "fuzzy_match": fuzzy,
        "journal_path": journal,
        "chaosdiff": chaosdiff,
        "verbosity": verbosity,
        "fuzzy_threshold": threshold,
        "fields": fields
    }

# ------------- File Loading and Comparison -------------
def load_agent_json(filepath: str) -> Dict[str, Any] | None:

    """
    Attempts to load an agent file as JSON.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[Savvy] Error reading {filepath}: {e}")
        return None

def list_mirror_files(path: str) -> List[str]:

    try:
        return [f for f in os.listdir(path) if f.lower().endswith(".mirror.json")]
    except Exception as e:
        print(f"[Savvy] Unable to list directory {path}: {e}")
        return []

def find_matching_agent_files(dir_A: str, dir_B: str, fuzzy: bool=False, fuzzy_threshold: float=0.82) -> List[Tuple[str, str]]:

    """
    Finds matching agent files between dir_A and dir_B.
    First, it checks for exact filename matches using the '.mirror.json' extension.
    If fuzzy matching is enabled, it will try to match files by the 'name' field (or closest name).
    """
    matches: List[Tuple[str, str]] = []
    files_A = list_mirror_files(dir_A)
    files_B = list_mirror_files(dir_B)

    # Fast path: exact filename match
    files_B_set = set(files_B)
    exact = [(os.path.join(dir_A, fa), os.path.join(dir_B, fa)) for fa in files_A if fa in files_B_set]
    matches.extend(exact)

    if not fuzzy:
        return matches

    # Build name indexes for fuzzy matching
    matched_A = set(os.path.basename(a) for a, _ in matches)
    unmatched_A = [fa for fa in files_A if fa not in matched_A]

    # Preload B name map
    b_map: Dict[str, Tuple[str, str]] = {}  # file -> (path, name.lower())
    for fb in files_B:
        pb = os.path.join(dir_B, fb)
        jb = load_agent_json(pb)
        nm = (jb.get("name") if isinstance(jb, dict) else "") or os.path.splitext(os.path.splitext(fb)[0])[0]
        b_map[fb] = (pb, str(nm).lower())

    used_B: set[str] = set(os.path.basename(b) for _, b in matches)

    for fa in unmatched_A:
        pa = os.path.join(dir_A, fa)
        ja = load_agent_json(pa)
        name_a = (ja.get("name") if isinstance(ja, dict) else "") or os.path.splitext(os.path.splitext(fa)[0])[0]
        name_a_l = str(name_a).lower()

        best: Tuple[str, float] | None = None  # (file_b, ratio)
        for fb, (pb, nb_l) in b_map.items():
            if fb in used_B:
                continue
            ratio = SequenceMatcher(None, name_a_l, nb_l).ratio()
            if best is None or ratio > best[1]:
                best = (fb, ratio)
        if best and best[1] >= fuzzy_threshold:
            fb = best[0]
            matches.append((pa, b_map[fb][0]))
            used_B.add(fb)

    return matches

def compare_json(a: Dict[str, Any], b: Dict[str, Any], fields: List[str] | None=None) -> Dict[str, Any]:

    """
    Compare two agent JSON dicts.
    Returns a dict with added/removed/changed fields (restricted to `fields` if provided).
    """
    if fields:
        keys_a = set(k for k in a.keys() if k in fields)
        keys_b = set(k for k in b.keys() if k in fields)
    else:
        keys_a = set(a.keys())
        keys_b = set(b.keys())
    added = sorted(list(keys_b - keys_a))
    removed = sorted(list(keys_a - keys_b))
    common = keys_a & keys_b

    changed: Dict[str, Dict[str, Any]] = {}
    for k in sorted(common):
        va = a.get(k)
        vb = b.get(k)
        if va != vb:
            sim = None
            if isinstance(va, str) and isinstance(vb, str):
                sim = SequenceMatcher(None, va, vb).ratio()
            changed[k] = {"from": va, "to": vb, "similarity": sim}
    return {"added": added, "removed": removed, "changed": changed}

# ------------- Output Formatting -------------
def format_observation(agent_name: str, path_a: str, path_b: str, diff: Dict[str, Any], verbosity: str) -> str:

    header = f"◆ Savvy Note – {agent_name}\n   A: {path_a}\n   B: {path_b}\n"
    if verbosity == "stoic":
        return header +
            f"   Δ added={len(diff['added'])}, removed={len(diff['removed'])}, changed={len(diff['changed'])}\n"

    lines = [header]
    if diff["added"]:
        lines.append(" + Fields only in B: " + ", ".join(diff["added"]))
    if diff["removed"]:
        lines.append(" - Fields only in A: " + ", ".join(diff["removed"]))
    if diff["changed"]:
        lines.append("   ~ Changed fields:")
        for k, meta in diff["changed"].items():
            sim_txt = f" (sim={meta['similarity']:.2f})" if meta.get("similarity") is not None else ""
            def trunc(v):

                s = json.dumps(v, ensure_ascii=False)
                return s if len(s) <= 160 else s[:157] + "…\""
            lines.append(f" - {k}:{sim_txt}")
            lines.append(f"          from: {trunc(meta['from'])}")
            lines.append(f"          to:   {trunc(meta['to'])}")
    if verbosity == "gossipy":
        lines.append("   Southern Aside: Sugar, matching files ain’t the same as aligned souls. Mind the deltas. 🌸")
    return "\n".join(lines) + "\n"

def make_chaosdiff(agent_name: str, diff: Dict[str, Any]) -> str:

    """
    Create a lightweight CHAOS-style diff block.
    """
    lines = [
        "::chaos.diff::",
        f"[AGENT]: {agent_name}",
        f"[STAMP]: {datetime.utcnow().isoformat()}Z",
        "[DELTA]:"
    ]
    if diff["added"]:
        lines.append(" + added: " + ", ".join(diff["added"]))
    if diff["removed"]:
        lines.append(" - removed: " + ", ".join(diff["removed"]))
    if diff["changed"]:
        lines.append("  ~ changed:")
        for k, meta in diff["changed"].items():
            sim_txt = f" (sim~{meta['similarity']:.2f})" if meta.get("similarity") is not None else ""
            lines.append(f" - {k}{sim_txt}")
    lines.append("::end.diff::")
    return "\\n".join(lines)

# ------------- Journal -------------
def write_journal(journal_path: str, content: str) -> None:

    os.makedirs(os.path.dirname(journal_path) or ".", exist_ok=True)
    with open(journal_path, "a", encoding="utf-8") as f:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"--- Savvy Journal @ {stamp} ---\\n")
        f.write(content)
        f.write("\\n")

# ------------- Runner -------------
def run_savvy() -> int:

    """
    Execute Savvy across all configured directory pairs.
    Returns the number of agent comparisons performed.
    """
    settings = get_savvy_settings()
    pairs = get_directory_pairs()
    if not pairs:
        print("[Savvy] No directory pairs configured under [Savvy] pair_* keys.")
        return 0

    total = 0
    journal_chunks: List[str] = []
    for pair in pairs:
        # Roll through the pair as sequential neighbors: (0,1), (1,2), ...
        for i in range(len(pair) - 1):
            A, B = pair[i], pair[i+1]
            if not os.path.isdir(A) or not os.path.isdir(B):
                print(f"[Savvy] Skipping non-existent dirs: {A} <-> {B}")
                continue
            matches = find_matching_agent_files(A, B, settings["fuzzy_match"], settings["fuzzy_threshold"])
            for path_a, path_b in matches:
                ja = load_agent_json(path_a) or {}
                jb = load_agent_json(path_b) or {}
                agent_name = (ja.get("name") or jb.get("name") or os.path.basename(path_a)).strip()
                diff = compare_json(ja, jb, settings.get("fields") or None)
                note = format_observation(agent_name, path_a, path_b, diff, settings["verbosity"])
                journal_chunks.append(note)
                if settings["chaosdiff"]:
                    # create a sibling .chaosdiff next to the 'A' file for traceability
                    base = os.path.splitext(os.path.splitext(os.path.basename(path_a))[0])[0]
                    out = os.path.join(os.path.dirname(path_a), f"{base}.savvy.diff.chaos")
                    with open(out, "w", encoding="utf-8") as df:
                        df.write(make_chaosdiff(agent_name, diff))
                total += 1

    if journal_chunks:
        write_journal(settings["journal_path"], "\\n".join(journal_chunks))
        print(f"[Savvy] Wrote observations for {total} comparisons → {settings['journal_path']}")
    else:
        print("[Savvy] No matches found; journal unchanged.")
    return total

if __name__ == "__main__":
    run_savvy()
