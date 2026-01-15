import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt

try:
    # Local imports (discovery + paths)
    from .eden_discovery import discover
    from .eden_paths import eden_root
except Exception:
    # Fallback to relative if executed directly
    from eden_discovery import discover
    from eden_paths import eden_root

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

        # Dynamic discovery
        self.daemons = [d.to_dict() for d in discover()]
        for d in self.daemons:
            box = QHBoxLayout()
            label = QLabel(f"{d['name']}: {d['role']} [{d['safety_level']}] -> {d['status']}")
            btn_plan = QPushButton("Awaken (plan)")
            btn_plan.setStyleSheet("background-color: #444; padding: 6px;")
            btn_plan.clicked.connect(lambda _, name=d['name']: self.run_daemon(name, confirm=False))
            btn_run = QPushButton("Awaken (confirm)")
            btn_run.setStyleSheet("background-color: #6a6; padding: 6px;")
            btn_run.clicked.connect(lambda _, name=d['name']: self.run_daemon(name, confirm=True))
            box.addWidget(label)
            box.addStretch()
            box.addWidget(btn_plan)
            box.addWidget(btn_run)
            content_layout.addLayout(box)

        scroll.setWidget(content)
        self.layout.addWidget(scroll)

        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #2a2a3d; color: #dddddd; padding: 10px;")
        self.layout.addWidget(self.log)

    def run_daemon(self, name: str, confirm: bool = False):
        try:
            eden = str(eden_root())
            env = os.environ.copy()
            env.setdefault("EDEN_ROOT", eden)
            cmd = [sys.executable, os.path.join(eden, "shared", "Daemon_tools", "scripts", "eden_daemon.py"),
                   "run", name]
            if confirm:
                cmd.append("--confirm")
            proc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.log.append(f" Launching {name} ({'confirm' if confirm else 'plan'})\n  cmd: {' '.join(cmd)}")
            # Stream a bit of output into the GUI log
            if proc.stdout:
                for i, line in enumerate(proc.stdout):
                    if i > 200:
                        break
                    self.log.append(line.rstrip())
        except Exception as e:
            self.log.append(f" Failed to awaken {name}: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DaemonCoreGUI()
    gui.resize(700, 600)
    gui.show()
    sys.exit(app.exec_())
