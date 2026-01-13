#!/usr/bin/env python3
"""
🚀 LYRA - Ultimate Codex PR Automation Beast
Auto-resolves conflicts, merges PRs, cleans up branches. ONE FILE TO RULE THEM ALL!
"""

import os
import sys
import time
import logging
import argparse
import yaml
import json
import requests
from datetime import datetime
import timezone
from typing import List
import Optional, Tuple, Dict, Any
import re
import tempfile
import shutil
from pathlib import Path

# External dependencies with fallbacks
try:
    from github import Github
import GithubException, Auth
    from github.PullRequest import PullRequest as PRType
    from github.Repository import Repository
    from github.GitCommit import GitCommit
    from github.Issue import Issue
    from git import Repo
    HAS_GIT = True
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Install with: pip install PyGithub gitpython PyYAML python-dotenv tenacity requests")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from tenacity import retry
import stop_after_attempt, wait_exponential, retry_if_exception_type
except ImportError:
def retry(x):

    return  x
    logger = logging.getLogger(__name__)
    logger.warning("tenacity not installed; rate-limit retries disabled.")

# ================================
# LOGGING SETUP
# ================================
def setup_logging(verbose: bool = False, log_path: str = "lyra.log") -> None:

    level = logging.DEBUG if verbose else logging.INFO
    handlers = [logging.StreamHandler(), logging.FileHandler(log_path)]
    logging.basicConfig(
        level=level,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers
    )

logger = logging.getLogger(__name__)

# ================================
# CONFIG & ENV
# ================================
def load_config(config_path: str = "lyra.yaml") -> Dict:

    defaults = {
        "merge_method": os.getenv("MERGE_METHOD", "squash"),
        "max_files": int(os.getenv("MAX_FILES", "50")),
        "max_attempts": int(os.getenv("MAX_ATTEMPTS", "3")),
        "conflict_strategy": os.getenv("CONFLICT_STRATEGY", "ours"),
        "kobold_url": os.getenv("KOBOLD_URL", "http://localhost:5001/api/v1/generate"),
        "slack_webhook": os.getenv("SLACK_WEBHOOK"),
        "label": os.getenv("CODEX_LABEL", "codex"),
        "auto_approve": os.getenv("AUTO_APPROVE", "true").lower() == "true"
    }
    
    try:
        if os.path.exists(config_path):
            with open(config_path) as f:
                config = yaml.safe_load(f) or {}
            defaults.update(config.get("global", {}))
    except Exception as e:
        logger.warning(f"Failed to load {config_path}: {e}")
    
    return defaults

def getenv(name: str, default: Optional[str] = None, required: bool = False) -> str:

    value = os.getenv(name, default)
    if required and not value:
        logger.error(f"Missing required env var: {name}")
        sys.exit(1)
    return value

def human_int(n: int) -> str:

    return f"{n:,}"

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
    except Exception as e:
        logger.warning(f"Failed to save cache: {e}")

# ================================
# AI INTEGRATION
# ================================
def query_ai(prompt: str, kobold_url: str) -> Optional[str]:

    try:
        payload = {"prompt": prompt, "max_length": 500, "temperature": 0.7, "top_p": 0.9}
        resp = requests.post(kobold_url, json=payload, timeout=15)
        resp.raise_for_status()
        return resp.json().get("results", [{}])[0].get("text", "").strip()
    except:
        return None

def ai_analyze_conflict(repo: Repository, pr: PRType, diff: str) -> str:

    prompt = f"""Analyze this GitHub PR conflict in {repo.full_name}:

PR #{pr.number}: {pr.title}
Status: CONFLICTED

{diff[:2000]}

RECOMMENDATION (ours/theirs/manual):"""
    
    suggestion = query_ai(prompt, load_config()["kobold_url"])
    return suggestion or "ours"

