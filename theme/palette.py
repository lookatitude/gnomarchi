"""Normalize Omarchy-flat and gnomarchi [colors] palettes to one dict."""

from __future__ import annotations

import tomllib
from pathlib import Path


def load_palette(pack: Path) -> dict[str, str]:
    """Load colors.toml — supports Omarchy flat keys or gnomarchi [colors] table."""
    data = tomllib.loads((pack / "colors.toml").read_text(encoding="utf-8"))
    if isinstance(data.get("colors"), dict):
        raw = {k: str(v) for k, v in data["colors"].items()}
    else:
        raw = {k: str(v) for k, v in data.items() if isinstance(v, str) and k != "mode"}

    def pick(*keys: str, default: str = "#808080") -> str:
        for k in keys:
            if k in raw and raw[k]:
                return raw[k]
        return default

    # Semantic map used by all emitters
    out = {
        "background": pick("background", "dark_background", default="#0b1220"),
        "foreground": pick("foreground", "bright_foreground", default="#e8eef7"),
        "accent": pick("accent", "blue", "bright_blue", default="#3d8bfd"),
        "surface": pick(
            "surface", "lighter_background", "dark_background", default="#121a2b"
        ),
        "muted": pick("muted", "dark_foreground", default="#8b9bb4"),
        "danger": pick("danger", "red", "bright_red", default="#e35d6a"),
        "success": pick("success", "green", "bright_green", default="#3ecf8e"),
        "selection": pick("selection", "selection_background", "lighter_background"),
        "cursor": pick("cursor", "bright_foreground", "accent", "foreground"),
        "red": pick("red", default="#f7768e"),
        "green": pick("green", default="#9ece6a"),
        "yellow": pick("yellow", default="#e0af68"),
        "blue": pick("blue", default="#7aa2f7"),
        "magenta": pick("magenta", default="#ad8ee6"),
        "cyan": pick("cyan", default="#449dab"),
        "bright_red": pick("bright_red", "red"),
        "bright_green": pick("bright_green", "green"),
        "bright_yellow": pick("bright_yellow", "yellow"),
        "bright_blue": pick("bright_blue", "blue"),
        "bright_magenta": pick("bright_magenta", "magenta"),
        "bright_cyan": pick("bright_cyan", "cyan"),
        "bright_foreground": pick("bright_foreground", "foreground"),
        "dark_background": pick("dark_background", "background"),
        "lighter_background": pick("lighter_background", "surface"),
        "dark_foreground": pick("dark_foreground", "muted"),
        "orange": pick("orange", "yellow"),
        "brown": pick("brown", "muted"),
    }
    # Keep any extra Omarchy keys
    for k, v in raw.items():
        out.setdefault(k, v)
    return out
