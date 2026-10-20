"""Music TUI launcher (Omarchy Cliamp → cmus / rmpc / ncmpcpp)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def _player() -> str | None:
    for cand in ("cmus", "rmpc", "ncmpcpp", "mocp"):
        if shutil.which(cand):
            return cand
    return None


def run() -> int:
    player = _player()
    if player is None:
        print(
            "error: install cmus (or rmpc/ncmpcpp). "
            "Try: sudo pacman -S cmus",
            file=sys.stderr,
        )
        return 1
    term = shutil.which("ghostty") or shutil.which("kgx") or "xterm"
    if term.endswith("ghostty"):
        return subprocess.call([term, "-e", player])
    if "kgx" in term:
        return subprocess.call([term, "-e", player])
    return subprocess.call([term, "-e", player])


def install() -> int:
    if not shutil.which("pacman"):
        print("pacman required", file=sys.stderr)
        return 1
    return subprocess.call(["sudo", "pacman", "-Sy", "--needed", "--noconfirm", "cmus"])
