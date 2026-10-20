"""Per-theme background cycle (Omarchy Super+Ctrl+W equivalent).

Prefers stills under theme/packs/<id>/backgrounds/ (ported Omarchy graphics with
CREDITS; Omarchy logos replaced by gnomarchi brand). Falls back to generated
color-field PNGs when a pack has no backgrounds.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from theme.emitters import _write_png, emit_gsettings
from theme.palette import load_palette
from theme.paths import find_pack, state_dir

STILL_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg", ".avif"}
VARIANT_COUNT = 4  # used only for generated fallback


def _active_theme_id() -> str | None:
    path = state_dir() / "active-theme"
    if not path.is_file():
        return None
    tid = path.read_text(encoding="utf-8").strip()
    return tid or None


def _variant_dir(theme_id: str) -> Path:
    return state_dir() / "wallpapers" / "variants" / theme_id


def _index_path(theme_id: str) -> Path:
    return _variant_dir(theme_id) / "index.json"


def list_pack_stills(pack: Path) -> list[Path]:
    bg = pack / "backgrounds"
    if not bg.is_dir():
        return []
    stills: list[Path] = []
    for path in sorted(bg.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in STILL_SUFFIXES:
            continue
        # Skip nested intros dir handled only if files sit at top level
        stills.append(path)
    # Also include one-level intros stills? Omarchy intros are video — skip.
    return stills


def ensure_variants(theme_id: str | None = None) -> list[Path]:
    """Return ordered background candidates for the theme."""
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme; run gnomarchi theme set first")
    pack = find_pack(tid)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {tid}")
    stills = list_pack_stills(pack)
    if stills:
        return stills
    # Generated fallback
    colors = load_palette(pack)
    dest = _variant_dir(tid)
    dest.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(VARIANT_COUNT):
        shifted = dict(colors)
        if i == 1:
            shifted["accent"], shifted["surface"] = (
                colors.get("surface", "#121a2b"),
                colors.get("accent", "#3d8bfd"),
            )
        elif i == 2:
            shifted["background"] = colors.get("surface", "#121a2b")
            shifted["surface"] = colors.get("background", "#0b1220")
        elif i == 3:
            shifted["accent"] = colors.get("foreground", "#e8eef7")
        out = dest / f"{i:02d}.png"
        _write_png(out, 1920, 1080, shifted)
        paths.append(out)
    return paths


def current_index(theme_id: str | None = None) -> int:
    tid = theme_id or _active_theme_id()
    if not tid:
        return 0
    variants = ensure_variants(tid)
    n = max(len(variants), 1)
    meta = _index_path(tid)
    if not meta.is_file():
        return 0
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        return int(data.get("index", 0)) % n
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def _activate(chosen: Path, pack: Path, tid: str, idx: int) -> Path:
    dest_dir = state_dir() / "wallpapers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    active = dest_dir / f"active{chosen.suffix.lower()}"
    # Clear other actives
    for old in dest_dir.glob("active.*"):
        if old != active:
            old.unlink(missing_ok=True)
    shutil.copy2(chosen, active)
    # Also keep active.png alias when source is png for older callers
    if active.suffix.lower() == ".png":
        pass
    elif chosen.suffix.lower() == ".png":
        shutil.copy2(chosen, dest_dir / "active.png")
    _index_path(tid).parent.mkdir(parents=True, exist_ok=True)
    _index_path(tid).write_text(
        json.dumps({"index": idx, "theme": tid, "path": str(chosen)}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    emit_gsettings(active, load_palette(pack))
    return active


def set_background(index: int, theme_id: str | None = None) -> Path:
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme")
    pack = find_pack(tid)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {tid}")
    variants = ensure_variants(tid)
    idx = index % len(variants)
    return _activate(variants[idx], pack, tid, idx)


def next_background(theme_id: str | None = None) -> Path:
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme")
    return set_background(current_index(tid) + 1, tid)


def first_background(theme_id: str | None = None) -> Path:
    return set_background(0, theme_id)
