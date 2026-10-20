"""user-service adapter: install and enable systemd --user unit."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


class UserServiceAdapter:
    runtime = "user-service"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        unit = plugin_dir / "gnomarchi-plugin.service"
        if not unit.is_file():
            errors.append("user-service: missing gnomarchi-plugin.service")
        return errors

    def enable(self, plugin_dir: Path, manifest: dict) -> str:
        home = Path(os.environ.get("HOME", "/tmp")).expanduser()
        unit_dir = home / ".config" / "systemd" / "user"
        unit_dir.mkdir(parents=True, exist_ok=True)
        plugin_id = str(manifest.get("id") or plugin_dir.name)
        src = plugin_dir / "gnomarchi-plugin.service"
        text = src.read_text(encoding="utf-8").replace("PLUGIN_ID", plugin_id)
        # Ensure WorkingDirectory points at plugin
        if "WorkingDirectory=" not in text:
            text = text.rstrip() + f"\nWorkingDirectory={plugin_dir}\n"
        dest = unit_dir / f"gnomarchi-{plugin_id}.service"
        dest.write_text(text, encoding="utf-8")
        systemctl = shutil.which("systemctl")
        if systemctl:
            subprocess.run(
                [systemctl, "--user", "daemon-reload"],
                check=False,
                capture_output=True,
            )
            subprocess.run(
                [systemctl, "--user", "enable", "--now", dest.name],
                check=False,
                capture_output=True,
            )
        return f"enabled user service → {dest}"

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
