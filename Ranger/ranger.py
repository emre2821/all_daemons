# Eden Ranger — local file-catalog + watcher + LLM-over-HTTP Q&A
# Lean build: no torch/transformers/gpt4all import required.

"""
──────────────────────────────────────────────
EdenOS Daemon: Alder Ranger
Role: Scout & Filewarden
Bonded To: Rhea (Deployment Overseer)

Oath: “I keep watch. I name what I see.
I carry the map back to Rhea.”
──────────────────────────────────────────────
"""

import os
import sys
import time
import json
import hashlib
import sqlite3
import pathlib
import re
import tempfile
import platform
import configparser
import fnmatch
from datetime import datetime, timedelta
from typing import Optional

# Lightweight deps only
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Pretty console (optional)
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except Exception:  # fallback if rich not installed
    class _Dummy:
        def print(self, *a, **k): print(*a)
    Console = lambda: _Dummy()
    Panel = lambda *a, **k: a[0] if a else ""
    Table = object

console = Console()

# ---------------------- Palette ----------------------
PALETTE = {
    "ink": "#E6E6E6",
    "eden_sky": "#89C2FF",
    "rootfire": "#FF7A59",
    "velvet": "#BF5AF2",
    "warning": "#FFB020",
    "danger": "#F54E4E",
    "ok": "#55D187",
}

# ---------------------- Identity ---------------------
AGENT_NAME = "Alder Ranger"

# ---------------------- Config -----------------------
HOME = pathlib.Path.home()

# Directories to crawl + watch (edit if you like)
WATCH_DIRS = [
    r"C:\EdenOS_Origin",
    rf"{HOME}\Documents",
    rf"{HOME}\Desktop",
    rf"{HOME}\Downloads",
]

# Database + Rhea inbox
DB_PATH = str(HOME / ".eden_ranger" / "ranger.db")
RHEA_INBOX = r"C:\EdenOS_Origin\all_daemons\Rhea\_inbox"

# LLM endpoint (OpenAI-compatible local server: LM Studio / Jan / GPT4All Server)
EDEN_LLM_BASE_URL = os.getenv("EDEN_LLM_BASE_URL", "http://127.0.0.1:2821/v1")
EDEN_LLM_MODEL    = os.getenv("EDEN_LLM_MODEL", "Llama 3.2 3B Instruct")

# Text intake limits
MAX_TEXT_BYTES = 200_000

# What we index into FTS (keep it light)
PLAIN_EXTS = {
    ".txt", ".md", ".py", ".json", ".csv", ".log", ".ini",
    ".html", ".htm", ".css", ".js", ".ts", ".yml", ".yaml"
}

# Suspicious patterns
SUSPICIOUS_EXTS = {".exe", ".bat", ".cmd", ".scr", ".ps1"}
DOUBLE_EXT_RE = re.compile(r"\.(pdf|jpg|png|txt|docx)\.(exe|scr|bat|cmd|ps1)$", re.I)

