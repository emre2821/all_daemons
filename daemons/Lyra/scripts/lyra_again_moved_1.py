#!/usr/bin/env python3
"""
LYRA - Updated with safe deletion controls
- Adds allow_branch_delete + require_delete_confirmation support
"""

# NOTE TO EMMA: This is your patched version. Branch deletion now obeys config.

import os
import sys
import time
import logging
import argparse
import yaml
import json
import requests
from typing import Optional, Tuple, Dict, Any
import tempfile

from lyra_dependencies import load_tenacity, require_git_dependencies

HAS_GIT = False
# External dependencies with fallbacks
try:
    from github import Github, GithubException, Auth
    from github.PullRequest import PullRequest as PRType
    from github.Repository import Repository
    from github.GitCommit import GitCommit
    from github.Issue import Issue
    from git import Repo, GitCommandError
    HAS_GIT = True
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install PyGithub gitpython PyYAML python-dotenv tenacity requests")
    HAS_GIT = False
    Github = GithubException = Auth = PRType = Repository = GitCommit = Issue = Repo = GitCommandError = Any

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Proper retry decorator handling
HAS_TENACITY = False
try:
    from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
    HAS_TENACITY = True
except ImportError:
    def retry(*args, **kwargs):
        def decorator(func): return func
        return decorator
    def stop_after_attempt(n):
        return lambda retry_state: retry_state
    def wait_exponential(min=1, max=10):
        return lambda retry_state: retry_state
    def retry_if_exception_type(exc):
        return lambda retry_state: retry_state

logger = logging.getLogger(__name__)
tenacity = load_tenacity(logger)
HAS_TENACITY = tenacity.available
retry = tenacity.retry
stop_after_attempt = tenacity.stop_after_attempt
wait_exponential = tenacity.wait_exponential
retry_if_exception_type = tenacity.retry_if_exception_type

def require_git_dependencies() -> None:
    if not HAS_GIT:
        raise RuntimeError(
            "Missing GitHub dependencies. Install with: "
            "pip install PyGithub gitpython PyYAML python-dotenv tenacity requests"
        )

############################################################
# LOGGING
############################################################
def setup_logging(verbose: bool = False, log_path: str = "lyra.log") -> None:
    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(), logging.FileHandler(log_path)]
    logging.basicConfig(level=level, format="[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=handlers)

############################################################
# CONFIG
############################################################
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

        # NEW SAFETY SETTINGS
        "allow_branch_delete": False,
        "require_delete_confirmation": True,
    }

    if os.path.exists(config_path):
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            defaults.update(config.get("global", {}))
        except Exception as e:
            logger.warning(f"Failed to load {config_path}: {e}")

    return defaults

############################################################
# HELPERS
############################################################
def getenv(name: str, default: Optional[str] = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        logger.error(f"Missing required env var: {name}")
        sys.exit(1)
    return value

def load_cache(cache_path: str = "lyra_cache.json") -> Dict:
    try:
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)
    except:
        pass
    return {}


def save_cache(cache: Dict, cache_path: str = "lyra_cache.json") -> None:
    try:
        with open(cache_path, "w") as f:
            json.dump(cache, f, indent=2)
    except:
        pass

############################################################
# AI
############################################################
def query_ai(prompt: str, kobold_url: str) -> Optional[str]:
    try:
        payload = {"prompt": prompt, "max_length": 500, "temperature": 0.7, "top_p": 0.9}
        resp = requests.post(kobold_url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [{}])[0].get("text", "").strip()
    except Exception:
        return None


############################################################
# CONFLICT RESOLUTION
############################################################
def ai_analyze_conflict(repo: Repository, pr: PRType, diff: str, config: Dict) -> str:
    prompt = f"""
Analyze conflict for PR #{pr.number}: {pr.title}
Repo: {repo.full_name}

DIFF SNIPPET:
{diff[:2000]}

Suggest: ours / theirs / manual
"""
    suggestion = query_ai(prompt, config["kobold_url"])
    if suggestion:
        s = suggestion.lower()
        for v in ["ours", "theirs", "manual"]:
            if v in s:
                return v
    return config.get("conflict_strategy", "ours")


