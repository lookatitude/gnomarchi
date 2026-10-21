"""status-indicator adapter: install StatusNotifier / AppIndicator autostart."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
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
        started = self._ensure_running(dest_dir, plugin_id)
        suffix = "; started" if started else "; already running or start skipped"
        return f"enabled status-indicator {plugin_id} → {link}{suffix}"

    def _ensure_running(self, dest_dir: Path, plugin_id: str) -> bool:
        """Launch installed indicator.py when not already alive (session enable)."""
        marker = f"indicators/{plugin_id}/indicator.py"
        check = subprocess.run(
            ["pgrep", "-f", marker],
            check=False,
            capture_output=True,
        )
        if check.returncode == 0:
            return False
        indicator = dest_dir / "indicator.py"
        if not indicator.is_file():
            return False
        env = os.environ.copy()
        uid = os.getuid()
        env.setdefault("DISPLAY", os.environ.get("DISPLAY", ":0"))
        env.setdefault(
            "DBUS_SESSION_BUS_ADDRESS",
            os.environ.get(
                "DBUS_SESSION_BUS_ADDRESS",
                f"unix:path=/run/user/{uid}/bus",
            ),
        )
        env.setdefault("XDG_RUNTIME_DIR", f"/run/user/{uid}")
        # Prefer tree under /usr/local when installed copy lacks parents[3] layout
        env.setdefault("GNOMARCHI_ROOT", "/usr/local/lib/gnomarchi")
        log = dest_dir / "indicator.log"
        with log.open("a", encoding="utf-8") as logf:
            subprocess.Popen(
                [sys.executable if sys.executable else "python3", str(indicator)],
                stdout=logf,
                stderr=subprocess.STDOUT,
                start_new_session=True,
                env=env,
                cwd=str(dest_dir),
            )
        return True

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
