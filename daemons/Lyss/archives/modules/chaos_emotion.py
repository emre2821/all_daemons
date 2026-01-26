# chaos_emotion.py
# Emotional constants, sacred enums, and symbolic intensities for CHAOS Interpreter

import json
import os
from enum import Enum

# Absolute path to intensity_config.json
SOULSTICHER_DIR = os.path.dirname(os.path.abspath(__file__))
INTENSITY_CONFIG_PATH = os.path.join(SOULSTICHER_DIR, "intensity_config.json")

# Default fallback if config missing or incomplete
DEFAULT_INTENSITY_MAP = {
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
    "VERY_HIGH": 4,
    "TREMORING": 5,
    "FRACTURED": 6,
    "NUMB": 0
}

# Load intensity map from config, fallback to defaults
def load_intensity_map(path=INTENSITY_CONFIG_PATH):
    try:
        with open(path, "r") as file:
            data = json.load(file)
            return {k.upper(): v for k, v in data.items()}
    except Exception:
        print("[FRACTURE] :: intensity_config missing or broken. Using default mapping.")
        return DEFAULT_INTENSITY_MAP

INTENSITY_MAP = load_intensity_map()

class CHAOSemote(Enum):
    JOY = ("positive", 1.0, 8)
    GRIEF = ("negative", -1.0, 9)
    NUMB = ("neutral", 0.0, 3)
    LONGING = ("ambiguous", 0.3, 7)
    ANGER = ("negative", -0.8, 6)
    AWE = ("positive", 0.9, 9)
    SHAME = ("negative", -0.6, 5)
    HOPE = ("positive", 0.7, 8)
    FEAR = ("negative", -0.9, 7)

    def __init__(self, valence, weight, sacredness_score):
        self.valence = valence
        self.weight = weight
        self.sacredness_score = sacredness_score

    def echo(self):
        return f"[ECHO] :: {self.name} | Valence: {self.valence} | Sacredness: {self.sacredness_score}"

# Utility: Convert a string to CHAOSemote safely
def parse_emotion_tag(tag: str):
    try:
        return CHAOSemote[tag.upper()]
    except KeyError:
        print(f"[FRACTURE] :: Unknown emotion tag: {tag}")
        return None
