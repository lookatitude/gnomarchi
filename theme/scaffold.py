"""Create a user theme pack under ~/.config/gnomarchi/themes (Omarchy custom themes)."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from theme.paths import find_pack, state_dir

_SAFE = re.compile(r"[^a-z0-9-]+")


def _user_themes() -> Path:
    d = state_dir() / "themes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def new_theme(
    theme_id: str,
    *,
    name: str | None = None,
    from_id: str = "tokyo-night",
    background: str = "#1a1b26",
    foreground: str = "#c0caf5",
    accent: str = "#7aa2f7",
) -> Path:
    tid = _SAFE.sub("-", theme_id.strip().lower()).strip("-")
    if not tid:
        raise ValueError("theme id required")
    dest = _user_themes() / tid
    if dest.exists():
        raise FileExistsError(f"theme already exists: {dest}")

    base = find_pack(from_id)
    if base is not None:
        shutil.copytree(
            base,
            dest,
            ignore=shutil.ignore_patterns(
                ".git", "__pycache__", "backgrounds", "*.mp4"
            ),
        )
        # Drop heavy/unwanted; keep preview if small
        for drop in ("CREDITS",):
            p = dest / drop
            if p.is_file() and from_id != tid:
                pass
    else:
        dest.mkdir(parents=True)
        (dest / "colors.toml").write_text(
            "\n".join(
                [
                    "[colors]",
                    f'background = "{background}"',
                    f'foreground = "{foreground}"',
                    f'accent = "{accent}"',
                    'surface = "#16161e"',
                    'muted = "#565f89"',
                    "",
                ]
            ),
            encoding="utf-8",
        )

    display = name or tid.replace("-", " ").title()
    (dest / "theme.toml").write_text(
        "\n".join(
            [
                "[theme]",
                f'id = "{tid}"',
                f'name = "{display}"',
                'version = "1.0.0"',
                "",
                "[provenance]",
                "official_omarchy = false",
                'note = "user-created via gnomarchi theme new"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    colors = dest / "colors.toml"
    if not colors.is_file():
        colors.write_text(
            "\n".join(
                [
                    "[colors]",
                    f'background = "{background}"',
                    f'foreground = "{foreground}"',
                    f'accent = "{accent}"',
                    'surface = "#16161e"',
                    'muted = "#565f89"',
                    "",
                ]
            ),
            encoding="utf-8",
        )
    (dest / "CREDITS").write_text(
        f"User theme {tid} scaffolded by gnomarchi theme new.\n",
        encoding="utf-8",
    )
    return dest
