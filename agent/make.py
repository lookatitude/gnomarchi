"""Make something starters — theme / plugin / app / menu."""

from __future__ import annotations

from agent.launch import run_prompt

STARTERS = {
    "theme": (
        "gnomarchi-theme",
        "Create a new gnomarchi theme pack under ~/.config/gnomarchi/themes/. "
        "Follow the gnomarchi-theme skill: colors.toml, validate, theme set. "
        "Do not claim official Omarchy affiliation.",
    ),
    "plugin": (
        "gnomarchi-plugin",
        "Scaffold and enable a gnomarchi plugin. Prefer overlay-app + menu-module "
        "or status-indicator. Follow the gnomarchi-plugin skill; validate before enable.",
    ),
    "app": (
        "gnomarchi-app",
        "Scaffold a GTK4/libadwaita desktop app that watches gnomarchi theme state. "
        "Follow the gnomarchi-app skill.",
    ),
    "menu": (
        "gnomarchi-menu",
        "Add a menu-module JSONC fragment under Install/Setup/Style/Trigger without "
        "colliding ids. Follow the gnomarchi-menu skill.",
    ),
}


def make_something(kind: str, extra: str = "") -> int:
    if kind not in STARTERS:
        raise ValueError(f"unknown make-something kind: {kind}; try {sorted(STARTERS)}")
    skill, prompt = STARTERS[kind]
    if extra.strip():
        prompt = f"{prompt} Extra brief: {extra.strip()}"
    return run_prompt(prompt, skill=skill, unattended=True)


def list_starters() -> list[dict[str, str]]:
    return [
        {"id": k, "skill": v[0], "prompt": v[1]} for k, v in STARTERS.items()
    ]
