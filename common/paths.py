"""Resolve repo root and state directories."""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def state_dir() -> Path:
    """Writable config/state: env → XDG → ~/.config → repo .local-state (dev only)."""
    override = os.environ.get("GNOMARCHI_STATE_DIR")
    if override:
        return Path(override).expanduser().resolve()
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser().resolve() / "gnomarchi"
    home = os.environ.get("HOME")
    if home:
        return Path(home).expanduser().resolve() / ".config" / "gnomarchi"
    # Last resort for CI sandboxes without HOME: only if the package tree is writable.
    candidate = REPO_ROOT / ".local-state"
    if os.access(REPO_ROOT, os.W_OK):
        return candidate
    raise RuntimeError(
        "cannot resolve writable gnomarchi state dir; set GNOMARCHI_STATE_DIR or HOME"
    )
