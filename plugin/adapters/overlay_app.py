"""overlay-app adapter stub: desktop entry + script under XDG apps."""

from __future__ import annotations

from pathlib import Path


class OverlayAppAdapter:
    runtime = "overlay-app"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        entry = plugin_dir / "app.desktop"
        if not entry.is_file():
            errors.append("overlay-app: missing app.desktop")
        return errors

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return f"would install desktop entry from {plugin_dir / 'app.desktop'}"
