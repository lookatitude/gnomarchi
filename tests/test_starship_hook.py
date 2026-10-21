"""Pinning tests for G1 starship shell hook + prompt CLI."""

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


class StarshipHookTests(unittest.TestCase):
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

    def test_cli_shell_ensure(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(CLI), "shell", "ensure"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("starship zsh", proc.stdout)
        zshrc = self.home / ".zshrc"
        self.assertTrue(zshrc.is_file())
        self.assertIn("starship init zsh", zshrc.read_text(encoding="utf-8"))

    def test_cli_prompt_status(self) -> None:
        from common.starship_hook import ensure_starship_hook

        ensure_starship_hook(self.home)
        proc = subprocess.run(
            [sys.executable, str(CLI), "prompt", "status"],
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": str(ROOT)},
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        data = json.loads(proc.stdout)
        self.assertTrue(data["zshrc"])
        self.assertTrue(data["bashrc"])


if __name__ == "__main__":
    unittest.main()
