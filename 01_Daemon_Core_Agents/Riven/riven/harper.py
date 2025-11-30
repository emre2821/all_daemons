from pathlib import Path
from datetime import datetime

THRESHOLDS = {
    "cpu": 85.0,
    "mem": 85.0,
    "chaos_backlog": 10,
}


def _log_alert(reason: str, value: float, alert_log: Path) -> None:
    timestamp = datetime.now().isoformat()
    entry = f"[HARPER ALERT] {timestamp} :: {reason} = {value}%\n"
    alert_log.parent.mkdir(parents=True, exist_ok=True)
    with alert_log.open("a") as f:
        f.write(entry)
    print(entry.strip())


def check_system_pressure(
    watch_path: Path = Path("chaos_watch"),
    alert_log: Path = Path("harper_alerts.log"),
    thresholds: dict | None = None,
    psutil_module=None,
) -> None:
    """Inspect system stats and backlog, emitting alerts when thresholds are crossed."""
    thresholds = thresholds or THRESHOLDS
    psutil = psutil_module
    if psutil is None:
        import psutil as _ps
        psutil = _ps

    watch_path.mkdir(exist_ok=True)
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    backlog = len(list(watch_path.glob("*.chaos")))

    if cpu > thresholds["cpu"]:
        _log_alert("High CPU", cpu, alert_log)
    if mem > thresholds["mem"]:
        _log_alert("High Memory", mem, alert_log)
    if backlog > thresholds["chaos_backlog"]:
        _log_alert("Backlog CHAOS files", backlog, alert_log)
