"""Agent core unit tests (no network / no real mise install)."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


class AgentCoreTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.state = Path(self._tmp.name)
        os.environ["GNOMARCHI_STATE_DIR"] = str(self.state)
        os.environ["HOME"] = str(self.state / "home")
        (self.state / "home").mkdir()

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_default_agent_roundtrip(self) -> None:
        from agent.default_agent import get_default_agent, set_default_agent

        self.assertIsNone(get_default_agent())
        set_default_agent("claude", install=False)
        self.assertEqual(get_default_agent(), "claude")

    def test_usage_update_writes_cache(self) -> None:
        from agent.usage import read_usage, update_usage

        data = update_usage()
        self.assertIn("providers", data)
        self.assertTrue((self.state / "agent" / "usage.json").is_file())
        again = read_usage()
        self.assertEqual(again["providers"].keys(), data["providers"].keys())

    def test_make_starters_listed(self) -> None:
        from agent.make import list_starters

        ids = {s["id"] for s in list_starters()}
        self.assertTrue({"theme", "plugin", "app", "menu"} <= ids)

    def test_accounts_add_list(self) -> None:
        from agent.accounts import add_account, list_accounts

        aid = add_account("claude", "work")
        self.assertEqual(aid, "claude:work")
        rows = list_accounts("claude")
        self.assertEqual(len(rows), 1)

    def test_skills_install(self) -> None:
        from agent.skills import install_skills

        linked = install_skills()
        self.assertGreaterEqual(len(linked), 1)

    def test_plugin_status_indicator_scaffold(self) -> None:
        from plugin.lifecycle import scaffold_plugin, validate_plugin

        target = scaffold_plugin(
            "ind-smoke", runtime="status-indicator", dest_root=self.state / "plugins"
        )
        self.assertEqual(validate_plugin(target), [])

    def test_clone_first_party_agents(self) -> None:
        from plugin.lifecycle import clone_plugin, validate_plugin

        target = clone_plugin("gnomarchi.agents", dest_root=self.state / "plugins")
        self.assertEqual(validate_plugin(target), [])

    def test_shell_config_loads(self) -> None:
        from common.shell_config import ensure_user_shell_toml, load_shell_config

        ensure_user_shell_toml()
        cfg = load_shell_config()
        self.assertIn("panel", cfg)


if __name__ == "__main__":
    unittest.main()
