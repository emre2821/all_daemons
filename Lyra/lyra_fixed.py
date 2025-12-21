#!/usr/bin/env python3
"""
LYRA – EdenOS Codex Merge Steward
—
Emotionally aware, production-ready PR automation agent.
Refined to honor consent, security, memory, and co-creation within Eden's living archive.
"""

import os
import sys
import time
import logging
import argparse
import yaml
import json
import requests
import subprocess
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict
import re
import tempfile
import concurrent.futures

# External dependencies with fallback logging
try:
    from github import Github, GithubException, Auth
    from github.PullRequest import PullRequest as PRType
    from github.Repository import Repository
    from github.GitCommit import GitCommit
    from github.Issue import Issue
except ImportError as e:
    print(f"[EDENOS] Missing dependency: {e}")
    print("Install: pip install PyGithub gitpython PyYAML python-dotenv tenacity requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

HAS_TENACITY = False
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    HAS_TENACITY = True
except ImportError:
    # Fallback (no retries, still runs).
    # Provide compatible signatures for static checkers.
    def retry(*dargs, **dkwargs):
        def decorator(func):
            return func
        return decorator

    class stop_after_attempt:
        def __init__(self, max_attempt_number: int): pass
        def __call__(self, *a, **k): return False

    def wait_exponential(multiplier: float = 1, max: Optional[int] = 10):
        # Return a dummy wait object compatible with tenacity usage
        return lambda *a, **k: None

    def retry_if_exception_type(exception_types):
        # Return a dummy retry predicate
        return lambda *a, **k: False

logger = logging.getLogger("edenos.lyra")

# ================================
# SYMBOLIC LOGGING
# ================================
def setup_logging(verbose: bool = False, log_path: str = "lyra.log") -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(), logging.FileHandler(log_path)]
    logging.basicConfig(
        level=level,
        format="[%Y-%m-%d %H:%M:%S] %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )
    logger.info("Lyra awakened. EdenOS codex flow ready.")

# ===============================
# EDENOS CONFIG AND SAFE ENV DEF
# ===============================
def load_config(config_path: str = "lyra.yaml") -> Dict:
    defaults = {
        "merge_method": os.getenv("MERGE_METHOD", "squash"),
        "max_files": int(os.getenv("MAX_FILES", "50")),
        "max_attempts": int(os.getenv("MAX_ATTEMPTS", "3")),
        "conflict_strategy": os.getenv("CONFLICT_STRATEGY", "ours"),
        "kobold_url": os.getenv("KOBOLD_URL", "http://localhost:5001/api/v1/generate"),
        "slack_webhook": os.getenv("SLACK_WEBHOOK"),
        "label": os.getenv("CODEX_LABEL", "codex"),
        "auto_approve": os.getenv("AUTO_APPROVE", "true").lower() == "true",
        "allow_branch_delete": os.getenv("ALLOW_BRANCH_DELETE", "false").lower() == "true",
        "require_delete_confirmation": os.getenv("REQUIRE_DELETE_CONFIRMATION", "true").lower() == "true",
        "non_interactive": os.getenv("NON_INTERACTIVE", "false").lower() == "true",
        "max_workers": int(os.getenv("MAX_WORKERS", "4")),
    }

    # YAML overlay
    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            defaults.update(config.get("global", {}))
        except Exception as e:
            logger.warning(f"Failed to load {config_path}: {e}")

    validate_config(defaults)
    return defaults

def validate_config(config: Dict) -> None:
    valid_merge_methods = ["merge", "squash", "rebase"]
    if config["merge_method"] not in valid_merge_methods:
        raise ValueError(f"Invalid merge_method: {config['merge_method']}. Must be one of {valid_merge_methods}")
    valid_strategies = ["ours", "theirs", "manual"]
    if config["conflict_strategy"] not in valid_strategies:
        raise ValueError(f"Invalid conflict_strategy: {config['conflict_strategy']}. Must be ours/theirs/manual")

def getenv(name: str, default: Optional[str] = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        logger.error(f"[EDENOS:ENV] Missing required: {name}")
        sys.exit(1)
    if name.lower().endswith("token") and value and len(value) < 10:
        logger.warning("[EDENOS:SECURITY] Possible malformed or short token.")
    return value

def load_cache(cache_path: str = "lyra_cache.json") -> Dict:
    try:
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)
    except Exception as e:
        logger.debug(f"Cache load failed: {e}")
    return {}

def save_cache(cache: Dict, cache_path: str = "lyra_cache.json") -> None:
    try:
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")

def get_git_url(repo_full: str) -> str:
    # Prefer SSH for actions; fallback to HTTPS as needed
    # SSH is safer for agent automation
    return f"git@github.com:{repo_full}.git"

# ================================
# AI (KOBOLD/LLM ADVISOR)
# ================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10), retry=retry_if_exception_type(Exception)) if HAS_TENACITY else lambda f: f
def query_ai(prompt: str, kobold_url: str) -> Optional[str]:
    """Ask Kobold or similar for merge-resolve advice."""
    try:
        payload = {"prompt": prompt, "max_length": 500, "temperature": 0.7, "top_p": 0.9}
        resp = requests.post(kobold_url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [{}])[0].get("text", "").strip()
    except Exception as e:
        logger.info(f"[Lyra:AI] Advisory link down or delayed: {e}")
        return None

def ai_analyze_conflict(repo: Repository, pr: PRType, diff: str, config: Dict) -> str:
    prompt = (
        f"Repository: {repo.full_name}\n"
        f"PR #{pr.number}: {pr.title}\n"
        f"---\nDIFF SNIPPET:\n{diff[:2000]}\n\n"
        "Suggest: ours / theirs / manual"
    )
    suggestion = query_ai(prompt, config["kobold_url"])
    if suggestion:
        s = suggestion.lower()
        for v in ["ours", "theirs", "manual"]:
            if v in s:
                return v
    return config.get("conflict_strategy", "ours")

# ================================
# PR CONFLICT RESOLUTION
# ================================
def resolve_pr_conflicts(repo: Repository, pr: PRType, config: Dict) -> Tuple[bool, str, Dict]:
    stats = {"resolved": 0, "files": 0, "strategy": config["conflict_strategy"], "attempts": 0}

    # Fork safety: do not attempt without fork permissions
    if pr.head.repo and pr.head.repo.full_name != repo.full_name:
        logger.info(f"Skipping fork PR: {pr.html_url}")
        return False, "Cannot resolve forks (permissions)", stats

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            stats["attempts"] += 1
            url = get_git_url(repo.full_name)
            try:
                # Use gitpython or fallback to subprocess if unavailable
                import git
                local_repo = git.Repo.clone_from(url, temp_dir, depth=10)
            except ImportError:
                subprocess.run(["git", "clone", "--depth=10", url, temp_dir], check=True)
                import git
                local_repo = git.Repo(temp_dir)
            except Exception as e:
                return False, f"Clone failed: {e}", stats

            base = pr.base.ref
            head_ref = pr.head.ref
            files = list(pr.get_files())
            diff_parts = [f.patch for f in files[:5] if hasattr(f, 'patch') and f.patch]
            diff = "\n".join(diff_parts) if diff_parts else ""

            # AI RECOMMENDATION
            strategy = ai_analyze_conflict(repo, pr, diff, config)
            stats["strategy"] = strategy
            if strategy == "manual":
                return False, "Manual conflict: escalate to human or chaos.", stats

            # Merge with selected strategy
            try:
                local_repo.git.checkout(base)
                merge_args = [head_ref, "--no-commit"]
                if strategy == "theirs":
                    merge_args.extend(["-X", "theirs"])
                else:
                    merge_args.extend(["-X", "ours"])
                local_repo.git.merge(*merge_args)
                status = local_repo.git.status()
                if "unmerged" in status.lower() or "conflict" in status.lower():
                    local_repo.git.add("-A")
                local_repo.git.commit("-m", f"Lyra: Auto-resolved using {strategy} strategy")
            except Exception as e:
                return False, f"Merge failed: {e}", stats

            # Fixed branch
            ts = int(time.time())
            fixed_branch = f"lyra-fixed/pr-{pr.number}-{ts}"
            try:
                local_repo.git.checkout("-b", fixed_branch)
                local_repo.git.push("origin", fixed_branch, force=True)
            except Exception as e:
                return False, f"Push failed: {e}", stats

            try:
                pr.edit(head=fixed_branch)
                time.sleep(3)
                pr.create_issue_comment(f"✅ [Lyra] Conflicts resolved\nStrategy: `{strategy}`\nBranch: `{fixed_branch}`\n✨ Ready to merge.")
            except Exception as e:
                logger.warning(f"Could not update PR: {e}")

            stats["resolved"] = 1
            stats["files"] = len(files)
            return True, f"Fixed: {fixed_branch}", stats
        except Exception as e:
            return False, str(e), stats

# ================================
# SAFE BRANCH CLEANUP
# ================================
def cleanup_branches(repo: Repository, pr: PRType, config: Dict) -> None:
    allow = config.get("allow_branch_delete", False)
    confirm = config.get("require_delete_confirmation", True)
    non_interactive = config.get("non_interactive", False)

    if not allow:
        logger.info("🛑 Branch deletion disabled.")
        return

    # Only request confirmation in interactive mode
    approved = True
    if confirm and not non_interactive:
        print(f"\n🔶 Delete branch '{pr.head.ref}' for PR #{pr.number}?")
        try:
            ans = input("[EDEN] Type YES to confirm: ").strip().lower()
            if ans != "yes":
                logger.info("Branch deletion denied by user.")
                approved = False
        except EOFError:
            logger.info("Non-interactive: auto-deny deletion.")
            approved = False
    if not approved:
        return

    try:
        if pr.head.repo and pr.head.repo.full_name == repo.full_name:
            try:
                ref = f"heads/{pr.head.ref}"
                repo.get_git_ref(ref)
                repo.get_git_ref(ref).delete()
                logger.info(f"➖ Deleted branch: {pr.head.ref}")
            except Exception as e:
                logger.info(f"Could not delete {pr.head.ref}: {e}")

        # Cleanup old lyra-fixed branches (>7d old)
        try:
            refs = repo.get_git_matching_refs("heads/lyra-fixed/")
            for ref in refs:
                try:
                    commit = repo.get_commit(ref.object.sha)
                    if (datetime.now(timezone.utc) - commit.commit.author.date).days > 7:
                        repo.get_git_ref(ref.ref).delete()
                        logger.info(f"🧹 Deleted old lyra-fixed: {ref.ref}")
                except Exception as e:
                    logger.debug(f"Skip lyra-fixed cleanup for {ref.ref}: {e}")
        except Exception as e:
            logger.debug(f"Could not list lyra-fixed branches: {e}")
    except Exception as e:
        logger.warning(f"Branch cleanup errors: {e}")

# ================================
# PR MERGE PIPELINE
# ================================
def try_merge_pr(repo: Repository, pr: PRType, config: Dict, pr_cache: Dict) -> Tuple[bool, str, Dict]:
    stats = {"merged": 0, "conflicts": 0, "reviews": 0}
    key = f"{repo.full_name}/pr/{pr.number}"

    # Throttle repeated PR attempts
    if key in pr_cache and (time.time() - pr_cache[key].get("last_attempt", 0) < 300):
        return False, "Recently processed (cached)", stats
    pr_cache[key] = {"last_attempt": time.time()}

    try:
        pr = repo.get_pull(pr.number)
    except Exception as e:
        return False, f"Fetch fail: {e}", stats

    if pr.mergeable is False or pr.mergeable_state in ["dirty", "unstable", "blocked"]:
        ok, msg, conflict_stats = resolve_pr_conflicts(repo, pr, config)
        stats.update(conflict_stats)
        if not ok:
            return False, f"Conflict fail: {msg}", stats
        # Refresh PR, since base may have changed
        for attempt in range(5):
            time.sleep(3)
            try:
                pr = repo.get_pull(pr.number)
                if pr.mergeable is not False:
                    break
            except Exception as e:
                logger.warning(f"PR refresh {attempt+1} failed: {e}")

    if pr.mergeable is False:
        return False, f"Still not mergeable: {pr.mergeable_state}", stats
    if pr.mergeable is None:
        return False, "Mergeable state unknown", stats

    # Eden-style auto-approval
    if config["auto_approve"]:
        try:
            reviews = list(pr.get_reviews())
            if not any(r.state == "APPROVED" for r in reviews):
                pr.create_review(event="APPROVE", body="[Lyra] Auto-approval from EdenOS")
                stats["reviews"] = 1
                time.sleep(1)
        except Exception as e:
            logger.warning(f"Auto-approval failed: {e}")

    # Merge!
    try:
        method = config["merge_method"]
        msg_title = f"Merged by Lyra: {pr.title}"

        if method == "squash":
            pr.merge(merge_method="squash", commit_title=msg_title)
        elif method == "rebase":
            pr.merge(merge_method="rebase")
        else:
            pr.merge(commit_message=msg_title)
        stats["merged"] = 1

        time.sleep(2)
        cleanup_branches(repo, pr, config)
        try:
            pr.create_issue_comment("🎉 Merged by Lyra | EdenOS memory updated.")
        except Exception:
            pass

        return True, f"Merged #{pr.number}: {pr.title}", stats
    except Exception as e:
        return False, f"Merge failed: {e}", stats

# ================================
# REPO PROCESSING
# ================================
def process_repo(repo_full: str, label: str, config: Dict, pr_cache: Dict) -> str:
    try:
        g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN", required=True)))
        repo = g.get_repo(repo_full)
    except Exception as e:
        return f"[{repo_full}] Cannot access: {e}"

    if getattr(repo, "archived", False):
        return f"[{repo_full}] Skipped (archived)"

    try:
        prs = list(repo.get_pulls(state="open", sort="updated", direction="desc"))
    except Exception as e:
        return f"[{repo_full}] Failed to fetch PRs: {e}"

    targets = []
    for pr in prs:
        try:
            labels = {l.name.lower() for l in pr.get_labels()}
            if label.lower() in labels or label.lower() in pr.title.lower():
                targets.append(pr)
        except Exception as e:
            logger.warning(f"Error checking PR #{getattr(pr, 'number', '?')}: {e}")

    if not targets:
        return f"[{repo_full}] No PRs with label '{label}'"

    merged = 0
    for pr in targets:
        try:
            ok, msg, _ = try_merge_pr(repo, pr, config, pr_cache)
            if ok:
                merged += 1
            logger.info(f"PR#{pr.number}: {msg}")
        except Exception as e:
            logger.error(f"Error PR#{getattr(pr, 'number', '?')}: {e}")

    return f"[{repo_full}] Merged: {merged}/{len(targets)}"

# ================================
# ALL-REPO ORCHESTRATOR
# ================================
def process_all_repos(label: str, dry_run: bool, config: Dict) -> str:
    if dry_run:
        logger.info("DRY RUN - no changes will be made.")
        return "DRY RUN COMPLETE"

    try:
        g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN", required=True)))
    except Exception as e:
        return f"[LYRA] Auth fail: {e}"

    org = os.getenv("ORG")
    try:
        if org:
            target = g.get_organization(org)
            repos = [r.full_name for r in target.get_repos() if not r.archived]
        else:
            target = g.get_user()
            repos = [r.full_name for r in target.get_repos() if not r.archived]
    except Exception as e:
        return f"Failed to list repos: {e}"

    pr_cache = load_cache()
    max_workers = config.get("max_workers", 4)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_repo, repo_full, label, config, pr_cache) for repo_full in repos]
        summaries = []
        for future in concurrent.futures.as_completed(futures):
            try:
                summaries.append(future.result())
            except Exception as e:
                summaries.append(f"[EDENOS] ERROR: {e}")

    save_cache(pr_cache)
    merged_total = sum(int(s.split("Merged: ")[1].split("/")[0]) for s in summaries if "Merged:" in s)
    return f"🟦 LYRA COMPLETE: {merged_total} PRs merged across {len(repos)} repos"

