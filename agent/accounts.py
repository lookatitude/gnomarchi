"""Multi-account switching for Claude / Codex / Grok families."""

from __future__ import annotations

import os
import shutil
import time
from pathlib import Path
from typing import Any

from agent.catalog import AGENTS
from agent.state import accounts_path, read_json, write_json

FAMILY_HOMES = {
    "claude": ("CLAUDE_CONFIG_DIR", Path.home() / ".claude"),
    "codex": ("CODEX_HOME", Path.home() / ".codex"),
    "grok": ("GROK_HOME", Path.home() / ".grok"),
}


def _store() -> dict[str, Any]:
    data = read_json(accounts_path(), None)
    if not isinstance(data, dict):
        data = {"accounts": {}, "active": {}, "autoswitch": {"enabled": False, "threshold": 95}}
        write_json(accounts_path(), data)
    data.setdefault("accounts", {})
    data.setdefault("active", {})
    data.setdefault("autoswitch", {"enabled": False, "threshold": 95})
    return data


def list_accounts(provider: str | None = None) -> list[dict[str, Any]]:
    store = _store()
    rows: list[dict[str, Any]] = []
    for key, meta in store["accounts"].items():
        if provider and meta.get("provider") != provider:
            continue
        rows.append({"id": key, **meta, "active": store["active"].get(meta.get("provider")) == key})
    return rows


def add_account(provider: str, name: str) -> str:
    if provider not in ("claude", "codex", "grok"):
        raise ValueError("accounts supported for: claude, codex, grok")
    if provider not in AGENTS:
        raise ValueError(f"unknown provider: {provider}")
    store = _store()
    aid = f"{provider}:{name}"
    if aid in store["accounts"]:
        raise FileExistsError(f"account exists: {aid}")
    # Snapshot current harness home into account slot.
    env_key, default_home = FAMILY_HOMES[provider]
    src = Path(os.environ.get(env_key, default_home)).expanduser()
    dest = Path.home() / ".config" / "gnomarchi" / "agent" / "accounts" / provider / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir() and not dest.exists():
        shutil.copytree(src, dest, dirs_exist_ok=True)
    else:
        dest.mkdir(parents=True, exist_ok=True)
    store["accounts"][aid] = {
        "provider": provider,
        "name": name,
        "path": str(dest),
        "created_at": int(time.time()),
    }
    if provider not in store["active"]:
        store["active"][provider] = aid
    write_json(accounts_path(), store)
    return aid


def use_account(account_id: str) -> str:
    store = _store()
    meta = store["accounts"].get(account_id)
    if not meta:
        # Allow shorthand: "work" means active provider's account named work
        matches = [k for k, v in store["accounts"].items() if v.get("name") == account_id]
        if len(matches) == 1:
            account_id = matches[0]
            meta = store["accounts"][account_id]
        else:
            raise KeyError(f"unknown account: {account_id}")
    provider = meta["provider"]
    env_key, default_home = FAMILY_HOMES[provider]
    dest = Path(meta["path"])
    live = Path(os.environ.get(env_key, default_home)).expanduser()
    if live.exists() or live.is_symlink():
        backup = live.with_name(live.name + ".gnomarchi-bak")
        if not backup.exists():
            try:
                live.rename(backup)
            except OSError:
                pass
    if live.exists():
        shutil.rmtree(live)
    if dest.is_dir():
        shutil.copytree(dest, live, dirs_exist_ok=True)
    store["active"][provider] = account_id
    write_json(accounts_path(), store)
    return account_id


def remove_account(account_id: str) -> None:
    store = _store()
    meta = store["accounts"].pop(account_id, None)
    if meta is None:
        raise KeyError(f"unknown account: {account_id}")
    provider = meta["provider"]
    if store["active"].get(provider) == account_id:
        store["active"].pop(provider, None)
    write_json(accounts_path(), store)


def set_autoswitch(enabled: bool, threshold: int = 95) -> dict[str, Any]:
    store = _store()
    store["autoswitch"] = {"enabled": enabled, "threshold": int(threshold)}
    write_json(accounts_path(), store)
    return store["autoswitch"]
