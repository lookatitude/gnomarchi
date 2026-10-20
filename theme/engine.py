"""Theme pack validate / set / list (P1 stubs)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from theme.paths import find_pack, pack_roots, state_dir

REQUIRED_THEME_KEYS = ("id", "name", "version")
REQUIRED_COLOR_KEYS = ("background", "foreground", "accent")


def _load_toml(path: Path) -> dict:
    with path.open("rb") as fh:
        return tomllib.load(fh)


def validate_theme(pack_dir: str | Path) -> list[str]:
    """Return a list of validation errors (empty = ok)."""
    root = Path(pack_dir).expanduser().resolve()
    errors: list[str] = []
    theme_toml = root / "theme.toml"
    colors_toml = root / "colors.toml"

    if not theme_toml.is_file():
        errors.append("missing theme.toml")
        return errors
    if not colors_toml.is_file():
        errors.append("missing colors.toml")

    try:
        theme = _load_toml(theme_toml)
    except tomllib.TOMLDecodeError as exc:
        errors.append(f"theme.toml: {exc}")
        return errors

    meta = theme.get("theme")
    if not isinstance(meta, dict):
        errors.append("theme.toml: missing [theme] table")
    else:
        for key in REQUIRED_THEME_KEYS:
            if not meta.get(key):
                errors.append(f"theme.toml: theme.{key} required")
        if meta.get("id") and meta["id"] != root.name:
            errors.append(
                f"theme.id {meta['id']!r} must match directory name {root.name!r}"
            )

    provenance = theme.get("provenance")
    if isinstance(provenance, dict) and provenance.get("official_omarchy"):
        errors.append("D7: packs must not claim official Omarchy affiliation")

    backgrounds = root / "backgrounds"
    if backgrounds.is_dir() and any(backgrounds.iterdir()):
        # Stub gate: refuse shipping Omarchy-style binary wallpaper trees by default.
        credits = root / "CREDITS"
        if not credits.is_file():
            errors.append(
                "backgrounds/ present without CREDITS (D7: no uncredited wallpapers)"
            )

    if colors_toml.is_file():
        try:
            from theme.palette import load_palette

            palette = load_palette(root)
        except Exception as exc:
            errors.append(f"colors.toml: {exc}")
            return errors
        for key in REQUIRED_COLOR_KEYS:
            if not palette.get(key):
                errors.append(f"colors.toml: colors.{key} required (or Omarchy-flat equivalent)")

    return errors


def list_themes() -> list[dict[str, str]]:
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for root in pack_roots():
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in seen:
                continue
            theme_toml = child / "theme.toml"
            if not theme_toml.is_file():
                continue
            try:
                meta = _load_toml(theme_toml).get("theme", {})
            except tomllib.TOMLDecodeError:
                meta = {}
            tid = str(meta.get("id") or child.name)
            seen.add(tid)
            out.append(
                {
                    "id": tid,
                    "name": str(meta.get("name") or tid),
                    "path": str(child),
                }
            )
    return out


def set_theme(theme_id: str) -> Path:
    """Validate pack, write state, and apply GTK/Ghostty/wallpaper emitters."""
    from theme.emitters import apply_theme

    pack = find_pack(theme_id)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {theme_id}")
    errors = validate_theme(pack)
    if errors:
        raise ValueError("; ".join(errors))

    dest = state_dir()
    dest.mkdir(parents=True, exist_ok=True)
    active = dest / "active-theme"
    active.write_text(f"{theme_id}\n", encoding="utf-8")
    (dest / "active-theme-path").write_text(f"{pack}\n", encoding="utf-8")
    apply_theme(pack)
    try:
        from theme.backgrounds import ensure_variants

        ensure_variants(theme_id)
    except Exception:
        pass
    return active
