#!/usr/bin/env python
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

try:
    from .eden_paths import eden_root, daemons_root, events_bus_path
    from .eden_discovery import discover, describe
    from .eden_safety import SafetyContext, log_event
except Exception:
    # Allow running as a plain script without package context
    import importlib.util as _ilu
    import pathlib as _pl
    _HERE = _pl.Path(__file__).resolve().parent
    if str(_HERE) not in sys.path:
        sys.path.append(str(_HERE))
    from eden_paths import eden_root, daemons_root, events_bus_path  # type: ignore
    from eden_discovery import discover, describe  # type: ignore
    from eden_safety import SafetyContext, log_event  # type: ignore


def _print_table(rows):
    # Simple text table: name, role, safety_level, status
    headers = ["name", "role", "safety", "status"]
    records = [{"name": r["name"], "role": r["role"], "safety": r.get("safety_level", ""), "status": r.get("status", "")}
               for r in rows]
    baseline = dict(zip(headers, headers))
    widths = []
    for c in headers:
        widths.append(max(len(str(x.get(c, ""))) for x in records + [baseline]))
    def fmt(r):
        return "  ".join(str(r.get(c, "")).ljust(w) for c, w in zip(headers, widths))
    print(fmt(baseline))
    print("  ".join("-" * w for w in widths))
    for r in records:
        print(fmt(r))


def cmd_list(_args) -> int:
    infos = [d.to_dict() for d in discover()]
    _print_table(infos)
    return 0


def cmd_describe(args) -> int:
    info = describe(args.name)
    if not info:
        print(f"Daemon '{args.name}' not found.")
        return 1
    print(json.dumps(info, indent=2))
    return 0


def _run_script(script: Path, pass_args: list[str]) -> int:
    # Launch with same Python
    env = os.environ.copy()
    env.setdefault("EDEN_ROOT", str(eden_root()))
    proc = subprocess.run([sys.executable, str(script), *pass_args], env=env)
    return proc.returncode


def _map_common_args(args) -> list[str]:
    out: list[str] = []
    # We pass a conventional set of flags that patched daemons understand
    if args.log_dir:
        out += ["--log-dir", args.log_dir]
    if args.scope:
        out += ["--scope", args.scope]
    if args.include:
        out += ["--include", args.include]
    if args.exclude:
        out += ["--exclude", args.exclude]
    if args.config:
        out += ["--config", args.config]
    if args.dry_run and not args.confirm:
        out += ["--dry-run"]
    if args.confirm:
        out += ["--confirm"]
    return out


def cmd_run(args) -> int:
    info = describe(args.name)
    if not info or not info.get("script"):
        print(f"Daemon '{args.name}' missing or has no runnable script.")
        return 1

    # safety-by-default
    dry_run = not args.confirm if args.dry_run is None else args.dry_run
    ctx = SafetyContext(daemon=info["name"], dry_run=dry_run, confirm=args.confirm)
    ctx.require_confirm()
    log_event(info["name"], action="launch", target=info.get("script") or "", outcome="start",
              extra={"dry_run": ctx.dry_run, "confirm": ctx.confirm})

    argv = _map_common_args(args)
    rc = _run_script(Path(info["script"]), argv)
    log_event(info["name"], action="launch", target=info.get("script") or "", outcome=f"exit:{rc}")
    return rc


def cmd_watch(args) -> int:
    # Delegates to the daemon script; patched watchers accept --watch
    info = describe(args.name)
    if not info or not info.get("script"):
        print(f"Daemon '{args.name}' missing or has no runnable script.")
        return 1
    dry_run = not args.confirm if args.dry_run is None else args.dry_run
    ctx = SafetyContext(daemon=info["name"], dry_run=dry_run, confirm=args.confirm)
    ctx.require_confirm()
    argv = _map_common_args(args) + ["--watch"]
    log_event(info["name"], action="watch", target=info.get("script") or "", outcome="start",
              extra={"dry_run": ctx.dry_run, "confirm": ctx.confirm})
    rc = _run_script(Path(info["script"]), argv)
    log_event(info["name"], action="watch", target=info.get("script") or "", outcome=f"exit:{rc}")
    return rc


def _iter_events():
    p = events_bus_path()
    if not p.exists():
        return []
    out = []
    with p.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except Exception:
                continue
    return out


def cmd_tail(args) -> int:
    filt_d = (args.daemon or "").lower()
    filt_a = (args.action or "").lower()
    def show(e):
        d = e.get("daemon", "")
        a = e.get("action", "")
        if filt_d and d.lower() != filt_d:
            return False
        if filt_a and a.lower() != filt_a:
            return False
        print(f"[{d}] {a} -> {e.get('target','')} ({e.get('outcome','')})" + (f" err={e.get('error')}" if e.get('error') else ""))
        return True
    for e in _iter_events():
        show(e)
    if args.follow:
        path = events_bus_path()
        with path.open("r", encoding="utf-8") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if not line:
                    try:
                        import time as _t
                        _t.sleep(0.5)
                        continue
                    except KeyboardInterrupt:
                        break
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                show(e)
    return 0


