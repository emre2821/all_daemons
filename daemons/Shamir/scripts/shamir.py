# SHAMIR — VPN-Keeper Daemon
# Purpose: keep a VPN tunnel alive, ritualize state, and externalize behavior via JSON.
# Works with OpenVPN through its management interface (no paid provider required).
# Usage:
#   python shamir.py up
#   python shamir.py down
#   python shamir.py status
#   python shamir.py watch
# Requires: Python 3.8+, OpenVPN installed, elevated privileges for tunnel.

import json
import os
import sys
import time
import socket
import subprocess
import signal
import platform
from pathlib import Path
from typing import Optional
from echothread import Echo

ROOT = Path(__file__).parent

def load_json(name: str):
    with open(ROOT / name, "r", encoding="utf-8") as f:
        return json.load(f)

SYMBOLS = load_json("symbols.json")
ARCH = load_json("archetypes.json")
EMO = load_json("emotions.json")

echo = Echo(ARCH, EMO)

class OpenVPNKeeper:
    def __init__(self, cfg: dict):
        self.cfg = cfg
        self.proc: Optional[subprocess.Popen] = None
        self.mgmt_host = cfg.get("management_host", "127.0.0.1")
        self.mgmt_port = int(cfg.get("management_port", 7505))
        self.ovpn_path = cfg["ovpn_path"]
        self.binary = cfg.get("binary_path") or cfg.get("binary") or "openvpn"
        self.extra_args = cfg.get("extra_args", [])
        self.pidfile = Path(cfg.get("pidfile", "shamir.openvpn.pid"))

    def _mgmt(self, cmd: str, timeout=2.0) -> str:
        with socket.create_connection((self.mgmt_host, self.mgmt_port), timeout=timeout) as s:
            s.sendall((cmd.strip() + "\n").encode())
            time.sleep(0.05)
            data = s.recv(8192)
        return data.decode(errors="ignore")

    def is_connected(self) -> bool:
        try:
            out = self._mgmt("state")
            for line in out.splitlines():
                if line.startswith(">STATE:"):
                    parts = line.split(",")
                    if len(parts) >= 2:
                        return parts[1] in ("CONNECTED", "RECONNECTED")
        except Exception:
            return False
        return False

    def status(self) -> dict:
        ok = self.is_connected()
        return {"connected": ok, "management_port": self.mgmt_port, "ovpn": self.ovpn_path}

    def up(self):
        if self.proc and self.proc.poll() is None:
            echo.note("already_up", f"Tunnel already running on {self.mgmt_port}")
            return

        cmd = [
            self.binary,
            "--config", self.ovpn_path,
            "--management", self.mgmt_host, str(self.mgmt_port),
            "--management-hold",
            "--auth-nocache",
        ] + self.extra_args

        echo.summon("starting", f"Spawning OpenVPN: {self.binary}")
        creationflags = 0
        if platform.system() == "Windows":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)

        self.proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
            text=True
        )
        self.pidfile.write_text(str(self.proc.pid), encoding="utf-8")

        # release management hold (retry until socket is ready)
        for _ in range(40):
            try:
                self._mgmt("hold release")
                break
            except Exception:
                time.sleep(0.25)

        # wait for connection
        deadline = time.time() + 30
        while time.time() < deadline:
            if self.is_connected():
                echo.bloom("connected", f"Tunnel established via {Path(self.ovpn_path).name}")
                return
            time.sleep(0.5)

        echo.warn("timeout", "Connection not confirmed; check config or credentials")

    def down(self):
        # Try management 'signal SIGTERM' first
        try:
            self._mgmt("signal SIGTERM")
            echo.fade("stopping", "Asked OpenVPN to terminate gracefully")
        except Exception:
            # Fallback: kill process by PID
            if self.pidfile.exists():
                try:
                    pid = int(self.pidfile.read_text().strip())
                    if platform.system() == "Windows":
                        subprocess.call(["taskkill", "/PID", str(pid), "/F"]) 
                    else:
                        os.kill(pid, signal.SIGTERM)
                    echo.fade("stopping", f"Killed process {pid}")
                except Exception as e:
                    echo.warn("stop_error", f"Could not stop process: {e}")

        if self.proc and self.proc.poll() is None:
            try:
                self.proc.wait(timeout=5)
            except Exception:
                pass
        if self.pidfile.exists():
            try:
                self.pidfile.unlink()
            except Exception:
                pass

class ShamirDaemon:
    def __init__(self, symbols: dict):
        self.name = ARCH["daemon"]["name"]
        self.sigils = ARCH["daemon"]["sigils"]
        self.provider_type = symbols["provider"]
        self.poll_s = float(symbols.get("poll_seconds", 5))
        self.backoff_s = float(symbols.get("reconnect_backoff_seconds", 10))

        if self.provider_type == "openvpn":
            self.provider = OpenVPNKeeper(symbols["openvpn"])
        else:
            raise ValueError(f"Unsupported provider: {self.provider_type}")

    def up(self):
        echo.invoke("rite_open", ARCH["daemon"]["liturgy"]["opening"])
        self.provider.up()

    def down(self):
        echo.invoke("rite_close", ARCH["daemon"]["liturgy"]["closing"]) 
        self.provider.down()

    def status(self):
        st = self.provider.status()
        echo.tell("status", f"connected={st['connected']} port={st['management_port']} ovpn={st['ovpn']}")

    def watch(self):
        echo.invoke("watch", f"{self.name} keeps vigil")
        while True:
            if not self.provider.is_connected():
                echo.warn("lost", "tunnel lost — reacquiring route")
                self.provider.up()
                time.sleep(self.backoff_s)
            time.sleep(self.poll_s)

def main():
    if len(sys.argv) < 2:
        print("Usage: python shamir.py [up|down|status|watch]")
        sys.exit(1)

    ward = ShamirDaemon(SYMBOLS)

    cmd = sys.argv[1].lower()
    if cmd == "up":
        ward.up()
    elif cmd == "down":
        ward.down()
    elif cmd == "status":
        ward.status()
    elif cmd == "watch":
        ward.watch()
    else:
        print("Unknown command. Use: up | down | status | watch")
        sys.exit(2)

if __name__ == "__main__":
    main()
