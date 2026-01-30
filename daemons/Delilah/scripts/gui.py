import os
from pathlib import Path
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
from collections import defaultdict
from scanner import do_scan, apply_moves
from models import SmartRecover
from utils import smarter_decide_category

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

        self.out.readonly = True

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
