#!/usr/bin/env python3
"""Mode indicators — DND / Night Light / Stay Awake (caffeine) tray toggles."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for candidate in (
    Path(os.environ.get("GNOMARCHI_ROOT", "")),
    Path("/usr/local/lib/gnomarchi"),
    ROOT,
):
    if candidate and (candidate / "desktop").is_dir():
        sys.path.insert(0, str(candidate))
        break


def main() -> int:
    from agent.indicator_runtime import MenuAction, run_indicator
    from desktop import modes

    def _notify(title: str, body: str) -> None:
        subprocess.run(["notify-send", title, body], check=False)

    return run_indicator(
        id="gnomarchi.modes",
        title="Modes",
        icon="preferences-desktop-display-symbolic",
        menu_actions=[
            MenuAction(
                label="Do Not Disturb",
                action=lambda: _notify(
                    "Do Not Disturb",
                    "on" if modes.toggle_dnd() else "off",
                ),
                get_active=modes.dnd_enabled,
            ),
            MenuAction(
                label="Night Light",
                action=lambda: _notify(
                    "Night Light",
                    "on" if modes.toggle_night_light() else "off",
                ),
                get_active=modes.night_light_enabled,
            ),
            MenuAction(
                label="Stay Awake",
                action=lambda: _notify(
                    "Stay Awake",
                    "on" if modes.toggle_stay_awake() else "off",
                ),
                get_active=modes.stay_awake_enabled,
            ),
        ],
    )


if __name__ == "__main__":
    raise SystemExit(main())
