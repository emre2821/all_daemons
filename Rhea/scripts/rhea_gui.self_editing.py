#!/usr/bin/env python3
# Rhea Self-Editing GUI — edit registry safely with validation, diff, and backups

import json, difflib
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from jsonschema import Draft7Validator

ROOT = Path(__file__).resolve().parent.parent  # .../Rhea
REGISTRY_PATH = ROOT / "config" / "rhea_registry.json"
SCHEMA_PATH = ROOT / "config" / "rhea_schema.json"
BACKUPS = ROOT / "backups"
BACKUPS.mkdir(parents=True, exist_ok=True)

PALETTE_KEY = "eden_dream"  # change via dropdown if you like
DEFAULTS = {
    "palettes": {
        "eden_dream": {"bg": "#0b1020", "fg": "#e6f0ff", "accent": "#7aa2f7", "muted": "#94a3b8"},
        "velvet_division": {"bg": "#1a1417", "fg": "#F7E7F3", "accent": "#E84C7F", "muted": "#A08A98"},
        "rootfire": {"bg": "#0e0f0a", "fg": "#f0f5e1", "accent": "#b0f566", "muted": "#93a48a"}
    }
}

def load_json(p: Path, fallback):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return fallback

class RheaGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rhea — Self-Editing Registry")
        self.geometry("1100x700")
        self.registry = load_json(REGISTRY_PATH, {"version": 1, **DEFAULTS, "daemons": {}, "teams": {}, "groups": {}, "pairs": [], "tasks": []})
        self.schema = load_json(SCHEMA_PATH, {})
        self.palette = self.registry.get("palettes", DEFAULTS["palettes"]).get(PALETTE_KEY, DEFAULTS["palettes"][PALETTE_KEY])
        self._style()
        self._build()

    def _style(self):
        self.configure(bg=self.palette["bg"])
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=self.palette["bg"], foreground=self.palette["fg"])
        style.configure("TLabel", background=self.palette["bg"], foreground=self.palette["fg"])
        style.configure("TButton", background=self.palette["accent"], foreground=self.palette["bg"], padding=6)
        style.map("TButton", background=[("active", self.palette["muted"])])
        style.configure("Treeview", background=self.palette["bg"], fieldbackground=self.palette["bg"], foreground=self.palette["fg"])

    def _build(self):
        root = ttk.Frame(self); root.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left = ttk.Frame(root); left.pack(side=tk.LEFT, fill=tk.Y)
        right = ttk.Frame(root); right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(left, columns=("type",), show="tree")
        self.tree.pack(fill=tk.Y, expand=True)
        self._reload_tree()
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        btns = ttk.Frame(left); btns.pack(fill=tk.X, pady=8)
        ttk.Button(btns, text="Add Daemon", command=self._add_daemon).pack(fill=tk.X)
        ttk.Button(btns, text="Remove", command=self._remove_selected).pack(fill=tk.X)
        ttk.Button(btns, text="Save", command=self._save).pack(fill=tk.X)
        ttk.Button(btns, text="Validate", command=self._validate).pack(fill=tk.X)
        ttk.Button(btns, text="Diff", command=self._diff).pack(fill=tk.X)
        ttk.Button(btns, text="Reload", command=self._reload_tree).pack(fill=tk.X)

        # Editor
        self.editor = tk.Text(right, wrap=tk.NONE)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self._show_json(self.registry)

    def _reload_tree(self):
        self.tree.delete(*self.tree.get_children())
        self.tree.insert("", tk.END, iid="daemons", text="Daemons")
        for name in sorted(self.registry.get("daemons", {}).keys()):
            self.tree.insert("daemons", tk.END, iid=f"d:{name}", text=name)
        self.tree.insert("", tk.END, iid="teams", text="Teams")
        for t in sorted(self.registry.get("teams", {}).keys()):
            self.tree.insert("teams", tk.END, iid=f"t:{t}", text=t)
        self.tree.insert("", tk.END, iid="pairs", text="Pairs")
        self.tree.insert("", tk.END, iid="tasks", text="Tasks")

    def _on_select(self, _=None):
        sel = self.tree.selection()
        if not sel: return
        node = sel[0]
        if node == "daemons":
            self._show_json(self.registry.get("daemons", {}))
        elif node.startswith("d:"):
            name = node.split(":",1)[1]
            self._show_json(self.registry["daemons"][name])
        elif node == "teams":
            self._show_json(self.registry.get("teams", {}))
        elif node.startswith("t:"):
            t = node.split(":",1)[1]
            self._show_json(self.registry["teams"][t])
        elif node == "pairs":
            self._show_json(self.registry.get("pairs", []))
        elif node == "tasks":
            self._show_json(self.registry.get("tasks", []))
        else:
            self._show_json(self.registry)

    def _show_json(self, obj):
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", json.dumps(obj, indent=2))

    def _read_editor_json(self):
        try:
            return json.loads(self.editor.get("1.0", tk.END))
        except Exception as e:
            messagebox.showerror("Invalid JSON", str(e))
            return None

    def _add_daemon(self):
        name = simple_prompt(self, "New daemon name:")
        if not name: return
        d = {
            "name": name,
            "path": f"all_daemons/{name}/{name.lower()}.py",
            "enabled": True,
            "tags": [],
            "team": "Unassigned",
            "group": "Default",
            "env": {},
            "start": {"type": "python", "args": [f"{name.lower()}.py"]}
        }
        self.registry.setdefault("daemons", {})[name] = d
        self.registry.setdefault("teams", {}).setdefault("Unassigned", {"members": []})
        if name not in self.registry["teams"]["Unassigned"]["members"]:
            self.registry["teams"]["Unassigned"]["members"].append(name)
        self._reload_tree(); self._show_json(d)

    def _remove_selected(self):
        sel = self.tree.selection();
        if not sel: return
        node = sel[0]
        if node.startswith("d:"):
            name = node.split(":",1)[1]
            if messagebox.askyesno("Confirm", f"Remove daemon {name} from registry? (File not deleted)"):
                self.registry["daemons"].pop(name, None)
                for t in self.registry.get("teams", {}).values():
                    if name in t.get("members", []):
                        t["members"] = [m for m in t["members"] if m != name]
                self._reload_tree(); self._show_json(self.registry)

    def _diff(self):
        if not REGISTRY_PATH.exists():
            messagebox.showinfo("Diff", "No saved registry yet.")
            return
        current = json.dumps(json.loads(REGISTRY_PATH.read_text(encoding="utf-8")), indent=2).splitlines()
        edited = json.dumps(self.registry, indent=2).splitlines()
        diff = "\n".join(difflib.unified_diff(current, edited, fromfile="saved", tofile="edited", lineterm=""))
        show_text(self, "Diff", diff or "No changes")

    def _validate(self):
        if not self.schema:
            messagebox.showinfo("Validate", "Schema not found; save anyway?")
            return True
        errors = list(Draft7Validator(self.schema).iter_errors(self.registry))
        if not errors:
            messagebox.showinfo("Validate", "Registry is VALID ✨")
            return True
        msg = "\n".join([f"/{'/'.join(map(str, e.path))}: {e.message}" for e in errors])
        show_text(self, "Validation errors", msg)
        return False

    def _save(self):
        # Pull JSON from editor if the user is editing a subset
        maybe = self._read_editor_json()
        if maybe is not None:
            # Try to smart-merge when the editor view is a nested object
            sel = self.tree.selection()
            if sel:
                node = sel[0]
                if node.startswith("d:"):
                    name = node.split(":",1)[1]
                    self.registry["daemons"][name] = maybe
                elif node.startswith("t:"):
                    t = node.split(":",1)[1]
                    self.registry["teams"][t] = maybe
                elif node == "daemons":
                    self.registry["daemons"] = maybe
                elif node == "teams":
                    self.registry["teams"] = maybe
                elif node == "pairs":
                    self.registry["pairs"] = maybe
                elif node == "tasks":
                    self.registry["tasks"] = maybe
                else:
                    self.registry = maybe
        if not self._validate():
            return
        # Backup (copy, do not move the original away)
        ts = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUPS / f"registry_{ts}.json"
        if REGISTRY_PATH.exists():
            try:
                import shutil as _shutil
                _shutil.copy2(REGISTRY_PATH, backup_path)
            except Exception:
                pass
        REGISTRY_PATH.write_text(json.dumps(self.registry, indent=2), encoding="utf-8")
        messagebox.showinfo("Saved", f"Registry saved. Backup at {backup_path.name}")
        self._reload_tree()


def show_text(parent, title, text):
    w = tk.Toplevel(parent); w.title(title)
    t = tk.Text(w, wrap=tk.NONE)
    t.pack(fill=tk.BOTH, expand=True)
    t.insert("1.0", text)


def simple_prompt(parent, prompt):
    w = tk.Toplevel(parent); w.title(prompt)
    var = tk.StringVar()
    ttk.Entry(w, textvariable=var).pack(fill=tk.X, padx=10, pady=10)
    out = {"value": None}
    def ok(): out["value"] = var.get(); w.destroy()
    ttk.Button(w, text="OK", command=ok).pack(pady=6)
    parent.wait_window(w)
    return out["value"]

if __name__ == "__main__":
    app = RheaGUI(); app.mainloop()
