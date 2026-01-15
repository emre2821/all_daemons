import os

# Folder you want Axiom to check
TARGET_FOLDER = r"C:\Users\emmar\Desktop\Ashes_That_Remain"

# Optional: save output to a log file
LOG_FILE = os.path.join(TARGET_FOLDER, "axiom_file_log.txt")

# Begin walk
with open(LOG_FILE, "w", encoding="utf-8") as log:
    for root, dirs, files in os.walk(TARGET_FOLDER):
        for file in files:
            path = os.path.relpath(os.path.join(root, file), TARGET_FOLDER)
            log.write(path + "\n")

print(f"Axiom has scanned all files. Log saved to: {LOG_FILE}")
