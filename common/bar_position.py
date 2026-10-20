"""Panel/bar edge: stock GNOME top bar by default; dash-to-panel when opted in."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path
from typing import Literal

from common.shell_config import ensure_user_shell_toml, user_shell_toml

Position = Literal["top", "bottom", "left", "right"]

_DTP_UUID = "dash-to-panel@jderose9.github.com"

_GSETTINGS_MAP = {
    "top": "TOP",
    "bottom": "BOTTOM",
    "left": "LEFT",
    "right": "RIGHT",
}


def get_bar_position() -> str:
    path = user_shell_toml()
    if not path.is_file():
        ensure_user_shell_toml()
        path = user_shell_toml()
    if not path.is_file():
        return "top"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    panel = data.get("panel") or {}
    return str(panel.get("position", "top")).lower()


def _ext(action: str, uuid: str) -> None:
    subprocess.run(
        ["gnome-extensions", action, uuid],
        check=False,
        capture_output=True,
    )


def set_bar_position(position: str) -> str:
    pos = position.strip().lower()
    if pos not in _GSETTINGS_MAP:
        raise ValueError(f"position must be one of {sorted(_GSETTINGS_MAP)}")
    ensure_user_shell_toml()
    path = user_shell_toml()
    text = path.read_text(encoding="utf-8") if path.is_file() else "[panel]\n"
    lines = text.splitlines()
    out: list[str] = []
    in_panel = False
    replaced = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            in_panel = stripped == "[panel]"
            out.append(line)
            continue
        if in_panel and stripped.startswith("position"):
            out.append(f'position = "{pos}"')
            replaced = True
            continue
        out.append(line)
    if not replaced:
        if "[panel]" not in text:
            out.append("[panel]")
        out.append(f'position = "{pos}"')
    path.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8")

    # top → stock GNOME top bar (disable dash-to-panel).
    # bottom|left|right → enable dash-to-panel on that edge.
    if pos == "top":
        _ext("disable", _DTP_UUID)
        return pos

    user_ext = Path.home() / ".local/share/gnome-shell/extensions" / _DTP_UUID
    sys_ext = Path("/usr/share/gnome-shell/extensions") / _DTP_UUID
    if not user_ext.is_dir() and sys_ext.is_dir():
        user_ext.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["cp", "-a", str(sys_ext), str(user_ext)], check=False)

    gval = _GSETTINGS_MAP[pos]
    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.shell.extensions.dash-to-panel",
            "panel-position",
            gval,
        ],
        check=False,
        capture_output=True,
    )
    subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.shell.extensions.dash-to-panel",
            "panel-positions",
            f'{{"0":"{gval}"}}',
        ],
        check=False,
        capture_output=True,
    )
    _ext("enable", _DTP_UUID)
    return pos
