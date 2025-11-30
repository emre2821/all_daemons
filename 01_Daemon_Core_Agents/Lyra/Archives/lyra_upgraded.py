import os
import sys
import time
import argparse
from datetime import datetime, timezone
from typing import List, Optional, Tuple

import requests
from github import Github
from github.PullRequest import PullRequest as PRType
from github.Repository import Repository

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ----------------------------
# Logging and Environment
# ----------------------------

def log(msg: str) -> None:
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{ts}] {msg}")

def getenv(name: str, default: Optional[str] = None, required: bool = False) -> str:
    v = os.getenv(name, default)
    if required and not v:
        raise SystemExit(f"Missing required env var: {name}")
    return v

def human_int(n: int) -> str:
    return f"{n:,}"

MERGE_METHOD = os.getenv("MERGE_METHOD", "squash")

# ----------------------------
# Comment Silencer
# ----------------------------

def post_pr_comment(pr: PRType, text: str) -> None:
    pass  # Silence is golden

# ----------------------------
# GitHub Logic
# ----------------------------

def fetch_codex_prs(repo: Repository, label: Optional[str]) -> List[PRType]:
    prs = list(repo.get_pulls(state="open", sort="updated", direction="desc"))
    results = []
    for pr in prs:
        title = pr.title or ""
        labels = {l.name.lower() for l in pr.get_labels()}
        if label:
            if label.lower() in labels or label.lower() in title.lower():
                results.append(pr)
        else:
            if "codex" in title.lower():
                results.append(pr)
    return results

def create_backup_branch(repo: Repository, pr: PRType) -> Optional[str]:
    try:
        head_sha = pr.head.sha
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        bname = f"backup/pr-{pr.number}-premerge-{ts}"
        ref_name = f"refs/heads/{bname}"
        repo.create_git_ref(ref=ref_name, sha=head_sha)
        log(f"Created backup branch {bname} -> {head_sha}")
        return bname
    except Exception as e:
        log(f"Failed to create backup branch for PR #{pr.number}: {e}")
        return None

def delete_branch(repo: Repository, pr: PRType) -> None:
    try:
        ref = f"heads/{pr.head.ref}"
        if pr.head.repo.full_name == repo.full_name:
            repo.get_git_ref(ref=f"refs/{ref}").delete()
            log(f"Deleted branch: {ref}")
    except Exception as e:
        log(f"Failed to delete branch {ref}: {e}")

def try_merge_now(repo: Repository, pr: PRType) -> Tuple[bool, str]:
    try:
        pr.update()
        state = getattr(pr, 'mergeable_state', None) or 'unknown'
        mergeable = getattr(pr, 'mergeable', None)
        log(f"PR #{pr.number} mergeable={mergeable} state={state}")

        backup = create_backup_branch(repo, pr)

        if state in {"clean", "has_hooks", "unstable"} or (mergeable is True):
            pr.merge(merge_method=MERGE_METHOD, commit_title=pr.title)
            delete_branch(repo, pr)
            return True, f"Merged PR #{pr.number}"

        elif state in {"behind", "dirty"}:
            try:
                pr.update_branch()
                return False, f"Branch updated for PR #{pr.number}"
            except Exception as e:
                return False, f"Cannot auto-update PR #{pr.number}: {e}"

        elif state in {"blocked", "unknown"}:
            try:
                pr.enable_automerge(merge_method=MERGE_METHOD)
                return False, f"Auto-merge armed for PR #{pr.number}"
            except Exception as e:
                return False, f"Blocked/conflicts on PR #{pr.number}: {e}"

        else:
            return False, f"Unhandled mergeable_state '{state}' on PR #{pr.number}"

    except Exception as e:
        return False, f"Merge attempt failed for PR #{pr.number}: {e}"

def sum_changes(pr: PRType) -> Tuple[int, int]:
    changed_lines = 0
    files_count = 0
    try:
        for f in pr.get_files():
            files_count += 1
            changed_lines += (f.additions or 0) + (f.deletions or 0)
    except Exception:
        pass
    return changed_lines, files_count

# ----------------------------
# Pings
# ----------------------------

def gentle_ping(summary: str) -> None:
    log("PING → " + summary.replace("\n", " | "))

# ----------------------------
# Core Loop
# ----------------------------

def process(repo_full: str, label: Optional[str], dry_run: bool = False) -> str:
    token = getenv("GITHUB_TOKEN", required=True)
    from github import Auth
    gh = Github(auth=Auth.Token(token), per_page=50)
    repo = gh.get_repo(repo_full)

    open_prs = fetch_codex_prs(repo, label)

    merged = 0
    updated = 0
    blocked = 0
    touched_lines = 0
    touched_files = 0
    notes: List[str] = []

    for pr in open_prs:
        cl, cf = sum_changes(pr)
        touched_lines += cl
        touched_files += cf

        if dry_run:
            notes.append(f"DRY RUN → would process PR #{pr.number}: {pr.title}")
            continue

        ok, msg = try_merge_now(repo, pr)
        if ok:
            merged += 1
        else:
            if "updated" in msg.lower():
                updated += 1
            else:
                blocked += 1
        notes.append(msg)

    summary = (
        f"Total PRs: {len(open_prs)} | Merged: {merged} | Updated: {updated} | Blocked: {blocked} | "
        f"Touched: {human_int(touched_lines)} lines in {human_int(touched_files)} files."
    )

    return summary

def process_all_repos(label: Optional[str], dry_run: bool = False) -> None:
    token = getenv("GITHUB_TOKEN", required=True)
    from github import Auth
    gh = Github(auth=Auth.Token(token), per_page=50)

    org_name = os.getenv("ORG")
    target = gh.get_organization(org_name) if org_name else gh.get_user()
    repos = target.get_repos()

    for repo in repos:
        try:
            summary = process(repo.full_name, label, dry_run=dry_run)
            gentle_ping(f"[{repo.full_name}]\n" + summary)
        except Exception as e:
            log(f"Error processing {repo.full_name}: {e}")

# ----------------------------
# Entrypoint
# ----------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Lyra — Codex MergeBot (silent mode)")
    parser.add_argument("--repo", help="single repo (user/repo). If omitted, Lyra scans all accessible repos.")
    parser.add_argument("--label", default=os.getenv("CODEX_LABEL", "codex"), help="label match")
    parser.add_argument("--interval", type=int, default=int(os.getenv("INTERVAL", "0")), help="seconds between runs")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    loop = max(args.interval, 0)

    def run_once():
        if args.repo:
            summary = process(args.repo, args.label, dry_run=args.dry_run)
            gentle_ping(summary)
        else:
            process_all_repos(args.label, dry_run=args.dry_run)

    if loop == 0:
        run_once()
        return

    log(f"Lyra watching {'all repos' if not args.repo else args.repo} every {loop}s; label='{args.label}'")
    while True:
        try:
            run_once()
        except KeyboardInterrupt:
            log("Stopped by user")
            break
        except Exception as e:
            log(f"Run error: {e}")
        time.sleep(loop)

if __name__ == "__main__":
    main()