STARTUP_DIRS = [
    os.path.join(os.getenv("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
    os.path.join(os.getenv("ProgramData", ""), r"Microsoft\Windows\Start Menu\Programs\StartUp"),
]

# === Hunt rotation defaults (overridable by INI) ===
CHAOS_PREFIXES_TO_STRIP = [
    r"C:\EdenOS_Origin",
    r"C:\Users\emmar\Desktop",
    r"C:\User\emmar\Desktop",  # typo safety
]
HUNT_ROTATE_KEEP_DAYS = 7  # keep daily snapshots for N days

# === INI config path ===
CONFIG_PATH = os.getenv(
    "RANGER_HUNTS_INI",
    r"C:\EdenOS_Origin\all_daemons\Ranger\ranger.hunts.ini"
)

# Ensure paths exist
def _ensure_dir(p: str):
    try:
        os.makedirs(p, exist_ok=True)
    except Exception:
        pass

_ensure_dir(os.path.dirname(DB_PATH))
_ensure_dir(RHEA_INBOX)

# ---------------------- Rhea Bridge ------------------
def _ts_for_filename() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S.%fZ")

def _atomic_json_write(dir_path: str, filename: str, data: dict) -> Optional[str]:
    _ensure_dir(dir_path)
    try:
        fd, tmp_path = tempfile.mkstemp(prefix="ranger_", suffix=".tmp", dir=dir_path)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        final_path = os.path.join(dir_path, filename)
        os.replace(tmp_path, final_path)  # atomic replace
        return final_path
    except Exception:
        try:
            os.remove(tmp_path)
        except Exception:
            pass
        return None

def report_to_rhea(event_type: str, payload: dict):
    """
    Drops a JSON envelope into Rhea's _inbox.
    event_type: "heartbeat" | "event" | "anomaly" | "report" | "query_answer" | "<hunt>_hunt"
    """
    envelope = {
        "agent": AGENT_NAME,
        "host": platform.node(),
        "ts_iso": datetime.utcnow().isoformat() + "Z",
        "type": event_type,
        **payload
    }
    slug = (payload.get("rule") or payload.get("event") or payload.get("query") or payload.get("hunt") or "note")
    slug = str(slug).replace(" ", "-").replace(":", "-")[:64]
    fname = f"{_ts_for_filename()}_{event_type}_{slug}.json"
    _atomic_json_write(RHEA_INBOX, fname, envelope)

def _write_rotating_reports_named(hunt_name: str, payload: dict, keep_days: int):
    """
    Writes three things into Rhea's _inbox:
      - standard '<hunt>_hunt' event for listeners
      - <hunt>_hunt.latest.json (overwritten)
      - <hunt>_hunt.{YYYY-MM-DD}.json (daily snapshot, pruned)
    """
    event_type = f"{hunt_name}_hunt"
    report_to_rhea(event_type, payload)

    latest_name = f"{hunt_name}_hunt.latest.json"
    _atomic_json_write(RHEA_INBOX, latest_name, payload)

    day = datetime.utcnow().strftime("%Y-%m-%d")
    daily_name = f"{hunt_name}_hunt.{day}.json"
    _atomic_json_write(RHEA_INBOX, daily_name, payload)

    # prune old snapshots
    cutoff = time.time() - keep_days * 24 * 3600
    try:
        for fn in os.listdir(RHEA_INBOX):
            if not fn.startswith(f"{hunt_name}_hunt."):
                continue
            if fn.endswith(".latest.json"):
                continue
            path = os.path.join(RHEA_INBOX, fn)
            if os.path.getmtime(path) < cutoff:
                try: os.remove(path)
                except Exception: pass
    except Exception:
        pass

# ---------------------- INI helpers ------------------
def _load_hunt_config() -> configparser.ConfigParser:
    cfg = configparser.ConfigParser()
    cfg.optionxform = str  # preserve case
    if os.path.isfile(CONFIG_PATH):
        cfg.read(CONFIG_PATH, encoding="utf-8")
    return cfg

def _cfg_prefixes(cfg) -> list[str]:
    try:
        raw = cfg.get("global", "prefixes_to_strip", fallback="")
        prefs = [s.strip() for s in raw.split(";") if s.strip()]
        return prefs or CHAOS_PREFIXES_TO_STRIP
    except Exception:
        return CHAOS_PREFIXES_TO_STRIP

def _cfg_watch_dirs(cfg) -> list[str]:
    try:
        raw = cfg.get("global", "watch_dirs", fallback="")
        dirs = [s.strip() for s in raw.split(";") if s.strip()]
        return dirs or WATCH_DIRS
    except Exception:
        return WATCH_DIRS

def _cfg_keep_days(cfg) -> int:
    try:
        return cfg.getint("global", "rotate_keep_days", fallback=HUNT_ROTATE_KEEP_DAYS)
    except Exception:
        return HUNT_ROTATE_KEEP_DAYS

# ---------------------- SQLite / FTS5 ---------------
def db() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.execute("PRAGMA journal_mode=WAL;")
    return c

def init_db():
    with db() as cx:
        cx.executescript("""
        CREATE TABLE IF NOT EXISTS files(
            id INTEGER PRIMARY KEY,
            path TEXT UNIQUE,
            name TEXT,
            ext TEXT,
            size INTEGER,
            mtime REAL,
            sha1 TEXT,
            tags TEXT
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS filetext
          USING fts5(path, content, tokenize='porter');
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY,
            ts REAL,
            type TEXT,
            path TEXT,
            info TEXT
        );
        CREATE TABLE IF NOT EXISTS anomalies(
            id INTEGER PRIMARY KEY,
            ts REAL,
            path TEXT,
            rule TEXT,
            note TEXT
        );
        """)
    console.print(Panel.fit("DB ready", style=f"bold {PALETTE['ok']}"))
    report_to_rhea("heartbeat", {
        "status": "db_ready",
        "db_path": DB_PATH,
        "watch_dirs": WATCH_DIRS
    })

# ---------------------- Helpers ---------------------
def sha1(path: str, limit_mb: int = 16) -> Optional[str]:
    try:
        h = hashlib.sha1()
        with open(path, "rb") as f:
            read = 0
            while True:
                chunk = f.read(1024 * 1024)
                if not chunk or read >= limit_mb * 1024 * 1024:
                    break
                h.update(chunk); read += len(chunk)
        return h.hexdigest()
    except Exception:
        return None

def read_text_for_index(path: str) -> str:
    # Plain-texty files only; PDFs/DOCX omitted to avoid heavy deps.
    ext = pathlib.Path(path).suffix.lower()
    if ext not in PLAIN_EXTS:
        return ""
    try:
        with open(path, "r", errors="ignore") as f:
            return f.read(MAX_TEXT_BYTES)
    except Exception:
        return ""

# ---------------------- Cataloging ------------------
def upsert_file(path: str):
    try:
        st = os.stat(path)
    except Exception:
        return
    p = pathlib.Path(path)
    with db() as cx:
        cx.execute("""
        INSERT INTO files(path, name, ext, size, mtime, sha1)
        VALUES(?,?,?,?,?,?)
        ON CONFLICT(path) DO UPDATE SET size=excluded.size, mtime=excluded.mtime
        """, (str(p), p.name, p.suffix.lower(), st.st_size, st.st_mtime, sha1(str(p))))
        # FTS: replace old row and insert fresh
        text = read_text_for_index(str(p))
        if text:
            cx.execute("DELETE FROM filetext WHERE path=?", (str(p),))
            cx.execute("INSERT INTO filetext(path, content) VALUES(?,?)", (str(p), text))

def remove_file(path: str):
    with db() as cx:
        cx.execute("DELETE FROM files WHERE path=?", (path,))
        cx.execute("DELETE FROM filetext WHERE path=?", (path,))

def log_event(evtype: str, path: str, info: str=""):
    with db() as cx:
        cx.execute("INSERT INTO events(ts,type,path,info) VALUES(?,?,?,?)",
                   (time.time(), evtype, path, info))
    report_to_rhea("event", {"event": evtype, "path": path, "info": info})

def flag_anomaly(path: str, rule: str, note: str):
    with db() as cx:
        cx.execute("INSERT INTO anomalies(ts,path,rule,note) VALUES(?,?,?,?)",
                   (time.time(), path, rule, note))
    console.print(f"[{PALETTE['danger']}]⚠ {rule}: {path} — {note}[/]")
    report_to_rhea("anomaly", {"path": path, "rule": rule, "note": note})

# ---------------------- Simple Rules ---------------
def run_rules(path: str):
    try:
        p = pathlib.Path(path)
        ext = p.suffix.lower()
        if ext in SUSPICIOUS_EXTS and any(seg.lower() == "downloads" for seg in p.parts):
            flag_anomaly(str(p), "exe_in_downloads", "New executable in Downloads")
        if DOUBLE_EXT_RE.search(p.name):
            flag_anomaly(str(p), "double_extension", "Disguised executable name")
        for sd in STARTUP_DIRS:
            if sd and str(p).lower().startswith(sd.lower()):
                flag_anomaly(str(p), "startup_drop", "File placed in Startup folder")
    except Exception:
        pass

# ---------------------- Watcher --------------------
class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory: return
        upsert_file(event.src_path); log_event("created", event.src_path); run_rules(event.src_path)
    def on_modified(self, event):
        if event.is_directory: return
        upsert_file(event.src_path); log_event("modified", event.src_path)
    def on_moved(self, event):
        if event.is_directory: return
        remove_file(event.src_path); upsert_file(event.dest_path)
        log_event("moved", f"{event.src_path} -> {event.dest_path}")
    def on_deleted(self, event):
        if event.is_directory: return
        remove_file(event.src_path); log_event("deleted", event.src_path)

def start_watch():
    obs = Observer()
    h = Handler()
    for d in WATCH_DIRS:
        if os.path.isdir(d):
            obs.schedule(h, d, recursive=True)
            console.print(f"[{PALETTE['eden_sky']}]Watching {d}[/]")
    obs.start()
    return obs

# ---------------------- Local LLM (HTTP) ----------
def llm_chat(system_prompt: str, user_prompt: str, temperature: float = 0.2, max_tokens: int = 400) -> str:
    """
    Talks to any OpenAI-compatible local endpoint (LM Studio, Jan, GPT4All Server, etc.).
    Set:
      EDEN_LLM_BASE_URL=http://127.0.0.1:2821/v1
      EDEN_LLM_MODEL=your-model-id (as shown by /v1/models)
    """
    base = EDEN_LLM_BASE_URL.rstrip("/")
    url = f"{base}/chat/completions"
    payload = {
        "model": EDEN_LLM_MODEL,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt}
        ]
    }
    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"(LLM error: {e})"

