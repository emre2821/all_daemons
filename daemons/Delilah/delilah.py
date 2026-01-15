import os
import re, json, shutil, hashlib
from pathlib import Path
from collections import defaultdict
import Counter
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.treeview import TreeView
import TreeViewLabel
from kivy.clock import Clock
import tkinter as tk
from tkinter import filedialog
import tempfile

PALETTES = {
    "DreambearerLight": ["#F6F3EE", "#E6D9C9", "#CFAF91", "#8B6B5A", "#3B2F2A"],
    "EdenSky": ["#DFF0FF", "#B8E1FF", "#7BC6FF", "#368DFF", "#1D4ED8"],
    "VelvetDivision": ["#1A1A1A", "#3A2E39", "#6A365D", "#A33EA1", "#EAD7EF"],
}
BG = PALETTES["DreambearerLight"][0]
FG = "#1A1A1A"
ACCENT = PALETTES["EdenSky"][3]

EDENISH_EXTS = {".chaos", ".chaosincarnet", ".chaos-ception", ".vas", ".mirror.json",
                ".shalfredlayer.chaos", ".chaosmeta", ".chaosscript", ".chaoscript"}
CODE_EXTS = {".py", ".ipynb", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml",
            ".toml", ".ini", ".cfg", ".md", ".html", ".css", ".scss", ".less", ".java",
            ".kt", ".cs", ".cpp", ".c", ".go", ".rs"}
DOC_EXTS = {".txt", ".rtf", ".pdf", ".doc", ".docx", ".odt"}
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg"}
AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg"}
ARCHIVE_EXTS = {".zip", ".tar", ".gz", ".bz2", ".7z"}
SAFE_MAX_BYTES_TO_PEEK = 96 * 1024
CATEGORY_FOLDERS = {
    "Eden": "Eden",
    "Code": "Code",
    "Docs": "Docs",
    "MediaImages": "Media/Images",
    "MediaAudio": "Media/Audio",
    "Archives": "Archives",
    "DevOps": "DevOps",
    "NodeProject": "Node",
    "Other": "Other"
}
PKG_HINT_PATTERNS = [
    ("python", re.compile(r"(^|/)setup\.py$|(^|/)pyproject\.toml$|(^|/)requirements\.txt$", re.I)),
    ("node", re.compile(r"(^|/)package\.json$|(^|/)vite\.config|webpack\.config", re.I)),
    ("kivy", re.compile(r"from\s+kivy|\[Kivy\]|buildozer\.spec", re.I)),
]
PFX_SPLIT = re.compile(r"[-_. ]+")
MAX_FILES = 10000

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
                            if file_count >= MAX_FILES:
                                self.errors.append(f"Stopped scanning at {MAX_FILES} files; folder {root} too large.")
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
    def build_plan(self) -> 'Plan':

        plan = Plan(self.roots, self.rhea_home)
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
                summary = f"This group appears to be a {sig.replace(' +
                    ', ' +
                    ')} project, likely focused on {dom_cat.lower()} tasks. It includes files like {file_samples}."
            else:
                summary = f"A collection of {dom_cat} files sharing the prefix '{token}'. Includes {file_samples}."
            plan.group_summaries[token] = summary
            for p in paths:
                plan.add_move(p, group_dir / p.name)
        plan.summary = {k: len(v) for k, v in self.cats.items()}
        if self.errors:
            plan.errors.extend(self.errors)
        return plan

def decide_category(p: Path) -> str:

    ext = p.suffix.lower()
    if ext in EDENISH_EXTS:
        return "Eden"
    if ext in CODE_EXTS:
        return "Code"
    if ext in DOC_EXTS:
        return "Docs"
    if ext in IMG_EXTS:
        return "MediaImages"
    if ext in AUDIO_EXTS:
        return "MediaAudio"
    if ext in ARCHIVE_EXTS:
        return "Archives"
    return "Other"


def smarter_decide_category(p: Path) -> str:

    """Context-aware categorization that looks inside small text files."""
    ext = p.suffix.lower()
    base = decide_category(p)
    try:
        if p.stat().st_size < SAFE_MAX_BYTES_TO_PEEK and ext in {".txt", ".md", ".json", ".yaml", ".yml"}:
            text = peek_text(p).lower()
            if "def " in text or "class " in text or "import " in text or "function " in text:
                return "Code"
            if "docker" in text or "services:" in text or "compose" in text:
                return "DevOps"
            if "dependencies" in text or "require(" in text:
                return "NodeProject"
    except Exception:
        pass
    return base

def peek_text(p: Path) -> str:

    try:
        with p.open("rb") as f:
            data = f.read(SAFE_MAX_BYTES_TO_PEEK)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def project_signals(file_paths):

    sigs = Counter()
    for p in file_paths:
        s = str(p).replace("\\", "/")
        for name, rx in PKG_HINT_PATTERNS:
            if rx.search(s):
                sigs[name] += 1
        if p.suffix.lower() == ".py" and "kivy" in peek_text(p).lower():
            sigs["kivy"] += 1
    return sigs

