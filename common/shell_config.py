"""Load ~/.config/gnomarchi/shell.toml (with packaged defaults)."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

from common.paths import REPO_ROOT, state_dir


def default_shell_toml() -> Path:
    return REPO_ROOT / "config" / "shell.toml"


def user_shell_toml() -> Path:
    return state_dir() / "shell.toml"


def load_shell_config() -> dict[str, Any]:
    path = user_shell_toml()
    if not path.is_file():
        path = default_shell_toml()
    if not path.is_file():
        return {
            "panel": {"indicators": ["gnomarchi.agents"]},
            "agents": {"usage_refresh_seconds": 900},
        }
    return tomllib.loads(path.read_text(encoding="utf-8"))


def ensure_user_shell_toml() -> Path:
    dest = user_shell_toml()
    if not dest.is_file():
        src = default_shell_toml()
        dest.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            dest.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        else:
            dest.write_text("[panel]\nindicators = [\"gnomarchi.agents\"]\n", encoding="utf-8")
    return dest
