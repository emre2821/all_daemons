# Eden-aware Dave: ranks daemon "power" from logs + outbox footprints
import os, json, re, time
from pathlib import Path
from collections import defaultdict

EDEN_ROOT = Path(os.environ.get("EDEN_ROOT", r"C:\EdenOS_Origin"))
RHEA_BASE = EDEN_ROOT / "all_daemons" / "Rhea"

LOGS_DIR  = RHEA_BASE / "_logs"
OUTBOX    = RHEA_BASE / "_outbox"
DAVE_OUT  = OUTBOX / "dave"
for d in (LOGS_DIR, DAVE_OUT):
    d.mkdir(parents=True, exist_ok=True)

LEADERBOARD = DAVE_OUT / "leaderboard.json"
POWER_CHAOS = DAVE_OUT / "dave.powerchart.chaos"
ALERTS_JSON = DAVE_OUT / "alerts.json"

ERROR_RE = re.compile(r"\b(ERROR|FATAL|Traceback)\b", re.IGNORECASE)
WARN_RE  = re.compile(r"\b(WARN|WARNING)\b", re.IGNORECASE)

def scan_logs():
    scores = defaultdict(int)
    details = defaultdict(lambda: {"errors":0,"warns":0,"lines":0,"files":0,"bytes":0})
    for log in LOGS_DIR.glob("*_daemon.log"):
        name = log.name.replace("_daemon.log","").lower()
        try:
            text = log.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        lines = text.splitlines()
        errs  = sum(1 for ln in lines if ERROR_RE.search(ln))
        warns = sum(1 for ln in lines if WARN_RE.search(ln))
        L = len(lines)
        # naive score: activity minus penalty
        sc = L * 0.5 + errs * 5 + warns * 1
        scores[name] += int(sc)
        details[name]["errors"] += errs
        details[name]["warns"]  += warns
        details[name]["lines"]  += L
    # add outbox signal
    for sub in OUTBOX.iterdir():
        if not sub.is_dir(): continue
        name = sub.name.lower()
        files = list(sub.rglob("*"))
        fcount = sum(1 for f in files if f.is_file())
        bcount = sum(f.stat().st_size for f in files if f.is_file()) if fcount else 0
        scores[name] += fcount * 2 + int(bcount / 50_000)  # ~2 pts/file + 1 per 50KB
        details[name]["files"] += fcount
        details[name]["bytes"] += bcount
    return scores, details

def rank(scores):
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)

def write_outputs(scores, details):
    ranks = rank(scores)
    data = [{"daemon": n, "score": s, **details.get(n, {})} for n, s in ranks]
    LEADERBOARD.write_text(json.dumps(data, indent=2), encoding="utf-8")

    lines = ["# Dave Power Chart\n"]
    for i,(n,s) in enumerate(ranks, start=1):
        lines.append(f"{i:02d}. {n} :: {s}")
    POWER_CHAOS.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # OP alert: any daemon > mean + 2*std
    vals = [s for _,s in ranks] or [0]
    mu = sum(vals)/len(vals)
    var = sum((v-mu)**2 for v in vals)/len(vals)
    std = var**0.5
    threshold = mu + 2*std
    ops = [n for n,s in ranks if s > threshold]
    ALERTS_JSON.write_text(json.dumps({"threshold":threshold,"ops":ops}, indent=2), encoding="utf-8")
    return ops, threshold

def main():
    print("[Dave] Scoring…")
    scores, details = scan_logs()
    ops, thr = write_outputs(scores, details)
    if ops:
        print(f"[Dave] OP detected (> {thr:.1f}): {', '.join(ops)}")
    else:
        print("[Dave] No OPs. Balance is kept.")

if __name__ == "__main__":
    main()