def group_candidates(files):

    buckets = defaultdict(list)
    for p in files:
        stem = p.stem
        token = PFX_SPLIT.split(stem)[0].lower() if stem else "_"
        key = (token, p.parent)
        buckets[key].append(p)
    merged = defaultdict(list)
    for (token, parent), lst in buckets.items():
        merged[token].extend(lst)
    groups = {}
    for token, lst in merged.items():
        uniq = sorted(set(lst))
        if len(uniq) < 2:
            continue
        if len({p.suffix.lower() for p in uniq}) >= 2 or len(uniq) >= 3:
            groups[token] = uniq
    return groups

def _hash(p: Path) -> str:

    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def _same_file(a: Path, b: Path) -> bool:

    try:
        return _hash(a) == _hash(b)
    except Exception:
        return False

def _disambig(p: Path) -> Path:

    base = p.with_suffix("")
    ext = p.suffix
    i = 1
    while p.exists():
        p = base.with_name(base.name + f"_{i}").with_suffix(ext)
        i += 1
    return p

def apply_moves(plan: Plan):

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

class EdenRecoveryUI(BoxLayout):
    def __init__(self, **kwargs):

        super().__init__(orientation='vertical', spacing=8, padding=8, **kwargs)
        grid = GridLayout(cols=3, row_default_height=40, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        try:
            default_root = os.path.normpath(os.path.join(os.getcwd(), "5_deployments"))
        except Exception as e:
            default_root = tempfile.gettempdir()
            print(f"[EdenRecovery] Fallback to temp dir: {e}")
        self.root_input = TextInput(text=default_root, multiline=False, hint_text="ROOT (scan from)")
        self.rhea_input = TextInput(text=str(Path(default_root).parent / "CHAOS_Logs"), multiline=False, hint_text="RHEA_HOME (destination)")
        self.root_folders = [Path(default_root)]  # Store multiple root folders
        def pick_root(_btn):

            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(initialdir=self.root_input.text, title="Select Root Folder(s)")
            root.destroy()
            if folder:
                folder_path = Path(os.path.normpath(folder))
                if folder_path not in self.root_folders:
                    self.root_folders = [folder_path]  # Replace with single folder for now
                    self.root_input.text = str(folder_path)
                    self.update_preview()
                    self.log(f"Selected root: {folder_path}")
        def pick_rhea(_btn):

            root = tk.Tk()
            root.withdraw()
            folder = filedialog.askdirectory(initialdir=self.rhea_input.text, title="Select Rhea Home Folder")
            root.destroy()
            if folder:
                self.rhea_input.text = os.path.normpath(folder)
                self.log(f"Selected rhea: {folder}")
        grid.add_widget(self._labeled("Root", self.root_input, pick_root))
        grid.add_widget(self._labeled("Rhea Home", self.rhea_input, pick_rhea))
        grid.add_widget(self._actions_bar())
        self.add_widget(grid)
        # Preview pane
        self.preview = FileChooserListView(path=default_root, size_hint_y=None, height=200, filters=['*.*'])
        self.preview.bind(path=self.update_preview_path)
        sv_preview = ScrollView(size_hint_y=None, height=200)
        sv_preview.add_widget(self.preview)
        self.add_widget(sv_preview)
        self.out = TextInput(text="Ready. Pick folders, then Scan or Preview.", readonly=True)
        sv = ScrollView()
        sv.add_widget(self.out)
        self.add_widget(sv)
        self._plan = None
        self._rec = None
    def _actions_bar(self):

        box = BoxLayout(spacing=6)
        box.add_widget(Button(text="Scan", on_release=lambda *_: self.scan_now()))
        box.add_widget(Button(text="Preview Plan", on_release=lambda *_: self.preview_plan()))
        box.add_widget(Button(text="Apply Moves", on_release=lambda *_: self.apply_moves()))
        box.add_widget(Button(text="Debug", on_release=lambda *_: self.debug_state()))
        return box
    def _labeled(self, title, widget, on_pick):

        col = BoxLayout(orientation='vertical', spacing=4)
        col.add_widget(Label(text=title, color=(0,0,0,1), size_hint_y=None, height=20))
        row = BoxLayout(spacing=6, size_hint_y=None, height=40)
        row.add_widget(widget)
        row.add_widget(Button(text="Browse", size_hint_x=None, width=100, on_release=on_pick))
        col.add_widget(row)
        return col
    def log(self, msg):

        self.out.readonly = False
        self.out.text += ("\n" + str(msg))
        self.out.readonly = True
        print(f"[EdenRecovery] {msg}")
    def update_preview_path(self, instance, value):

        self.root_folders = [Path(value)]
        self.root_input.text = str(value)
        self.log(f"Preview updated to: {value}")
    def update_preview(self):

        self.preview.path = str(self.root_folders[0]) if self.root_folders else tempfile.gettempdir()
    def scan_now(self):

        self.out.readonly = False
        self.out.text = "Scanning..."
        self.out.readonly = True
        print("[EdenRecovery] Starting scan...")
        Clock.schedule_once(lambda *_: self._scan_work(), 0)
    def _scan_work(self):

        try:
            raw_root = self.root_input.text.strip('"\' ')
            roots = [Path(os.path.normpath(raw_root)).resolve()]
            raw_rhea = self.rhea_input.text.strip('"\' ')
            rhea = Path(os.path.normpath(raw_rhea)).resolve()
            self.log(f"Raw root input: {raw_root}")
            self.log(f"Resolved roots: {roots}")
            self.log(f"Raw rhea input: {raw_rhea}")
            self.log(f"Resolved rhea: {rhea}")
            if not all(root.exists() for root in roots):
                self.log(f"[!] Root not found: {roots}. Try C:\\Users\\{os.getlogin()}\\Desktop\\5_deployments")
                return
            self.log(f"Scanning {len(roots)} folder(s)...")
            rec = SmartRecover(roots, rhea).scan().categorise().detect_groups().compute_signals()
            self._rec = rec
            self._plan = rec.build_plan()
            self.out.readonly = False
            self.out.text = "[Summary]\n"
            for root in roots:
                self.out.text += f"Root: {root}\n"
                root_files = [f for f in rec.files if root in f.parents]
                root_cats = defaultdict(list)
                for f in root_files:
                    cat = smarter_decide_category(f)
                    root_cats[cat].append(f)
                self.out.text += "\n".join([f"  {k:12} : {len(root_cats[k])}" for k in sorted(root_cats.keys())])
                self.out.text += f"\n  groups     : {sum(1 for t, ps in rec.groups.items() if any(root in p.parents for p in ps))}"
            self.out.text += f"\n  rhea_home  : {rhea}"
            if rec.errors:
                self.out.text += "\n[Scan Errors]\n" + "\n".join(rec.errors)
            self.out.readonly = True
            print("[EdenRecovery] Scan complete.")
        except Exception as e:
            self.log(f"[!] Scan failed: {e}")
            print(f"[EdenRecovery] Scan error: {e}")
    def preview_plan(self):

        if not self._plan:
            self.scan_now()
            return
        vas = self._plan.to_vas()
        self.out.readonly = False
        self.out.text = "[.vas plan preview]\n\n" + vas
        self.out.readonly = True
        print("[EdenRecovery] Previewed plan.")
    def apply_moves(self):

        if not self._plan:
            self.scan_now()
            return
        content = BoxLayout(orientation='vertical', spacing=6, padding=6)
        content.add_widget(Label(text="Want me to move these files for you? Yeah, organize it all—or nah, just wanted to see?"))
        btns = BoxLayout(spacing=6, size_hint_y=None, height=48)
        nah_btn = Button(text="Nah")
        yeah_btn = Button(text="Yeah")
        btns.add_widget(nah_btn)
        btns.add_widget(yeah_btn)
        content.add_widget(btns)
        popup = Popup(title="Organize time?", content=content, size_hint=(0.6,0.3))
        nah_btn.bind(on_release=lambda *_: popup.dismiss())
        yeah_btn.bind(on_release=lambda *_: self._do_apply(popup))
        popup.open()
        print("[EdenRecovery] Showing apply moves popup.")
    def _do_apply(self, popup):

        popup.dismiss()
        try:
            undo_path, vas_path = apply_moves(self._plan)
            self.log(f"Applied. Undo → {undo_path}\nPlan saved → {vas_path}")
            print(f"[EdenRecovery] Moves applied: {vas_path}")
        except Exception as e:
            self.log(f"[!] Apply failed: {e}")
            print(f"[EdenRecovery] Apply error: {e}")
    def debug_state(self):

        self.out.readonly = False
        self.out.text = "[Debug State]\n"
        self.out.text += f"Roots: {self.root_folders}\n"
        self.out.text += f"Rhea Home: {self.rhea_input.text}\n"
        self.out.text += f"Plan exists: {bool(self._plan)}\n"
        self.out.text += f"Recover exists: {bool(self._rec)}\n"
        if self._rec:
            self.out.text += f"Files scanned: {len(self._rec.files)}\n"
            self.out.text += f"Groups found: {len(self._rec.groups)}\n"
            if self._rec.errors:
                self.out.text += "[Errors]\n" + "\n".join(self._rec.errors)

class EdenRecoveryApp(App):
    title = "Eden Recovery (GUI)"
    def build(self):

        print("[EdenRecovery] Starting GUI...")
        try:
            ui = EdenRecoveryUI()
            print("[EdenRecovery] GUI initialized.")
            return ui
        except Exception as e:
            print(f"[EdenRecovery] GUI failed to start: {e}")
            raise


if __name__ == '__main__':
    EdenRecoveryApp().run()
