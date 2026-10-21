"""Create a user theme pack under ~/.config/gnomarchi/themes (Omarchy custom themes)."""

from __future__ import annotations

import colorsys
import re
import shutil
from collections import Counter
from pathlib import Path

from theme.paths import find_pack, state_dir

_SAFE = re.compile(r"[^a-z0-9-]+")


def _user_themes() -> Path:
    d = state_dir() / "themes"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def colors_from_wallpaper(path: Path) -> tuple[str, str, str]:
    """Sample dominant colors from an image → (background, foreground, accent)."""
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow required for --from-wallpaper") from exc
    img = Image.open(path).convert("RGB")
    img = img.resize((64, 64))
    counts = Counter(img.getdata())
    ranked = [c for c, _n in counts.most_common(24)]

    def lum(rgb: tuple[int, int, int]) -> float:
        r, g, b = (x / 255.0 for x in rgb)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    darks = sorted(ranked, key=lum)[:6]
    lights = sorted(ranked, key=lum, reverse=True)[:6]
    background = darks[0] if darks else (26, 27, 38)
    foreground = lights[0] if lights else (192, 202, 245)

    def sat(rgb: tuple[int, int, int]) -> float:
        h, s, v = colorsys.rgb_to_hsv(*(x / 255.0 for x in rgb))
        return s * v

    vivid = sorted(ranked, key=sat, reverse=True)
    accent = vivid[0] if vivid else (122, 162, 247)
    # Prefer a saturated mid tone over near-black/white
    for cand in vivid:
        if 0.15 < lum(cand) < 0.85 and sat(cand) > 0.2:
            accent = cand
            break
    return _hex(background), _hex(foreground), _hex(accent)


def new_theme(
    theme_id: str,
    *,
    name: str | None = None,
    from_id: str = "tokyo-night",
    background: str = "#1a1b26",
    foreground: str = "#c0caf5",
    accent: str = "#7aa2f7",
    from_wallpaper: str | Path | None = None,
) -> Path:
    if from_wallpaper:
        wp = Path(from_wallpaper).expanduser().resolve()
        if not wp.is_file():
            raise FileNotFoundError(f"wallpaper not found: {wp}")
        background, foreground, accent = colors_from_wallpaper(wp)
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
    credit = f"User theme {tid} scaffolded by gnomarchi theme new.\n"
    if from_wallpaper:
        credit += f"Colors sampled from {Path(from_wallpaper).expanduser().resolve()}\n"
        # Copy a preview background when possible
        bg_dir = dest / "backgrounds"
        bg_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(Path(from_wallpaper).expanduser().resolve(), bg_dir / "1.jpg")
        except OSError:
            pass
    (dest / "CREDITS").write_text(credit, encoding="utf-8")
    # Rewrite colors.toml with sampled / provided palette
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
    return dest
