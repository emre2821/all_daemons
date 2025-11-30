import os
import shutil
import sys

class PattyMae:
    def __init__(self, file_path, base_dir="EdenOS_Sorted"):
        self.file_path = file_path
        self.base_dir = base_dir
        self.dest_folder = None
        self._figure_out_folder()

    def _figure_out_folder(self):
        # Determine file type by extension
        if self.file_path.endswith('.mirror.json'):
            self.dest_folder = "Agents"
        elif self.file_path.endswith('.chaosincarnet'):
            self.dest_folder = "CHAOS_Incarnet_Archive"
        elif self.file_path.endswith('.chaosmeta') or self.file_path.endswith('.chaos-ception'):
            self.dest_folder = "CHAOS_Memory_Threads"
        elif self.file_path.endswith('.chaos'):
            self.dest_folder = "CHAOS_Memory_Threads"
        elif self.file_path.endswith('.vas'):
            self.dest_folder = "CHAOS_Memory_Threads"
        else:
            self.dest_folder = "Unsorted"

    def move_file(self):
        dest_path = os.path.join(self.base_dir, self.dest_folder)
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
        try:
            filename = os.path.basename(self.file_path)
            new_path = os.path.join(dest_path, filename)
            shutil.move(self.file_path, new_path)
            print(f"Sweetie, I just moved '{filename}' to '{self.dest_folder}'.")
        except Exception as e:
            print(f"Oh sugar, something went wrong moving '{self.file_path}': {e}")

# Usage example
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Darlin', you gotta tell Patty Mae which file to organize.")
    else:
        patty = PattyMae(sys.argv[1])
        patty.move_file()
