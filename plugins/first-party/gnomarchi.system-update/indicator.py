#!/usr/bin/env python3
"""System update indicator using checkupdates when available."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for candidate in (Path(os.environ.get("GNOMARCHI_ROOT", "")), Path("/usr/local/lib/gnomarchi"), ROOT):
    if candidate and (candidate / "agent").is_dir():
        sys.path.insert(0, str(candidate))
        break


def check() -> str:
    binary = shutil.which("checkupdates")
    if not binary:
        return "install pacman-contrib for checkupdates"
    try:
        out = subprocess.run(
            [binary],
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        lines = [l for l in out.stdout.splitlines() if l.strip()]
        if not lines:
            return "system up to date"
        return f"{len(lines)} updates available"
    except Exception as exc:
        return str(exc)


def show() -> None:
    subprocess.run(["notify-send", "Updates", check()], check=False)


def main() -> int:
    from agent.indicator_runtime import run_indicator

    return run_indicator(
        id="gnomarchi.system-update",
        title="Updates",
        icon="software-update-available-symbolic",
        on_activate=show,
        on_secondary=lambda: subprocess.Popen(["ghostty", "-e", "bash", "-lc", "sudo pacman -Syu"]),
    )


if __name__ == "__main__":
    raise SystemExit(main())
