"""Omarchy-parity coding agent catalogue (mise-lazy launchers)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentSpec:
    id: str
    command: str
    label: str
    mise_tool: str | None
    """mise package id, or None if installed another way (e.g. hermes desktop)."""
    family: str
    supports_usage: bool = True
    unattended_flags: tuple[str, ...] = ()
    theme_paths: tuple[str, ...] = ()


AGENTS: dict[str, AgentSpec] = {
    "claude": AgentSpec(
        id="claude",
        command="claude",
        label="Claude Code",
        mise_tool="claude",
        family="claude",
        unattended_flags=("--dangerously-skip-permissions",),
        theme_paths=("~/.claude/settings.json",),
    ),
    "codex": AgentSpec(
        id="codex",
        command="codex",
        label="OpenAI Codex",
        mise_tool="codex",
        family="codex",
        unattended_flags=("--full-auto",),
        theme_paths=("~/.codex/config.toml",),
    ),
    "opencode": AgentSpec(
        id="opencode",
        command="opencode",
        label="OpenCode",
        mise_tool="opencode",
        family="opencode",
        theme_paths=("~/.config/opencode/config.json",),
    ),
    "agy": AgentSpec(
        id="agy",
        command="agy",
        label="Google Antigravity CLI",
        mise_tool="agy",
        family="agy",
        supports_usage=False,
    ),
    "copilot": AgentSpec(
        id="copilot",
        command="copilot",
        label="GitHub Copilot CLI",
        mise_tool="copilot",
        family="copilot",
        supports_usage=False,
    ),
    "crush": AgentSpec(
        id="crush",
        command="crush",
        label="Crush",
        mise_tool="crush",
        family="crush",
        supports_usage=False,
    ),
    "grok": AgentSpec(
        id="grok",
        command="grok",
        label="Grok Build",
        mise_tool="grok",
        family="grok",
    ),
    "kimi": AgentSpec(
        id="kimi",
        command="kimi",
        label="Kimi Code",
        mise_tool="kimi",
        family="kimi",
    ),
    "pi": AgentSpec(
        id="pi",
        command="pi",
        label="Pi",
        mise_tool="pi",
        family="pi",
        theme_paths=("~/.pi/agent/settings.json",),
    ),
    "omp": AgentSpec(
        id="omp",
        command="omp",
        label="Oh My Pi",
        mise_tool="omp",
        family="pi",
        supports_usage=False,
    ),
    "ori": AgentSpec(
        id="ori",
        command="ori",
        label="Ori (OpenRouter)",
        mise_tool="ori",
        family="ori",
        supports_usage=False,
    ),
    "hermes": AgentSpec(
        id="hermes",
        command="hermes",
        label="Hermes",
        mise_tool=None,
        family="hermes",
        theme_paths=("~/.hermes/skins/gnomarchi.json",),
    ),
    "muse": AgentSpec(
        id="muse",
        command="muse",
        label="Muse Code",
        mise_tool="muse",
        family="muse",
        supports_usage=False,
    ),
    "cursor-agent": AgentSpec(
        id="cursor-agent",
        command="cursor-agent",
        label="Cursor CLI",
        mise_tool="cursor-agent",
        family="cursor",
        supports_usage=False,
    ),
}

# Terminal aliases matching Omarchy muscle memory.
ALIASES = {
    "a": "default",
    "cy": "claude",
    "cx": "codex",
    "c": "opencode",
}
