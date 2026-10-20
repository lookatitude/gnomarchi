"""Install gnomarchi neovim seed into ~/.config/nvim."""

from __future__ import annotations

import shutil
from pathlib import Path

from common.paths import REPO_ROOT


def install(force: bool = False) -> Path:
    src = REPO_ROOT / "config" / "nvim" / "init.lua"
    if not src.is_file():
        raise FileNotFoundError(src)
    dest_dir = Path.home() / ".config" / "nvim"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / "init.lua"
    if dest.is_file() and not force:
        backup = dest_dir / "init.lua.gnomarchi-bak"
        if not backup.is_file():
            shutil.copy2(dest, backup)
    shutil.copy2(src, dest)
    return dest
