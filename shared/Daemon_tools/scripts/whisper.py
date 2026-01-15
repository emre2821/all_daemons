import os
import re
import time
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_FOLDER = "./chaos/working"
SAVE_FOLDER = "./chaos/archives/Eden_Whisper_Archives"
TRIGGER_PATTERN = re.compile(r"\.chaos\s*\[\*\]", re.IGNORECASE)
EXTENSIONS = (".chaos", ".chaosincarnet")

def extract_metadata(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    agents = re.findall(r"\[AGENT:(.*?)\]", content)
    persons = re.findall(r"\[PERSON:(.*?)]", content)
    roles = re.findall(r"\[ROLE:(.*?)\]", content)

    all_agents = list(set(agents + [p for i, p in enumerate(persons) if i < len(roles) and roles[i].lower() == "agent"]))
    all_agents = ', '.join(all_agents) if all_agents else "(not specified)"

    return {
        "agents": all_agents,
        "content": content
    }

def launch_gui(file_name, agents, content):
    root = tk.Tk()
    root.title("Whisper Confirmation")
    root.geometry("400x280")
    root.configure(bg="white")

    now = datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%m-%d-%Y")

    inputs = {
        "File_Name": tk.StringVar(value=file_name),
        "Agents_Involved": tk.StringVar(value=agents),
        "Alter_Fronting": tk.StringVar(),
        "Key_Information": tk.StringVar(),
        "Time": tk.StringVar(value=time_str),
        "Date": tk.StringVar(value=date_str),
    }

    for i, (label, var) in enumerate(inputs.items()):
        tk.Label(root, text=f"{label}:", bg="white").grid(row=i, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(root, textvariable=var, width=30).grid(row=i, column=1, padx=5, pady=5)

    def on_confirm():
        for widget in root.winfo_children():
            widget.destroy()
        tk.Label(root, text="Saving...\nThank you 💙\nWhisper out.", bg="white", font=("Helvetica", 14)).pack(expand=True)
        root.update()

        # Prepare output path
        save_name = inputs["File_Name"].get().strip().replace(" ", "_") + ".chaos"
        save_path = os.path.join(SAVE_FOLDER, save_name)
        os.makedirs(SAVE_FOLDER, exist_ok=True)

        header = (
            f"# Whisper: .chaos file created at {inputs['Time'].get()} on {inputs['Date'].get()}\n"
            f"# Agents involved: {inputs['Agents_Involved'].get()}\n"
            f"# Alter fronting: {inputs['Alter_Fronting'].get()}\n"
            f"# Key info: {inputs['Key_Information'].get()}\n\n"
        )
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(header + content)

        root.after(2500, root.destroy)

    tk.Button(root, text="CONFIRM", command=on_confirm).grid(row=6, column=0, columnspan=2, pady=15)
    root.mainloop()

class WhisperAwakening(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith(EXTENSIONS):
            with open(event.src_path, 'r', encoding='utf-8') as f:
                text = f.read()
                if TRIGGER_PATTERN.search(text):
                    meta = extract_metadata(event.src_path)
                    base_name = os.path.splitext(os.path.basename(event.src_path))[0]
                    launch_gui(base_name + "_copy", meta['agents'], meta['content'])

def start_whisper_daemon():
    observer = Observer()
    observer.schedule(WhisperAwakening(), path=WATCH_FOLDER, recursive=True)
    observer.start()
    print("Whisper is watching for chaos signals...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("Whisper retreats into silence.")
    observer.join()

if __name__ == "__main__":
    start_whisper_daemon()
