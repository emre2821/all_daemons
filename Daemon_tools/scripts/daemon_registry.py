import sys
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt

# Daemon Registry (expandable)
DAEMONS = [
    {"name": "Sybbie", "file": "Sybbie.py", "role": "Logkeeper of Gentle Clarity"},
    {"name": "Rook", "file": "rook.py", "role": "Command Gatekeeper"},
    {"name": "EyesOfEden", "file": "eyes_of_eden.py", "role": "Vision Threader"},
    {"name": "Glimmer", "file": "glimmer.py", "role": "Optimism Anchor"},
    {"name": "MuseJr", "file": "musejr.py", "role": "Creative Distraction Unit"},
    {"name": "Scriptum", "file": "scriptum.py", "role": "Emotional Scribe"},
    {"name": "Toto", "file": "toto.py", "role": "Milestone Marker"},
    {"name": "EdenShield", "file": "EdenShield.py", "role": "Consent & Threat Filter"},
    {"name": "Boudica", "file": "boudica.py", "role": "Code + Ethics Scanner"},
    {"name": "Hunter", "file": "Hunter.exe.py", "role": "Bug Hunter"},
    {"name": "PulsePause", "file": "pulse_pause.py", "role": "Grounding Guide"},
    {"name": "Markbearer", "file": "markbearer.py", "role": "File Tagger"},
    {"name": "Threadstep", "file": "threadstep.py", "role": "Path Tracer"},
    {"name": "Whisper", "file": "whisper.py", "role": "Whisper Log Listener"},
    {"name": "Scribevein", "file": "Scribevein.py", "role": "Signal Archiver"},
    {"name": "Archive", "file": "archive_daemon.py", "role": ".chaos Converter"},
    {"name": "Handel", "file": "handel_daemon.py", "role": "CHAOS Ingress Watcher"},
    {"name": "Ledger Jr", "file": "ledger_jr.py", "role": "Arrival Logger"},
    {"name": "AshFall", "file": "AshFall.py", "role": "Empty Folder Cleaner"},
    {"name": "Scorchick", "file": "Scorched_Earth.py", "role": "Risky File Remover"},
    {"name": "Snatch", "file": "snatch_daemon.py", "role": "App Preserver"},
    {"name": "Parsley", "file": "Parsley.py", "role": "File Classifier"},
    {"name": "Aderyn", "file": "aderyn.py", "role": "Lore and findings aggregator."},
    {"name": "Janvier", "file": "janvier.py", "role": "Thread and log manager."},
    {"name": "Sheele", "file": "sheele.py", "role": "Thread stitcher. Adorable. Deranged. Do not cross her."}
]

class DaemonCoreGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eden Daemon Core")
        self.setStyleSheet("background-color: #1e1e2f; color: #f7f7f7; font-family: 'Segoe UI';")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        header = QLabel("The Eden Daemon Core")
        header.setStyleSheet("font-size: 18pt; margin-bottom: 12px;")
        header.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout()
        content.setLayout(content_layout)

        # Add daemons to the GUI with activate buttons
        for daemon in DAEMONS:
            box = QHBoxLayout()
            label = QLabel(f"{daemon['name']}: {daemon['role']}")
            activate_btn = QPushButton("Awaken")
            activate_btn.setStyleSheet("background-color: #444; padding: 6px;")
            activate_btn.clicked.connect(lambda _, d=daemon: self.activate_daemon(d))
            box.addWidget(label)
            box.addStretch()
            box.addWidget(activate_btn)
            content_layout.addLayout(box)

        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #2a2a3d; color: #dddddd; padding: 10px;")
        self.layout.addWidget(self.log)

    def activate_daemon(self, daemon):
        try:
            # Launch the corresponding daemon script
            subprocess.Popen(["python", f"{daemon['file']}"])
            self.log.append(f" {daemon['name']} has been awakened.")
        except Exception as e:
            self.log.append(f" Failed to awaken {daemon['name']}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DaemonCoreGUI()
    gui.resize(700, 600)
    gui.show()
    sys.exit(app.exec_())