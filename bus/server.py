"""Minimal Unix-socket bus stub for local smoke (D-Bus later)."""

from __future__ import annotations

import json
import os
import socket
import sys
from pathlib import Path

from common.paths import state_dir


def socket_path() -> Path:
    override = os.environ.get("GNOMARCHI_BUS_SOCK")
    if override:
        return Path(override)
    return state_dir() / "bus.sock"


def handle(line: str) -> dict:
    try:
        msg = json.loads(line)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid json"}
    method = msg.get("method")
    if method == "Ping":
        return {"ok": True, "result": "pong"}
    if method == "SummonMenu":
        return {"ok": True, "result": "menu-summon-stub"}
    if method == "ThemeApplied":
        return {"ok": True, "result": msg.get("params", {})}
    return {"ok": False, "error": f"unknown method: {method}"}


def serve_once() -> None:
    path = socket_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.unlink()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(str(path))
    sock.listen(1)
    print(f"gnomarchi-bus stub listening on {path}", flush=True)
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
        print("usage: python -m bus.server --once", file=sys.stderr)
        sys.exit(2)
