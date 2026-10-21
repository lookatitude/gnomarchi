"""Pinning tests for desktop.branding store + CLI."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "bin" / "gnomarchi"


class BrandingTests(unittest.TestCase):
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

    def test_ensure_store_seeds_files(self) -> None:
        from desktop.branding import ensure_store, logo_path, read_surface, surface_path

        ensure_store()
        self.assertTrue(surface_path("screensaver").is_file())
        self.assertTrue(surface_path("about").is_file())
        self.assertTrue(logo_path().is_file())
        ss = read_surface("screensaver")
        # FIGlet / shipped art should contain underscore glyph rows
        self.assertTrue(any(c in ss for c in ("_", "/", "|", "\\")))
        self.assertGreater(len(ss.strip()), 20)

    def test_reset_and_text(self) -> None:
        from desktop.branding import read_surface, reset_surface, set_text, write_surface

        write_surface("screensaver", "custom-art\n")
        self.assertEqual(read_surface("screensaver").strip(), "custom-art")
        reset_surface("screensaver")
        self.assertNotEqual(read_surface("screensaver").strip(), "custom-art")
        set_text("about", "gnomarchi")
        about = read_surface("about")
        self.assertIn("not affiliated with Omarchy", about)

    def test_image_without_pillow_notes_todo(self) -> None:
        from desktop.branding import branding_dir, set_from_image

        img = self.state / "mark.png"
        # minimal invalid-as-image file is fine — Pillow missing path returns before decode
        img.write_bytes(b"not-a-real-png")
        path, msg = set_from_image("screensaver", img)
        self.assertIsNone(path)
        self.assertIn("Pillow", msg)
        note = branding_dir() / "screensaver.image-todo.txt"
        self.assertTrue(note.is_file())
        self.assertIn(str(img.resolve()), note.read_text(encoding="utf-8"))

    def test_cli_reset_and_logo_status(self) -> None:
        env = os.environ.copy()
        proc = subprocess.run(
            [sys.executable, str(CLI), "branding", "screensaver", "reset"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("reset", proc.stdout.lower())
        proc2 = subprocess.run(
            [sys.executable, str(CLI), "branding", "logo", "status"],
            check=False,
            capture_output=True,
            text=True,
            env=env,
        )
        self.assertEqual(proc2.returncode, 0, proc2.stderr)
        self.assertIn("branding_logo", proc2.stdout)
        self.assertIn("plymouth", proc2.stdout.lower())

    def test_menu_has_style_screensaver_about(self) -> None:
        menu = (ROOT / "menu" / "default.jsonc").read_text(encoding="utf-8")
        self.assertIn("style.screensaver", menu)
        self.assertIn("style.about", menu)
        self.assertIn("branding", menu)
        self.assertIn("install", menu)  # plymouth install path unchanged
        self.assertIn("plymouth", menu)


if __name__ == "__main__":
    unittest.main()
