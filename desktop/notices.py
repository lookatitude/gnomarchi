"""Omarchy-style notices: time / battery / weather via notify-send."""

from __future__ import annotations

import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


def _notify(title: str, body: str, *, icon: str | None = None) -> int:
    if not shutil.which("notify-send"):
        print(f"{title}: {body}")
        return 0
    cmd = ["notify-send", "-a", "gnomarchi", title, body]
    if icon:
        cmd.extend(["-i", icon])
    return subprocess.call(cmd)


def notice_time() -> int:
    now = datetime.now().strftime("%A %-d %B · %H:%M")
    return _notify("Time", now, icon="appointment-soon-symbolic")


def _battery_text() -> str:
    base = Path("/sys/class/power_supply")
    if not base.is_dir():
        return "No battery detected"
    lines: list[str] = []
    for bat in sorted(base.glob("BAT*")):
        cap = bat / "capacity"
        status = bat / "status"
        pct = cap.read_text(encoding="utf-8").strip() if cap.is_file() else "?"
        st = status.read_text(encoding="utf-8").strip() if status.is_file() else "?"
        lines.append(f"{bat.name}: {pct}% ({st})")
    return "\n".join(lines) if lines else "No battery detected"


def notice_battery() -> int:
    return _notify("Battery", _battery_text(), icon="battery-symbolic")


def notice_weather() -> int:
    try:
        import urllib.request

        with urllib.request.urlopen("https://wttr.in/?format=%l:+%c+%t+%h", timeout=8) as resp:
            text = resp.read().decode("utf-8", errors="replace").strip()
    except Exception as exc:
        text = f"unavailable ({exc})"
    return _notify("Weather", text or "unavailable", icon="weather-few-clouds-symbolic")


def run(kind: str) -> int:
    table = {
        "time": notice_time,
        "battery": notice_battery,
        "weather": notice_weather,
    }
    fn = table.get(kind)
    if fn is None:
        print(f"error: unknown notice {kind} (time|battery|weather)", file=__import__("sys").stderr)
        return 2
    return fn()


def demo_all() -> int:
    """Fire all three (spaced) for screenshot / QA."""
    rc = 0
    for kind in ("time", "battery", "weather"):
        rc = run(kind) or rc
        time.sleep(0.4)
    return rc
