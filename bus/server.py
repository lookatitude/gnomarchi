"""Session bus: Unix socket with summon / theme / agents methods."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

from common.paths import REPO_ROOT, state_dir


def socket_path() -> Path:
    override = os.environ.get("GNOMARCHI_BUS_SOCK")
    if override:
        return Path(override)
    return state_dir() / "bus.sock"


def _spawn(argv: list[str]) -> dict[str, Any]:
    try:
        subprocess.Popen(argv, start_new_session=True)
        return {"ok": True, "result": {"spawned": argv}}
    except OSError as exc:
        return {"ok": False, "error": str(exc)}


def handle(line: str) -> dict:
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid json"}
    method = msg.get("method")
    params = msg.get("params") or {}
    cli = str(REPO_ROOT / "bin" / "gnomarchi")
    if method == "Ping":
        return {"ok": True, "result": "pong"}
    if method in ("SummonMenu", "Menu.Open"):
        return _spawn([sys.executable, cli, "menu", "open"])
    if method in ("Agents.Open", "SummonAgents"):
        return _spawn([sys.executable, cli, "agent", "window"])
    if method == "Agent.Launch":
        aid = params.get("id")
        argv = [sys.executable, cli, "agent", "launch"]
        if aid:
            argv.append(str(aid))
        return _spawn(argv)
    if method == "Theme.Changed" or method == "ThemeApplied":
        # Broadcast file for indicators to watch
        stamp = state_dir() / "theme-changed.json"
        stamp.write_text(json.dumps(params) + "\n", encoding="utf-8")
        return {"ok": True, "result": params}
    if method == "MakeSomething":
        kind = params.get("kind", "theme")
        return _spawn([sys.executable, cli, "agent", "make-something", str(kind)])
    return {"ok": False, "error": f"unknown method: {method}"}


def serve_forever() -> None:
    path = socket_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    sock.listen(16)
    print(f"gnomarchi-bus listening on {path}", flush=True)
    try:
        while True:
            conn, _ = sock.accept()
            with conn:
                data = conn.recv(65536).decode("utf-8")
                for line in data.splitlines():
                    if not line.strip():
                        continue
                    resp = handle(line.strip())
                    conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
    finally:
        sock.close()
        if path.exists():
            path.unlink()


def serve_once() -> None:
    path = socket_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    sock.listen(1)
    print(f"gnomarchi-bus once on {path}", flush=True)
    conn, _ = sock.accept()
    with conn:
        data = conn.recv(65536).decode("utf-8")
        resp = handle(data.strip())
        conn.sendall((json.dumps(resp) + "\n").encode("utf-8"))
    sock.close()
    if path.exists():
        path.unlink()


if __name__ == "__main__":
    if "--once" in sys.argv:
        serve_once()
    else:
        serve_forever()
