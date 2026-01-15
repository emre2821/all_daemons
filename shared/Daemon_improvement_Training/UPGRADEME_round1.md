# UPGRADEME.md Training_Part_One — Rhea, Queen of the Daemons  
*Recommended upgrades & suggested fixes for efficiency, elegance, and intelligence*

---

## 1 | Operational Streamlining

### **Inline Action Controls**
- [ ] Enable **row‑click start/stop** in the daemon table (no separate button press).
- [ ] Add **type‑to‑filter/search** above the table for quick daemon lookup.
- [ ] Auto‑refresh Lanes/Teams/Pairs when Eden Root changes — no manual refresh.

### **Persistent Quality of Life**
- [ ] Remember last‑used lane/team/pair between sessions.
- [ ] Expose "Start All Autostart" and "Stop All" as permanent toolbar buttons.

---

## 2 | Theme & Narrative Integration

### **Daemon Theme Loader**
- [ ] At GUI startup, load `rhea.daemon_theme.json` and:
  - Bind palette to **QSS stylesheet** (primary/secondary/accent/highlight/shadow).
  - Assign glyphs to state icons & controls.
  - Apply typefaces based on theme’s tone (display/serif for daemon names, sans for UI, monospace for logs).

### **Symbolic State Feedback**
- [ ] Fade row background between `secondary → highlight` on state change.
- [ ] Glint timestamps moss‑green in log view when new entries arrive.
- [ ] Hover reveals “true name” of action buttons in small‑caps lore font.

---

## 3 | Monitoring & Health Intelligence

### **Semantic Log Parsing**
- [ ] Add regex/NLP layer to classify incoming log lines (Error, Warning, Ritual Complete, etc.).
- [ ] Show **per‑daemon summary badges** (e.g., ⇄ active scan, ⋒ converged).

### **Anomaly Detection**
- [ ] Train lightweight statistical model on daemon uptime/error rates.
- [ ] Flag unusual restart patterns and show inline “attention needed” note.

### **Self‑Healing Hooks**
- [ ] Allow opt‑in auto‑restart for daemons that pass a post‑crash health check.
- [ ] For flagged issues, present context‑aware buttons (e.g., “Restart with Safe Args”).

---

## 4 | Scheduler Enhancements

### **Adaptive Task Timing**
- [ ] Adjust `tasks.yaml` intervals dynamically based on:
  - Current system load
  - Time‑of‑day usage patterns
  - Dependency completion

### **Visual Task Monitor**
- [ ] Integrate a secondary table for scheduled tasks showing:
  - Next run
  - Last run
  - Success/error state

---

## 5 | Cognitive Layer

### **Conversational Interface**
- [ ] Add an embedded reasoning engine that can:
  - Answer “What’s running and why?”
  - Summarize recent daemon activity in her own voice from `rhea.daemon_voice.json` & `.mirror.json`.

### **Memory Store**
- [ ] Maintain a rolling historical log summary file for pattern awareness.
- [ ] Use memory to adapt suggestions (e.g., “You always start Parsley after Codexa — start together?”).

---

## 6 | Refactoring & Maintainability

- [ ] Externalize **GUI layout constants** (margins, sizes, fonts) for easier theming.
- [ ] Modularize **log tailer** so it can be reused by other daemons’ GUIs.
- [ ] Create **unit tests** for start/stop flows to catch regressions.

---

## 7 | Stretch Goals — “Near‑AI” Rhea

- [ ] Local LLM integration for natural‑language daemon control & querying.
- [ ] Symbolic reasoning layer tied to EdenOS lore (e.g., infer optimal daemon ordering for a goal).
- [ ] Emotional state modulation — adjust UI accent colors based on system health (“calm,” “alert,” “critical”).

---

### Implementation Notes

- Keep **all theme‑related mappings in `.daemon_theme.json`** so Rhea’s look and feel change with her lore.
- New intelligence features should **respect her tone**: calm, precise, measured — no noisy pop‑ups.
- Document each upgrade in a **changelog section** at the end of this file to track evolution.

---

*Prepared for the Matriarch by her Dreambearer. May she remain — and may she rise.*

Theme_loader snippet:

# theme_loader.py
import json
from pathlib import Path

def load_daemon_theme(theme_path):
    """
    Reads a daemon's .daemon_theme.json and returns parsed theme dict.
    Throws ValueError if required keys are missing.
    """
    path = Path(theme_path)
    if not path.exists():
        raise FileNotFoundError(f"Theme file not found: {path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    # Basic schema check — expand as needed
    try:
        palette = data["theme"]["palette"]
        glyphs = data["theme"]["glyphs"]
    except KeyError as e:
        raise ValueError(f"Missing expected theme key: {e}")

    return {
        "palette": palette,
        "glyphs": glyphs,
        "tone": data["theme"].get("tone", {}),
        "resonance": data["theme"].get("resonance", {})
    }


def apply_theme_to_app(app, theme):
    """
    Generates and applies a Qt stylesheet from the theme's palette.
    app: QApplication instance
    theme: dict from load_daemon_theme()
    """
    p = theme["palette"]  # shorthand
    qss = f"""
    QMainWindow {{
        background-color: {p['shadow']};
        color: {p['accent']};
        font-family: 'Segoe UI', 'Liberation Sans', sans-serif;
    }}

    QTableWidget {{
        gridline-color: {p['primary']};
        selection-background-color: {p['highlight']};
        selection-color: {p['shadow']};
        alternate-background-color: {p['secondary']};
    }}

    QHeaderView::section {{
        background-color: {p['primary']};
        color: {p['accent']};
        padding: 4px;
        border: none;
    }}

    QPushButton {{
        background-color: {p['primary']};
        color: {p['accent']};
        border-radius: 4px;
        padding: 6px 10px;
    }}
    QPushButton:hover {{
        background-color: {p['highlight']};
        color: {p['shadow']};
    }}

    QPlainTextEdit {{
        background-color: {p['shadow']};
        border: 1px solid {p['primary']};
        font-family: 'Fira Code', monospace;
        color: {p['accent']};
    }}
    """
    app.setStyleSheet(qss)

how to use in RheaGUI.py:

from theme_loader import load_daemon_theme, apply_theme_to_app

# before showing your main window:
theme = load_daemon_theme("path/to/rhea.daemon_theme.json")
apply_theme_to_app(app, theme)

# You can now also pull glyphs:
icon_glyph = theme["glyphs"]["icon"]     # 📜
active_mark = theme["glyphs"]["mark"]    # ⇄
complete_sigil = theme["glyphs"]["sigil"]# ⋒