def ask(query: str, k: int = 25) -> str:
    with db() as cx:
        rows = cx.execute(
            "SELECT path, snippet(filetext, 1, '[', ']', ' … ', 10) AS snip "
            "FROM filetext WHERE filetext MATCH ? ORDER BY rank LIMIT ?",
            (query, k)
        ).fetchall()
    if not rows:
        answer = "No matches. Try different keywords."
        report_to_rhea("query_answer", {"query": query, "answer": answer})
        return answer

    context = "\n\n".join(f"[{p}]\n{snip}" for p, snip in rows[:8])
    system_prompt = (
        "You are Alder Ranger, EdenOS Scout & Filewarden. "
        "Answer strictly from the provided context. "
        "If unsure, say what to search next. Always include file paths when relevant."
    )
    user_prompt = f"Context:\n{context}\n\nQuestion: {query}\nAnswer:"
    answer = llm_chat(system_prompt, user_prompt, temperature=0.2, max_tokens=400)
    report_to_rhea("query_answer", {"query": query, "answer": answer})
    return answer

# ---------------------- CHAOS + Config Hunts -----------------
def _strip_prefixes(path_str: str) -> str:
    low = path_str.lower()
    for pref in CHAOS_PREFIXES_TO_STRIP:
        p = pref.lower().rstrip("\\/")
        if low.startswith(p):
            out = path_str[len(pref):]
            return out.lstrip("\\/") or "."
    return path_str

