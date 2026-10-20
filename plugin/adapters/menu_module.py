"""menu-module adapter: install JSONC fragment into extensions dir."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


class MenuModuleAdapter:
    runtime = "menu-module"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        fragment = plugin_dir / "menu.jsonc"
        if not fragment.is_file():
            errors.append("menu-module: missing menu.jsonc")
        return errors

    def enable(self, plugin_dir: Path, manifest: dict) -> str:
        home = Path(os.environ.get("HOME", "/tmp")).expanduser()
        dest_dir = home / ".config" / "gnomarchi" / "extensions"
        dest_dir.mkdir(parents=True, exist_ok=True)
        plugin_id = str(manifest.get("id") or plugin_dir.name)
        dest = dest_dir / f"{plugin_id}.jsonc"
        shutil.copy2(plugin_dir / "menu.jsonc", dest)
        return f"merged menu module → {dest}"

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
