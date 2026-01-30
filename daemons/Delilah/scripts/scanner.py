import os
from collections import defaultdict
from models import SmartRecover
from utils import smarter_decide_category

def do_scan(roots, rhea):
    rec = SmartRecover(roots, rhea).scan().categorise().detect_groups().compute_signals()
    plan = rec.build_plan()
    summary_lines = []
    for root in roots:
        summary_lines.append(f"Root: {root}")
        root_files = [f for f in rec.files if root in f.parents]
        root_cats = defaultdict(list)
        for f in root_files:
            cat = smarter_decide_category(f)
            root_cats[cat].append(f)
        summary_lines.extend([f"  {k:12} : {len(root_cats[k])}" for k in sorted(root_cats.keys())])
        summary_lines.append(f"  groups     : {sum(1 for t, ps in rec.groups.items() if any(root in p.parents for p in ps))}")
    summary_lines.append(f"  rhea_home  : {rhea}")
    if rec.errors:
        summary_lines.append("")
        summary_lines.extend(rec.errors)
    summary = "\n".join(summary_lines)
    return rec, plan, summary

def apply_moves(plan):
    import shutil
    import json
    from datetime import datetime
    from .utils import _same_file, _disambig
    undo = []
    for src, dst in plan.moves:
        try:
            dst.parent.mkdir(parents=True, exist_ok=True)
            if dst.exists():
                if _same_file(src, dst):
                    continue
                dst = _disambig(dst)
            shutil.move(str(src), str(dst))
            undo.append({"from": str(dst), "to": str(src)})
        except Exception as e:
            plan.errors.append(f"Failed {src} → {dst}: {e}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logs_dir = plan.rhea_home / "_recovery_logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    undo_path = logs_dir / f"undo_{timestamp}.json"
    vas_path = logs_dir / f"plan_{timestamp}.vas"
    undo_path.write_text(json.dumps({"undo": undo}, indent=2), encoding="utf-8")
    vas_path.write_text(plan.to_vas(), encoding="utf-8")
    return undo_path, vas_path
