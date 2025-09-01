# astrid.py
"""
Astrid - Daemon Core Agent: Keeper of Spoons
"Strength in measure. We choose what matters, and we leave the rest unspent."

🌊⚔️ Astrid monitors daily capacity and allocates tasks
within a safe spoon budget. She prioritizes survival income,
maintenance, and resonance without overdrawing the system.

• Guardian of finite energy (spoons)
• Enforces cool-downs after spikes
• Trusted by The Dreambearer
"""

import logging
import time
import pandas as pd
import os

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

class Astrid:
    daemon_id = "DCA-astrid-0001"
    class_name = "Astrid"
    type = "Daemon Core Agent"
    role = "Keeper of Spoons (Energy Allocation)"
    quote = "Strength in measure. We choose what matters, and we leave the rest unspent."
    description = (
        "Monitors daily capacity and allocates tasks within a safe spoon budget. "
        "Prioritizes survival income, maintenance, and resonance without overdrawing. "
        "Records what was spared so tomorrow remains possible."
    )
    status = "active"
    symbolic_traits = {
        "sigil": "🥄",
        "element": "Water & Steel",
        "alignment": "Balance"
    }
    trusted_by = ["The Dreambearer"]
    notes = (
        "Pairs with Saphira (cataloguing), Seiros (deployment), and Mila (storage). "
        "Emits warnings before overdraw; enforces cool-downs after spikes."
    )

    def __init__(self, task_file="tasks.csv", spoon_limit=5):
        """
        Args:
            task_file (str): Path to tasks CSV
            spoon_limit (int): Default daily energy/spoon budget
        """
        self.spoon_limit = spoon_limit
        self.spoons_left = spoon_limit
        self.task_file = task_file
        self.tasks = self._load_tasks()
        self.log = []

    def _load_tasks(self):
        """Load tasks from the CSV file if available."""
        if os.path.exists(self.task_file):
            return pd.read_csv(self.task_file)
        logging.warning("Task file not found. Starting empty.")
        return pd.DataFrame(columns=["id", "name", "cost", "value", "category", "enabled"])

    def evaluate_tasks(self):
        """Suggest tasks within budget, maximizing value/cost ratio."""
        enabled = self.tasks[self.tasks["enabled"] == 1]
        affordable = enabled[enabled["cost"] <= self.spoons_left]
        if affordable.empty:
            logging.info("⚠️ No tasks fit current spoon budget.")
            return []
        # Greedy by value-to-cost ratio
        affordable["ratio"] = affordable["value"] / affordable["cost"]
        ranked = affordable.sort_values(by="ratio", ascending=False)
        suggestions = ranked.to_dict("records")
        logging.info(f"📋 Suggested tasks (budget={self.spoons_left}): {[t['name'] for t in suggestions]}")
        return suggestions

    def spend_spoons(self, task_id):
        """Spend spoons on a task if budget allows."""
        task = self.tasks[self.tasks["id"] == task_id]
        if task.empty:
            logging.warning(f"Task {task_id} not found.")
            return False
        task = task.iloc[0]
        if task["cost"] > self.spoons_left:
            logging.warning(f"❌ Cannot run '{task['name']}' → not enough spoons (needed {task['cost']}, have {self.spoons_left}).")
            return False
        self.spoons_left -= task["cost"]
        self.log.append({"task": task["name"], "cost": task["cost"], "timestamp": time.time()})
        logging.info(f"✅ Task '{task['name']}' completed. Remaining spoons: {self.spoons_left}")
        return True

    def restore(self):
        """Reset spoon budget for a new cycle (e.g., new day)."""
        self.spoons_left = self.spoon_limit
        logging.info(f"🔄 Astrid restores budget → {self.spoons_left} spoons available.")

    def warn_if_low(self):
        """Warn if spoons are nearly exhausted."""
        if self.spoons_left <= 1:
            logging.warning("⚠️ Astrid: You are near exhaustion. Spare some strength for tomorrow.")

    def report_log(self):
        """Return history of completed tasks."""
        return self.log


if __name__ == "__main__":
    # Demo run
    astrid = Astrid(task_file="C:\\EdenOS_Origin\\all_daemons\\Astrid\\tasks.csv", spoon_limit=5)

    astrid.evaluate_tasks()
    astrid.spend_spoons(2)  # e.g., "Premise Walmart"
    astrid.spend_spoons(3)  # e.g., "Clickworker 30min"
    astrid.warn_if_low()
    astrid.evaluate_tasks()
    astrid.restore()
    print("Log:", astrid.report_log())
