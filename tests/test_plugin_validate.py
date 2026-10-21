"""Smoke tests for plugin manifest validate and scaffold."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "bin" / "gnomarchi"


class PluginValidateTests(unittest.TestCase):
    def test_scaffold_overlay_validates(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import scaffold_plugin, validate_plugin

        with tempfile.TemporaryDirectory() as tmp:
            target = scaffold_plugin("smoke-overlay", runtime="overlay-app", dest_root=tmp)
            self.assertEqual(validate_plugin(target), [])
            manifest = json.loads((target / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["id"], "smoke-overlay")
            self.assertEqual(manifest["runtime"], "overlay-app")

    def test_unknown_runtime_rejected(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import validate_plugin

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "bad"
            root.mkdir()
            (root / "manifest.json").write_text(
                json.dumps(
                    {
                        "id": "bad",
                        "name": "Bad",
                        "version": "0.1.0",
                        "runtime": "quickshell",
                        "permissions": [],
                        "hooks": {},
                    }
                ),
                encoding="utf-8",
            )
            errors = validate_plugin(root)
        self.assertTrue(any("unknown runtime" in e for e in errors))

    def test_shell_extension_not_default_scaffold(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import scaffold_plugin

        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                scaffold_plugin("ext", runtime="gnome-shell-extension", dest_root=tmp)

    def test_cli_plugin_scaffold_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "GNOMARCHI_STATE_DIR": tmp}
            dest = Path(tmp) / "plugins"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(CLI),
                    "plugin",
                    "scaffold",
                    "cli-smoke",
                    "--runtime",
                    "menu-module",
                    "--dest",
                    str(dest),
                ],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            plugin_dir = dest / "cli-smoke"
            v = subprocess.run(
                [sys.executable, str(CLI), "plugin", "validate", str(plugin_dir)],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(v.returncode, 0, v.stderr)

    def test_sudo_hook_rejected(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import validate_plugin

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
            (root / "app.desktop").write_text("[Desktop Entry]\nName=Evil\n", encoding="utf-8")
            errors = validate_plugin(root)
        self.assertTrue(any("escalating" in e for e in errors), errors)

    def test_add_refuses_without_confirm(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import add_plugin, scaffold_plugin

        with tempfile.TemporaryDirectory() as tmp:
            src = scaffold_plugin("need-confirm", runtime="overlay-app", dest_root=tmp)
            with self.assertRaises(PermissionError):
                add_plugin(src, confirm=False, prompt_confirm=lambda: "n", dest_root=tmp)

    def test_add_and_enable_with_confirm(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import add_plugin, enable_plugin, scaffold_plugin

        with tempfile.TemporaryDirectory() as tmp:
            src = scaffold_plugin("ok-add", runtime="menu-module", dest_root=Path(tmp) / "src")
            dest = Path(tmp) / "installed"
            target = add_plugin(src, confirm=True, dest_root=dest)
            msg = enable_plugin(target)
            self.assertIn("ok-add", msg.lower() + str(target))

    def test_hypr_path_hook_rejected(self) -> None:
        sys.path.insert(0, str(REPO))
        from plugin.lifecycle import check_hooks_no_sudo

        errs = check_hooks_no_sudo({"on_enable": "cp x ~/.config/hypr/hyprland.conf"})
        self.assertTrue(errs)
        errs2 = check_hooks_no_sudo({"on_enable": "quickshell --reload"})
        self.assertTrue(errs2)


if __name__ == "__main__":
    unittest.main()

