
import subprocess
import time

try:
    from .eden_paths import eden_root
except Exception:
    from eden_paths import eden_root  # type: ignore

ROOT = eden_root()
DAEMONS = ROOT / "daemons"

print("[DaemonCore] Launching Sheele First, Watch out...")

subprocess.Popen(["python", str(DAEMONS / "Sheele" / "Sheele.py")])
time.sleep(15.0)

print("[DaemonCore] Launching Briar's next. Don't be worried, she doesn't bite... Unless you ask nicely!")

subprocess.Popen(["python", str(DAEMONS / "Briar" / "Briar.py")])
time.sleep(15.0)

print("[DaemonCore] Launching Janvier, the bestest little cleaner mans this side of EdenOS!")

subprocess.Popen(["python", str(DAEMONS / "Janvier" / "janvier.py")])
time.sleep(10.0)

print("[DaemonCore] Launching Last, but not least, the sweetest daemon bean, Aderyn")

subprocess.Popen(["python", str(DAEMONS / "Aderyn" / "aderyn.py")])
time.sleep(10.0)

print("[DaemonCore] All daemons have done their jobs!! PHEW!!")