def _is_chaos_path(p: pathlib.Path) -> bool:
    suffixes = p.suffixes
    if not suffixes:
        return False
    return suffixes[-1].lower().startswith(".chaos")

def hunt_chaos(max_results: int = 100000, contains: str | None = None) -> list[str]:
    """
    Scans WATCH_DIRS for any file whose final extension starts with .chaos
    Optional: filter results to paths containing a substring (case-insensitive).
    Saves rotating reports (latest + daily snapshot) and prints a clean list.
    """
    hits: list[str] = []
    for root in WATCH_DIRS:
        if not os.path.isdir(root):
            continue
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                p = pathlib.Path(dirpath) / fn
                try:
                    if _is_chaos_path(p):
                        s = str(p)
                        if contains and (contains.lower() not in s.lower()):
                            continue
                        hits.append(s)
                except Exception:
                    pass
                if len(hits) >= max_results:
                    break

    hits = sorted(set(hits), key=lambda s: s.lower())
    cleaned = [_strip_prefixes(h) for h in hits]

    console.print(
        f"[bold]{len(cleaned)}[/] CHAOS files found"
        + (f" (filter: '{contains}')" if contains else "")
        + ":"
    )
    for h in cleaned:
        console.print(f" • {h}")

    _write_rotating_reports_named(
        "chaos",
        {
            "hunt": "chaos",
            "found": len(cleaned),
            "prefixes_stripped": CHAOS_PREFIXES_TO_STRIP,
            "filter": contains or "",
            "results": cleaned,
        },
        keep_days=HUNT_ROTATE_KEEP_DAYS,
    )
    return cleaned

