"""
sync.py — ForenShield GitHub sync script
Stages all changes, commits with a message, and pushes to GitHub.

Usage:
    python sync.py                          # auto commit message + push
    python sync.py "feat: add timeline fix" # custom commit message
    python sync.py --set-remote <url>       # save your GitHub remote URL
    python sync.py --status                 # show git status only
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT        = Path(__file__).parent.resolve()
CONFIG_FILE = ROOT / ".sync_config.json"

BANNER = """
╔══════════════════════════════════════════════════════════╗
║         ForenShield — GitHub Sync                        ║
╚══════════════════════════════════════════════════════════╝
"""

IS_WIN = sys.platform == "win32"

# ── Colour helpers ─────────────────────────────────────────────────────────────
def _c(code: str, text: str) -> str:
    if IS_WIN and not os.environ.get("WT_SESSION"):
        return text
    return f"\033[{code}m{text}\033[0m"

def ok(msg):    print(_c("92", f"  ✓  {msg}"))
def info(msg):  print(_c("96", f"  →  {msg}"))
def warn(msg):  print(_c("93", f"  !  {msg}"))
def error(msg): print(_c("91", f"  ✗  {msg}")); sys.exit(1)
def head(msg):  print(_c("95", f"\n  {msg}\n" + "  " + "─" * (len(msg) + 2)))


# ── Config: store the GitHub remote URL ───────────────────────────────────────
def _load_config() -> dict:
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    return {}


def _save_config(data: dict):
    CONFIG_FILE.write_text(json.dumps(data, indent=2))


def get_remote() -> str | None:
    cfg = _load_config()
    if cfg.get("remote"):
        return cfg["remote"]
    # Try to read from git config
    try:
        r = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except Exception:
        pass
    return None


def set_remote(url: str):
    # Check if origin already exists
    r = subprocess.run(
        ["git", "remote"], capture_output=True, text=True, cwd=str(ROOT)
    )
    remotes = r.stdout.strip().split()

    if "origin" in remotes:
        subprocess.run(
            ["git", "remote", "set-url", "origin", url],
            cwd=str(ROOT), check=True
        )
        ok(f"Updated origin → {url}")
    else:
        subprocess.run(
            ["git", "remote", "add", "origin", url],
            cwd=str(ROOT), check=True
        )
        ok(f"Added origin → {url}")

    cfg = _load_config()
    cfg["remote"] = url
    _save_config(cfg)
    ok("Saved to .sync_config.json")


# ── Git helpers ────────────────────────────────────────────────────────────────
def _run_git(*args, check=True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=check,
    )


def ensure_git():
    r = subprocess.run(["git", "--version"], capture_output=True)
    if r.returncode != 0:
        error("Git is not installed. Download from https://git-scm.com")


def ensure_git_repo():
    if not (ROOT / ".git").exists():
        info("Initialising git repository...")
        _run_git("init")
        _run_git("branch", "-M", "main")
        ok("Git repository initialised (branch: main)")


def show_status():
    head("Git Status")
    r = _run_git("status", "--short")
    if r.stdout.strip():
        for line in r.stdout.strip().splitlines():
            status = line[:2].strip()
            fname  = line[3:]
            colour = {"A": "92", "M": "93", "D": "91", "?": "37"}.get(status[0], "37")
            print(f"    {_c(colour, status):6s}  {fname}")
    else:
        ok("Working tree is clean — nothing to commit")

    # Show branch + remote
    branch = _run_git("branch", "--show-current", check=False).stdout.strip() or "main"
    remote = get_remote()
    print()
    info(f"Branch: {branch}")
    info(f"Remote: {remote or '(not set — run: python sync.py --set-remote <url>)'}")
    print()


def auto_message() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Count changed files for the message
    r = _run_git("status", "--short", check=False)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    n = len(lines)

    # Smart categorisation
    types = set()
    for line in lines:
        fname = line[3:].lower()
        if fname.startswith("forenshield-react"):
            types.add("frontend")
        elif fname.endswith(".py"):
            types.add("backend")
        elif fname.endswith(".md"):
            types.add("docs")
        elif fname in ("requirements.txt", "package.json", ".gitignore"):
            types.add("config")
        else:
            types.add("misc")

    scope = "+".join(sorted(types)) if types else "misc"
    return f"chore({scope}): update {n} file{'s' if n != 1 else ''} [{now}]"


def sync(commit_msg: str | None, branch: str = "main", push: bool = True):
    head("Checking Git status")
    ensure_git()
    ensure_git_repo()

    # Stage everything
    _run_git("add", "--all")

    # Check if there is anything to commit
    r = _run_git("status", "--short")
    if not r.stdout.strip():
        ok("Nothing to commit — repository is already up to date")
        remote = get_remote()
        if remote and push:
            info("Pushing any un-pushed local commits...")
            _push(branch)
        return

    # Build commit message
    msg = commit_msg or auto_message()

    head("Committing changes")
    info(f"Message: {msg}")
    _run_git("commit", "-m", msg)
    ok("Committed")

    # Show what was committed
    r = _run_git("show", "--stat", "--format=", "HEAD")
    for line in r.stdout.strip().splitlines()[-10:]:
        print(f"    {line}")

    if push:
        _push(branch)


def _push(branch: str):
    remote = get_remote()
    if not remote:
        warn("No GitHub remote configured.")
        warn("Run:  python sync.py --set-remote https://github.com/your-org/forenshield.git")
        warn("Then: python sync.py  to push")
        return

    head(f"Pushing to GitHub  →  {remote}")
    info(f"Branch: {branch}")

    # Attempt push; if upstream not set, set it
    r = _run_git("push", "-u", "origin", branch, check=False)
    if r.returncode == 0:
        ok(f"Pushed to {remote} [{branch}]")
    else:
        stderr = r.stderr.strip()
        if "rejected" in stderr:
            warn("Push rejected — remote has changes. Pulling first...")
            _run_git("pull", "--rebase", "origin", branch)
            _run_git("push", "-u", "origin", branch)
            ok("Pushed after rebase")
        else:
            error(f"Push failed:\n{stderr}")

    print()
    ok("Sync complete!")
    info(f"View on GitHub: {remote.rstrip('.git')}")


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="ForenShield GitHub sync")
    parser.add_argument(
        "message",
        nargs="?",
        default=None,
        help='Commit message (auto-generated if omitted)',
    )
    parser.add_argument(
        "--set-remote",
        metavar="URL",
        help="Set the GitHub remote URL and save it",
    )
    parser.add_argument(
        "--branch",
        default="main",
        help="Git branch to push to (default: main)",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Commit locally but do not push to GitHub",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show git status and exit",
    )
    args = parser.parse_args()

    ensure_git()
    ensure_git_repo()

    if args.set_remote:
        head("Setting GitHub Remote")
        set_remote(args.set_remote)
        return

    if args.status:
        show_status()
        return

    sync(
        commit_msg=args.message,
        branch=args.branch,
        push=not args.no_push,
    )


if __name__ == "__main__":
    main()
