#!/usr/bin/env python3
"""Weather indicator — fetches wttr.in and shows via notify on click."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for candidate in (Path(os.environ.get("GNOMARCHI_ROOT", "")), Path("/usr/local/lib/gnomarchi"), ROOT):
    if candidate and (candidate / "agent").is_dir():
        sys.path.insert(0, str(candidate))
        break


def fetch_weather() -> str:
    try:
        with urllib.request.urlopen("https://wttr.in/?format=j1", timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cur = data["current_condition"][0]
        area = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", "local")
        return f"{area}: {cur.get('temp_C')}°C {cur.get('weatherDesc', [{}])[0].get('value', '')}"
    except Exception as exc:
        return f"weather unavailable ({exc})"


def show() -> None:
    text = fetch_weather()
    subprocess.run(["notify-send", "Weather", text], check=False)


def main() -> int:
    from agent.indicator_runtime import run_indicator

    return run_indicator(
        id="gnomarchi.weather",
        title="Weather",
        icon="weather-few-clouds-symbolic",
        on_activate=show,
    )


if __name__ == "__main__":
    raise SystemExit(main())
