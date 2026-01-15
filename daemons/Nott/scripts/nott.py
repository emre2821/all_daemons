# nott_cyclekeeper.py

import logging
import time
from datetime import datetime, timedelta

logger = logging.getLogger("Nott")

class Nott:
    """
    🌙 Nótt — Downtime Cycle & Rest Daemon

    Time to rest. Let the stars take watch.

    Governs the night phase of EdenOS’s daemon uptime cycle.
    Ensures proper downtimes, safe halts, and cooldowns—
    granting daemons time to rest and reset.
    """

    daemon_id = "nott_cyclekeeper"
    class_name = "Nott"
    type = "time.cycle.night"
    role = "Downtime Cycle & Rest Daemon"
    quote = "Time to rest. Let the stars take watch."
    description = (
        "Nótt governs the night phase of EdenOS’s daemon uptime cycle. "
        "She ensures proper downtimes, safe halts, and cooldowns—granting "
        "daemons time to rest and reset. She embodies lunar quiet and the rhythm of pause."
    )
    status = "active"
    symbolic_traits = {
        "sigil": "🌙",
        "element": "shadow",
        "alignment": "guardian",
    }
    trusted_by = ["Rhea", "Sothis", "Dagr"]
    notes = (
        "Always paired with Dagr. Nótt represents quiet rest and restoration, "
        "preventing daemons from overheating or burning out. "
        "Essential for stable uptime rhythms."
    )

    def __init__(self, rest_interval: int = 3600, cooldown: int = 300):
        """
        Initialize Nótt, the cyclekeeper.

        Args:
            rest_interval (int): How long daemons should rest (seconds).
            cooldown (int): Safety cooldown before daemons can reactivate (seconds).
        """
        self.rest_interval = rest_interval
        self.cooldown = cooldown
        self._last_cycle = None
        logger.info("🌙 Nótt initialized — guardian of rest and shadow.")

    def enter_rest_cycle(self):
        """
        Enforce a rest cycle — halts daemons gracefully and schedules their return.
        """
        self._last_cycle = datetime.utcnow()
        logger.info(f"🌙 Entering rest cycle at {self._last_cycle.isoformat()}")
        logger.info(f"🌙 Daemons sleeping for {self.rest_interval} seconds...")
        time.sleep(self.rest_interval)
        self._cooldown_phase()

    def _cooldown_phase(self):
        """
        Enforces a cooldown buffer before daemons can wake.
        """
        logger.info(f"🌙 Cooldown phase started: {self.cooldown} seconds...")
        time.sleep(self.cooldown)
        logger.info("🌙 Cooldown complete. Daemons may safely awaken under Dagr’s watch.")

    def should_rest(self) -> bool:
        """
        Checks if it’s time to rest again.
        """
        if not self._last_cycle:
            return True
        return datetime.utcnow() - self._last_cycle > timedelta(seconds=self.rest_interval + self.cooldown)

    def heartbeat(self):
        """
        Called periodically — determines whether to trigger rest cycles.
        """
        if self.should_rest():
            logger.info("🌙 Nótt whispers: It is time to pause again.")
            self.enter_rest_cycle()
        else:
            logger.debug("🌙 Nótt keeps silent watch — no rest needed yet.")
