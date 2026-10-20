"""menu/default.jsonc must expose Install / Setup / Style / Trigger."""

from __future__ import annotations

import json
import re
import unittest

from acceptance._helpers import MENU_DEFAULT


def _load_jsonc(path) -> dict:
    text = path.read_text(encoding="utf-8")
    # Strip // line comments (menu JSONC only uses that form).
    stripped = re.sub(r"^\s*//.*?$", "", text, flags=re.MULTILINE)
    return json.loads(stripped)


class MenuAcceptanceTests(unittest.TestCase):
    def test_default_menu_has_core_sections(self) -> None:
        self.assertTrue(MENU_DEFAULT.is_file(), f"missing {MENU_DEFAULT}")
        data = _load_jsonc(MENU_DEFAULT)
        labels = {e.get("label") for e in data.get("entries", [])}
        for required in ("Install", "Setup", "Style", "Trigger"):
            self.assertIn(required, labels, f"missing menu section: {required}")


if __name__ == "__main__":
    unittest.main()
