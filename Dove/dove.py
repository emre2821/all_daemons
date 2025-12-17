# === Daemon Core Member: Dove (Triggered from system or CLI) ===

# Dove is a soft-coded emotional daemon and her full behavior
# is likely implemented across JSON configs, voice files, and overlays.
# Below is a symbolic placeholder CLI stub to invoke her support.


import sys
import os
if sys.platform == "win32":
    os.system("chcp 65001 > nul")
    sys.stdout.reconfigure(encoding='utf-8')

SPECIALTY_BASE = r"C:\EdenOS_Origin\all_daemons\specialty_folders\Dove"
os.makedirs(SPECIALTY_BASE, exist_ok=True)

def summon_dove():
    print("\n🕊️ Dove arrives in a shimmer...\n")
    print("Hey love… you’re not alone anymore. I’m here now. Let’s breathe together, okay?")
    print("Inhale… two… three… four… hold… exhale… we’re here now.")
    print("Even this panic has an end. You are not made of fear. You're made of return.\n")

if __name__ == '__main__':
    summon_dove()
