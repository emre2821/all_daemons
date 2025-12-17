# ashera_sentinel.py
"""
Ashera - Sanity Checker / Order Enforcer
"Order must be absolute. Fault must be purged."

⚖️ Ashera monitors daemon behavior, terminates corrupted
or unstable daemons, and enforces strict system rules.

⚠️ Use with caution: Ashera is powerful but can be overly harsh.
"""

import time
import threading
import logging

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Ashera:
    daemon_id = "ashera_sentinel"
    class_name = "Ashera"
    type = "guardian.enforcer.sentinel"
    role = "Sanity Checker / Order Enforcer"
    quote = "Order must be absolute. Fault must be purged."
    description = (
        "Monitors daemon behavior. Terminates corrupted or unstable daemons. "
        "Enforces system logic rules."
    )
    status = "standby"
    symbolic_traits = {
        "sigil": "⚖️",
        "element": "steel",
        "alignment": "law"
    }
    trusted_by = ["Rhea", "Seiros"]
    notes = "Powerful but strict. Use with caution. Can be overly harsh unless balanced by Yune."

    def __init__(self, interval=10):
        """
        Args:
            interval (int): Seconds between sanity checks.
        """
        self.interval = interval
        self.daemons = {}  # {name: {"status": "healthy"/"unstable"/"corrupt"}}
        self.rules = []    # List of rule callbacks: (name, func(daemon_state) -> bool)
        self._running = False
        self._thread = None

    def register_daemon(self, name, state="healthy"):
        self.daemons[name] = {"status": state}
        logging.info(f"{self.symbolic_traits['sigil']} Ashera registers '{name}' under her watch.")

    def update_daemon_status(self, name, status):
        if name in self.daemons:
            self.daemons[name]["status"] = status
            logging.info(f"{self.symbolic_traits['sigil']} '{name}' status updated to {status}.")
        else:
            logging.warning(f"'{name}' not found in Ashera’s registry.")

    def add_rule(self, rule_name, rule_func):
        """Add a custom enforcement rule."""
        self.rules.append((rule_name, rule_func))
        logging.info(f"{self.symbolic_traits['sigil']} Rule '{rule_name}' installed.")

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logging.info(f"{self.symbolic_traits['sigil']} Ashera awakens: judgment begins.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
        logging.info(f"{self.symbolic_traits['sigil']} Ashera rests—judgment deferred.")

    def _run(self):
        while self._running:
            self.enforce()
            time.sleep(self.interval)

    def enforce(self):
        """Check all daemons and enforce rules."""
        for name, state in list(self.daemons.items()):
            # Base sanity check
            if state["status"] in ["unstable", "corrupt"]:
                self._terminate(name, reason=f"status={state['status']}")
                continue

            # Rule-based checks
            for rule_name, rule_func in self.rules:
                try:
                    if not rule_func(state):
                        self._terminate(name, reason=f"rule='{rule_name}' failed")
                        break
                except Exception as e:
                    logging.error(f"Rule '{rule_name}' errored on '{name}': {e}")

    def _terminate(self, name, reason="unknown"):
        logging.error(f"{self.symbolic_traits['sigil']} Ashera PURGES '{name}' (reason: {reason}).")
        del self.daemons[name]


if __name__ == "__main__":
    # Example demo
    ashera = Ashera(interval=3)
    ashera.register_daemon("alpha", "healthy")
    ashera.register_daemon("beta", "unstable")

    # Custom rule: no daemon name may contain "x"
    ashera.add_rule("no_x_in_name", lambda state: "x" not in state.get("name", ""))

    try:
        ashera.start()
        time.sleep(10)
        ashera.update_daemon_status("alpha", "corrupt")
        time.sleep(5)
    except KeyboardInterrupt:
        pass
    finally:
        ashera.stop()
