import os
import shutil

# 👇 SET THIS TO YOUR DAEMON SOURCE FOLDER
source_folder = r"C:\Users\emmar\Desktop\borington\03_Projects\Compressed\01_Urgent\Echolace_DI_EdenOS_Core\Daemon_Core\Daemons_I_Will_Use"

# This will move each .py file into a same-named folder
for filename in os.listdir(source_folder):
    if filename.endswith(".py"):
        filepath = os.path.join(source_folder, filename)
        daemon_name = filename[:-3]  # remove ".py"

        # Create new folder with same name as the daemon (if it doesn't exist)
        daemon_folder = os.path.join(source_folder, daemon_name)
        os.makedirs(daemon_folder, exist_ok=True)

        # Move the file into its new home
        new_path = os.path.join(daemon_folder, filename)
        shutil.move(filepath, new_path)
        print(f"Moved: {filename} → {daemon_folder}")
