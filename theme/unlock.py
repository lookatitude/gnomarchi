"""Lock / unlock screensaver art from theme packs (Omarchy Style→Unlock → GNOME).

Copies pack unlock.png to ~/.config/gnomarchi/branding/unlock.png and sets
org.gnome.desktop.screensaver picture-uri. GDM greeter branding is separate
(see desktop.branding); this module never touches SDDM.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from theme.paths import find_pack, pack_roots, state_dir


def _run(argv: list[str]) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            argv, check=False, capture_output=True, text=True, timeout=15
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def branding_dir() -> Path:
    d = state_dir() / "branding"
    d.mkdir(parents=True, exist_ok=True)
    return d


def unlock_path() -> Path:
    return branding_dir() / "unlock.png"


def _meta_path() -> Path:
    return branding_dir() / "unlock.json"


def pack_unlock_file(pack: Path) -> Path | None:
    candidate = pack / "unlock.png"
    return candidate if candidate.is_file() else None


def list_unlock_packs() -> list[dict[str, str]]:
    """Packs that ship unlock.png (and optional preview-unlock.png)."""
    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for root in pack_roots():
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in seen:
                continue
            unlock = pack_unlock_file(child)
            if unlock is None:
                continue
            seen.add(child.name)
            preview = child / "preview-unlock.png"
            out.append(
                {
                    "id": child.name,
                    "name": child.name,
                    "path": str(unlock),
                    "preview": str(preview) if preview.is_file() else str(unlock),
                }
            )
    return out


def _emit_screensaver(image: Path) -> None:
    uri = image.resolve().as_uri()
    _run(["gsettings", "set", "org.gnome.desktop.screensaver", "picture-uri", uri])
    _run(
        [
            "gsettings",
            "set",
            "org.gnome.desktop.screensaver",
            "picture-options",
            "zoom",
        ]
    )


def apply_unlock(
    pack: Path | None = None, *, theme_id: str | None = None
) -> Path | None:
    """Copy pack unlock.png into branding and point the GNOME screensaver at it.

    Returns the destination path, or None if the pack has no unlock.png.
    """
    tid = theme_id
    if pack is None:
        if not tid:
            active = state_dir() / "active-theme"
            if active.is_file():
                tid = active.read_text(encoding="utf-8").strip() or None
        if not tid:
            return None
        pack = find_pack(tid)
        if pack is None:
            return None
    elif tid is None:
        tid = pack.name

    src = pack_unlock_file(pack)
    if src is None:
        return None

    dest = unlock_path()
    shutil.copy2(src, dest)
    _emit_screensaver(dest)
    _meta_path().write_text(
        json.dumps({"pack": tid, "source": str(src), "path": str(dest)}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    return dest


def set_unlock(theme_id: str) -> Path:
    """Select unlock art from a pack id (does not change the active theme)."""
    pack = find_pack(theme_id)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {theme_id}")
    dest = apply_unlock(pack, theme_id=theme_id)
    if dest is None:
        raise FileNotFoundError(f"pack has no unlock.png: {theme_id}")
    return dest


def status() -> dict[str, str | None]:
    meta = _meta_path()
    dest = unlock_path()
    pack = None
    path = str(dest) if dest.is_file() else None
    if meta.is_file():
        try:
            data = json.loads(meta.read_text(encoding="utf-8"))
            pack = data.get("pack")
            path = data.get("path") or path
        except (json.JSONDecodeError, TypeError):
            pass
    return {"pack": pack, "path": path}
