"""Herdr-like agent session manager on tmux (Omarchy Herdr parity)."""

from __future__ import annotations

import shutil
import subprocess
import sys


SESSION = "gnomarchi-agents"


def _tmux() -> str | None:
    return shutil.which("tmux")


def list_sessions() -> list[str]:
    if not _tmux():
        return []
    out = subprocess.run(
        ["tmux", "list-sessions", "-F", "#{session_name}"],
        capture_output=True,
        text=True,
        check=False,
    )
    return [ln.strip() for ln in (out.stdout or "").splitlines() if ln.strip()]


def ensure() -> int:
    tmux = _tmux()
    if not tmux:
        print("error: install tmux", file=sys.stderr)
        return 1
    if SESSION in list_sessions():
        print(SESSION)
        return 0
    return subprocess.call([tmux, "new-session", "-d", "-s", SESSION])


def attach() -> int:
    tmux = _tmux()
    if not tmux:
        print("error: install tmux", file=sys.stderr)
        return 1
    ensure()
    # Prefer Ghostty if present
    term = shutil.which("ghostty") or shutil.which("kgx") or shutil.which("gnome-terminal")
    if term and term.endswith("ghostty"):
        return subprocess.call([term, "-e", "tmux", "attach", "-t", SESSION])
    if term and "gnome-terminal" in term:
        return subprocess.call([term, "--", "tmux", "attach", "-t", SESSION])
    return subprocess.call([tmux, "attach", "-t", SESSION])


def new_window(name: str = "agent") -> int:
    tmux = _tmux()
    if not tmux:
        return 1
    ensure()
    return subprocess.call([tmux, "new-window", "-t", SESSION, "-n", name])


def run(action: str, *, name: str = "agent") -> int:
    if action == "list":
        for s in list_sessions():
            print(s)
        return 0
    if action == "ensure":
        return ensure()
    if action == "attach":
        return attach()
    if action == "new":
        return new_window(name)
    print("usage: herdr list|ensure|attach|new", file=sys.stderr)
    return 2
