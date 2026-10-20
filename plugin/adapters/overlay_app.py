"""overlay-app adapter: install .desktop into user applications."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


class OverlayAppAdapter:
    runtime = "overlay-app"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        entry = plugin_dir / "app.desktop"
        if not entry.is_file():
            errors.append("overlay-app: missing app.desktop")
        return errors

    def enable(self, plugin_dir: Path, manifest: dict) -> str:
        home = Path(os.environ.get("HOME", "/tmp")).expanduser()
        apps = home / ".local" / "share" / "applications"
        apps.mkdir(parents=True, exist_ok=True)
        plugin_id = str(manifest.get("id") or plugin_dir.name)
        src = plugin_dir / "app.desktop"
        dest = apps / f"gnomarchi-{plugin_id}.desktop"
        text = src.read_text(encoding="utf-8")
        # Point Path=/Exec helpers at plugin dir when relative.
        if "Path=" not in text:
            text = text.rstrip() + f"\nPath={plugin_dir}\n"
        dest.write_text(text, encoding="utf-8")
        update = shutil.which("update-desktop-database")
        if update:
            import subprocess

            subprocess.run([update, str(apps)], check=False, capture_output=True)
        return f"installed overlay-app desktop entry → {dest}"

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
