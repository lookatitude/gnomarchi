"""Arch-first system update (Omarchy `omarchy update` equivalent).

Uses official pacman mirrors only by default — no custom gnomarchi repo required.
"""

from __future__ import annotations

import shutil
import subprocess
import sys


def run_update(*, noconfirm: bool = False, sync_only: bool = False) -> int:
    pacman = shutil.which("pacman")
    if not pacman:
        print("error: pacman not found (Arch Linux required)", file=sys.stderr)
        return 1
    argv = ["sudo", pacman, "-Syu"]
    if sync_only:
        argv = ["sudo", pacman, "-Sy"]
    if noconfirm:
        argv.append("--noconfirm")
    print("gnomarchi update →", " ".join(argv))
    print("Using Arch official repos (and any user-configured mirrors).")
    try:
        return subprocess.call(argv)
    except KeyboardInterrupt:
        return 130