# ================================
# CONFLICT RESOLUTION BEAST 🔥
# ================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=10))
def resolve_pr_conflicts(repo: Repository, pr: PRType, config: Dict) -> Tuple[bool, str, Dict]:

    """The heart of Lyra - auto-resolves conflicts like magic ✨"""
    
    if pr.mergeable_state != "conflicted":
        return True, "No conflicts", {"resolved": 0}
    
    stats = {"resolved": 0, "files": 0, "strategy": config["conflict_strategy"]}
    
    logger.info(f"🔧 RESOLVING CONFLICTS → PR #{pr.number}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Clone repo
            token = getenv("GITHUB_TOKEN", required=True)
            url = f"https://{token}@github.com/{repo.full_name}.git"
            local_repo = Repo.clone_from(url, temp_dir)
            
            base = pr.base.ref
            head = pr.head.ref
            
            # Setup for merge
            local_repo.git.checkout(base)
            local_repo.git.fetch(f"origin", f"pull/{pr.number}/head:{head}")
            
            # AI-powered strategy decision
            files = list(pr.get_files())
            diff = "\n".join([f.file_to_patch() for f in files[:3]])
            strategy = ai_analyze_conflict(repo, pr, diff)
            logger.info(f"🧠 AI suggests: {strategy}")
            
            # Execute merge with strategy
            merge_args = [head]
            if strategy == "theirs":
                merge_args.extend(["--strategy-option=theirs"])
            else:  # ours or default
                merge_args.extend(["--strategy-option=ours"])
            
            local_repo.git.merge(*merge_args)
            
            # Create fixed branch
            ts = int(time.time())
            fixed_branch = f"lyra-fixed/pr-{pr.number}-{ts}"
            local_repo.git.checkout("-b", fixed_branch)
            local_repo.git.push("origin", fixed_branch, force=True)
            
            # Update PR
            pr.edit(head=fixed_branch)
            pr.create_issue_comment(
                f"✅ **LYRA CONFLICTS RESOLVED!**\n\n"
                f"🔧 Strategy: `{strategy}`\n"
                f"🎯 Fixed branch: `{fixed_branch}`\n"
                f"🚀 **READY TO MERGE**"
            )
            
            stats["resolved"] = 1
            stats["files"] = len(files)
            
            logger.info(f"🎉 FIXED PR #{pr.number} → {fixed_branch}")
            return True, f"Fixed: {fixed_branch}", stats
            
        except Exception as e:
            logger.error(f"❌ Conflict resolution failed PR #{pr.number}: {e}")
            return False, str(e), stats

# ================================
# MERGE + CLEANUP
# ================================
def try_merge_pr(repo: Repository, pr: PRType, config: Dict, pr_cache: Dict) -> Tuple[bool, str, Dict]:

    """Attempt merge with full conflict resolution pipeline"""
    
    stats = {"merged": 0, "conflicts": 0, "reviews": 0}
    cache_key = f"{repo.full_name}/pr/{pr.number}"
    
    # Conflict resolution first
    if not pr.mergeable and pr.mergeable_state == "conflicted":
        success, msg, conflict_stats = resolve_pr_conflicts(repo, pr, config)
        stats.update(conflict_stats)
        
        if not success:
            return False, f"Conflict resolution failed: {msg}", stats
        
        # Refresh PR after resolution
        time.sleep(2)
        pr = repo.get_pull(pr.number)
    
    if not pr.mergeable:
        return False, f"Still not mergeable: {pr.mergeable_state}", stats
    
    # Auto-approve if enabled
    if config["auto_approve"]:
        reviews = list(pr.get_reviews())
        if len([r for r in reviews if r.state == "APPROVED"]) == 0:
            try:
                pr.create_review(event="APPROVE", body="✅ Lyra Auto-Approval")
                stats["reviews"] = 1
            except:
                pass
    
    # Merge!
    try:
        method = config["merge_method"]
        if method == "squash":
            pr.merge(merge_method="squash")
        elif method == "rebase":
            pr.merge(merge_method="rebase")
        else:
            pr.merge()
        
        stats["merged"] = 1
        
        # CLEANUP BRANCHES 🧹
        cleanup_branches(repo, pr)
        
        msg = f"✅ MERGED #{pr.number}: {pr.title}"
        logger.info(msg)
        
        # Notify
        pr.create_issue_comment(f"🎉 **MERGED BY LYRA!** 🏆")
        send_slack(f"✅ {repo.full_name} PR #{pr.number} MERGED!")
        
        return True, msg, stats
        
    except Exception as e:
        return False, f"Merge failed: {str(e)}", stats

def cleanup_branches(repo: Repository, pr: PRType) -> None:

    """Delete source branch + all lyra-fixed branches"""
    try:
        # Original branch
        if pr.head.repo.full_name == repo.full_name:
            repo.delete_git_ref(f"heads/{pr.head.ref}")
        
        # All lyra-fixed branches for this PR
        branches = [b.name for b in repo.get_branches()]
        pattern = re.compile(rf"lyra-fixed/pr-{pr.number}-\d+")
        
        for branch in branches:
            if pattern.match(branch):
                repo.delete_git_ref(f"heads/{branch}")
                logger.info(f"🧹 Deleted: {branch}")
                
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

# ================================
# NOTIFICATIONS
# ================================
def send_slack(message: str) -> None:

    webhook = load_config()["slack_webhook"]
    if not webhook:
        return
    try:
        requests.post(webhook, json={"text": f"🤖 *Lyra*\n{message}"})
    except:
        pass

# ================================
# MAIN PROCESSING ENGINE
# ================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=4, max=10))
def process_repo(repo_full: str, label: str, config: Dict, pr_cache: Dict) -> str:

    """Process single repo - THE CORE LOGIC"""
    
    g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN")))
    repo = g.get_repo(repo_full)
    
    if repo.archived:
        return f"[{repo_full}] Skipped (archived)"
    
    # Fetch PRs
    prs = list(repo.get_pulls(state="open", sort="updated", direction="desc"))
    codex_prs = []
    
    for pr in prs:
        title = pr.title.lower()
        labels = {l.name.lower() for l in pr.get_labels()}
        
        if label.lower() in labels or label.lower() in title:
            codex_prs.append(pr)
    
    if not codex_prs:
        return f"[{repo_full}] No codex PRs"
    
    stats = {"merged": 0, "conflicts": 0, "updated": 0, "blocked": 0}
    notes = []
    
    for pr in codex_prs:
        ok, msg, pr_stats = try_merge_pr(repo, pr, config, pr_cache)
        stats.update(pr_stats)
        
        if ok:
            stats["merged"] += 1
        elif "conflict" in msg.lower():
            stats["conflicts"] += 1
        elif "behind" in msg.lower():
            stats["updated"] += 1
        else:
            stats["blocked"] += 1
            
        notes.append(msg)
    
    summary = (
        f"[{repo_full}] PRs: {len(codex_prs)} | "
        f"✅{stats['merged']} 🔧{stats['conflicts']} 🔄{stats['updated']} "
        f"⏳{stats['blocked']}"
    )
    
    logger.info(f"{summary} | {' | '.join(notes)}")
    return summary

# ================================
# ORCHESTRATOR
# ================================
def process_all_repos(label: str, dry_run: bool, config: Dict) -> str:

    """Process ALL repos"""
    if dry_run:
        logger.info("🧪 DRY RUN MODE")
        return "DRY RUN COMPLETE"
    
    g = Github(auth=Auth.Token(getenv("GITHUB_TOKEN")))
    org = os.getenv("ORG")
    
    if org:
        target = g.get_organization(org)
    else:
        target = g.get_user()
    
    repos = [r.full_name for r in target.get_repos() if not r.archived]
    pr_cache = load_cache()
    summaries = []
    
    for repo_full in repos:
        try:
            summary = process_repo(repo_full, label, config, pr_cache)
            summaries.append(summary)
        except Exception as e:
            summaries.append(f"[{repo_full}] ERROR: {e}")
    
    save_cache(pr_cache)
    final = f"🎯 LYRA COMPLETE: {len([s for s in summaries if '✅' in s])} merged!"
    logger.info(final)
    
    return "\n".join(summaries)

# ================================
# CLI + MAIN
# ================================
def main():

    parser = argparse.ArgumentParser(description="🚀 Lyra - Codex PR Automation Beast")
    parser.add_argument("--repo", help="Single repo (org/repo)")
    parser.add_argument("--label", default="codex", help="PR label/keyword")
    parser.add_argument("--interval", type=int, default=0, help="Run every N seconds")
    parser.add_argument("--dry-run", action="store_true", help="Simulate only")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--config", default="lyra.yaml")
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    config = load_config(args.config)
    
    def run_once():

        if args.repo:
            summary = process_repo(args.repo, args.label, config, {})
        else:
            summary = process_all_repos(args.label, args.dry_run, config)
        print(summary)
        send_slack(summary)
    
    if args.interval == 0:
        run_once()
    else:
        logger.info(f"👀 Lyra watching every {args.interval}s | Label: {args.label}")
        while True:
            try:
                run_once()
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("👋 Lyra stopped")
                break

if __name__ == "__main__":
    main()