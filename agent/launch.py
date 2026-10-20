"""Launch agents in Ghostty (or $TERMINAL) and run unattended prompts."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from agent.catalog import AGENTS
from agent.default_agent import get_default_agent
from agent.mise import ensure_agent, which_agent


def _work_dir() -> Path:
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    work = home / "Work"
    cwd = Path.cwd().resolve()
    if cwd == home.resolve():
        work.mkdir(parents=True, exist_ok=True)
        return work
    return cwd


def _terminal_argv(inner: list[str]) -> list[str]:
    term = (
        os.environ.get("GNOMARCHI_TERMINAL")
        or shutil.which("ghostty")
        or shutil.which("xdg-terminal-exec")
        or shutil.which("gnome-terminal")
        or shutil.which("xterm")
    )
    if not term:
        return inner
    name = Path(term).name
    if name == "ghostty":
        return [term, "-e"] + inner
    if name == "xdg-terminal-exec":
        return [term] + inner
    if name == "gnome-terminal":
        return [term, "--"] + inner
    return [term, "-e"] + inner


def launch_agent(
    agent_id: str | None = None,
    *,
    extra_args: list[str] | None = None,
    unattended: bool = False,
    in_terminal: bool = True,
) -> int:
    aid = agent_id or get_default_agent()
    if not aid:
        raise ValueError("no default agent; run: gnomarchi default agent <id>")
    ensure_agent(aid, install=True)
    spec = AGENTS[aid]
    binary = which_agent(aid) or spec.command
    argv = [binary]
    if unattended and spec.unattended_flags:
        argv.extend(spec.unattended_flags)
    if extra_args:
        argv.extend(extra_args)
    cwd = str(_work_dir())
    env = os.environ.copy()
    graphical = bool(os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY"))
    if in_terminal and graphical:
        full = _terminal_argv(argv)
        subprocess.Popen(full, cwd=cwd, env=env)
        return 0
    return subprocess.call(argv, cwd=cwd, env=env)


def run_prompt(
    prompt: str,
    *,
    agent_id: str | None = None,
    skill: str | None = None,
    unattended: bool = True,
) -> int:
    """Run agent with a prompt (Make something / scripted)."""
    aid = agent_id or get_default_agent()
    if not aid:
        raise ValueError("no default agent; run: gnomarchi default agent <id>")
    ensure_agent(aid, install=True)
    spec = AGENTS[aid]
    binary = which_agent(aid) or spec.command
    text = prompt
    if skill:
        text = f"Use the {skill} skill. {prompt}"
    argv = [binary]
    if unattended and spec.unattended_flags:
        argv.extend(spec.unattended_flags)
    if spec.family == "claude":
        argv.extend(["-p", text])
    elif spec.family == "codex":
        argv.extend(["exec", text])
    else:
        argv.append(text)
    cwd = str(_work_dir())
    return subprocess.call(argv, cwd=cwd, env=os.environ.copy())
