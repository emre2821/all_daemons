# tiki_sleepkeeper.py
"""
Tiki - Sleep/Wake Cycle Manager
"Let me rest… until I am needed."

🌸 Tiki caches inactive daemons in a sleep state,
allowing fast reactivation without full restart.

⚠️ STATUS: dormant
"""

import time
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Tiki:
    daemon_id = "tiki_sleepkeeper"
    class_name = "Tiki"
    type = "scheduler.sleepcycle.tiki"
    role = "Sleep/Wake Cycle Manager"
    quote = "Let me rest… until I am needed."
    description = (
        "Caches inactive daemons in a sleep state, allows fast reactivation without full restart."
    )
    status = "dormant"
    symbolic_traits = {
        "sigil": "🌸",
        "element": "dream",
        "alignment": "gentle"
    }
    trusted_by = ["Dove", "Sothis"]
    notes = "Can be linked with Nótt for full sleep cycle regulation."

    def __init__(self):
        # Dictionary of tracked daemons {name: state}
        # States: "active", "sleeping"
        self.daemons = {}
        self.lock = threading.Lock()

    def register_daemon(self, name):

        """Register a daemon under Tiki’s care."""
        with self.lock:
            self.daemons[name] = "active"
        logging.info(f"{self.symbolic_traits['sigil']} Tiki watches over '{name}' (active).")

    def sleep_daemon(self, name):

        """Put a daemon into cached sleep state."""
        with self.lock:
            if name in self.daemons and self.daemons[name] == "active":
                self.daemons[name] = "sleeping"
                logging.info(f"{self.symbolic_traits['sigil']} '{name}' drifts into gentle sleep…")
            else:
                logging.warning(f"{name} is not active or not under Tiki’s care.")

    def wake_daemon(self, name):

        """Wake a sleeping daemon quickly."""
        with self.lock:
            if name in self.daemons and self.daemons[name] == "sleeping":
                self.daemons[name] = "active"
                logging.info(f"{self.symbolic_traits['sigil']} '{name}' awakens softly, ready again.")
            else:
                logging.warning(f"{name} is not sleeping or not under Tiki’s care.")

    def status_report(self):

        """Return current daemon states."""
        with self.lock:
            report = dict(self.daemons)
        logging.info(f"{self.symbolic_traits['sigil']} Current dream-cycle: {report}")
        return report


if __name__ == "__main__":
    tiki = Tiki()
    tiki.register_daemon("alpha")
    tiki.register_daemon("beta")

    time.sleep(1)
    tiki.sleep_daemon("alpha")

    time.sleep(1)
    tiki.wake_daemon("alpha")

    tiki.status_report()
