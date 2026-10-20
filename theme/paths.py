"""Resolve theme pack roots and state directories."""

from __future__ import annotations

from pathlib import Path

from common.paths import REPO_ROOT, state_dir

__all__ = ["REPO_ROOT", "state_dir", "pack_roots", "find_pack"]


def pack_roots() -> list[Path]:
    roots: list[Path] = []
    seeded = REPO_ROOT / "theme" / "packs"
    if seeded.is_dir():
        roots.append(seeded)
    user = state_dir() / "themes"
    if user.is_dir():
        roots.append(user)
    return roots


def find_pack(theme_id: str) -> Path | None:
    for root in pack_roots():
        candidate = root / theme_id
        if (candidate / "theme.toml").is_file():
            return candidate
    return None
