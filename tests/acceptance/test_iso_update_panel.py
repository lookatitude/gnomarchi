"""ISO profile, update=Syu, panel/tiling/gaming menu, registry done marks."""

from __future__ import annotations

import json
import re
import subprocess
import unittest

from acceptance._helpers import CLI, MENU_DEFAULT, OVERLAY, REPO, REGISTRY


def _load_jsonc(path) -> dict:
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"^\s*//.*?$", "", text, flags=re.MULTILINE)
    return json.loads(stripped)


def _registry_status(fid: str) -> str | None:
    text = REGISTRY.read_text(encoding="utf-8")
    rows = re.split(r"\n  - id:", text)
    for chunk in rows[1:]:
        first = chunk.splitlines()[0].strip().strip("\"'")
        if first != fid:
            continue
        m = re.search(r"^    status:\s*(\S+)", chunk, re.MULTILINE)
        return m.group(1) if m else None
    return None


class IsoUpdatePanelAcceptance(unittest.TestCase):
    def test_iso_build_artifacts(self) -> None:
        self.assertTrue((REPO / "iso" / "README.md").is_file())
        self.assertTrue((REPO / "iso" / "build.sh").is_file())
        self.assertTrue((REPO / "iso" / "packages.x86_64").is_file())
        build = (REPO / "iso" / "build.sh").read_text(encoding="utf-8")
        self.assertIn("overlay.sh", build)
        self.assertIn("mkarchiso", build)

    def test_update_is_pacman_syu(self) -> None:
        src = (REPO / "common" / "arch_update.py").read_text(encoding="utf-8")
        self.assertIn('"-Syu"', src)
        self.assertNotIn("[gnomarchi]", src)
        proc = subprocess.run(
            [str(CLI), "update", "--help"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("pacman", (proc.stdout + proc.stderr).lower())

    def test_menu_install_panel_tiling_gaming_vm(self) -> None:
        data = _load_jsonc(MENU_DEFAULT)
        blob = json.dumps(data)
        for needle in (
            "install.desktop.panel",
            "install.dev.paperwm",
            "install.gaming",
            "install.windows-vm",
            "setup.bar",
            "bar-position",
        ):
            self.assertIn(needle, blob, f"missing menu id/ref: {needle}")

    def test_overlay_panel_plymouth_stages(self) -> None:
        text = OVERLAY.read_text(encoding="utf-8")
        self.assertIn("stage_panel", text)
        self.assertIn("stage_plymouth", text)
        self.assertIn("dash-to-panel", text)
        self.assertIn("caffeine", text)
        self.assertIn("PaperWM", text)
        proc = subprocess.run(
            ["bash", "-n", str(OVERLAY)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_plymouth_theme_has_logo(self) -> None:
        theme = REPO / "plymouth" / "gnomarchi"
        self.assertTrue((theme / "gnomarchi.plymouth").is_file())
        self.assertTrue((theme / "gnomarchi.script").is_file())
        self.assertTrue((theme / "logo.png").is_file())
        brand = REPO / "assets" / "brand" / "logo.png"
        self.assertTrue(brand.is_file())

    def test_registry_targets_done(self) -> None:
        for fid in (
            "omarchy.install.iso",
            "omarchy.update.alpm",
            "omarchy.shell.bar-drag",
            "omarchy.wm.tiling-layouts",
            "omarchy.theme.unlock-art",
            "omarchy.gaming.windows-vm",
        ):
            self.assertEqual(_registry_status(fid), "done", fid)

    def test_shell_bar_position_cli(self) -> None:
        proc = subprocess.run(
            [str(CLI), "shell", "bar-position", "--help"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
