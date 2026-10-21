"""Pinning tests for modes / capture / clipboard / reminders / video / shell CSS."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "gnomarchi"


class ParityDesktopTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.state = Path(self._tmpdir.name)
        self.home = self.state / "home"
        self.home.mkdir()
        os.environ["GNOMARCHI_STATE_DIR"] = str(self.state)
        os.environ["HOME"] = str(self.home)
        os.environ["GNOMARCHI_ROOT"] = str(ROOT)
        if str(ROOT) not in sys.path:
            sys.path.insert(0, str(ROOT))

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def test_reminders_parse_and_add(self) -> None:
        from desktop.reminders import add, list_reminders, parse_duration

        self.assertEqual(parse_duration("10m"), 600.0)
        self.assertEqual(parse_duration("1h30m"), 5400.0)
        rem = add("ping", in_seconds=30)
        items = list_reminders()
        self.assertTrue(any(r.id == rem.id and r.text == "ping" for r in items))

    def test_video_wallpaper_flag_and_stage(self) -> None:
        from theme.emitters import (
            emit_video_wallpaper,
            set_video_wallpaper_enabled,
            video_wallpaper_enabled,
        )

        set_video_wallpaper_enabled(False)
        self.assertFalse(video_wallpaper_enabled())
        pack = self.state / "pack"
        (pack / "backgrounds").mkdir(parents=True)
        video = pack / "backgrounds" / "loop.mp4"
        video.write_bytes(b"\x00\x00\x00\x18ftypmp42")
        dest = emit_video_wallpaper(pack)
        self.assertIsNotNone(dest)
        assert dest is not None
        self.assertTrue(dest.is_file())
        unit = self.home / ".config" / "systemd" / "user" / "gnomarchi-video-wallpaper.service"
        self.assertTrue(unit.is_file())
        self.assertIn("mpv", unit.read_text(encoding="utf-8"))
        set_video_wallpaper_enabled(True)
        self.assertTrue(video_wallpaper_enabled())

    def test_shell_css_covers_notifications_osd_lock(self) -> None:
        from theme.emitters import emit_gnome_shell_colors

        path = emit_gnome_shell_colors(
            {
                "background": "#111111",
                "foreground": "#eeeeee",
                "accent": "#4488ff",
                "surface": "#222222",
                "muted": "#888888",
                "red": "#ff5555",
            }
        )
        css = path.read_text(encoding="utf-8")
        self.assertIn("notification-banner", css)
        self.assertIn("osd-window", css)
        self.assertIn("unlock-dialog", css)
        self.assertIn("polkit-dialog", css)

    def test_modes_plugin_manifest(self) -> None:
        manifest = ROOT / "plugins" / "first-party" / "gnomarchi.modes" / "manifest.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(data["id"], "gnomarchi.modes")
        self.assertEqual(data["runtime"], "status-indicator")
        self.assertTrue((manifest.parent / "indicator.py").is_file())
        self.assertTrue((manifest.parent / "autostart.desktop").is_file())

    def test_cli_subcommands_wired(self) -> None:
        for argv in (
            ["capture", "--help"],
            ["clipboard", "--help"],
            ["remind", "--help"],
            ["mode", "--help"],
            ["theme", "bg", "video", "--help"],
            ["theme", "unlock", "--help"],
            ["branding", "gdm", "apply", "--help"],
            ["notice", "--help"],
            ["webapp", "--help"],
            ["share", "--help"],
            ["theme", "new", "--help"],
            ["herdr", "--help"],
            ["display", "--help"],
            ["idle", "--help"],
            ["config", "--help"],
            ["cliamp", "--help"],
            ["nvim", "seed", "--help"],
        ):
            proc = subprocess.run(
                [sys.executable, str(CLI), *argv],
                capture_output=True,
                text=True,
                timeout=15,
                env={**os.environ, "PYTHONPATH": str(ROOT)},
            )
            self.assertEqual(proc.returncode, 0, msg=(argv, proc.stderr))

    def test_webapp_add_list_remove(self) -> None:
        from desktop import webapps

        sid = webapps.add("TestApp", "https://example.com")
        ids = [r["id"] for r in webapps.list_apps()]
        self.assertIn(sid, ids)
        self.assertTrue(webapps.remove(sid))

    def test_theme_scaffold_new(self) -> None:
        from theme.scaffold import new_theme

        dest = new_theme("parity-test-theme", from_id="tokyo-night")
        self.assertTrue((dest / "theme.toml").is_file())
        self.assertTrue((dest / "colors.toml").is_file())

    def test_starship_emit(self) -> None:
        from theme.emitters import emit_starship

        path = emit_starship(
            {
                "background": "#111111",
                "foreground": "#eeeeee",
                "accent": "#4488ff",
                "muted": "#888888",
                "red": "#ff5555",
                "green": "#55aa55",
            }
        )
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("4488ff", text)
        self.assertIn("55aa55", text)
        self.assertIn("$directory$git_branch$git_status$character", text)
        self.assertIn("[git_status]", text)

    def test_starship_hook_idempotent(self) -> None:
        from common.starship_hook import ensure_starship_hook, has_starship_hook

        first = ensure_starship_hook(self.home)
        self.assertEqual(first["zsh"], "created")
        self.assertEqual(first["bash"], "created")
        zshrc = self.home / ".zshrc"
        bashrc = self.home / ".bashrc"
        self.assertTrue(has_starship_hook(zshrc))
        self.assertTrue(has_starship_hook(bashrc))
        self.assertIn('starship init zsh', zshrc.read_text(encoding="utf-8"))
        self.assertIn('starship init bash', bashrc.read_text(encoding="utf-8"))
        second = ensure_starship_hook(self.home)
        self.assertEqual(second["zsh"], "present")
        self.assertEqual(second["bash"], "present")
        # Still a single hook block
        self.assertEqual(zshrc.read_text(encoding="utf-8").count("starship init"), 1)

    def test_registry_target_ids_done(self) -> None:
        text = (ROOT / "features" / "registry.yaml").read_text(encoding="utf-8")
        for fid in (
            "omarchy.shell.bar-indicators",
            "omarchy.shell.notifications-osd-lock",
            "omarchy.shell.clipboard-reminders",
            "omarchy.shell.video-wallpaper",
            "omarchy.capture.suite",
        ):
            idx = text.find(f"- id: {fid}")
            self.assertGreaterEqual(idx, 0, fid)
            chunk = text[idx : idx + 280]
            self.assertIn("status: done", chunk, fid)


if __name__ == "__main__":
    unittest.main()
