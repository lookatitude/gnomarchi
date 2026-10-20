#!/usr/bin/env python3
"""systemd --user loop: poll coredumps and notify."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.crash import watch_once  # noqa: E402


def main() -> int:
    while True:
        try:
            watch_once()
        except Exception:
            pass
        time.sleep(60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
