"""Ensure mise-managed agent CLIs exist (lazy install on first use)."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from agent.catalog import AGENTS, AgentSpec
from common.paths import state_dir


def _mise_bin() -> str | None:
    return shutil.which("mise")


def mise_config_path() -> Path:
    return Path(os.environ.get("HOME", "/tmp")).expanduser() / ".config" / "mise" / "config.toml"


def write_mise_agent_tools(agents: list[str] | None = None) -> Path:
    """Seed mise config from Omarchy-adapted gnomarchi-tools.toml (+ wrappers)."""
    from common.paths import REPO_ROOT

    ids = agents or [a.id for a in AGENTS.values() if a.mise_tool]
    path = mise_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conf_d = path.parent / "conf.d"
    conf_d.mkdir(parents=True, exist_ok=True)
    upstream = REPO_ROOT / "config" / "mise" / "gnomarchi-tools.toml"
    if upstream.is_file():
        dest = conf_d / "gnomarchi-tools.toml"
        dest.write_text(upstream.read_text(encoding="utf-8"), encoding="utf-8")
    existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    marker = "# gnomarchi agents"
    block_lines = [marker, "[tools]"]
    for aid in ids:
        spec = AGENTS.get(aid)
        if not spec or not spec.mise_tool:
            continue
        # Prefer Omarchy-style lazy + auto_update when writing fallback block
        block_lines.append(
            f'{spec.mise_tool} = {{ version = "latest", lazy = true, auto_update = "4h" }}'
        )
    block = "\n".join(block_lines) + "\n"
    if marker in existing:
        head, _, _ = existing.partition(marker)
        path.write_text(head.rstrip() + "\n\n" + block, encoding="utf-8")
    elif not (conf_d / "gnomarchi-tools.toml").is_file():
        path.write_text(
            (existing.rstrip() + "\n\n" if existing.strip() else "") + block,
            encoding="utf-8",
        )
    elif marker not in existing:
        # Point at conf.d; keep a short include note
        note = f"{marker}\n# tools also in conf.d/gnomarchi-tools.toml (Omarchy-adapted)\n"
        path.write_text(
            (existing.rstrip() + "\n\n" if existing.strip() else "") + note,
            encoding="utf-8",
        )
    _write_local_wrappers(ids)
    return path



def _write_local_wrappers(ids: list[str]) -> None:
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    bindir = home / ".local" / "bin"
    bindir.mkdir(parents=True, exist_ok=True)
    for aid in ids:
        spec = AGENTS.get(aid)
        if not spec or not spec.mise_tool:
            continue
        wrapper = bindir / spec.command
        if wrapper.is_file() and "gnomarchi mise wrapper" not in wrapper.read_text(
            encoding="utf-8", errors="ignore"
        ):
            continue
        wrapper.write_text(
            f"""#!/usr/bin/env bash
# gnomarchi mise wrapper — lazy-install {spec.mise_tool} on first use
set -euo pipefail
if command -v mise >/dev/null 2>&1; then
  exec mise exec -- {spec.command} "$@"
fi
if command -v {spec.command} >/dev/null 2>&1 && [[ "$(command -v {spec.command})" != "$0" ]]; then
  exec "$(command -v {spec.command})" "$@"
fi
echo "gnomarchi: install mise (https://mise.jdx.dev) then re-run: {spec.command}" >&2
exit 127
""",
            encoding="utf-8",
        )
        wrapper.chmod(0o755)


def ensure_agent(agent_id: str, *, install: bool = True) -> AgentSpec:
    """Resolve agent spec; optionally trigger mise install for its tool."""
    spec = AGENTS.get(agent_id)
    if spec is None:
        raise ValueError(f"unknown agent: {agent_id}")
    if not install:
        return spec
    if spec.mise_tool is None:
        # Hermes: ensure desktop/runtime path note.
        stamp = state_dir() / "agent" / "hermes-invite"
        stamp.parent.mkdir(parents=True, exist_ok=True)
        if not stamp.is_file():
            stamp.write_text(
                "Install Hermes Desktop via: gnomarchi menu → Install → AI → Hermes\n",
                encoding="utf-8",
            )
        return spec
    write_mise_agent_tools()
    mise = _mise_bin()
    if mise and install:
        subprocess.run(
            [mise, "install", spec.mise_tool],
            check=False,
            capture_output=True,
            text=True,
            timeout=600,
        )
    return spec


def which_agent(agent_id: str) -> str | None:
    spec = AGENTS.get(agent_id)
    if not spec:
        return None
    path = shutil.which(spec.command)
    if path:
        return path
    mise = _mise_bin()
    if mise and spec.mise_tool:
        try:
            out = subprocess.run(
                [mise, "which", spec.command],
                check=False,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if out.returncode == 0 and out.stdout.strip():
                return out.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
    return None