def run_config_hunt(hunt_name: str, contains: str | None = None, max_results: int = 200000):
    """
    Run a hunt defined in ranger.hunts.ini as [hunt:<hunt_name>].
    Supported types:
      - glob             : pattern=*.mirror.json
      - suffix_startswith: suffix=.chaos
      - ext_equals       : ext=.vas
      - size_gt          : mb=100
      - mtime_older_than : days=180
      - fts_match        : query=Echomarker  (searches filetext FTS)
    Optional for any hunt:
      - limit            : cap results (default 200k)
    """
    cfg = _load_hunt_config()
    section = f"hunt:{hunt_name}"
    if not cfg.has_section(section):
        console.print(f"[{PALETTE['danger']}]No such hunt in config: {hunt_name}[/]")
        return []

    prefixes = _cfg_prefixes(cfg)
    watch_dirs = _cfg_watch_dirs(cfg)
    keep_days = _cfg_keep_days(cfg)

    htype = cfg.get(section, "type", fallback="glob").strip()
    limit = int(cfg.get(section, "limit", fallback=str(max_results)))
    hits: list[str] = []

    if htype == "fts_match":
        query = cfg.get(section, "query", fallback="").strip()
        if not query:
            console.print(f"[{PALETTE['warning']}]fts_match requires 'query'[/]")
            return []
        with db() as cx:
            rows = cx.execute(
                "SELECT path FROM filetext WHERE filetext MATCH ? ORDER BY rank LIMIT ?",
                (query, limit),
            ).fetchall()
        hits = [r[0] for r in rows]

    else:
        pat = cfg.get(section, "pattern", fallback="").strip()
        suffix = cfg.get(section, "suffix", fallback="").strip().lower()
        ext = cfg.get(section, "ext", fallback="").strip().lower()
        mb = float(cfg.get(section, "mb", fallback="0") or 0)
        days = int(cfg.get(section, "days", fallback="0") or 0)

        for root in watch_dirs:
            if not os.path.isdir(root):
                continue
            for dirpath, _, filenames in os.walk(root):
                for fn in filenames:
                    full = os.path.join(dirpath, fn)
                    p = pathlib.Path(full)
                    try:
                        if htype == "glob":
                            if not pat or not fnmatch.fnmatch(fn, pat):
                                continue
                        elif htype == "suffix_startswith":
                            suffs = p.suffixes
                            if not suffs or not suffs[-1].lower().startswith(suffix):
                                continue
                        elif htype == "ext_equals":
                            if p.suffix.lower() != ext:
                                continue
                        elif htype == "size_gt":
                            st = os.stat(full)
                            if st.st_size <= mb * 1024 * 1024:
                                continue
                        elif htype == "mtime_older_than":
                            st = os.stat(full)
                            age_days = (time.time() - st.st_mtime) / 86400.0
                            if age_days <= days:
                                continue
                        else:
                            continue  # unknown type

                        if contains and (contains.lower() not in full.lower()):
                            continue

                        hits.append(full)
                        if len(hits) >= limit:
                            break
                    except Exception:
                        # Skip files that error out (permissions, broken symlinks, etc.)
                        continue

                if len(hits) >= limit:
                    break

    hits = sorted(set(hits), key=lambda s: s.lower())
    cleaned: list[str] = []
    for h in hits:
        low = h.lower()
        out = h
        for pref in prefixes:
            p = pref.lower().rstrip("\\/")
            if low.startswith(p):
                out = h[len(pref):].lstrip("\\/")
                break
        cleaned.append(out or ".")

    filt = f" (filter: '{contains}')" if contains else ""
    console.print(f"[bold]{len(cleaned)}[/] results for hunt '{hunt_name}'{filt}:")
    for c in cleaned:
        console.print(f" • {c}")

    _write_rotating_reports_named(
        hunt_name,
        {
            "hunt": hunt_name,
            "found": len(cleaned),
            "prefixes_stripped": prefixes,
            "filter": contains or "",
            "results": cleaned,
        },
        keep_days=keep_days,
    )
    return cleaned

