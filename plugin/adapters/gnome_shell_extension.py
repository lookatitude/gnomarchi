"""gnome-shell-extension adapter: install under ~/.local/share/gnome-shell/extensions."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path


class GnomeShellExtensionAdapter:
    runtime = "gnome-shell-extension"

    def validate_artifacts(self, plugin_dir: Path, manifest: dict) -> list[str]:
        errors: list[str] = []
        meta = plugin_dir / "metadata.json"
        ext = plugin_dir / "extension.js"
        if not meta.is_file():
            errors.append("gnome-shell-extension: missing metadata.json")
        else:
            try:
                data = json.loads(meta.read_text(encoding="utf-8"))
                if "uuid" not in data:
                    errors.append("metadata.json: uuid required")
            except json.JSONDecodeError as exc:
                errors.append(f"metadata.json: {exc}")
        if not ext.is_file():
            errors.append("gnome-shell-extension: missing extension.js")
        if not manifest.get("explicit_shell_extension"):
            errors.append("explicit_shell_extension=true required")
        return errors

    def enable(self, plugin_dir: Path, manifest: dict) -> str:
        meta = json.loads((plugin_dir / "metadata.json").read_text(encoding="utf-8"))
        uuid = meta["uuid"]
        home = Path(os.environ.get("HOME", "/tmp")).expanduser()
        dest = home / ".local" / "share" / "gnome-shell" / "extensions" / uuid
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(plugin_dir, dest)
        # Enable via gnome-extensions if available
        ge = shutil.which("gnome-extensions")
        if ge:
            subprocess.run([ge, "enable", uuid], check=False, capture_output=True)
        return f"installed and enabled Shell extension {uuid} → {dest}"

    def enable_stub(self, plugin_dir: Path, manifest: dict) -> str:
        return self.enable(plugin_dir, manifest)
