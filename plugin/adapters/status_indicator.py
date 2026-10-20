"""status-indicator adapter: install StatusNotifier / AppIndicator autostart."""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path


class StatusIndicatorAdapter:
    runtime = "status-indicator"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        entry = plugin_dir / "indicator.py"
        desktop = plugin_dir / "autostart.desktop"
        if not entry.is_file():
            errors.append("status-indicator: missing indicator.py")
        if not desktop.is_file():
            errors.append("status-indicator: missing autostart.desktop")
        return errors

    def enable(self, plugin_dir: Path, manifest: dict) -> str:
        home = Path(os.environ.get("HOME", "/tmp")).expanduser()
        autostart = home / ".config" / "autostart"
        autostart.mkdir(parents=True, exist_ok=True)
        plugin_id = str(manifest.get("id") or plugin_dir.name)
        dest_dir = home / ".local" / "share" / "gnomarchi" / "indicators" / plugin_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        for name in ("indicator.py", "autostart.desktop"):
            src = plugin_dir / name
            if src.is_file():
                shutil.copy2(src, dest_dir / name)
        # Rewrite Exec= to installed path
        desktop_src = dest_dir / "autostart.desktop"
        text = desktop_src.read_text(encoding="utf-8")
        exec_line = f"Exec=python3 {dest_dir / 'indicator.py'}"
        lines = []
        replaced = False
        for line in text.splitlines():
            if line.startswith("Exec="):
                lines.append(exec_line)
                replaced = True
            else:
                lines.append(line)
        if not replaced:
            lines.append(exec_line)
        desktop_src.write_text("\n".join(lines) + "\n", encoding="utf-8")
        link = autostart / f"gnomarchi-{plugin_id}.desktop"
        shutil.copy2(desktop_src, link)
        enabled = home / ".config" / "gnomarchi" / "enabled-indicators.json"
        enabled.parent.mkdir(parents=True, exist_ok=True)
        data: list[str] = []
        if enabled.is_file():
            try:
                data = json.loads(enabled.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = []
        if plugin_id not in data:
            data.append(plugin_id)
        enabled.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        return f"enabled status-indicator {plugin_id} → {link}"

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
