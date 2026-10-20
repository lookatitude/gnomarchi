"""Theme validate/set smoke via bin/gnomarchi."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from acceptance._helpers import CLI, REPO


class ThemeCliAcceptanceTests(unittest.TestCase):
    def test_theme_validate_seed(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CLI), "theme", "validate", "--id", "midnight-harbor"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("ok:", proc.stdout)

    def test_theme_set_smoke(self) -> None:
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
