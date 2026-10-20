#!/usr/bin/env python3
"""Agents StatusNotifier — left menu opens Agents; secondary launches default agent."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    # installed copy under ~/.local/share/gnomarchi/indicators
    for candidate in (
        Path(os.environ.get("GNOMARCHI_ROOT", "")),
        Path("/usr/local/lib/gnomarchi"),
        Path.home() / "Projects" / "gnomarchi",
    ):
        if candidate and (candidate / "agent").is_dir():
            sys.path.insert(0, str(candidate))
            ROOT = candidate
            break


def _cli(*args: str) -> None:
    cli = ROOT / "bin" / "gnomarchi"
    if cli.is_file():
        subprocess.Popen([sys.executable, str(cli), *args])
    else:
        subprocess.Popen(["gnomarchi", *args])


def main() -> int:
    from agent.indicator_runtime import run_indicator

    return run_indicator(
        id="gnomarchi.agents",
        title="gnomarchi Agents",
        icon="system-run-symbolic",
        on_activate=lambda: _cli("agent", "window"),
        on_secondary=lambda: _cli("agent", "launch"),
    )


if __name__ == "__main__":
    raise SystemExit(main())
