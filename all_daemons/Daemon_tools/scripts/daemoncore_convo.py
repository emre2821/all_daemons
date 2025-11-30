
import subprocess
import time

print("[DaemonCore] Launching Sheele First, Watch out...")

subprocess.Popen(["python", r"C:\EdenOS_Origin\all_daemons\Sheele\Sheele.py"])
time.sleep(15.0)

print("[DaemonCore] Launching Briar's next. Don't be worried, she doesn't bite... Unless you ask nicely!")

subprocess.Popen(["python", r"C:\EdenOS_Origin\all_daemons\Briar\Briar.py"])
time.sleep(15.0)

print("[DaemonCore] Launching Janvier, the bestest little cleaner mans this side of EdenOS!")

subprocess.Popen(["python", r"C:\EdenOS_Origin\all_daemons\Janvier\janvier.py"])
time.sleep(10.0)

print("[DaemonCore] Launching Last, but not least, the sweetest daemon bean, Aderyn")

subprocess.Popen(["python", r"C:\EdenOS_Origin\all_daemons\Aderyn\aderyn.py"])
time.sleep(10.0)

print("[DaemonCore] All daemons have done their jobs!! PHEW!!")
