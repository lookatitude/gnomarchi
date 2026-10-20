"""Default agent selection."""

from __future__ import annotations

from agent.catalog import AGENTS
from agent.mise import ensure_agent
from agent.state import default_agent_path


def get_default_agent() -> str | None:
    path = default_agent_path()
    if not path.is_file():
        return None
    value = path.read_text(encoding="utf-8").strip()
    return value if value in AGENTS else None


def set_default_agent(agent_id: str, *, install: bool = True) -> str:
    if agent_id not in AGENTS:
        raise ValueError(
            f"unknown agent {agent_id!r}; known: {', '.join(sorted(AGENTS))}"
        )
    ensure_agent(agent_id, install=install)
    path = default_agent_path()
    path.write_text(agent_id + "\n", encoding="utf-8")
    return agent_id
