"""Dotfiles sync for ~/.config/gnomarchi (Omarchy dotfiles chapter)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from common.paths import state_dir


def _repo() -> Path:
    return state_dir()


def status() -> int:
    root = _repo()
    print(f"state: {root}")
    git = root / ".git"
    if not git.is_dir():
        print("not a git repo — run: gnomarchi config init")
        return 0
    return subprocess.call(["git", "-C", str(root), "status", "-sb"])


def init(remote: str | None = None) -> int:
    root = _repo()
    root.mkdir(parents=True, exist_ok=True)
    if not (root / ".git").is_dir():
        rc = subprocess.call(["git", "-C", str(root), "init", "-b", "main"])
        if rc != 0:
            return rc
        (root / "README.md").write_text(
            "# gnomarchi user state\n\nSynced via `gnomarchi config`.\n",
            encoding="utf-8",
        )
        subprocess.call(["git", "-C", str(root), "add", "-A"])
        subprocess.call(
            ["git", "-C", str(root), "commit", "-m", "gnomarchi config init"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if remote:
        remotes = subprocess.getoutput(f"git -C {root} remote")
        if "origin" not in remotes:
            subprocess.call(["git", "-C", str(root), "remote", "add", "origin", remote])
        else:
            subprocess.call(["git", "-C", str(root), "remote", "set-url", "origin", remote])
    print(root)
    return 0


def pull() -> int:
    root = _repo()
    if not (root / ".git").is_dir():
        print("error: run gnomarchi config init first", file=sys.stderr)
        return 1
    return subprocess.call(["git", "-C", str(root), "pull", "--ff-only"])


def push() -> int:
    root = _repo()
    if not (root / ".git").is_dir():
        print("error: run gnomarchi config init first", file=sys.stderr)
        return 1
    subprocess.call(["git", "-C", str(root), "add", "-A"])
    # commit if dirty
    dirty = subprocess.call(
        ["git", "-C", str(root), "diff", "--quiet", "--cached"]
    )
    if dirty != 0:
        subprocess.call(
            ["git", "-C", str(root), "commit", "-m", "gnomarchi config sync"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    return subprocess.call(["git", "-C", str(root), "push", "-u", "origin", "HEAD"])


def export_bundle(dest: str) -> int:
    if not shutil.which("tar"):
        return 1
    root = _repo()
    out = Path(dest).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    return subprocess.call(
        ["tar", "czf", str(out), "-C", str(root.parent), root.name]
    )