# ---------------------- Reports --------------------
def daily_report():
    since = time.time() - 24*3600
    with db() as cx:
        evs = cx.execute("SELECT ts,type,path,info FROM events WHERE ts>?", (since,)).fetchall()
        anns = cx.execute("SELECT ts,path,rule,note FROM anomalies WHERE ts>?", (since,)).fetchall()

    if isinstance(Table, type):
        table = Table(title="Eden Ranger — last 24h")
        table.add_column("When"); table.add_column("Type/Rule"); table.add_column("Path")
        for ts,t,p,info in evs:
            table.add_row(datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M"), t, p)
        for ts,p,rule,note in anns:
            table.add_row(datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M"),
                          f"[ANOMALY] {rule}", f"{p} ({note})")
        console.print(table)
    else:
        console.print(f"Events: {len(evs)}  Anomalies: {len(anns)}")

    report_to_rhea("report", {
        "window": "24h",
        "events": [{"ts": ts, "type": t, "path": p} for ts,t,p,info in evs],
        "anomalies": [{"ts": ts, "path": p, "rule": rule, "note": note} for ts,p,rule,note in anns]
    })

# ---------------------- Timing helper -------------------
def _seconds_until(hour: int, minute: int) -> int:
    now = datetime.now()
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=1)
    return int((target - now).total_seconds())

# ---------------------- CLI -----------------------
def main():
    init_db()

    if len(sys.argv) > 1:
        cmd = sys.argv[1]

        if cmd == "ask":
            q = " ".join(sys.argv[2:]) or "Where are my largest logs?"
            ans = ask(q)
            console.print(Panel(ans, title="Answer", style=f"bold {PALETTE['velvet']}"))
            return

        if cmd == "report":
            daily_report(); return

        if cmd == "hunt-chaos":
            contains = sys.argv[2] if len(sys.argv) > 2 else None
            hunt_chaos(contains=contains); return

        if cmd == "hunt":
            if len(sys.argv) < 3:
                console.print("Usage: hunt <name> [contains]")
                return
            name = sys.argv[2]
            contains = sys.argv[3] if len(sys.argv) > 3 else None
            run_config_hunt(name, contains=contains); return

        if cmd == "autohunt":
            if len(sys.argv) < 3:
                console.print("Usage: autohunt <name> [HH:MM] [contains]")
                return
            name = sys.argv[2]
            when = sys.argv[3] if len(sys.argv) > 3 else "10:00"
            contains = sys.argv[4] if len(sys.argv) > 4 else None
            try:
                hh, mm = map(int, when.split(":"))
            except Exception:
                hh, mm = 10, 0
            console.print(Panel(f"Scheduling autohunt '{name}' daily at {hh:02d}:{mm:02d}", style="bold #89C2FF"))
            while True:
                time.sleep(_seconds_until(hh, mm))
                try:
                    run_config_hunt(name, contains=contains)
                except Exception as e:
                    console.print(f"[{PALETTE['danger']}]Autohunt error: {e}[/]")
                time.sleep(60)

    # Initial crawl
    console.print(Panel("Initial crawl…", style=f"bold {PALETTE['eden_sky']}"))
    for root in WATCH_DIRS:
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                path = os.path.join(dirpath, fn)
                try:
                    upsert_file(path)
                except Exception:
                    pass
    console.print(Panel("Crawl done.", style=f"bold {PALETTE['ok']}"))

    # Start watcher
    obs = start_watch()
    console.print(Panel("Daemon running. Ctrl+C to stop.",
                        style=f"bold {PALETTE['ink']} on #222222"))
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()

if __name__ == "__main__":
    main()