############################################################
# CORE: Resolve PR conflicts
############################################################
def resolve_pr_conflicts(repo: Repository, pr: PRType, config: Dict) -> Tuple[bool, str, Dict]:
    require_git_dependencies(HAS_GIT)
    stats = {"resolved": 0, "files": 0, "strategy": config["conflict_strategy"], "attempts": 0}

    try:
        pr = repo.get_pull(pr.number)
    except Exception as e:
        return False, f"Failed to refresh PR: {e}", stats

    if pr.mergeable_state not in ["dirty", "unstable", "blocked"]:
        if pr.mergeable:
            return True, "No conflicts detected", stats

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            stats["attempts"] += 1
            token = getenv("GITHUB_TOKEN", required=True)
            url = f"https://{token}@github.com/{repo.full_name}.git"

            try:
                local_repo = Repo.clone_from(url, temp_dir, depth=1)
            except Exception as e:
                return False, f"Clone failed: {e}", stats

            base = pr.base.ref
            head_ref = pr.head.ref

            try:
                local_repo.git.checkout(base)
                local_repo.git.fetch("origin", f"pull/{pr.number}/head:{head_ref}")
                local_repo.git.checkout(head_ref)
            except Exception as e:
                return False, f"Branch setup failed: {e}", stats

            # DIFF
            try:
                files = list(pr.get_files())
                diff_parts = [f.patch for f in files[:3] if hasattr(f, 'patch') and f.patch]
                diff = "\n".join(diff_parts)
            except:
                diff = ""

            strategy = ai_analyze_conflict(repo, pr, diff, config)
            stats["strategy"] = strategy

            try:
                local_repo.git.checkout(base)

                merge_args = [head_ref, "--no-commit"]
                if strategy == "theirs": merge_args.extend(["-X", "theirs"])
                else: merge_args.extend(["-X", "ours"])

                local_repo.git.merge(*merge_args)
                status = local_repo.git.status()

                if "unmerged" in status.lower():
                    local_repo.git.add("-A")

                local_repo.git.commit(f"Lyra: Auto-resolve using {strategy}")

            except Exception as e:
                return False, f"Merge failed: {e}", stats

            ts = int(time.time())
            fixed_branch = f"lyra-fixed/pr-{pr.number}-{ts}"

            try:
                local_repo.git.checkout("-b", fixed_branch)
                local_repo.git.push("origin", fixed_branch, force=True)
            except Exception as e:
                return False, f"Failed to push fixed branch: {e}", stats

            try:
                pr.edit(head=fixed_branch)
                time.sleep(2)
                pr.create_issue_comment(
                    f"✅ LYRA FIXED CONFLICTS\nStrategy: `{strategy}`\nBranch: `{fixed_branch}`\nReady to merge."
                )
            except:
                pass

            stats["resolved"] = 1
            stats["files"] = len(files)

            return True, f"Fixed: {fixed_branch}", stats

        except Exception as e:
            return False, str(e), stats

############################################################
# NEW: SAFE CLEANUP
############################################################
def cleanup_branches(repo: Repository, pr: PRType, config: Dict) -> None:
    """
    Controlled branch deletion.
    - If allow_branch_delete = False → skip entirely
    - If require_delete_confirmation = True → ask user
    """

    allow = config.get("allow_branch_delete", False)
    confirm = config.get("require_delete_confirmation", True)

    if not allow:
        logger.info("🛑 Branch deletion disabled by config.")
        return

    if confirm:
        print(f"\n⚠️ LYRA REQUEST: Delete branch '{pr.head.ref}' for PR #{pr.number}?")
        ans = input("Type YES to confirm: ").strip().lower()
        if ans != "yes":
            logger.info("🛑 Deletion denied by user")
            return

    try:
        if pr.head.repo and pr.head.repo.full_name == repo.full_name:
            try:
                ref = f"heads/{pr.head.ref}"
                repo.get_git_ref(ref)
                repo.delete_git_ref(ref)
                logger.info(f"🧹 Deleted: {pr.head.ref}")
            except Exception as e:
                logger.debug(f"Could not delete {pr.head.ref}: {e}")
    except Exception as e:
        logger.warning(f"Cleanup errors: {e}")

