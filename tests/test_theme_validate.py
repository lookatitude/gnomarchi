"""Smoke tests for theme pack validation and set."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CLI = REPO / "bin" / "gnomarchi"
SEED = REPO / "theme" / "packs" / "midnight-harbor"


class ThemeValidateTests(unittest.TestCase):
    def test_seed_pack_validates(self) -> None:
        sys.path.insert(0, str(REPO))
        from theme.engine import validate_theme

        self.assertEqual(validate_theme(SEED), [])

    def test_missing_theme_toml_fails(self) -> None:
        sys.path.insert(0, str(REPO))
        from theme.engine import validate_theme

        with tempfile.TemporaryDirectory() as tmp:
            errors = validate_theme(tmp)
        self.assertTrue(any("missing theme.toml" in e for e in errors))

    def test_cli_theme_validate_seed(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CLI), "theme", "validate", "--id", "midnight-harbor"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok:", proc.stdout)

    def test_cli_theme_set_writes_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = {**os.environ, "GNOMARCHI_STATE_DIR": tmp}
            proc = subprocess.run(
                [sys.executable, str(CLI), "theme", "set", "midnight-harbor"],
                cwd=REPO,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            active = Path(tmp) / "active-theme"
            self.assertTrue(active.is_file())
            self.assertEqual(active.read_text(encoding="utf-8").strip(), "midnight-harbor")


if __name__ == "__main__":
    unittest.main()

    def test_accent_gsettings_name_nearest(self) -> None:
        sys.path.insert(0, str(REPO))
        from theme.emitters import accent_gsettings_name

        self.assertEqual(accent_gsettings_name("#7aa2f7"), "blue")
        self.assertEqual(accent_gsettings_name("#9ece6a"), "green")
        self.assertEqual(accent_gsettings_name("#f7768e"), "red")