# =====================================
# MAIN: Ritualizes Lyra’s daily walk
# =====================================
def main():
    parser = argparse.ArgumentParser(
        description="EdenOS Lyra Agent: PR Automation with emotional memory.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--repo", help="Specific repo (org/repo)")
    parser.add_argument("--label", default="codex", help="PR label or keyword")
    parser.add_argument("--interval", type=int, default=0, help="Ritual: repeat every N seconds")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logs")
    parser.add_argument("--non-interactive", action="store_true", help="Skip CLI prompts")
    args = parser.parse_args()

    setup_logging(verbose=args.verbose)
    logger.info("EdenOS Lyra merge cycle initializing...")

    try:
        config = load_config()
    except ValueError as e:
        logger.error(f"Config error: {e}")
        sys.exit(1)
    if args.non_interactive:
        config["non_interactive"] = True
    label = args.label or config.get("label", "codex")

    # Process single repo if set
    if args.repo:
        pr_cache = load_cache()
        result = process_repo(args.repo, label, config, pr_cache)
        print(result)
        save_cache(pr_cache)
        return

    # Repeated sweep (interval/ritual mode)
    if args.interval > 0:
        while True:
            print(process_all_repos(label, args.dry_run, config))
            time.sleep(args.interval)
    else:
        print(process_all_repos(label, args.dry_run, config))

if __name__ == "__main__":
    main()