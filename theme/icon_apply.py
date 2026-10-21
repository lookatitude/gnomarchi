"""Apply Omarchy-style icon themes on Arch/GNOME.

Omarchy packs name Ubuntu Yaru-* variants (not in Arch repos). We:
1. Prefer a real /usr/share/icons/<name> if present (AUR yaru, etc.).
2. Else map Yaru-* → Papirus / Papirus-Dark + papirus-folders color.
3. Install applications/icons/*.png into the user hicolor theme for webapps/launchers.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

from common.paths import REPO_ROOT

# Omarchy icons.theme value → papirus-folders color (when Yaru not installed)
YARU_TO_PAPIRUS_FOLDER: dict[str, str] = {
    "Yaru-blue": "blue",
    "Yaru-purple": "violet",
    "Yaru-magenta": "magenta",
    "Yaru-red": "red",
    "Yaru-yellow": "yellow",
    "Yaru-olive": "green",
    "Yaru-sage": "teal",
    "Yaru-sage-dark": "teal",
    "Yaru-wartybrown": "brown",
    "Yaru-gray": "grey",
    "Yaru-grey": "grey",
}

# papirus-folders -C colors → approx RGB for accent nearest-match
PAPIRUS_FOLDER_RGB: dict[str, tuple[int, int, int]] = {
    "blue": (66, 133, 244),
    "indigo": (63, 81, 181),
    "violet": (156, 39, 176),
    "purple": (156, 39, 176),
    "magenta": (233, 30, 99),
    "pink": (233, 30, 99),
    "red": (244, 67, 54),
    "orange": (255, 152, 0),
    "yellow": (253, 216, 53),
    "green": (76, 175, 80),
    "teal": (0, 150, 136),
    "cyan": (0, 188, 212),
    "brown": (121, 85, 72),
    "grey": (158, 158, 158),
    "black": (33, 33, 33),
    "white": (245, 245, 245),
}

_SAFE = re.compile(r"[^a-zA-Z0-9._+-]+")


def _run(argv: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            argv, check=False, capture_output=True, text=True, timeout=timeout
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _icon_roots() -> list[Path]:
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    return [
        home / ".local" / "share" / "icons",
        Path("/usr/share/icons"),
        Path("/usr/local/share/icons"),
    ]


def theme_installed(name: str) -> bool:
    if not name:
        return False
    for root in _icon_roots():
        if (root / name).is_dir():
            return True
    return False


def _parse_hex(color: str) -> tuple[int, int, int] | None:
    raw = color.strip().lstrip("#")
    if len(raw) == 3:
        raw = "".join(c * 2 for c in raw)
    if len(raw) != 6:
        return None
    try:
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)
    except ValueError:
        return None


def folder_color_from_accent(hex_color: str) -> str:
    """Map accent hex to nearest papirus-folders color (hue-aware; skip grey neutrals)."""
    import colorsys

    rgb = _parse_hex(hex_color)
    if rgb is None:
        return "blue"
    r, g, b = (c / 255.0 for c in rgb)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    if s < 0.12:
        return "grey" if v > 0.35 else "black"
    best, best_d = "blue", 1e18
    for name, ref in PAPIRUS_FOLDER_RGB.items():
        if name in ("grey", "black", "white"):
            continue
        rr, gg, bb = (c / 255.0 for c in ref)
        rh, rs, rv = colorsys.rgb_to_hsv(rr, gg, bb)
        dh = min(abs(h - rh), 1.0 - abs(h - rh))
        # Prefer hue match; soft-weight saturation/value
        d = (dh * 4.0) ** 2 + (s - rs) ** 2 + 0.25 * (v - rv) ** 2
        if d < best_d:
            best, best_d = name, d
    return best


def accent_from_pack(pack: Path) -> str | None:
    colors = pack / "colors.toml"
    if not colors.is_file():
        return None
    for line in colors.read_text(encoding="utf-8").splitlines():
        if "accent" in line.lower() and "=" in line:
            val = line.split("=", 1)[1].strip().strip("\"'")
            if _parse_hex(val):
                return val
    return None


def resolve_icon_theme(
    requested: str, *, accent: str | None = None
) -> tuple[str, str | None]:
    """Return (gsettings_icon_theme, optional papirus_folders_color)."""
    name = (requested or "").strip()
    folder = YARU_TO_PAPIRUS_FOLDER.get(name)
    if folder is None and accent:
        folder = folder_color_from_accent(accent)
    if theme_installed(name) and not name.startswith("Yaru"):
        # Real theme present (e.g. Papirus); still tint folders from accent/Yaru map.
        return name, folder
    if theme_installed(name):
        return name, folder
    for candidate in ("Papirus-Dark", "Papirus", "Papirus-Light"):
        if theme_installed(candidate):
            return candidate, folder
    return "Adwaita", folder


def ensure_papirus_folders_bin() -> str | None:
    """Return path to papirus-folders, installing a user copy from upstream if needed."""
    found = shutil.which("papirus-folders")
    if found:
        return found
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    dest = home / ".local" / "bin" / "papirus-folders"
    if dest.is_file() and os.access(dest, os.X_OK):
        return str(dest)
    url = (
        "https://raw.githubusercontent.com/PapirusDevelopmentTeam/"
        "papirus-folders/master/papirus-folders"
    )
    try:
        import urllib.request

        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=20) as resp:
            body = resp.read()
        dest.write_bytes(body)
        dest.chmod(0o755)
        return str(dest)
    except Exception:
        return None


def apply_papirus_folders(color: str | None, theme: str) -> None:
    if not color:
        return
    bin_ = ensure_papirus_folders_bin()
    if not bin_:
        return
    base = "Papirus-Dark" if "Dark" in theme else "Papirus"
    if theme_installed("Papirus-Light") and "Light" in theme:
        base = "Papirus-Light"
    if not theme_installed(base):
        for cand in ("Papirus-Dark", "Papirus", "Papirus-Light"):
            if theme_installed(cand):
                base = cand
                break
    _run([bin_, "-C", color, "--theme", base], timeout=120)


def install_app_icons(src_dir: Path | None = None) -> list[Path]:
    """Copy Omarchy-derived PNG app icons into ~/.local/share/icons/hicolor/256x256/apps/."""
    src = src_dir or (REPO_ROOT / "applications" / "icons")
    if not src.is_dir():
        # Installed tree
        alt = Path("/usr/local/lib/gnomarchi/applications/icons")
        src = alt if alt.is_dir() else src
    if not src.is_dir():
        return []
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    dest_dir = home / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    dest_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for png in sorted(src.glob("*.png")):
        slug = _SAFE.sub("-", png.stem.strip().lower()).strip("-") or "app"
        # Also keep a readable alias without spaces
        dest = dest_dir / f"gnomarchi-{slug}.png"
        shutil.copy2(png, dest)
        written.append(dest)
        # Common Omarchy launcher names (ChatGPT.png → chatgpt)
        alias = dest_dir / f"{slug}.png"
        if alias != dest:
            shutil.copy2(png, alias)
            written.append(alias)
    # Refresh cache when possible
    hicolor = home / ".local" / "share" / "icons" / "hicolor"
    if shutil.which("gtk-update-icon-cache"):
        _run(["gtk-update-icon-cache", "-f", str(hicolor)])
    return written


def icon_name_for_app(label: str) -> str:
    """Desktop Icon= key for a labeled app (webapp / menu)."""
    slug = _SAFE.sub("-", label.strip().lower()).strip("-") or "app"
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    apps = home / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    for cand in (f"gnomarchi-{slug}", slug, label.strip().lower()):
        if (apps / f"{cand}.png").is_file():
            return cand
    return f"gnomarchi-{slug}"


def apply_pack_icons(pack: Path) -> dict[str, str]:
    """Full icon apply for a theme pack. Returns status dict for last-apply.json."""
    icons_file = pack / "icons.theme"
    requested = ""
    if icons_file.is_file():
        requested = icons_file.read_text(encoding="utf-8").strip().splitlines()[0].strip()
    accent = accent_from_pack(pack)
    theme, folder = resolve_icon_theme(requested, accent=accent)
    if shutil.which("gsettings"):
        _run(["gsettings", "set", "org.gnome.desktop.interface", "icon-theme", theme])
    apply_papirus_folders(folder, theme)
    app_icons = install_app_icons()
    return {
        "requested": requested,
        "applied": theme,
        "papirus_folder": folder or "",
        "accent": accent or "",
        "yaru_available": str(theme_installed(requested)).lower(),
        "app_icons": str(len(app_icons)),
    }
