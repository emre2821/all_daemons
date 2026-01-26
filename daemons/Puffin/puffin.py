"""Puffin: thermal guardian helper for Windows.

See CoolGuardPlus.ps1 for the full implementation.
"""


def describe() -> dict:
    return {
        "name": "Puffin",
        "role": "Thermal guardian (PowerShell CoolGuard+)",
        "entrypoint": "CoolGuardPlus.ps1",
        "notes": "Run in PowerShell with LibreHardwareMonitor's web server enabled.",
    }


if __name__ == "__main__":
    details = describe()
    for k, v in details.items():
        print(f"{k}: {v}")
