"""Agent state paths under gnomarchi config."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from common.paths import state_dir


def agent_dir() -> Path:
    d = state_dir() / "agent"
    d.mkdir(parents=True, exist_ok=True)
    return d


def default_agent_path() -> Path:
    return agent_dir() / "default"


def usage_path() -> Path:
    return agent_dir() / "usage.json"


def accounts_path() -> Path:
    return agent_dir() / "accounts.json"


def read_json(path: Path, default: Any) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return default


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
