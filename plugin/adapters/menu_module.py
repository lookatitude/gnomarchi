"""menu-module adapter stub: JSONC fragment merged into menu tree."""

from __future__ import annotations

from pathlib import Path


class MenuModuleAdapter:
    runtime = "menu-module"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        fragment = plugin_dir / "menu.jsonc"
        if not fragment.is_file():
            errors.append("menu-module: missing menu.jsonc")
        return errors

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return f"would merge {plugin_dir / 'menu.jsonc'} into menu tree"
