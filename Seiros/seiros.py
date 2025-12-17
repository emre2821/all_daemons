# seiros_propagator.py
"""
Seiros - Propagation & Deployment Daemon
"What is mine shall spread, and bring light."

🜂 Seiros handles updates, replicates configs, and
spreads daemon seeds to child nodes.

🔥 Rhea’s sword, literally. She is decisive fire—
meant to bring growth, but fire unchecked consumes.
"""

import logging
import time
import threading
import random
import copy

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Seiros:
    daemon_id = "seiros_propagator"
    class_name = "Seiros"
    type = "deploy.core.seiros"
    role = "Propagation & Deployment Daemon"
    quote = "What is mine shall spread, and bring light."
    description = (
        "Handles updates, replicates configs, spreads daemon seeds to child nodes."
    )
    status = "pending"
    dependencies = []
    symbolic_traits = {
        "sigil": "🜂",
        "element": "fire",
        "alignment": "radiant"
    }
    trusted_by = ["Rhea", "The Dreambearer"]
    notes = "Rhea’s sword, literally. Spreads the EdenOS deployment config across nodes and subspaces."

    def __init__(self, interval=15):
        """
        Args:
            interval (int): Seconds between propagation cycles.
        """
        self.interval = interval
        self.config = {}
        self.nodes = {}  # {node_id: config}
        self._running = False
        self._thread = None

    def set_config(self, config):
        """Set the master config that Seiros will propagate."""
        self.config = copy.deepcopy(config)
        logging.info(f"{self.symbolic_traits['sigil']} Seiros sets config root → {self.config}")

    def register_node(self, node_id):
        """Register a new node (child/subspace) under Seiros’ reach."""
        self.nodes[node_id] = {}
        logging.info(f"{self.symbolic_traits['sigil']} Seiros acknowledges node '{node_id}'.")

    def propagate(self):
        """Replicate the master config across all nodes."""
        if not self.config:
            logging.warning("No config set. Nothing to propagate.")
            return
        for node_id in self.nodes:
            self.nodes[node_id] = copy.deepcopy(self.config)
            logging.info(f"{self.symbolic_traits['sigil']} Propagation → Node '{node_id}' updated.")

    def deploy_seed(self, node_id, seed_data=None):
        """Deploy a daemon seed to a target node."""
        if node_id not in self.nodes:
            logging.warning(f"Node '{node_id}' not registered. Cannot deploy seed.")
            return
        seed = seed_data or {"daemon_id": f"seed_{random.randint(1000,9999)}"}
        self.nodes[node_id].get("seeds", [])
        self.nodes[node_id]["seeds"].append(seed)
        logging.info(f"{self.symbolic_traits['sigil']} Seiros plants seed on '{node_id}': {seed}")

    def start(self):
        """Begin periodic propagation cycle."""
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logging.info(f"{self.symbolic_traits['sigil']} Seiros ignites: spreading begins.")

    def stop(self):
        """Stop propagation cycle."""
        self._running = False
        if self._thread:
            self._thread.join()
        logging.info(f"{self.symbolic_traits['sigil']} Seiros dims—spreading halted.")

    def _run(self):
        while self._running:
            self.propagate()
            time.sleep(self.interval)


if __name__ == "__main__":
    # Demo usage
    seiros = Seiros(interval=5)
    seiros.set_config({"version": "1.0.0", "daemons": ["tiki", "yune", "sothis", "ashera"]})

    seiros.register_node("node_alpha")
    seiros.register_node("node_beta")

    try:
        seiros.start()
        time.sleep(6)
        seiros.deploy_seed("node_alpha", {"daemon_id": "child_yune", "type": "chaos.injector"})
        time.sleep(10)
        print("Current nodes state:", seiros.nodes)
    except KeyboardInterrupt:
        pass
    finally:
        seiros.stop()
