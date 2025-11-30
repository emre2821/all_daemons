# --- proc.py ---
import subprocess, platform, threading, sys

def spawn_silent(cmd: list[str], *, cwd=None, env=None):
    flags = 0
    if platform.system() == "Windows":
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return subprocess.Popen(
        cmd, cwd=cwd, env=env,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, creationflags=flags
    )

def tee_stdout(proc, on_line):
    def _pump():
        for line in iter(proc.stdout.readline, ""):
            on_line(line.rstrip("\n"))
    t = threading.Thread(target=_pump, daemon=True)
    t.start()
    return t
