"""Aggregate agent usage meters (Claude / Codex / Grok style caches)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from agent.catalog import AGENTS
from agent.state import read_json, usage_path, write_json


def _read_claude_usage() -> dict[str, Any] | None:
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    # Claude Code stores usage in various places; probe known files.
    candidates = [
        home / ".claude" / "stats-cache.json",
        home / ".claude" / "usage.json",
        home / ".config" / "claude" / "usage.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return {"source": str(path), "raw": data}
            except json.JSONDecodeError:
                continue
    return None


def _read_codex_usage() -> dict[str, Any] | None:
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    candidates = [
        home / ".codex" / "usage.json",
        home / ".codex" / "stats.json",
    ]
    for path in candidates:
        if path.is_file():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                return {"source": str(path), "raw": data}
            except json.JSONDecodeError:
                continue
    return None


def _normalize(provider: str, blob: dict[str, Any] | None) -> dict[str, Any]:
    if blob is None:
        return {
            "provider": provider,
            "available": False,
            "session_pct": None,
            "weekly_pct": None,
            "message": "sign in / run agent once to populate usage",
        }
    raw = blob.get("raw") if isinstance(blob.get("raw"), dict) else blob
    session = raw.get("session_pct") or raw.get("five_hour_pct") or raw.get("session")
    weekly = raw.get("weekly_pct") or raw.get("week_pct") or raw.get("weekly")
    return {
        "provider": provider,
        "available": True,
        "session_pct": session,
        "weekly_pct": weekly,
        "source": blob.get("source"),
        "raw": raw,
    }


def update_usage() -> dict[str, Any]:
    """Refresh usage cache from local harness files (every ~15m via timer)."""
    providers: dict[str, Any] = {}
    if "claude" in AGENTS:
        providers["claude"] = _normalize("claude", _read_claude_usage())
    if "codex" in AGENTS:
        providers["codex"] = _normalize("codex", _read_codex_usage())
    if "grok" in AGENTS:
        providers["grok"] = _normalize("grok", None)
    payload = {
        "updated_at": int(time.time()),
        "providers": providers,
    }
    write_json(usage_path(), payload)
    return payload


def read_usage() -> dict[str, Any]:
    data = read_json(usage_path(), {})
    if not data:
        return update_usage()
    return data
