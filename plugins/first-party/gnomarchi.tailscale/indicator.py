#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

for candidate in (Path(os.environ.get("GNOMARCHI_ROOT", "")), Path("/usr/local/lib/gnomarchi"), Path(__file__).resolve().parents[3]):
    if candidate and (candidate / "agent").is_dir():
        sys.path.insert(0, str(candidate))
        break


def status() -> str:
    ts = shutil.which("tailscale")
    if not ts:
        return "tailscale not installed"
    try:
        out = subprocess.run(
            [ts, "status", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
        if out.returncode != 0:
            return out.stderr.strip() or "tailscale error"
        import json

        data = json.loads(out.stdout)
        backend = data.get("BackendState", "unknown")
        self_name = (data.get("Self") or {}).get("HostName", "")
        return f"{backend} {self_name}".strip()
    except Exception as exc:
        return str(exc)


def show() -> None:
    subprocess.run(["notify-send", "Tailscale", status()], check=False)


def toggle() -> None:
    ts = shutil.which("tailscale")
    if not ts:
        return
    st = status()
    if "Running" in st:
        subprocess.run([ts, "down"], check=False)
    else:
        subprocess.run([ts, "up"], check=False)


def main() -> int:
    from agent.indicator_runtime import run_indicator

    return run_indicator(
        id="gnomarchi.tailscale",
        title="Tailscale",
        icon="network-vpn-symbolic",
        on_activate=show,
        on_secondary=toggle,
    )


if __name__ == "__main__":
    raise SystemExit(main())
