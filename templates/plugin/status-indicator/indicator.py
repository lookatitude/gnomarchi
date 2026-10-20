#!/usr/bin/env python3
"""Template status indicator."""

from __future__ import annotations

import subprocess
import sys


def main() -> int:
    try:
        from agent.indicator_runtime import run_indicator
    except ImportError:
        print("agent.indicator_runtime not on PYTHONPATH", file=sys.stderr)
        return 1
    return run_indicator(
        id="PLUGIN_ID",
        title="PLUGIN_ID",
        on_activate=lambda: subprocess.run(["notify-send", "PLUGIN_ID", "clicked"], check=False),
    )


if __name__ == "__main__":
    raise SystemExit(main())
