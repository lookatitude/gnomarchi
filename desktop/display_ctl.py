"""Display / scale helpers wrapping GNOME tools (Omarchy monitors chapter)."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys


def _run(argv: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False)


def list_monitors() -> int:
    if shutil.which("gdctl"):
        proc = _run(["gdctl", "show"])
        sys.stdout.write(proc.stdout or proc.stderr or "")
        return proc.returncode
    if shutil.which("gnome-randr"):
        proc = _run(["gnome-randr", "query"])
        sys.stdout.write(proc.stdout or proc.stderr or "")
        return proc.returncode
    # gsettings fallback — logical layout only
    print("(open GNOME Settings › Displays; gdctl not installed)")
    if shutil.which("gnome-control-center"):
        subprocess.Popen(["gnome-control-center", "display"], start_new_session=True)
    return 0


def open_settings() -> int:
    if shutil.which("gnome-control-center"):
        subprocess.Popen(["gnome-control-center", "display"], start_new_session=True)
        return 0
    print("error: gnome-control-center missing", file=sys.stderr)
    return 1


def set_scale(scale: str) -> int:
    """Best-effort fractional scale via gsettings / gdctl."""
    if shutil.which("gdctl"):
        # gdctl syntax varies; try common form then fall through
        proc = _run(["gdctl", "set", "--scale", scale])
        if proc.returncode == 0:
            return 0
    # GNOME experimental fractional scaling toggle + text scaling
    try:
        factor = float(scale)
    except ValueError:
        print(f"error: bad scale {scale}", file=sys.stderr)
        return 2
    _run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "text-scaling-factor",
            str(factor),
        ]
    )
    print(f"text-scaling-factor → {factor}")
    return 0


def status_json() -> int:
    data = {"tool": None, "raw": None}
    if shutil.which("gdctl"):
        data["tool"] = "gdctl"
        data["raw"] = _run(["gdctl", "show"]).stdout
    print(json.dumps(data, indent=2))
    return 0
