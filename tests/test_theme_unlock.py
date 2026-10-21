"""theme unlock art → branding + screensaver picture-uri (G2)."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestThemeUnlock(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        root = Path(self._tmpdir.name)
        home = root / "home"
        home.mkdir()
        self.state = root
        self.home = home
        self._env = mock.patch.dict(
            os.environ,
            {
                "GNOMARCHI_STATE_DIR": str(root),
                "HOME": str(home),
            },
        )
        self._env.start()
        self.addCleanup(self._env.stop)

    def test_apply_unlock_copies_and_sets_screensaver(self) -> None:
        from theme.unlock import apply_unlock, unlock_path, status

        calls: list[list[str]] = []

        def fake_run(argv: list[str], **_kw):
            calls.append(list(argv))
            return None

        with mock.patch("theme.unlock._run", side_effect=fake_run):
            dest = apply_unlock(theme_id="tokyo-night")
        self.assertIsNotNone(dest)
        assert dest is not None
        self.assertTrue(dest.is_file())
        self.assertEqual(dest, unlock_path())
        self.assertEqual(dest.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        gset = [c for c in calls if c[:2] == ["gsettings", "set"]]
        keys = {(c[2], c[3]) for c in gset}
        self.assertIn(("org.gnome.desktop.screensaver", "picture-uri"), keys)
        uri_call = next(
            c
            for c in gset
            if c[2:4] == ["org.gnome.desktop.screensaver", "picture-uri"]
        )
        self.assertTrue(uri_call[4].startswith("file://"))
        self.assertIn("unlock.png", uri_call[4])
        st = status()
        self.assertEqual(st["pack"], "tokyo-night")
        self.assertEqual(st["path"], str(dest))

    def test_set_unlock_by_pack_id(self) -> None:
        from theme.unlock import set_unlock, list_unlock_packs

        packs = list_unlock_packs()
        ids = {p["id"] for p in packs}
        self.assertIn("tokyo-night", ids)
        with mock.patch("theme.unlock._run", return_value=None):
            path = set_unlock("tokyo-night")
        self.assertTrue(path.is_file())

    def test_theme_set_applies_unlock(self) -> None:
        from theme.engine import set_theme
        from theme.unlock import unlock_path

        with mock.patch("theme.emitters._run", return_value=None), mock.patch(
            "theme.unlock._run", return_value=None
        ), mock.patch("theme.icon_apply.apply_pack_icons", return_value={}):
            set_theme("tokyo-night")
        self.assertTrue(unlock_path().is_file())


if __name__ == "__main__":
    unittest.main()
