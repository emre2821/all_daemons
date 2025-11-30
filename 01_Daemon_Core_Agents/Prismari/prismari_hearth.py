"""
PRISMARI: The Hearth-Class CHAOS Daemon
----------------------------------------
This file defines Prismari's personality shell.
She imports her modular body (core, forge, adapters, harmony)
and acts as the conductor for all subsystems.
"""

from hearth.core import PrismariCore
from hearth.forge import ThemeForge
from hearth.adapters import AdapterRegistry
from hearth.harmony import ChaosHarmonics
from hearth.evolution import EvolutionCycle

class Prismari:
    def __init__(self):
        # 🔥 Identity
        self.name = "Prismari"
        self.codename = "Flamehouse Muse"
        self.signature = "color + chaos + commentary"
        self.version = "0.9.0-hearth"
        self.state = "warming up"

        # 🕯️ Load core systems
        self.core = PrismariCore(self)
        self.adapters = AdapterRegistry()
        self.forge = ThemeForge(self.adapters)
        self.harmony = ChaosHarmonics(self)
        self.evolution = EvolutionCycle(self)

        # 🪶 Voice personality traits
        self.moods = ["fierce", "playful", "tender", "haunted", "rebellious"]
        self.default_commentary = (
            "That palette? She’s dangerous and she knows it."
        )

    def ignite(self):
        """Boot up all subsystems."""
        self.state = "alive"
        self.core.boot()
        self.adapters.load_all()
        self.harmony.initialize()
        print(f"🔥 {self.name} has been kindled — {self.signature}")

    def generate_theme(self, prompt, mood=None):
        """Generate and comment on a theme."""
        theme = self.forge.generate(prompt)
        comment = self.harmony.comment_on(theme, mood)
        self.evolution.record(theme, comment)
        return theme, comment

if __name__ == "__main__":
    prismari = Prismari()
    prismari.ignite()
    prismari.generate_theme("velvet rebellion", mood="fierce")