def cmd_report(args) -> int:
    from datetime import datetime, date
    rows = _iter_events()
    if args.daemon:
        rows = [r for r in rows if r.get("daemon","" ).lower() == args.daemon.lower()]
    if args.daily:
        today = date.today().isoformat()
        # if entries had timestamp, we would filter; we aggregate anyway
    agg: dict = {}
    for r in rows:
        key = (r.get("daemon",""), r.get("outcome",""))
        agg[key] = agg.get(key, 0) + 1
    print("daemon        outcome     count")
    print("------------  ----------  -----")
    for (d, o), c in sorted(agg.items()):
        print(f"{d:12}  {o:10}  {c}")
    print(f"Total events: {len(rows)}")
    return 0


def cmd_doctor(args) -> int:
    infos = discover()
    print("name        script     describe  healthcheck  status  notes")
    print("----------  ---------  --------  -----------  ------  -----")
    for info in infos:
        name = info.name
        script = info.script
        desc_ok = "no"; hc_ok = "no"; status = "ok"; notes = []
        mod = None
        if script and Path(script).exists():
            try:
                import importlib.util as ilu
                spec = ilu.spec_from_file_location(f"eden.daemon.{name}", script)
                if spec and spec.loader:
                    mod = ilu.module_from_spec(spec)
                    spec.loader.exec_module(mod)  # type: ignore
            except Exception as e:
                status = "warn"; notes.append(f"import: {e}")
        else:
            status = "warn"; notes.append("missing script")
        if mod is not None:
            desc_ok = "yes" if callable(getattr(mod, "describe", None)) else "no"
            hc_fn = getattr(mod, "healthcheck", None)
            hc_ok = "yes" if callable(hc_fn) else "no"
            if callable(hc_fn):
                try:
                    res = hc_fn()
                    if isinstance(res, dict):
                        notes.append(res.get("notes",""))
                        if res.get("status") in ("warn","fail"):
                            status = res.get("status")
                except Exception as e:
                    status = "warn"; notes.append(f"hc err: {e}")
        print(f"{name:10}  {('yes' if script else 'no'):9}  {desc_ok:8}  {hc_ok:11}  {status:6}  {'; '.join([n for n in notes if n])}")

    if args.fix:
        try:
            import importlib.util as ilu
            saphira_path = daemons_root() / "Saphira" / "scripts" / "saphira.py"
            spec = ilu.spec_from_file_location("eden.saphira", saphira_path)
            if spec and spec.loader:
                mod = ilu.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
                Sync = getattr(mod, "SaphiraSynchronizer", None)
                if Sync:
                    Sync(str(daemons_root())).run(audit=True, force=True)
                    print("Saphira auto-fix complete.")
        except Exception as e:
            print(f"Saphira fix failed: {e}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="eden-daemon", description="Eden Daemon CLI")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("list", help="List discovered daemons")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("describe", help="Describe a daemon")
    sp.add_argument("name")
    sp.set_defaults(func=cmd_describe)

    def add_common_flags(sp_):
        sp_.add_argument("name")
        sp_.add_argument("--config")
        sp_.add_argument("--scope")
        sp_.add_argument("--include")
        sp_.add_argument("--exclude")
        sp_.add_argument("--log-dir")
        sp_.add_argument("--dry-run", action="store_true", default=None,
                         help="Plan only (default unless --confirm)")
        sp_.add_argument("--confirm", action="store_true", help="Execute changes")

    sp = sub.add_parser("run", help="Run a daemon once")
    add_common_flags(sp)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("watch", help="Run a daemon in watch mode")
    add_common_flags(sp)
    sp.set_defaults(func=cmd_watch)

    # doctor
    sp = sub.add_parser("doctor", help="Check daemons for readiness")
    sp.add_argument("--fix", action="store_true", help="Attempt to auto-fix manifests via Saphira")
    sp.set_defaults(func=cmd_doctor)

    # tail events
    sp = sub.add_parser("tail", help="Tail events bus")
    sp.add_argument("--daemon", help="Filter by daemon name")
    sp.add_argument("--action", help="Filter by action")
    sp.add_argument("--follow", action="store_true")
    sp.set_defaults(func=cmd_tail)

    # report
    sp = sub.add_parser("report", help="Summarize events")
    sp.add_argument("--daily", action="store_true", help="Summary for today")
    sp.add_argument("--since", help="ISO date/time to start from")
    sp.add_argument("--daemon", help="Filter by daemon")
    sp.set_defaults(func=cmd_report)

    return p


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "cmd", None):
        parser.print_help()
        return 2
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
