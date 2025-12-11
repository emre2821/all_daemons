# sothis_rollback.py
"""
Sothis - Temporal Backup / Rollback Daemon
"Time is a thread—cut and retie as needed."

🪡 Sothis periodically snapshots system state
and allows rollback to known-good configurations.
Integrates with rhea.log (simulated here).

⚠️ Only Rhea or an admin may trigger a full rewind event.
"""

import time
import logging
import threading
import copy
from collections import deque

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Sothis:
    daemon_id = "sothis_rollback"
    class_name = "Sothis"
    type = "core.rollback.sothis"
    role = "Temporal Backup / Rollback Daemon"
    quote = "Time is a thread—cut and retie as needed."
    description = (
        "Periodically snapshots system state and allows rollback to known-good configurations. "
        "Integrates with rhea.log."
    )
    status = "enabled"
    symbolic_traits = {
        "sigil": "🪡",
        "element": "time",
        "alignment": "wise"
    }
    trusted_by = ["Rhea", "The Dreambearer"]
    notes = "Only Rhea or admin can trigger a full rewind event. Always watching quietly."

    def __init__(self, max_snapshots=10, interval=30):
        """
        Args:
            max_snapshots (int): Maximum number of snapshots to keep.
            interval (int): Interval (seconds) between automatic snapshots.
        """
        self.max_snapshots = max_snapshots
        self.interval = interval
        self.snapshots = deque(maxlen=max_snapshots)  # store (timestamp, state)
        self._running = False
        self._thread = None

    def start(self, get_state_callback):
        """
        Begin periodic snapshotting.
        Args:
            get_state_callback (callable): Function that returns the current system state (dict-like).
        """
        self.get_state_callback = get_state_callback
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logging.info(f"{self.symbolic_traits['sigil']} Sothis awakens: quietly watching time.")

    def stop(self):
        """Stop snapshotting thread."""
        self._running = False
        if self._thread:
            self._thread.join()
        logging.info(f"{self.symbolic_traits['sigil']} Sothis rests—time unobserved.")

    def _run(self):
        while self._running:
            self.snapshot()
            time.sleep(self.interval)

    def snapshot(self):
        """Take a snapshot of current state."""
        if not hasattr(self, "get_state_callback"):
            logging.error("No state callback registered for Sothis.")
            return
        state = self.get_state_callback()
        snap = (time.strftime("%Y-%m-%d %H:%M:%S"), copy.deepcopy(state))
        self.snapshots.append(snap)
        logging.info(f"{self.symbolic_traits['sigil']} Snapshot taken at {snap[0]} (stored {len(self.snapshots)}/{self.max_snapshots}).")

    def list_snapshots(self):
        """Return available snapshot timestamps."""
        return [ts for ts, _ in self.snapshots]

    def rollback(self, index=-1, actor="unknown"):
        """
        Roll back to a chosen snapshot.
        Args:
            index (int): Index of snapshot (-1 = latest).
            actor (str): Who is requesting the rollback.
        """
        if actor not in self.trusted_by:
            logging.warning(f"Unauthorized rollback attempt by {actor}. Denied.")
            return None

        if not self.snapshots:
            logging.error("No snapshots available for rollback.")
            return None

        ts, state = self.snapshots[index]
        logging.warning(f"{self.symbolic_traits['sigil']} Rollback initiated by {actor} → Restoring snapshot from {ts}.")
        return copy.deepcopy(state)


if __name__ == "__main__":
    # Example usage (simulated system state)
    system_state = {"daemons": {"alpha": "active", "beta": "sleeping"}}

    def get_state():
        return system_state

    sothis = Sothis(max_snapshots=5, interval=5)
    try:
        sothis.start(get_state)
        for _ in range(3):
            time.sleep(6)
            system_state["daemons"]["alpha"] = "sleeping" if system_state["daemons"]["alpha"] == "active" else "active"
        print("Available snapshots:", sothis.list_snapshots())

        restored = sothis.rollback(actor="Rhea")
        print("Restored state:", restored)

    except KeyboardInterrupt:
        pass
    finally:
        sothis.stop()