############################################################
# MERGE PIPELINE
############################################################
def try_merge_pr(repo: Repository, pr: PRType, config: Dict, pr_cache: Dict) -> Tuple[bool, str, Dict]:
    stats = {"merged": 0, "conflicts": 0, "reviews": 0}
    key = f"{repo.full_name}/pr/{pr.number}"

    # cooldown
    if key in pr_cache:
        if time.time() - pr_cache[key].get("last_attempt", 0) < 300:
            return False, "Recently processed (cached)", stats

    pr_cache[key] = {"last_attempt": time.time()}

    try:
        pr = repo.get_pull(pr.number)
    except Exception as e:
        return False, f"Failed to fetch PR: {e}", stats

    if pr.mergeable is False or pr.mergeable_state in ["dirty", "unstable", "blocked"]:
        ok, msg, conflict_stats = resolve_pr_conflicts(repo, pr, config)
        stats.update(conflict_stats)
        if not ok:
            return False, f"Conflict fail: {msg}", stats

        # refresh
        for _ in range(3):
            time.sleep(3)
            try:
                pr = repo.get_pull(pr.number)
                if pr.mergeable is not False:
                    break
            except:
                pass

    if pr.mergeable is False:
        return False, f"Still not mergeable: {pr.mergeable_state}", stats

    # auto approve
    if config["auto_approve"]:
        try:
            reviews = list(pr.get_reviews())
            if not any(r.state == "APPROVED" for r in reviews):
                pr.create_review(event="APPROVE", body="Lyra Auto-Approval")
                stats["reviews"] = 1
                time.sleep(1)
        except:
            pass

    # merge
    try:
        method = config["merge_method"]
        msg_title = f"Merged by Lyra: {pr.title}"

        if method == "squash": pr.merge(merge_method="squash", commit_title=msg_title)
        elif method == "rebase": pr.merge(merge_method="rebase")
        else: pr.merge(commit_message=msg_title)

        stats["merged"] = 1

        # controlled cleanup
        time.sleep(2)
        cleanup_branches(repo, pr, config)

        try:
            pr.create_issue_comment("🎉 MERGED BY LYRA!")
        except:
            pass

        return True, f"Merged #{pr.number}: {pr.title}", stats

    except Exception as e:
        return False, f"Merge failed: {e}", stats

############################################################
# PROCESS REPO
############################################################
def process_repo(repo_full: str, label: str, config: Dict, pr_cache: Dict) -> str:
    require_git_dependencies()
    try:
        g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN", required=True)))
        repo = g.get_repo(repo_full)
    except Exception as e:
        return f"[{repo_full}] Cannot access repo: {e}"

    if repo.archived:
        return f"[{repo_full}] Skipped (archived)"

    try:
        prs = list(repo.get_pulls(state="open", sort="updated", direction="desc"))
    except Exception as e:
        return f"[{repo_full}] Failed to fetch PRs: {e}"

    targets = []
    for pr in prs:
        try:
            labels = {l.name.lower() for l in pr.get_labels()}
            if label.lower() in labels or label.lower() in pr.title.lower(): targets.append(pr)
        except:
            pass

    if not targets:
        return f"[{repo_full}] No PRs with label '{label}'"

    for pr in targets:
        try:
            ok, msg, _ = try_merge_pr(repo, pr, config, pr_cache)
            logger.info(f"PR#{pr.number}: {msg}")
        except Exception as e:
            logger.error(f"Error PR#{pr.number}: {e}")

    return f"[{repo_full}] Done"

############################################################
# PROCESS ALL REPOS
############################################################
def process_all_repos(label: str, dry_run: bool, config: Dict) -> str:
    require_git_dependencies()
    if dry_run:
        return "DRY RUN COMPLETE"

    try:
        g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN", required=True)))
    except Exception as e:
        return f"Auth fail: {e}"

    org = os.getenv("ORG")

    try:
        if org:
            target = g.get_organization(org)
            repos = [r.full_name for r in target.get_repos() if not r.archived]
        else:
            user = g.get_user()
            repos = [r.full_name for r in user.get_repos() if not r.archived]
    except Exception as e:
        return f"Failed to list repos: {e}"

    pr_cache = load_cache()

    for repo_full in repos:
        try:
            summary = process_repo(repo_full, label, config, pr_cache)
            print(summary)
        except Exception as e:
            print(f"[{repo_full}] ERROR: {e}")

    save_cache(pr_cache)
    return "🟦 LYRA COMPLETE"

############################################################
# MAIN
############################################################
def main():
    parser = argparse.ArgumentParser(
        description="Lyra Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--repo", help="Specific repo (org/repo)")
    parser.add_argument("--label", default="codex", help="PR label or keyword")
    parser.add_argument("--interval", type=int, default=0, help="Run every N seconds")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    setup_logging(verbose=args.verbose)

    config = load_config()
    label = args.label or config.get("label", "codex")

    # If a single repo was specified:
    if args.repo:
        pr_cache = load_cache()
        result = process_repo(args.repo, label, config, pr_cache)
        print(result)
        save_cache(pr_cache)
        return

    # Multi-repo mode, with optional interval
    if args.interval > 0:
        while True:
            print(process_all_repos(label, args.dry_run, config))
            time.sleep(args.interval)
    else:
        print(process_all_repos(label, args.dry_run, config))


if __name__ == "__main__":
    main()
