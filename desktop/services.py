"""Opt-in Install › Service package map (commercial / share / PDF / input)."""

from __future__ import annotations

import shutil
import subprocess

# Official Arch names where possible; AUR/flatpak noted in hint.
SERVICES: dict[str, dict[str, str | list[str]]] = {
    "tailscale": {
        "pkgs": ["tailscale"],
        "hint": "sudo systemctl enable --now tailscaled; tailscale up",
    },
    "docker": {
        "pkgs": ["docker", "docker-compose"],
        "hint": "sudo systemctl enable --now docker; sudo usermod -aG docker $USER",
    },
    "spotify": {
        "pkgs": ["spotify-launcher"],
        "hint": "AUR alternative: spotify",
    },
    "bitwarden": {"pkgs": ["bitwarden"], "hint": ""},
    "signal": {"pkgs": ["signal-desktop"], "hint": ""},
    "obsidian": {"pkgs": ["obsidian"], "hint": "may be AUR/extra"},
    "pinta": {"pkgs": ["pinta"], "hint": ""},
    "libreoffice": {"pkgs": ["libreoffice-fresh"], "hint": ""},
    "evince": {"pkgs": ["evince"], "hint": "PDF viewer"},
    "xournalpp": {"pkgs": ["xournalpp"], "hint": "PDF annotate (Signed interim)"},
    "fcitx5": {
        "pkgs": ["fcitx5", "fcitx5-configtool", "fcitx5-gtk", "fcitx5-qt"],
        "hint": "Set GTK_IM_MODULE=fcitx; reboot session",
    },
    "localsend": {
        "pkgs": [],
        "hint": "flatpak install -y flathub org.localsend.localsend_app",
        "flatpak": "org.localsend.localsend_app",
    },
    "cmus": {"pkgs": ["cmus"], "hint": "gnomarchi cliamp"},
}


def list_services() -> list[str]:
    return sorted(SERVICES)


def install(name: str, *, noconfirm: bool = True) -> int:
    row = SERVICES.get(name)
    if row is None:
        print(f"error: unknown service {name}", file=__import__("sys").stderr)
        print("known:", ", ".join(list_services()))
        return 2
    pkgs = list(row.get("pkgs") or [])
    flatpak = row.get("flatpak")
    if flatpak and isinstance(flatpak, str):
        if not shutil.which("flatpak"):
            print("error: flatpak required for", name, file=__import__("sys").stderr)
            return 1
        return subprocess.call(
            ["flatpak", "install", "-y", "flathub", flatpak]
        )
    if not pkgs:
        print(row.get("hint") or f"no packages mapped for {name}")
        return 0
    cmd = ["sudo", "pacman", "-Sy", "--needed"]
    if noconfirm:
        cmd.append("--noconfirm")
    cmd.extend(str(p) for p in pkgs)
    rc = subprocess.call(cmd)
    hint = row.get("hint")
    if hint:
        print(hint)
    return rc
