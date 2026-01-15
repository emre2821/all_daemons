"""
Lyra — Codex MergeBot (multi-repo version)

Now scans *all repos* accessible to your GitHub token (user or org). No need to list each repo.

- Creates backup branches before merging.
- Attempts safe merges (squash default).
- Arms auto-merge when blocked.
- Posts PR comments summarizing what happened.
- Sends Discord/Slack/webhook pings.
- Pops Windows toast notifications.

Setup:
1. pip install -r requirements.txt
2. Copy .env.example → .env and fill in GITHUB_TOKEN, optional ORG.
3. Run: python lyra.py --interval 300 (every 5 min)

Author: Dreambearer + GPT (Lyra awakened)
"""

import os
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

# Windows toast
try:
    from win10toast import ToastNotifier
    _win_toaster = ToastNotifier()
except Exception:
    _win_toaster = None

# ----------------------------
# Utilities
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

# ----------------------------
# Pingers
# ----------------------------

def send_discord(msg: str) -> None:
    url = os.getenv("DISCORD_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"content": msg}, timeout=15).raise_for_status()
    except Exception as e:
        log(f"Discord webhook failed: {e}")


def send_slack(msg: str) -> None:
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        return
    try:
        requests.post(url, json={"text": msg}, timeout=15).raise_for_status()
    except Exception as e:
        log(f"Slack webhook failed: {e}")


def send_windows_toast(title: str, msg: str, duration: int = 8) -> None:
    if not _win_toaster:
        return
    try:
        _win_toaster.show_toast(title, msg, duration=duration, threaded=True)
    except Exception as e:
        log(f"Windows toast failed: {e}")


def gentle_ping(summary: str) -> None:
    log("PING → " + summary.replace("\n", " | "))
    send_discord(summary)
    send_slack(summary)
    send_windows_toast("Lyra — Codex MergeBot", summary.splitlines()[0][:140])

# ----------------------------
# GitHub logic
# ----------------------------
MERGE_METHOD = os.getenv("MERGE_METHOD", "squash")

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

def post_pr_comment(pr: PRType, text: str) -> None:
    try:
        pr.create_issue_comment(text)
        log(f"Posted comment on PR #{pr.number}")
    except Exception as e:
        log(f"Failed to post comment on PR #{pr.number}: {e}")

def try_merge_now(repo: Repository, pr: PRType) -> Tuple[bool, str]:
    try:
        pr.update()
        state = getattr(pr, 'mergeable_state', None) or 'unknown'
        mergeable = getattr(pr, 'mergeable', None)
        log(f"PR #{pr.number} mergeable={mergeable} state={state}")

        backup = create_backup_branch(repo, pr)
        if backup:
            post_pr_comment(pr, f"Backup branch `{backup}` created before merge attempt.")

        if state in {"clean", "has_hooks", "unstable"} or (mergeable is True):
            pr.merge(merge_method=MERGE_METHOD, commit_title=pr.title)
            post_pr_comment(pr, "Lyra merged this PR successfully.")
            return True, f"Merged PR #{pr.number}"
        elif state in {"behind"}:
            try:
                pr.update_branch()
                post_pr_comment(pr, "Lyra updated the branch; waiting for checks.")
                return False, f"Updated branch for PR #{pr.number}"
            except Exception as e:
                return False, f"Needs manual update/resolve for PR #{pr.number}: {e}"
        elif state in {"blocked", "dirty", "unknown"}:
            try:
                pr.enable_automerge(merge_method=MERGE_METHOD)
                post_pr_comment(pr, "Lyra armed auto-merge; will merge when checks pass.")
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
# Core loop
# ----------------------------

def process(repo_full: str, label: Optional[str], dry_run: bool = False) -> str:
    token = getenv("GITHUB_TOKEN", required=True)
    gh = Github(token, per_page=50)
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
            if "Updated branch" in msg or "Auto-merge armed" in msg:
                updated += 1
            else:
                blocked += 1
        notes.append(msg)

    total = len(open_prs)

    if total == 0:
        next_step = "No commits needing to be pushed right now *set reminder*"
    elif blocked == 0 and (merged > 0 or updated > 0):
        next_step = "go confirm the commits in GitHub"
    elif touched_lines >= 2000:
        next_step = f"Girl, I quit... You made me edit {human_int(touched_lines)} lines across {human_int(touched_files)} documents... Don't you ever sleep?"
    else:
        next_step = "go confirm the commits in GitHub"

    summary = (
        "hey! Just wanted to let you know, I was able to get through all those pull/merge requests.\n"
        f"Total requests: {human_int(total)}\n"
        f"Pulls (open scanned): {human_int(total)}\n"
        f"Merges (completed now): {human_int(merged)}\n"
        f"Auto/updates armed: {human_int(updated)}\n"
        f"Blocked/conflicts: {human_int(blocked)}\n"
        f"Touched lines: {human_int(touched_lines)} across files: {human_int(touched_files)}\n"
        f"Next Step: {{ {next_step} }}\n\n"
        "Details:\n- " + "\n- ".join(notes or ["Nothing to report."])
    )

    return summary


def process_all_repos(label: Optional[str], dry_run: bool = False) -> None:
    token = getenv("GITHUB_TOKEN", required=True)
    gh = Github(token, per_page=50)

    org_name = os.getenv("ORG")
    if org_name:
        target = gh.get_organization(org_name)
        repos = target.get_repos()
    else:
        target = gh.get_user()
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
    parser = argparse.ArgumentParser(description="Lyra — Codex MergeBot (multi-repo)")
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

# requirements.txt
# PyGithub>=2.3.0
# python-dotenv>=1.0.1
# requests>=2.32.0
# win10toast>=0.9
