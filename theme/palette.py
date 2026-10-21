"""Normalize Omarchy-flat and gnomarchi [colors] palettes to one dict."""

from __future__ import annotations

import tomllib
from pathlib import Path


def load_palette(pack: Path) -> dict[str, str]:
    """Load colors.toml — supports Omarchy flat keys or gnomarchi [colors] table."""
    data = tomllib.loads((pack / "colors.toml").read_text(encoding="utf-8"))
    # Top-level mode= light|dark (Omarchy flat packs); keep for gsettings color-scheme.
    pack_mode = str(data.get("mode") or "").strip().lower()
    if isinstance(data.get("colors"), dict):
        raw = {k: str(v) for k, v in data["colors"].items()}
        if not pack_mode and isinstance(data["colors"].get("mode"), str):
            pack_mode = str(data["colors"]["mode"]).strip().lower()
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
    if pack_mode:
        out["mode"] = pack_mode
    elif "mode" not in out:
        # Heuristic: light backgrounds → prefer-light when mode omitted
        bg = out.get("background", "#000000").lstrip("#")
        try:
            if len(bg) == 3:
                bg = "".join(c * 2 for c in bg)
            r, g, b = int(bg[0:2], 16), int(bg[2:4], 16), int(bg[4:6], 16)
            luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255.0
            out["mode"] = "light" if luminance >= 0.55 else "dark"
        except (ValueError, IndexError):
            out["mode"] = "dark"
    return out

