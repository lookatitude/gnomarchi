"""Resolve repo root and state directories."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def state_dir() -> Path:
    """Prefer GNOMARCHI_STATE_DIR, else XDG, else repo .local-state for tests."""
    override = os.environ.get("GNOMARCHI_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / "gnomarchi"
    return REPO_ROOT / ".local-state"
