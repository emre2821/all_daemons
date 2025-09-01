import os

INPUT_FILE = "make_a_new_file_list.txt"
KEEP_FILE = "keep_files.txt"
PURGE_FILE = "purge_files.txt"
REVIEW_FILE = "review_files.txt"

def classify_file(file_path):
    # Customize this logic with regex or keywords
    file_lower = file_path.lower()
    if file_lower.endswith((".tmp", ".log", ".bak", ".old")):
        return "purge"
    elif any(keyword in file_lower for keyword in ["eden", "important", "archive", "sacred"]):
        return "keep"
    else:
        return "review"

def process_file_list():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, "r", encoding="utf-8", errors="ignore") as infile,          open(KEEP_FILE, "w") as keep_out,          open(PURGE_FILE, "w") as purge_out,          open(REVIEW_FILE, "w") as review_out:

        for line in infile:
            path = line.strip()
            category = classify_file(path)
            if category == "keep":
                keep_out.write(path + "\n")
            elif category == "purge":
                purge_out.write(path + "\n")
            else:
                review_out.write(path + "\n")

    print("Classification complete.")

if __name__ == "__main__":
    process_file_list()
