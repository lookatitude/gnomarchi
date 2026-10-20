"""Client for the Unix-socket bus stub."""

from __future__ import annotations

import json
import socket
from typing import Any

from bus.server import socket_path


def call(method: str, params: dict[str, Any] | None = None, timeout: float = 2.0) -> dict:
    payload = {"method": method, "params": params or {}}
    path = socket_path()
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    sock.connect(str(path))
    sock.sendall((json.dumps(payload) + "\n").encode("utf-8"))
    data = sock.recv(65536).decode("utf-8")
    sock.close()
    return json.loads(data)
