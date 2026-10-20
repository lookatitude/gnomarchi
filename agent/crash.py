"""Crash capture: watch coredumps and hand off to default agent + diagnose skill."""

from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path

from agent.default_agent import get_default_agent
from agent.launch import run_prompt
from agent.state import agent_dir, read_json, write_json
from common.paths import state_dir


def mute_path() -> Path:
    return agent_dir() / "crash-mute.json"


def muted() -> set[str]:
    data = read_json(mute_path(), {"muted": []})
    return set(data.get("muted") or [])


def mute(name: str, *, off: bool = False) -> list[str]:
    items = muted()
    key = name.strip()
    if off:
        items.discard(key)
    else:
        items.add(key)
    write_json(mute_path(), {"muted": sorted(items)})
    return sorted(items)


def list_coredumps(limit: int = 20) -> list[dict[str, str]]:
    try:
        out = subprocess.run(
            ["coredumpctl", "list", "--no-pager", "-q"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    rows: list[dict[str, str]] = []
    for line in out.stdout.splitlines()[-limit:]:
        parts = line.split()
        if len(parts) >= 5:
            rows.append({"raw": line, "pid": parts[4] if parts[4].isdigit() else parts[-1]})
    return rows


def diagnose(pid: str | None = None) -> int:
    if not get_default_agent():
        raise ValueError("no default agent set")
    target = pid or (list_coredumps(1)[-1]["pid"] if list_coredumps(1) else None)
    if not target:
        raise ValueError("no coredump found; pass a PID from coredumpctl list")
    prompt = (
        f"Diagnose crash for PID {target} using coredumpctl. "
        "Establish facts, decide if worth upstream report, offer mute."
    )
    return run_prompt(prompt, skill="gnomarchi-diagnose-crash", unattended=True)


def notify_crash(exe: str, pid: str) -> None:
    if exe in muted() or Path(exe).name in muted():
        return
    stamp = state_dir() / "agent" / "last-crash-notify"
    stamp.parent.mkdir(parents=True, exist_ok=True)
    payload = {"exe": exe, "pid": pid, "ts": int(time.time())}
    stamp.write_text(json.dumps(payload), encoding="utf-8")
    try:
        subprocess.run(
            [
                "notify-send",
                "--action=diagnose=Diagnose",
                "Process crashed",
                f"{exe} (pid {pid}) — click to diagnose with gnomarchi agent",
            ],
            check=False,
            capture_output=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass


def watch_once() -> int:
    """Scan recent coredumps and notify for new ones."""
    seen_path = agent_dir() / "crash-seen.json"
    seen = set(read_json(seen_path, {"seen": []}).get("seen") or [])
    new_seen = set(seen)
    for row in list_coredumps(10):
        key = row.get("raw") or row.get("pid")
        if not key or key in seen:
            continue
        new_seen.add(key)
        notify_crash(row.get("raw", "unknown").split()[-1] if row.get("raw") else "unknown", row.get("pid", "?"))
    write_json(seen_path, {"seen": sorted(new_seen)[-200:]})
    return 0
