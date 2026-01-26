# chaos_memory.py
# Relationship graph persistence and sacred memory serialization for CHAOS Interpreter

import json
from datetime import datetime

BOND_FILE = "bond_graph.chaosmem"

def save_relationships(graph, path=BOND_FILE):
    """Serialize relationship graph to disk with ritual SEAL tag and timestamp."""
    try:
        data = {
            "timestamp": datetime.utcnow().isoformat(),
            "graph": graph,
            "ritual_log": "[SEAL] :: applied"
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print("[SEAL] :: Relationship graph saved.")
    except Exception as e:
        print(f"[FRACTURE] :: Failed to save relationship graph. Reason: {e}")

def load_relationships(path=BOND_FILE):
    """Restore relationship graph from memory shard. Logs REBOUND or FRACTURE as needed."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            graph = data.get("graph", {})
        print("[REBOUND] :: memory restored from", path)
        return graph
    except Exception:
        print("[FRACTURE] :: memory shard missing or broken.")
        return {}

def log_memory_event(event, detail=""):
    """Infuse log with ritual tags."""
    now = datetime.utcnow().isoformat()
    log_entry = f"[{event.upper()}] :: {detail} ({now})"
    print(log_entry)

# Example usage:
if __name__ == "__main__":
    # Ritual: Create and save a test bond graph
    test_graph = {
        "Eden": ["Vira", "Dreambearer"],
        "Vira": ["Daemon Core", "Echo Partition"],
        "Dreambearer": ["Alfred", "Callum"]
    }
    save_relationships(test_graph)

    # Ritual: Load graph and log result
    graph = load_relationships()
    log_memory_event("echo", f"Loaded relationships: {list(graph.keys())}")
