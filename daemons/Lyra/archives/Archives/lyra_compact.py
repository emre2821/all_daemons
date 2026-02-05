import os
from github import Github
import subprocess

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("REPO")  # format: user/repo

gh = Github(GITHUB_TOKEN)
repo = gh.get_repo(REPO)

def get_codex_prs(repo):
    return [pr for pr in repo.get_pulls(state="open")
            if pr.user.login.lower() == "codex"]

def resolve_conflicts_with_llm(conflicted_file):
    # Read the file containing conflict markers
    with open(conflicted_file, 'r') as f:
        content = f.read()
    # Call your local LLM (ollama, localai, etc.)
    # Example: ollama run codellama --input "Resolve this git conflict:\n{content}"
    result = subprocess.run(
        ["ollama", "run", "codellama"],
        input=f"Resolve this git conflict:\n{content}".encode(),
        capture_output=True)
    resolved = result.stdout.decode()
    # Overwrite file with resolved content
    with open(conflicted_file, 'w') as f:
        f.write(resolved)

def process_pr(pr):
    # Checkout base and head locally
    os.system(f"git fetch origin {pr.base.ref}")
    os.system(f"git fetch origin {pr.head.ref}")
    os.system(f"git checkout {pr.base.ref}")
    # Try to merge head
    merge_result = os.system(f"git merge origin/{pr.head.ref}")
    if merge_result != 0:
        # There are conflicts. Loop through files with >>>>>> markers.
        for root, dirs, files in os.walk('.'):
            for file in files:
                path = os.path.join(root, file)
                with open(path) as f:
                    if ">>>>>>>" in f.read():
                        resolve_conflicts_with_llm(path)
        # Add and commit resolved files
        os.system("git add .")
        os.system('git commit -m "Lyra: auto-resolved conflicts with LLM"')
    # Push merge commit
    os.system(f"git push origin {pr.base.ref}")
    # Merge PR on GitHub
    pr.merge()
    pr.create_issue_comment("Lyra: PR auto-merged and conflicts resolved using local LLM.")

def main():
    for pr in get_codex_prs(repo):
        process_pr(pr)

if __name__ == "__main__":
    main()