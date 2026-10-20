"""Overlay script syntax, wipe refuse, no Hyprland as required package."""

from __future__ import annotations

import re
import subprocess
import unittest

from acceptance._helpers import OVERLAY, REPO


def _bash_array(text: str, name: str) -> list[str]:
    # Single-line: NAME=(a b) or multiline: NAME=(\n  a\n)
    m = re.search(
        rf"^{re.escape(name)}=\(([^)]*)\)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not m:
        return []
    return re.findall(r"[A-Za-z0-9_./+-]+", m.group(1))


class OverlayAcceptanceTests(unittest.TestCase):
    def test_bash_n(self) -> None:
        self.assertTrue(OVERLAY.is_file(), f"missing {OVERLAY}")
        proc = subprocess.run(
            ["bash", "-n", str(OVERLAY)],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_wipe_and_destroy_exit_nonzero(self) -> None:
        for cmd in ("wipe", "destroy"):
            with self.subTest(cmd=cmd):
                proc = subprocess.run(
                    ["bash", str(OVERLAY), cmd],
                    cwd=REPO,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
                self.assertIn("refus", (proc.stderr + proc.stdout).lower())

    def test_no_hyprland_as_required_package(self) -> None:
        text = OVERLAY.read_text(encoding="utf-8")
        required = _bash_array(text, "GNOME_PKGS") + _bash_array(text, "DEFAULT_APP_PKGS")
        self.assertTrue(required, "expected GNOME_PKGS / DEFAULT_APP_PKGS arrays")
        for pkg in required:
            self.assertNotIn(
                "hyprland",
                pkg.lower(),
                f"Hyprland must not be a required package: {pkg}",
            )
        forbidden = _bash_array(text, "FORBIDDEN_PKGS")
        self.assertTrue(
            any("hyprland" in p.lower() for p in forbidden),
            "FORBIDDEN_PKGS should list hyprland",
        )


if __name__ == "__main__":
    unittest.main()
