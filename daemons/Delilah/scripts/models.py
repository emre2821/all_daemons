from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
from config import CATEGORY_FOLDERS
from utils import smarter_decide_category, group_candidates, project_signals

class Plan:
    def __init__(self, roots: list[Path], rhea_home: Path):

        self.roots = roots
        self.rhea_home = rhea_home
        self.moves = []
        self.errors = []
        self.summary = {}
        self.group_summaries = {}
    def add_move(self, src: Path, dst: Path):

        self.moves.append((src, dst))
    def to_vas(self) -> str:

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = []
        lines.append(":title: Eden Recovery Plan (.vas)")
        lines.append(f":generated: {now}")
        lines.append(":roots:")
        for root in self.roots:
            lines.append(f" - {root}")
        lines.append(f":rhea_home: {self.rhea_home}")
        lines.append(":counts:")
        for k, v in sorted(self.summary.items()):
            lines.append(f" - {k}: {v}")
        lines.append(":groups:")
        for token, summary in sorted(self.group_summaries.items()):
            lines.append(f" - {token}:")
            lines.append(f"      summary: {summary}")
        lines.append(":moves:")
        for src, dst in self.moves:
            lines.append(f" - from: {src}")
            lines.append(f"    to:   {dst}")
        if self.errors:
            lines.append(":errors:")
            for e in self.errors:
                lines.append(f" - {e}")
        return "\n".join(lines) + "\n"

class SmartRecover:
    def __init__(self, roots: list[Path], rhea_home: Path):

        self.roots = roots
        self.rhea_home = rhea_home
        self.files = []
        self.cats = defaultdict(list)
        self.groups = {}
        self.signals = {}
        self.errors = []
    def scan(self):

        file_count = 0
        for root in self.roots:
            try:
                for p in root.rglob("*"):
                    try:
                        if p.is_file() and self.rhea_home not in p.parents:
                            self.files.append(p)
                            file_count += 1
                            if file_count >= 10000:  # MAX_FILES
                                self.errors.append(f"Stopped scanning at {10000} files; folder {root} too large.")
                                break
                    except PermissionError:
                        self.errors.append(f"Skipped {p}: Permission denied.")
                    except OSError as e:
                        self.errors.append(f"Skipped {p}: OS error ({e}).")
                    except Exception as e:
                        self.errors.append(f"Skipped {p}: Unexpected error ({e}).")
            except Exception as e:
                self.errors.append(f"Scan failed for {root}: {e}")
        return self
    def categorise(self):

        for p in self.files:
            cat = smarter_decide_category(p)
            self.cats[cat].append(p)
        return self
    def detect_groups(self):

        pool = []
        for k in ("Code", "Docs", "Eden"):
            pool.extend(self.cats.get(k, []))
        self.groups = group_candidates(pool)
        return self
    def compute_signals(self):

        self.signals = {}
        for token, paths in self.groups.items():
            self.signals[token] = project_signals(paths)
        return self
    def _plan_category_moves(self, plan):
        for cat, lst in self.cats.items():
            sub = CATEGORY_FOLDERS.get(cat, cat)
            for p in lst:
                try:
                    # Preserve relative path from root
                    root = next(r for r in self.roots if r in p.parents)
                    rel_path = p.relative_to(root)
                    dst = self.rhea_home / sub / rel_path
                    try:
                        if p.resolve() == dst.resolve():
                            continue
                    except Exception:
                        pass
                    plan.add_move(p, dst)
                except Exception as e:
                    plan.errors.append(f"Failed to plan move for {p}: {e}")

    def _plan_group_moves(self, plan):
        for token, paths in self.groups.items():
            cat_counts = Counter(smarter_decide_category(p) for p in paths)
            dom_cat, _ = max(cat_counts.items(), key=lambda kv: kv[1])
            sub = CATEGORY_FOLDERS.get(dom_cat, dom_cat)
            sig = "+".join(sorted(self.signals.get(token, {})))
            folder_name = f"{token}"
            if sig:
                folder_name = f"{token}__{sig}"
            group_dir = self.rhea_home / sub / folder_name
            file_samples = ", ".join(p.name for p in paths[:3])
            if len(paths) > 3:
                file_samples += "..."
            if sig:
                summary = f"This group appears to be a {sig.replace('+', ' + ')} project, likely focused on {dom_cat.lower()} tasks. It includes files like {file_samples}."
            else:
                summary = f"A collection of {dom_cat} files sharing the prefix '{token}'. Includes {file_samples}."
            plan.group_summaries[token] = summary
            for p in paths:
                plan.add_move(p, group_dir / p.name)

    def _set_summaries(self, plan):
        plan.summary = {k: len(v) for k, v in self.cats.items()}

    def _handle_errors(self, plan):
        if self.errors:
            plan.errors.extend(self.errors)

    def build_plan(self) -> 'Plan':

        plan = Plan(self.roots, self.rhea_home)
        self._plan_category_moves(plan)
        self._plan_group_moves(plan)
        self._set_summaries(plan)
        self._handle_errors(plan)
        return plan
