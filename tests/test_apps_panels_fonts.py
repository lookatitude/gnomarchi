"""Pinning tests for gnoma apps, panels, fonts, menu Style/Install font branches."""

from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "bin" / "gnomarchi"
MENU = REPO / "menu" / "default.jsonc"
REGISTRY = REPO / "features" / "registry.yaml"


def _load_jsonc(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    stripped = re.sub(r"^\s*//.*?$", "", text, flags=re.MULTILINE)
    return json.loads(stripped)


def _leaf_ids(node: dict, acc: list[str] | None = None) -> list[str]:
    acc = acc if acc is not None else []
    if "id" in node:
        acc.append(str(node["id"]))
    for child in node.get("children") or []:
        _leaf_ids(child, acc)
    return acc


class AppsPanelsFontsTests(unittest.TestCase):
    def test_app_scripts_exist(self) -> None:
        for name in ("gnoma-write", "gnoma-cut", "gnoma-calc"):
            p = REPO / "apps" / name / "main.py"
            self.assertTrue(p.is_file(), f"missing {p}")
            self.assertIn("Adw", p.read_text(encoding="utf-8"))

    def test_desktop_files(self) -> None:
        for name in ("Write", "Cut", "Calc"):
            p = REPO / "applications" / f"org.gnomarchi.{name}.desktop"
            self.assertTrue(p.is_file(), f"missing {p}")
            body = p.read_text(encoding="utf-8")
            self.assertIn("Exec=gnomarchi app", body)
            self.assertNotIn("Omarchy", body)
            self.assertNotIn("omarchy", body.lower())

    def test_calc_cli(self) -> None:
        proc = subprocess.run(
            ["/usr/bin/python3", str(REPO / "apps" / "gnoma-calc" / "main.py"), "2+3*4"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), "14")

    def test_cut_cli_crop(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "in.png"
            dest = Path(td) / "out.png"
            make = subprocess.run(
                [
                    "/usr/bin/python3",
                    "-c",
                    "from PIL import Image; Image.new('RGB',(40,20),(10,20,30)).save(%r)"
                    % str(src),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(make.returncode, 0, make.stderr)
            proc = subprocess.run(
                [
                    "/usr/bin/python3",
                    str(REPO / "apps" / "gnoma-cut" / "main.py"),
                    str(src),
                    "--left",
                    "5",
                    "--top",
                    "2",
                    "--right",
                    "25",
                    "--bottom",
                    "18",
                    "-o",
                    str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertTrue(dest.is_file())
            size = subprocess.run(
                [
                    "/usr/bin/python3",
                    "-c",
                    "from PIL import Image; print(Image.open(%r).size)" % str(dest),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(size.stdout.strip(), "(20, 16)", size.stderr)

    def test_font_list_cli(self) -> None:
        proc = subprocess.run(
            ["python3", str(CLI), "font", "list"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(REPO),
            env={**dict(**__import__("os").environ), "PYTHONPATH": str(REPO)},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("cascadia", proc.stdout)
        self.assertIn("jetbrains", proc.stdout)

    def test_panel_unknown(self) -> None:
        proc = subprocess.run(
            ["python3", str(CLI), "panel", "nope"],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(REPO),
            env={**dict(**__import__("os").environ), "PYTHONPATH": str(REPO)},
        )
        self.assertNotEqual(proc.returncode, 0)

    def test_menu_style_and_install_fonts(self) -> None:
        data = _load_jsonc(MENU)
        ids = []
        for e in data["entries"]:
            _leaf_ids(e, ids)
        for required in (
            "style.font",
            "style.font.cascadia",
            "install.style",
            "install.style.font.fira",
            "install.gaming",
        ):
            self.assertIn(required, ids, f"missing menu id {required}")

    def test_registry_done(self) -> None:
        text = REGISTRY.read_text(encoding="utf-8")
        self.assertRegex(
            text,
            r"id:\s*omarchy\.shell\.panels\n(?:.*\n)*?\s+status:\s*done",
        )
        self.assertRegex(
            text,
            r"id:\s*omarchy\.apps\.oma-\*\n(?:.*\n)*?\s+status:\s*done",
        )


if __name__ == "__main__":
    unittest.main()
