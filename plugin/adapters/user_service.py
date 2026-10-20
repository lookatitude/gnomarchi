"""user-service adapter stub: systemd --user unit after validate."""

from __future__ import annotations

from pathlib import Path


class UserServiceAdapter:
    runtime = "user-service"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        unit = plugin_dir / "gnomarchi-plugin.service"
        if not unit.is_file():
            errors.append("user-service: missing gnomarchi-plugin.service")
        return errors

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return (
            f"would systemctl --user enable {plugin_dir / 'gnomarchi-plugin.service'} "
            "(after explicit confirm)"
        )
