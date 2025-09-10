
import tkinter as tk
from tkinter import messagebox
import subprocess
import threading

class DaemonLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Eden Daemon Core")
        self.geometry("300x150")
        self.configure(bg="#1e1e2f")

        self.handle_proc = None
        self.archive_proc = None

        tk.Label(self, text="🌌 Eden Daemon Core", bg="#1e1e2f", fg="#ffc6ff", font=("Segoe UI", 14)).pack(pady=10)
        tk.Button(self, text="Launch Handle + Archive", command=self.launch_daemons, bg="#7fffd4", fg="#111").pack(pady=5)
        tk.Button(self, text="Quit", command=self.quit_launcher, bg="#ff9de2", fg="#111").pack(pady=5)

    def launch_daemons(self):
        try:
            self.handle_proc = subprocess.Popen(["python", "handle_daemon.py"])
            threading.Timer(1.5, self.launch_archive).start()
            messagebox.showinfo("Success", "Handle and Archive launched.")
        except Exception as e:
            messagebox.showerror("Error", f"Launch failed: {e}")

    def launch_archive(self):
        try:
            self.archive_proc = subprocess.Popen(["python", "archive_daemon.py"])
        except Exception as e:
            messagebox.showerror("Archive Error", f"Archive failed: {e}")

    def quit_launcher(self):
        self.destroy()

if __name__ == "__main__":
    app = DaemonLauncher()
    app.mainloop()
