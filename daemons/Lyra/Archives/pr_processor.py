import logging
from typing import List, Optional, Tuple, Dict
from datetime import datetime, timezone
from github import GithubException
from github.PullRequest import PullRequest as PRType
from github.Repository import Repository
from github.Issue import Issue  # For closing linked issues
from github.Review import Review

# Assuming MERGE_METHOD is loaded from config/env elsewhere
MERGE_METHOD = "squash"  # Default; override via config

logger = logging.getLogger(__name__)

def fetch_codex_prs(repo: Repository, label: Optional[str]) -> List[PRType]:
    """Fetch open PRs matching the label or 'codex' keyword."""
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
    """Create a backup branch before any risky ops like rebasing."""
    try:
        head_sha = pr.head.sha
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        bname = f"backup/pr-{pr.number}-pre-resolve-{ts}"
        ref_name = f"refs/heads/{bname}"
        repo.create_git_ref(ref=ref_name, sha=head_sha)
        logger.info(f"Created backup branch {bname} -> {head_sha}")
        return bname
    except GithubException as e:
        logger.error(f"Backup failed for PR #{pr.number}: {e}")
        return None

def delete_branch(repo: Repository, pr: PRType) -> None:
    """Delete the PR branch post-merge if it's in the same repo."""
    try:
        if pr.head.repo.full_name == repo.full_name:
            ref = f"refs/heads/{pr.head.ref}"
            repo.get_git_ref(ref).delete()
            logger.info(f"Deleted branch: {pr.head.ref}")
    except GithubException as e:
        logger.warning(f"Failed to delete branch {pr.head.ref}: {e}")

def resolve_linked_issues(repo: Repository, pr: PRType) -> List[str]:
    """Scan PR body/title for 'fixes #N' or 'closes #N' and close matching issues."""
    resolved = []
    body = (pr.body or "") + " " + (pr.title or "")
    import re
    issue_matches = re.findall(r'(?:fixes?|closes?)\s*#(\d+)', body, re.IGNORECASE)
    
    for issue_num in issue_matches:
        try:
            issue = repo.get_issue(int(issue_num))
            if issue.state == "open":
                issue.edit(state="closed")
                resolved.append(f"Closed issue #{issue_num}")
                logger.info(f"Resolved linked issue #{issue_num} via PR #{pr.number}")
        except GithubException as e:
            logger.warning(f"Failed to close issue #{issue_num} for PR #{pr.number}: {e}")
    
    return resolved

def handle_review_comments(pr: PRType, auto_approve: bool = False) -> str:
    """Flag or auto-approve pending reviews (basic; extend for AI suggestions later)."""
    try:
        reviews = list(pr.get_reviews())
        pending = [r for r in reviews if r.state == "REQUEST_CHANGES"]
        if not pending:
            return "No pending reviews."
        
        summary = f"{len(pending)} pending review(s): "
        if auto_approve:
            for review in pending:
                review.submit_review(event="APPROVE", body="🤖 Auto-approved by Lyra (simple changes detected).")
                summary += f"Auto-approved {review.user.login}; "
            return summary
        else:
            return summary + "Flagged for manual review."
    except GithubException as e:
        return f"Review check failed: {e}"

def auto_resolve_conflicts(pr: PRType) -> Tuple[bool, str]:
    """Attempt to rebase/update branch to fix 'behind' or 'dirty' states."""
    state = pr.mergeable_state or 'unknown'
    if state not in {"behind", "dirty"}:
        return False, f"No conflicts to resolve (state: {state})."
    
    try:
        backup = create_backup_branch(pr.repo, pr)  # Backup before rebase
        pr.update_branch()  # This triggers rebase if possible
        pr.update()  # Refresh state
        new_state = pr.mergeable_state
        if new_state in {"clean", "has_hooks", "unstable"}:
            return True, f"Conflicts resolved via rebase (new state: {new_state})."
        else:
            return False, f"Rebase attempted but state still {new_state}."
    except GithubException as e:
        return False, f"Rebase failed: {e}. Manual intervention needed."

def try_merge_now(repo: Repository, pr: PRType, auto_approve_reviews: bool = False) -> Tuple[bool, str, Dict[str, int]]:
    """Full merge attempt with built-in issue/conflict resolution."""
    stats = {"resolved_issues": 0, "resolved_conflicts": 0, "reviews_handled": 0}
    try:
        pr.update()
        state = pr.mergeable_state or 'unknown'
        mergeable = pr.mergeable
        logger.info(f"PR #{pr.number} | State: {state} | Mergeable: {mergeable}")

        # Step 1: Handle reviews
        review_msg = handle_review_comments(pr, auto_approve_reviews)
        if "pending" in review_msg and not auto_approve_reviews:
            return False, f"Reviews pending: {review_msg}", stats

        # Step 2: Resolve conflicts if needed
        conflict_resolved, conflict_msg = auto_resolve_conflicts(pr)
        if conflict_resolved:
            stats["resolved_conflicts"] += 1
            logger.info(conflict_msg)

        # Step 3: Backup before merge
        create_backup_branch(repo, pr)

        # Step 4: Merge if clean now
        if state in {"clean", "has_hooks", "unstable"} or (mergeable is True) or conflict_resolved:
            pr.merge(merge_method=MERGE_METHOD, commit_title=pr.title)
            
            # Step 5: Post-merge resolutions
            resolved_issues = resolve_linked_issues(repo, pr)
            stats["resolved_issues"] = len(resolved_issues)
            
            delete_branch(repo, pr)
            msg = f"Merged PR #{pr.number} | {review_msg} | {conflict_msg} | {', '.join(resolved_issues) if resolved_issues else 'No issues closed'}"
            return True, msg, stats

        elif state in {"blocked", "unknown"}:
            try:
                pr.enable_automerge(merge_method=MERGE_METHOD)
                return False, f"Auto-merge enabled for PR #{pr.number} | {review_msg}", stats
            except GithubException as e:
                return False, f"Auto-merge failed: {e} | {review_msg}", stats

        else:
            return False, f"Unhandled state '{state}' | {review_msg}", stats

    except GithubException as e:
        return False, f"Operation failed for PR #{pr.number}: {e}", stats

def sum_changes(pr: PRType) -> Tuple[int, int]:
    """Tally changed lines/files for reporting."""
    try:
        files = list(pr.get_files())
        lines = sum((f.additions or 0) + (f.deletions or 0) for f in files)
        return lines, len(files)
    except Exception:
        return 0, 0