"""Monospace font catalog — Style > Font / Install > Style > Font."""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Any


# Nerd Font packages common on Arch (AUR or community).
FONT_CATALOG: list[dict[str, str]] = [
    {
        "id": "jetbrains",
        "label": "JetBrains Mono",
        "package": "ttf-jetbrains-mono-nerd",
        "family": "JetBrainsMono Nerd Font",
    },
    {
        "id": "cascadia",
        "label": "Cascadia Mono",
        "package": "ttf-cascadia-mono-nerd",
        "family": "CaskaydiaMono Nerd Font",
    },
    {
        "id": "meslo",
        "label": "Meslo LG Mono",
        "package": "ttf-meslo-nerd",
        "family": "MesloLGL Nerd Font",
    },
    {
        "id": "fira",
        "label": "Fira Code",
        "package": "ttf-firacode-nerd",
        "family": "FiraCode Nerd Font",
    },
    {
        "id": "victor",
        "label": "Victor Code",
        "package": "ttf-victor-mono-nerd",
        "family": "VictorMono Nerd Font",
    },
    {
        "id": "bitstream",
        "label": "Bitstream Vera Mono",
        "package": "ttf-bitstream-vera-mono-nerd",
        "family": "BitstromWera Nerd Font",
    },
    {
        "id": "iosevka",
        "label": "Iosevka",
        "package": "ttf-iosevka-nerd",
        "family": "Iosevka Nerd Font Mono",
    },
]


def list_fonts() -> list[dict[str, str]]:
    return list(FONT_CATALOG)


def find_font(key: str) -> dict[str, str] | None:
    key_l = key.strip().lower()
    for row in FONT_CATALOG:
        if key_l in (
            row["id"].lower(),
            row["label"].lower(),
            row["family"].lower(),
            row["package"].lower(),
        ):
            return row
    return None


def current_monospace() -> str | None:
    if not shutil.which("gsettings"):
        return None
    proc = subprocess.run(
        ["gsettings", "get", "org.gnome.desktop.interface", "monospace-font-name"],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        return None
    return proc.stdout.strip().strip("'\"")


def set_monospace(family: str, size: int = 11) -> int:
    """Set GNOME monospace font (terminal + UI mono)."""
    row = find_font(family)
    name = row["family"] if row else family
    value = f"{name} {size}"
    if not shutil.which("gsettings"):
        print(f"would set monospace-font-name={value}", file=sys.stderr)
        return 0
    proc = subprocess.run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.interface",
            "monospace-font-name",
            value,
        ],
        check=False,
    )
    if proc.returncode == 0:
        print(f"monospace → {value}")
    return int(proc.returncode)


def install_font(key: str) -> int:
    row = find_font(key)
    if row is None:
        print(f"error: unknown font: {key}", file=sys.stderr)
        return 1
    pkg = row["package"]
    if not shutil.which("pacman"):
        print(f"error: pacman not found; install {pkg} manually", file=sys.stderr)
        return 1
    print(f"installing {pkg} ({row['label']})…")
    code = subprocess.call(["sudo", "pacman", "-Sy", "--needed", "--noconfirm", pkg])
    if code == 0:
        set_monospace(row["family"])
    return int(code)


def catalog_as_dicts() -> list[dict[str, Any]]:
    current = current_monospace() or ""
    out = []
    for row in FONT_CATALOG:
        item = dict(row)
        item["active"] = row["family"] in current
        out.append(item)
    return out
