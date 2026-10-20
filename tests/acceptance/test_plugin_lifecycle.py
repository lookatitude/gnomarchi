"""Plugin scaffold/validate/add-refuse/sudo-hook/enable acceptance via CLI."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from acceptance._helpers import CLI, REPO


class PluginLifecycleAcceptanceTests(unittest.TestCase):
    def test_scaffold_validate_add_refuse_enable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "GNOMARCHI_STATE_DIR": tmp}
            dest = Path(tmp) / "src"
            scaffold = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "plugin",
                    "scaffold",
                    "accept-plugin",
                    "--runtime",
                    "overlay-app",
                    "--dest",
                    str(dest),
                ],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(scaffold.returncode, 0, scaffold.stderr)
            plugin_dir = dest / "accept-plugin"

            validate = subprocess.run(
                [sys.executable, str(CLI), "plugin", "validate", str(plugin_dir)],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(validate.returncode, 0, validate.stderr)

            refuse = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "plugin",
                    "add",
                    str(plugin_dir),
                    "--dest",
                    str(Path(tmp) / "installed"),
                ],
                cwd=REPO,
                env=env,
                input="n\n",
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(refuse.returncode, 2, refuse.stderr)
            self.assertIn("refused", refuse.stderr.lower())

            added = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "plugin",
                    "add",
                    str(plugin_dir),
                    "--confirm",
                    "--dest",
                    str(Path(tmp) / "installed"),
                ],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(added.returncode, 0, added.stderr)
            installed = Path(tmp) / "installed" / "accept-plugin"

            enable = subprocess.run(
                [sys.executable, str(CLI), "plugin", "enable", str(installed)],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(enable.returncode, 0, enable.stderr)

    def test_sudo_hook_refused_by_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "evil"
            root.mkdir()
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "id": "evil",
                        "name": "Evil",
                        "version": "0.1.0",
                        "runtime": "overlay-app",
                        "permissions": [],
                        "hooks": {"install": "sudo pacman -S evil"},
                    }
                ),
                encoding="utf-8",
            )
            (root / "app.desktop").write_text(
                "[Desktop Entry]\nName=Evil\n", encoding="utf-8"
            )
            proc = subprocess.run(
                [sys.executable, str(CLI), "plugin", "validate", str(root)],
                cwd=REPO,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(proc.returncode, 0)
            self.assertTrue(
                "escalat" in proc.stderr.lower() or "invalid" in proc.stderr.lower(),
                proc.stderr,
            )


if __name__ == "__main__":
    unittest.main()
