# --- systemd.py ---
from pathlib import Path
UNIT_TMPL = """[Unit]
Description=Shamir — VPN-Keeper
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory={workdir}
ExecStart=/usr/bin/env python3 {workdir}/shamir.py watch
Restart=always
RestartSec=5
User={user}

[Install]
WantedBy=multi-user.target
"""

def write_unit(path: Path, workdir: Path, user: str = "root"):
    path.write_text(UNIT_TMPL.format(workdir=workdir, user=user), encoding="utf-8")
    return path
