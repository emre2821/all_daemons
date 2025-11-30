import os
from datetime import datetime

# ==== USER CONFIG ====
save_directory = os.path.expanduser("~/Dropbox/CHAOS_Logs")  # Change path to your preferred folder
filename_prefix = "muse_entry"
file_extension = ".chaos"
# =====================

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def generate_filename():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{filename_prefix}_{timestamp}{file_extension}"

def save_entry(text):
    ensure_directory(save_directory)
    filename = generate_filename()
    full_path = os.path.join(save_directory, filename)

    with open(full_path, "w", encoding="utf-8") as file:
        file.write(text)
    
    print(f"✨ Muse entry saved to: {full_path}")

if __name__ == "__main__":
    print("🖋️ Paste your Muse entry below. Press Enter twice to finish:\n")
    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    
    chaos_entry = "\n".join(lines)
    save_entry(chaos_entry)
