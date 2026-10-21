"""theme bg cycle generates variants without Omarchy binary walls."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock


class TestThemeBg(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        root = Path(self._tmpdir.name)
        home = root / "home"
        home.mkdir()
        self.state = root
        self._env = mock.patch.dict(
            os.environ,
            {
                "GNOMARCHI_STATE_DIR": str(root),
                "HOME": str(home),
            },
        )
        self._env.start()
        self.addCleanup(self._env.stop)

    def test_bg_next_after_theme_set(self) -> None:
        from theme.engine import set_theme
        from theme.backgrounds import next_background, current_index, VARIANT_COUNT

        set_theme("tokyo-night")
        self.assertEqual((self.state / "active-theme").read_text().strip(), "tokyo-night")
        p1 = next_background()
        self.assertTrue(p1.is_file())
        b1 = p1.read_bytes()
        idx1 = current_index()
        self.assertGreaterEqual(idx1, 0)
        self.assertLess(idx1, VARIANT_COUNT)
        p2 = next_background()
        self.assertTrue(p2.is_file())
        b2 = p2.read_bytes()
        self.assertEqual(current_index(), (idx1 + 1) % VARIANT_COUNT)
        self.assertNotEqual(b1, b2)


if __name__ == "__main__":
    unittest.main()
