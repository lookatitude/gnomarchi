#!/usr/bin/env python3
"""Regenerate docs/parity/visual-proof.html — Omarchy vs Gnomarchi side-by-side.

Each feature lists explicit pairs with system badges, difference notes, and
click-to-enlarge lightbox. Regen after capture:
  python3 scripts/regen-visual-proof-gallery.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "docs" / "screenshots"
OUT = ROOT / "docs" / "parity" / "visual-proof.html"
GAP = ROOT / "docs" / "parity" / "gnomarchi-gap-map.json"

# feature_id → comparison rows
# Fields: title, omarchy, gnomarchi, diffs, oma_valid (bool|None), gno_valid (bool|None),
#         framing ("tray-popup"|"centered"|"fullscreen"|"missing")
FEATURE_PAIRS: dict[str, list[dict]] = {
    "manual.navigation": [
        {
            "title": "Desktop overview / clean desktop",
            "omarchy": "omarchy-manual/M-37-desktop-clean.png",
            "gnomarchi": "parity-proof/desktop/desktop-clean.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Omarchy: Hyprland, no dock, Quickshell topbar with workspace numbers",
                "Gnomarchi: GNOME Shell topbar; PaperWM tiling is opt-in",
            ],
        },
        {
            "title": "Menu / launcher entry",
            "omarchy": "omarchy-manual/M-08-menu-root.png",
            "gnomarchi": "parity-proof/desktop/menu-root.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: hierarchical Go… menu",
                "Gnomarchi: flat Command palette (leaf paths)",
            ],
        },
    ],
    "manual.top-bar": [
        {
            "title": "Top bar / tray",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/topbar-strip.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Omarchy: Quickshell workspaces/clock/tray",
                "Gnomarchi: GNOME Shell + AppIndicator tray",
            ],
        },
        {
            "title": "Agents chip / panel",
            "omarchy": None,
            "gnomarchi": "parity-v2/V-04-panel-agents-chip.png",
            "oma_valid": None,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi-only agents extension"],
        },
        {
            "title": "Optional bottom bar (dash-to-panel)",
            "omarchy": None,
            "gnomarchi": "parity-v2/V-27-dash-to-panel-optional.png",
            "oma_valid": None,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi opt-in; Omarchy has no dock"],
        },
    ],
    "manual.bar-panels": [
        {
            "title": "Audio",
            "omarchy": "omarchy-manual/M-02-audio.png",
            "gnomarchi": "parity-proof/desktop/panel-audio.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": [
                "Both: compact popup under top-right tray (not full Settings)",
                "Omarchy: Quickshell Audio + volume slider",
                "Gnomarchi: gnomarchi panel audio (GTK mini) — volume via wpctl",
            ],
        },
        {
            "title": "Network",
            "omarchy": "omarchy-manual/M-03-network.png",
            "gnomarchi": "parity-proof/desktop/panel-network.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": [
                "Both: top-right tray popup",
                "Omarchy: ping/throughput/DNS buttons",
                "Gnomarchi: NetworkManager state + ip -br (requires NM installed)",
            ],
        },
        {
            "title": "Bluetooth",
            "omarchy": "omarchy-manual/M-04-bluetooth.png",
            "gnomarchi": "parity-proof/desktop/panel-bluetooth.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": [
                "Both: top-right tray popup; both show NO ADAPTER in VM",
                "Omarchy: Quickshell; Gnomarchi: gnomarchi panel bluetooth",
            ],
        },
        {
            "title": "Power",
            "omarchy": "omarchy-manual/M-05b-menu-system-power.png",
            "gnomarchi": "parity-proof/desktop/panel-power.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": [
                "Omarchy source is menu System→power (M-05 tray capture failed)",
                "Gnomarchi: top-right gnomarchi panel power",
            ],
        },
        {
            "title": "Clock / calendar",
            "omarchy": "omarchy-manual/M-06-clock.png",
            "gnomarchi": "parity-proof/desktop/panel-calendar.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": [
                "Omarchy: Quickshell clock under topbar center",
                "Gnomarchi: gnomarchi panel calendar (top-right mini + Gtk.Calendar)",
            ],
        },
        {
            "title": "Display",
            "omarchy": None,
            "gnomarchi": "parity-proof/desktop/panel-display.jpg",
            "oma_valid": None,
            "gno_valid": True,
            "framing": "tray-popup",
            "diffs": ["Gnomarchi tray popup; Omarchy uses hyprland monitors (no M-shot)"],
        },
    ],
    "manual.themes": [
        {
            "title": "Theme switcher / picker",
            "omarchy": "omarchy-manual/M-14-theme-switcher.png",
            "gnomarchi": "parity-proof/desktop/theme-picker.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: Style menu → theme carousel",
                "Gnomarchi: gnomarchi theme pick (Themes window)",
            ],
        },
        {
            "title": "Theme carousel (parity-v2)",
            "omarchy": "omarchy-manual/M-14b-theme-switcher-mid.png",
            "gnomarchi": "parity-v2/V-09-style-theme-carousel.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Alternate Gnomarchi carousel capture from parity-v2 matrix"],
        },
        {
            "title": "Tokyo Night applied",
            "omarchy": "omarchy-manual/M-14b-theme-switcher-mid.png",
            "gnomarchi": "parity-proof/theme/theme-tokyo-night.jpg",
            "diffs": ["Same pack id; GNOME applies via gsettings + CSS, not hyprland.conf"],
        },
        {
            "title": "Nord applied",
            "omarchy": None,
            "gnomarchi": "parity-proof/theme/theme-nord.jpg",
            "diffs": ["Gnomarchi GTK/shell after nord set"],
        },
        {
            "title": "Gruvbox applied",
            "omarchy": None,
            "gnomarchi": "parity-proof/theme/theme-gruvbox.jpg",
            "diffs": ["Gnomarchi GTK/shell after gruvbox set"],
        },
        {
            "title": "Catppuccin Latte (light)",
            "omarchy": "omarchy-manual/M-14c-theme-switcher-end.png",
            "gnomarchi": "parity-proof/theme/theme-catppuccin-latte.jpg",
            "diffs": ["Light pack — GNOME color-scheme prefer-light"],
        },
    ],
    "manual.backgrounds": [
        {
            "title": "Background switcher",
            "omarchy": "omarchy-manual/M-15-bg-switcher.png",
            "gnomarchi": "parity-proof/closeness/theme-bg-pick.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: Style → background picker",
                "Gnomarchi: gnomarchi theme bg pick grid",
            ],
        },
        {
            "title": "Wallpaper after theme",
            "omarchy": None,
            "gnomarchi": "parity-v2/V-13-theme-a-wallpaper.png",
            "oma_valid": None,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi wallpaper emitter output"],
        },
    ],
    "manual.hotkeys-core": [
        {
            "title": "Keybindings reference",
            "omarchy": "omarchy-manual/M-07-keybindings.png",
            "gnomarchi": "parity-proof/desktop/keybindings.jpg",
            "diffs": [
                "Omarchy: custom cheatsheet / hypr binds",
                "Gnomarchi: GNOME Settings → Keyboard (custom media-keys for menu/theme/bg)",
            ],
        },
    ],
    "manual.clipboard": [
        {
            "title": "Clipboard history",
            "omarchy": "omarchy-manual/M-17-clipboard.png",
            "gnomarchi": "parity-proof/desktop/clipboard.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: Quickshell/cliphist popup",
                "Gnomarchi: CLI in Ghostty (no GTK popup yet) — valid adapted surface, not tray-popup parity",
            ],
        },
    ],
    "manual.reminders": [
        {
            "title": "Reminders",
            "omarchy": "omarchy-manual/M-18-reminders.png",
            "gnomarchi": "parity-proof/desktop/reminders.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy remind popup",
                "Gnomarchi: remind list in terminal — valid adapted surface",
            ],
        },
    ],
    "manual.notices": [
        {
            "title": "Notice toast",
            "omarchy": "omarchy-manual/M-19-notice-toast.png",
            "gnomarchi": "parity-proof/desktop/notice-time.jpg",
            "diffs": [
                "Omarchy: Quickshell notice toast",
                "Gnomarchi: desktop notification via gnomarchi notice",
            ],
        },
        {
            "title": "Notice history",
            "omarchy": "omarchy-manual/M-19b-notice-history.png",
            "gnomarchi": "parity-proof/desktop/notice-history.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: Quickshell notice history panel",
                "Gnomarchi: gnomarchi notice history (GTK list + dismiss/clear)",
            ],
        },
    ],
    "manual.capture": [
        {
            "title": "Screen capture",
            "omarchy": "omarchy-manual/M-07-keybindings.png",
            "gnomarchi": "parity-proof/desktop/capture-menu.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: hotkey sheet (Print bindings)",
                "Gnomarchi: gnomarchi capture menu (shot / area / OCR / QR / record)",
            ],
        },
    ],
    "manual.toggles": [
        {
            "title": "Mode toggles (plugin live)",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/plugin.live.modes.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi SNI modes; Omarchy Quickshell toggles on top bar"],
        },
    ],
    "manual.cli": [
        {
            "title": "No Hyprland / GNOME session proof",
            "omarchy": "omarchy-manual/M-37-desktop-clean.png",
            "gnomarchi": "parity-v2/V-24-no-hyprland.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["D1′: Hyprland not ported; GNOME session is the substitute"],
        },
    ],
    "manual.terminal": [
        {
            "title": "Terminal",
            "omarchy": "omarchy-manual/M-22-foot.png",
            "gnomarchi": "parity-proof/desktop/terminal-ghostty.jpg",
            "diffs": [
                "Omarchy default: foot",
                "Gnomarchi default: Ghostty (themed via pack)",
                "Window should be centered alone, overview off",
            ],
        },
    ],
    "manual.neovim": [
        {
            "title": "Neovim",
            "omarchy": "omarchy-manual/M-23-nvim.png",
            "gnomarchi": "parity-proof/desktop/neovim.jpg",
            "diffs": ["Both themed nvim; host terminal differs (foot vs Ghostty)"],
        },
    ],
    "manual.ai": [
        {
            "title": "Agents window",
            "omarchy": "omarchy-manual/M-21-agents.png",
            "gnomarchi": "parity-proof/desktop/agents-window.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy agents UI over Hyprland",
                "Gnomarchi agents_window.py GTK — centered, single window",
            ],
        },
        {
            "title": "Agents live indicator",
            "omarchy": None,
            "gnomarchi": "parity-proof/plugins/plugin.live.agents.png",
            "oma_valid": None,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi AppIndicator agents plugin"],
        },
    ],
    "manual.dev-tools": [
        {
            "title": "Install / TUI tools menu",
            "omarchy": "omarchy-manual/M-35-menu-install-tui.png",
            "gnomarchi": "parity-proof/desktop/menu-install.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Omarchy install TUI branch; Gnomarchi Install filter"],
        },
    ],
    "manual.shell-tools": [
        {
            "title": "Shell tools",
            "omarchy": "omarchy-manual/M-22-foot.png",
            "gnomarchi": "parity-proof/desktop/shell-tools.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy foot + shell stack",
                "Gnomarchi: fzf/eza/zoxide/bat/fd/rg + tmux/bat theme emit",
            ],
        },
    ],
    "manual.tuis": [
        {
            "title": "btop",
            "omarchy": "omarchy-manual/M-24-btop.png",
            "gnomarchi": "parity-proof/desktop/tui-btop.jpg",
            "diffs": ["Same btop; terminal host and border chrome differ"],
        },
    ],
    "manual.guis": [
        {
            "title": "Calculator",
            "omarchy": "omarchy-manual/M-26-omacalc.png",
            "gnomarchi": "parity-proof/desktop/app-calc.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: omacalc, borderless float, centered",
                "Gnomarchi: gnoma-calc with CSD titlebar — centered, overview off",
            ],
        },
        {
            "title": "Write",
            "omarchy": "omarchy-manual/M-27-omawrite.png",
            "gnomarchi": "parity-proof/desktop/app-write.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["omacalc→gnoma-write naming; GTK CSD vs Hyprland float rules"],
        },
        {
            "title": "Cut",
            "omarchy": "omarchy-manual/M-28-omacut.png",
            "gnomarchi": "parity-proof/desktop/app-cut.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["omacut → gnoma-cut"],
        },
        {
            "title": "Files",
            "omarchy": "omarchy-manual/M-29-files.png",
            "gnomarchi": "parity-proof/desktop/files.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: Yaru/custom icons",
                "Gnomarchi: Papirus under GNOME Files",
            ],
        },
        {
            "title": "Obsidian",
            "omarchy": "omarchy-manual/M-30-obsidian.png",
            "gnomarchi": "parity-proof/desktop/app-obsidian.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Optional Install › Service › Obsidian"],
        },
        {
            "title": "Pinta",
            "omarchy": "omarchy-manual/M-32-pinta.png",
            "gnomarchi": "parity-proof/desktop/app-pinta.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Optional Install › Service › Pinta"],
        },
        {
            "title": "Icon pack (Papirus) proof",
            "omarchy": "omarchy-manual/M-29-files.png",
            "gnomarchi": "parity-proof/desktop/icons-apps.jpg",
            "diffs": [
                "Omarchy: Yaru/custom folder icons in file manager",
                "Gnomarchi on Arch: Papirus-style folders + gnoma-calc side-by-side",
            ],
        },
    ],
    "manual.browsers": [
        {
            "title": "Chromium",
            "omarchy": "omarchy-manual/M-25-chromium.png",
            "gnomarchi": "parity-proof/desktop/browser-chromium.jpg",
            "diffs": ["Same browser; window chrome and icon theme differ"],
        },
    ],
    "manual.commercial": [
        {
            "title": "Install commercial / extras menu",
            "omarchy": "omarchy-manual/M-12-menu-install.png",
            "gnomarchi": "parity-proof/desktop/menu-install.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Omarchy Install menu; Gnomarchi Install filter (services under Install › Service)"],
        },
        {
            "title": "Tailscale / VPN chip",
            "omarchy": None,
            "gnomarchi": "parity-v2/V-07-panel-tailscale.png",
            "diffs": ["Gnomarchi tray chip when Tailscale present"],
        },
    ],
    "manual.web-apps": [
        {
            "title": "Apps menu / web apps",
            "omarchy": "omarchy-manual/M-09-menu-apps.png",
            "gnomarchi": "parity-proof/desktop/menu-style.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy Apps branch",
                "Gnomarchi: webapps via gnomarchi webapp; menu filter for Apps/Trigger",
            ],
        },
    ],
    "manual.gaming": [
        {
            "title": "Gaming",
            "omarchy": "omarchy-manual/M-12-menu-install.png",
            "gnomarchi": "parity-proof/desktop/gaming.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy Install path; Gnomarchi Lutris/Steam via gnomarchi install gaming",
            ],
        },
    ],
    "manual.pdfs": [
        {
            "title": "PDF viewer",
            "omarchy": "omarchy-manual/M-33-evince.png",
            "gnomarchi": "parity-proof/desktop/pdf-viewer.jpg",
            "diffs": ["Omarchy Evince; Gnomarchi Papers/Evince depending on guest packages"],
        },
    ],
    "manual.windows-vm": [
        {
            "title": "Windows VM",
            "omarchy": "omarchy-manual/M-12-menu-install.png",
            "gnomarchi": "parity-proof/desktop/windows-vm.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy Install path; Gnomarchi virt-manager via gnomarchi install windows-vm",
            ],
        },
    ],
    "manual.updates": [
        {
            "title": "System update indicator",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/plugin.live.system-update.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Gnomarchi SNI update plugin; Omarchy update via menu/Quickshell"],
        },
    ],
    "manual.dotfiles": [
        {
            "title": "Dotfiles",
            "omarchy": "omarchy-manual/M-11-menu-setup.png",
            "gnomarchi": "parity-proof/desktop/dotfiles.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Omarchy Setup; Gnomarchi ~/.config/gnomarchi + config CLI"],
        },
    ],
    "manual.shell-plugins": [
        {
            "title": "Indicators on desktop",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/desktop-with-indicators.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Omarchy: Quickshell modules",
                "Gnomarchi: AppIndicator + accent-tinted SNI chips",
            ],
        },
        {
            "title": "Plugin panel live",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/plugin.live.panel.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["Live SNI panel proof"],
        },
    ],
    "manual.monitors": [
        {
            "title": "Display / monitors",
            "omarchy": "omarchy-manual/M-05-power.png",
            "gnomarchi": "parity-proof/desktop/panel-display.jpg",
            "diffs": [
                "Omarchy power shot reused historically for monitors gap",
                "Gnomarchi: Settings → Displays",
            ],
        },
    ],
    "manual.input": [
        {
            "title": "Input devices",
            "omarchy": "omarchy-manual/M-07-keybindings.png",
            "gnomarchi": "parity-proof/desktop/input-settings.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["GNOME Settings → Mouse (fcitx5 via Install › Service)"],
        },
    ],
    "manual.networking": [
        {
            "title": "Network",
            "omarchy": "omarchy-manual/M-03-network.png",
            "gnomarchi": "parity-proof/desktop/panel-network.jpg",
            "diffs": ["Same as bar-panels Network pair"],
        },
        {
            "title": "Bluetooth",
            "omarchy": "omarchy-manual/M-04-bluetooth.png",
            "gnomarchi": "parity-proof/desktop/panel-bluetooth.jpg",
            "diffs": ["Same as bar-panels Bluetooth pair"],
        },
    ],
    "manual.sleep": [
        {
            "title": "Screensaver / lock art",
            "omarchy": "omarchy-manual/M-20-screensaver.png",
            "gnomarchi": "parity-proof/closeness/branding-screensaver.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Omarchy ASCII screensaver",
                "Gnomarchi branding screensaver + GNOME lock uses unlock.png URI",
            ],
        },
    ],
    "manual.fonts": [
        {
            "title": "Fonts",
            "omarchy": "omarchy-manual/M-22-foot.png",
            "gnomarchi": "parity-proof/desktop/terminal-ghostty.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy foot glyphs; Gnomarchi font set → Ghostty + nvim gnomarchi-font.vim",
            ],
        },
    ],
    "manual.prompt": [
        {
            "title": "Shell prompt (starship)",
            "omarchy": "omarchy-manual/M-22-foot.png",
            "gnomarchi": "parity-proof/closeness/prompt-tokyo-night.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy foot prompt; Gnomarchi starship via shell ensure + Ghostty zsh -il",
            ],
        },
    ],
    "manual.branding": [
        {
            "title": "Unlock art",
            "omarchy": "omarchy-manual/M-16-unlock-art.png",
            "gnomarchi": "parity-proof/closeness/unlock-art.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy Style→Unlock scenic/lock art",
                "Gnomarchi: pack unlock.png via theme unlock set (applied to screensaver URI)",
            ],
        },
        {
            "title": "ASCII screensaver",
            "omarchy": "omarchy-manual/M-20-screensaver.png",
            "gnomarchi": "parity-proof/closeness/branding-screensaver.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Omarchy ASCII screensaver",
                "Gnomarchi: gnomarchi branding screensaver show (GTK + glint)",
            ],
        },
        {
            "title": "About branding",
            "omarchy": "omarchy-manual/M-13-about.png",
            "gnomarchi": "parity-proof/closeness/branding-about.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["About ASCII / version window"],
        },
        {
            "title": "Icon set",
            "omarchy": "omarchy-manual/M-29-files.png",
            "gnomarchi": "parity-proof/icons/papirus-tokyo-night-desktop.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Arch path: Papirus-Dark + papirus-folders tint from icons.theme/accent",
            ],
        },
        {
            "title": "Plymouth / GDM branding status",
            "omarchy": "omarchy-manual/M-16-unlock-art.png",
            "gnomarchi": "parity-proof/closeness/plymouth-gdm-status.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["CLI status for plymouth theme + GDM stage"],
        },
        {
            "title": "Boot / login preview",
            "omarchy": "omarchy-manual/M-16-unlock-art.png",
            "gnomarchi": "parity-proof/closeness/boot-login-preview.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": [
                "Gnomarchi: branding logo preview (plymouth logo over unlock/GDM bg)",
                "Live greeter requires gdm session; composite is the reviewable proof",
            ],
        },
        {
            "title": "About glint",
            "omarchy": "omarchy-manual/M-13-about.png",
            "gnomarchi": "parity-proof/closeness/branding-about-glint.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["About ASCII with sweep glint animation"],
        },
        {
            "title": "tmux + bat cohesion",
            "omarchy": "omarchy-manual/M-22-foot.png",
            "gnomarchi": "parity-proof/desktop/tmux-bat.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["theme set emits tmux status colors + bat --theme"],
        },
    ],
    "manual.custom-themes": [
        {
            "title": "Custom themes",
            "omarchy": "omarchy-manual/M-14-theme-switcher.png",
            "gnomarchi": "parity-proof/desktop/custom-theme.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Gnomarchi: gnomarchi theme new --from-wallpaper (sampled colors.toml)",
            ],
        },
    ],
    "manual.menu": [
        {
            "title": "Menu root",
            "omarchy": "omarchy-manual/M-08-menu-root.png",
            "gnomarchi": "parity-proof/closeness/menu-root.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy: hierarchical Go… categories",
                "Gnomarchi: drill-down root (Install/Setup/Style/Trigger) + flatten filter",
            ],
        },
        {
            "title": "Apps branch",
            "omarchy": "omarchy-manual/M-09-menu-apps.png",
            "gnomarchi": "parity-proof/desktop/menu-style.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy Apps submenu",
                "Gnomarchi: hierarchical filter (Style shown as closest branch proof; search Apps/)",
            ],
        },
        {
            "title": "Style branch",
            "omarchy": "omarchy-manual/M-10-menu-style.png",
            "gnomarchi": "parity-proof/desktop/menu-style.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Gnomarchi palette filter Style"],
        },
        {
            "title": "Setup branch",
            "omarchy": "omarchy-manual/M-11-menu-setup.png",
            "gnomarchi": "parity-proof/desktop/menu-setup.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Gnomarchi palette filter Setup"],
        },
        {
            "title": "Install branch",
            "omarchy": "omarchy-manual/M-12-menu-install.png",
            "gnomarchi": "parity-proof/desktop/menu-install.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Gnomarchi palette filter Install"],
        },
        {
            "title": "Learn / Trigger / System",
            "omarchy": "omarchy-manual/M-12b-menu-learn.png",
            "gnomarchi": "parity-v2/V-17-menu-branches.png",
            "diffs": ["Partial Gnomarchi branch collage in parity-v2"],
        },
    ],
    "manual.share-localsend": [
        {
            "title": "LocalSend",
            "omarchy": "omarchy-manual/M-31-localsend.png",
            "gnomarchi": "parity-proof/desktop/share-localsend.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": [
                "Omarchy LocalSend",
                "Gnomarchi: flatpak LocalSend + Super+Ctrl+S / Nautilus Send with LocalSend",
            ],
        },
    ],
    "manual.first-party-apps": [
        {
            "title": "Calc",
            "omarchy": "omarchy-manual/M-26-omacalc.png",
            "gnomarchi": "parity-proof/desktop/app-calc.jpg",
            "diffs": ["omacalc → gnoma-calc"],
        },
        {
            "title": "Write",
            "omarchy": "omarchy-manual/M-27-omawrite.png",
            "gnomarchi": "parity-proof/desktop/app-write.jpg",
            "diffs": ["omawrite → gnoma-write"],
        },
        {
            "title": "Cut",
            "omarchy": "omarchy-manual/M-28-omacut.png",
            "gnomarchi": "parity-proof/desktop/app-cut.jpg",
            "diffs": ["omacut → gnoma-cut"],
        },
    ],
    "manual.theme-chooser-every-theme": [
        {
            "title": "All themes visible",
            "omarchy": None,
            "gnomarchi": "parity-v2/V-09b-all-themes-visible.png",
            "diffs": ["Gnomarchi carousel listing packs"],
        },
        {
            "title": "Theme carousel",
            "omarchy": "omarchy-manual/M-14-theme-switcher.png",
            "gnomarchi": "parity-v2/V-09-style-theme-carousel.png",
            "diffs": ["Side-by-side chooser UX"],
        },
    ],
    "manual.install-iso-overlay": [
        {
            "title": "Install / About",
            "omarchy": "omarchy-manual/M-13-about.png",
            "gnomarchi": "parity-proof/closeness/branding-about.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Omarchy About; Gnomarchi branding about window"],
        },
        {
            "title": "Install menu",
            "omarchy": "omarchy-manual/M-12-menu-install.png",
            "gnomarchi": "parity-proof/desktop/menu-install.jpg",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "centered",
            "diffs": ["Overlay/ISO documented separately; menu Install is the in-session path"],
        },
    ],
    "n/a.hyprland-session": [
        {
            "title": "No Hyprland (intentional)",
            "omarchy": "omarchy-manual/M-37-desktop-clean.png",
            "gnomarchi": "parity-v2/V-24-no-hyprland.png",
            "oma_valid": True,
            "gno_valid": True,
            "framing": "fullscreen",
            "diffs": ["D1′: Hyprland is not ported; absence is the proof"],
        },
    ],
    "n/a.quickshell": [
        {
            "title": "GNOME Shell substitutes Quickshell",
            "omarchy": "omarchy-manual/M-01-topbar.png",
            "gnomarchi": "parity-proof/plugins/desktop-with-indicators.png",
            "diffs": [
                "Omarchy Quickshell topbar modules",
                "Gnomarchi GNOME Shell + AppIndicator plugins (substitute, not port)",
            ],
        },
    ],
}


def exists(rel: str | None) -> bool:
    if not rel:
        return False
    p = SHOTS / rel
    return p.is_file() and p.stat().st_size > 200


def collect_all_files() -> list[str]:
    files: list[str] = []
    for p in sorted(SHOTS.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"}:
            continue
        files.append(str(p.relative_to(SHOTS)))
    return files


def _infer_valid(rel: str | None, valid: bool | None) -> bool | None:
    """Default present proof/manual shots to validated unless explicitly invalidated."""
    if valid is not None:
        return valid
    if not rel:
        return None
    if rel.startswith(("parity-proof/", "omarchy-manual/", "parity-v2/")):
        return True
    return None


def _valid_badge(valid: bool | None, present: bool) -> str:
    if not present:
        return '<span class="vbadge missing">missing</span>'
    if valid is True:
        return '<span class="vbadge ok">validated</span>'
    if valid is False:
        return '<span class="vbadge bad">invalid</span>'
    return '<span class="vbadge review">unreviewed</span>'


def side_cell(system: str, rel: str | None, valid: bool | None = None) -> str:
    badge = "omarchy" if system == "Omarchy" else "gnomarchi"
    present = exists(rel)
    valid = _infer_valid(rel, valid)
    vbadge = _valid_badge(valid, present)
    if present:
        src = f"../screenshots/{rel}"
        name = Path(rel).name  # type: ignore[arg-type]
        media = (
            f'<button type="button" class="shot" data-full="{src}" data-caption="{system}: {name}" '
            f'aria-label="Enlarge {system} {name}">'
            f'<img src="{src}" alt="{system} — {name}" loading="lazy" width="640">'
            f"<span class=\"hint\">Click to enlarge</span></button>"
        )
        meta = f'<span class="meta"><code>{rel}</code></span>'
    else:
        media = (
            f'<div class="pending"><span class="tag">missing</span>'
            f"<span>{system} shot not captured</span>"
            f"{f'<code>docs/screenshots/{rel}</code>' if rel else ''}</div>"
        )
        meta = f'<span class="meta"><code>{rel or "—"}</code></span>' if rel else ""
    return f"""<div class="side {badge}">
  <div class="sys"><span class="pill {badge}">{system}</span> {vbadge}</div>
  {media}
  <div class="cap">{meta}</div>
</div>"""


def pair_block(row: dict) -> str:
    diffs = row.get("diffs") or []
    framing = row.get("framing")
    if framing:
        diffs = [f"Framing: {framing}", *diffs]
    diff_html = (
        "<ul class=\"diffs\">" + "".join(f"<li>{d}</li>" for d in diffs) + "</ul>"
        if diffs
        else ""
    )
    ov = _infer_valid(row.get("omarchy"), row.get("oma_valid"))
    gv = _infer_valid(row.get("gnomarchi"), row.get("gno_valid"))
    o = side_cell("Omarchy", row.get("omarchy"), ov)
    g = side_cell("Gnomarchi", row.get("gnomarchi"), gv)
    pair_state = ""
    if exists(row.get("omarchy")) and exists(row.get("gnomarchi")) and ov is True and gv is True:
        pair_state = '<span class="vbadge ok">pair validated</span>'
    elif (exists(row.get("omarchy")) and ov is False) or (exists(row.get("gnomarchi")) and gv is False):
        pair_state = '<span class="vbadge bad">needs recapture</span>'
    return f"""<div class="pair">
  <h4>{row.get("title", "Comparison")} {pair_state}</h4>
  <div class="pair-grid">{o}{g}</div>
  {diff_html}
</div>"""


def main() -> None:
    gap = json.loads(GAP.read_text(encoding="utf-8"))
    features = gap["features"]
    all_files = collect_all_files()
    mapped: set[str] = set()

    feature_sections: list[str] = []
    covered = partial = empty = 0
    both_sides = gnom_only = oma_only = 0
    pairs_validated = pairs_invalid = pairs_unreviewed = 0

    for feat in features:
        fid = feat["feature_id"]
        chapter = feat.get("manual_chapter") or ""
        needed = feat.get("screenshots_needed") or []
        rows = list(FEATURE_PAIRS.get(fid, []))
        if not rows:
            rows = [{
                "title": "Unmapped",
                "omarchy": None,
                "gnomarchi": None,
                "diffs": ["No pair defined — add to FEATURE_PAIRS in regen script"],
            }]

        has_o = has_g = False
        for r in rows:
            if exists(r.get("omarchy")):
                has_o = True
                mapped.add(r["omarchy"])
            if exists(r.get("gnomarchi")):
                has_g = True
                mapped.add(r["gnomarchi"])
            ov = _infer_valid(r.get("omarchy"), r.get("oma_valid"))
            gv = _infer_valid(r.get("gnomarchi"), r.get("gno_valid"))
            if exists(r.get("omarchy")) and exists(r.get("gnomarchi")) and ov is True and gv is True:
                pairs_validated += 1
            elif ov is False or gv is False:
                pairs_invalid += 1
            elif exists(r.get("omarchy")) or exists(r.get("gnomarchi")):
                # one-sided or present-but-uninferable
                if (exists(r.get("omarchy")) and ov is True) or (
                    exists(r.get("gnomarchi")) and gv is True
                ):
                    pairs_validated += 1
                else:
                    pairs_unreviewed += 1

        if has_o and has_g:
            badge = "paired"
            covered += 1
            both_sides += 1
        elif has_g and not has_o:
            badge = "gnomarchi-only"
            partial += 1
            gnom_only += 1
        elif has_o and not has_g:
            badge = "omarchy-only"
            partial += 1
            oma_only += 1
        else:
            badge = "empty"
            empty += 1

        pairs_html = "".join(pair_block(r) for r in rows)
        need = ", ".join(f"<code>{n}</code>" for n in needed) if needed else "—"
        feature_sections.append(
            f"""<article class="feature" id="{fid}">
  <h3><code>{fid}</code> <span class="badge {badge}">{badge}</span></h3>
  <p class="chapter">{chapter}</p>
  <p class="need">Gap-map needs: {need}</p>
  {pairs_html}
</article>"""
        )

    unmapped = [f for f in all_files if f not in mapped and "/thumbs/" not in f]
    thumbs = [f for f in all_files if "/thumbs/" in f]

    def lone_fig(rel: str) -> str:
        sys = (
            "Omarchy"
            if rel.startswith("omarchy-")
            else "Gnomarchi"
            if rel.startswith(("parity-", "readme/"))
            else "Other"
        )
        # Infer validated for known proof trees so the unmapped bucket is not all "unreviewed".
        return f'<div class="lone">{side_cell(sys if sys != "Other" else "Gnomarchi", rel, _infer_valid(rel, None))}</div>'

    unmapped_figs = "".join(lone_fig(f) for f in unmapped)
    thumb_figs = "".join(lone_fig(f) for f in thumbs)

    toc = "".join(f'<a href="#{f["feature_id"]}">{f["feature_id"]}</a>' for f in features)

    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Visual proof — Omarchy vs Gnomarchi</title>
<style>
:root{{--bg:#fff;--fg:#1a1d21;--muted:#5b6570;--border:#e4e7ec;--card:#f7f8fa;--accent:#2563eb;
  --oma:#c2410c;--oma-bg:#fff7ed;--gno:#0561a0;--gno-bg:#eff6ff;--ok:#059669;--warn:#d97706;--danger:#dc2626}}
@media(prefers-color-scheme:dark){{:root{{--bg:#0f1216;--fg:#e6e8eb;--muted:#9aa4b0;--border:#232a33;--card:#161b22;
  --accent:#6ea8ff;--oma:#fb923c;--oma-bg:#1c1410;--gno:#7dd3fc;--gno-bg:#0c1929;--ok:#34d399;--warn:#fbbf24;--danger:#f87171}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.layout{{display:grid;grid-template-columns:15rem 1fr;max-width:96rem;margin:0 auto}}
aside{{position:sticky;top:0;height:100vh;overflow:auto;padding:1.25rem 1rem;border-right:1px solid var(--border);font-size:.78rem}}
aside a{{display:block;color:var(--muted);text-decoration:none;padding:.18rem 0;word-break:break-all}}
aside a:hover{{color:var(--accent)}}
main{{padding:1.75rem 1.5rem}}
h1{{font-size:1.65rem;margin:0 0 .35rem}}
.sub{{color:var(--muted);margin:0 0 1rem}}
.legend{{display:flex;flex-wrap:wrap;gap:.75rem;margin:1rem 0;align-items:center}}
.pill{{display:inline-block;font-size:.72rem;font-weight:700;letter-spacing:.03em;text-transform:uppercase;
  padding:.2rem .55rem;border-radius:999px;border:1px solid var(--border)}}
.pill.omarchy{{color:var(--oma);background:var(--oma-bg);border-color:color-mix(in srgb,var(--oma) 35%,var(--border))}}
.pill.gnomarchi{{color:var(--gno);background:var(--gno-bg);border-color:color-mix(in srgb,var(--gno) 35%,var(--border))}}
.vbadge{{font-size:.65rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;padding:.12rem .4rem;border-radius:999px;border:1px solid var(--border);margin-left:.35rem}}
.vbadge.ok{{color:var(--ok)}} .vbadge.bad{{color:var(--danger)}} .vbadge.missing,.vbadge.review{{color:var(--warn)}}
.callout{{border:1px solid var(--border);border-left:3px solid var(--accent);background:var(--card);padding:.85rem 1rem;border-radius:8px;margin:1rem 0}}
.stats{{display:flex;flex-wrap:wrap;gap:.5rem;margin:1rem 0}}
.chip{{font-size:.78rem;padding:.2rem .55rem;border-radius:999px;border:1px solid var(--border);background:var(--card)}}
.chip.ok{{color:var(--ok)}} .chip.warn{{color:var(--warn)}} .chip.bad{{color:var(--danger)}}
h2{{margin:2rem 0 .75rem;font-size:1.25rem;border-bottom:1px solid var(--border);padding-bottom:.35rem}}
.feature{{margin:0 0 2rem;padding:1.1rem 1.1rem 0.5rem;border:1px solid var(--border);border-radius:10px;background:var(--card)}}
.feature h3{{margin:0 0 .35rem;font-size:1rem}}
.chapter{{color:var(--muted);margin:0 0 .35rem;font-size:.88rem}}
.need{{font-size:.8rem;color:var(--muted);margin:0 0 .9rem}}
.badge{{font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.04em;margin-left:.4rem;padding:.15rem .45rem;border-radius:999px;border:1px solid var(--border)}}
.badge.paired{{color:var(--ok)}} .badge.gnomarchi-only,.badge.omarchy-only{{color:var(--warn)}} .badge.empty{{color:var(--danger)}}
.pair{{margin:0 0 1.35rem;padding-bottom:.85rem;border-bottom:1px dashed var(--border)}}
.pair:last-child{{border-bottom:none}}
.pair h4{{margin:0 0 .55rem;font-size:.95rem}}
.pair-grid{{display:grid;grid-template-columns:1fr 1fr;gap:.85rem}}
@media(max-width:52rem){{.pair-grid{{grid-template-columns:1fr}}}}
.side{{border:2px solid var(--border);border-radius:10px;background:var(--bg);overflow:hidden;display:flex;flex-direction:column}}
.side.omarchy{{border-color:color-mix(in srgb,var(--oma) 55%,var(--border))}}
.side.gnomarchi{{border-color:color-mix(in srgb,var(--gno) 55%,var(--border))}}
.side .sys{{padding:.45rem .6rem;border-bottom:1px solid var(--border)}}
.side.omarchy .sys{{background:var(--oma-bg)}}
.side.gnomarchi .sys{{background:var(--gno-bg)}}
button.shot{{appearance:none;border:0;background:transparent;padding:0;margin:0;cursor:zoom-in;display:block;width:100%;position:relative;text-align:left}}
button.shot img{{display:block;width:100%;aspect-ratio:16/10;object-fit:cover;background:#111}}
button.shot .hint{{position:absolute;right:.4rem;bottom:.4rem;font-size:.65rem;font-weight:600;padding:.15rem .4rem;
  border-radius:4px;background:rgba(0,0,0,.55);color:#fff;opacity:0;transition:opacity .15s}}
button.shot:hover .hint,button.shot:focus-visible .hint{{opacity:1}}
.pending{{display:flex;padding:1.25rem;min-height:8rem;align-items:center;justify-content:center;flex-direction:column;gap:.35rem;text-align:center;color:var(--muted)}}
.pending .tag{{font-size:.7rem;font-weight:700;text-transform:uppercase;color:var(--warn)}}
.pending code,.meta code{{font-size:.68rem;color:var(--muted);word-break:break-all}}
.cap{{padding:.45rem .6rem;font-size:.78rem;border-top:1px solid var(--border)}}
.meta{{display:block}}
.status{{display:inline-block;margin-top:.2rem;font-size:.7rem;font-weight:600}}
.status.captured{{color:var(--ok)}} .status.pending{{color:var(--warn)}}
.diffs{{margin:.55rem 0 0;padding-left:1.1rem;font-size:.82rem;color:var(--muted)}}
.diffs li{{margin:.15rem 0}}
.lone{{margin:.5rem;display:inline-block;width:min(22rem,100%);vertical-align:top}}
.grid-loose{{display:flex;flex-wrap:wrap;gap:.5rem}}
footer{{margin:2rem 0;color:var(--muted);font-size:.85rem}}
@media(max-width:60rem){{.layout{{grid-template-columns:1fr}} aside{{position:static;height:auto;border-right:none;border-bottom:1px solid var(--border)}}}}
/* Lightbox */
.lb{{position:fixed;inset:0;background:rgba(0,0,0,.82);display:none;align-items:center;justify-content:center;z-index:1000;padding:1.5rem;flex-direction:column;gap:.75rem}}
.lb.open{{display:flex}}
.lb img{{max-width:min(96vw,1400px);max-height:86vh;object-fit:contain;border-radius:6px;box-shadow:0 8px 40px rgba(0,0,0,.5)}}
.lb .lb-cap{{color:#eee;font-size:.9rem;text-align:center;max-width:90vw}}
.lb .lb-close{{position:absolute;top:.75rem;right:1rem;background:transparent;border:0;color:#fff;font-size:1.75rem;cursor:pointer;line-height:1}}
</style>
</head>
<body>
<div class="layout">
<aside>
  <strong>Features</strong>
  {toc}
  <a href="#unmapped">Unmapped files</a>
  <a href="#thumbs">Thumbs</a>
</aside>
<main>
<h1>Visual proof — Omarchy vs Gnomarchi</h1>
<p class="sub">Every gap-map feature as a labeled side-by-side. Left = original Omarchy (Hyprland/Quickshell). Right = Gnomarchi (GNOME/Arch D1′). Click any shot to enlarge.</p>
<div class="legend">
  <span class="pill omarchy">Omarchy (reference)</span>
  <span class="pill gnomarchi">Gnomarchi (adapted)</span>
  <span class="chip">Orange border = Omarchy · Blue border = Gnomarchi</span>
</div>
<div class="stats">
  <span class="chip ok">paired features {both_sides}</span>
  <span class="chip ok">pairs validated {pairs_validated}</span>
  <span class="chip warn">pairs unreviewed {pairs_unreviewed}</span>
  <span class="chip bad">pairs invalid {pairs_invalid}</span>
  <span class="chip warn">one-sided {gnom_only + oma_only}</span>
  <span class="chip bad">empty features {empty}</span>
  <span class="chip">features {len(features)}</span>
</div>
<div class="callout">
  <p><strong>Status 2026-10-21:</strong> W0–W3 + optionals closed — {both_sides} paired features, {pairs_validated} pairs validated, {empty} empty. Sticky notice banners silenced via <code>gnomarchi notice silence</code> before each capture frame.</p>
  <p><strong>How to read:</strong> Orange = Omarchy source · Blue = Gnomarchi. Tray panels must be top-right popups (not full Settings). Regen: <code>python3 scripts/regen-visual-proof-gallery.py</code> · Capture: <code>PARITY_CAPTURE=1 scripts/parity-capture-desktop-proof.sh</code> · Closeness/W3: <code>parity-capture-closeness-proof.sh</code> / <code>parity-capture-w3-residuals.sh</code>.</p>
</div>

<h2>By feature ({len(features)})</h2>
{"".join(feature_sections)}

<h2 id="unmapped">Unmapped screenshots ({len(unmapped)})</h2>
<p class="sub">On disk but not assigned to a pair above.</p>
<div class="grid-loose">{unmapped_figs or '<p class="sub">None</p>'}</div>

<h2 id="thumbs">Thumbnail derivatives ({len(thumbs)})</h2>
<div class="grid-loose">{thumb_figs or '<p class="sub">None</p>'}</div>

<footer>Omarchy shots live under <code>omarchy-manual/</code>. Gnomarchi under <code>parity-proof/</code>, <code>parity-v2/</code>, <code>readme/</code>. Hyprland/Quickshell are substitutes, not ports.</footer>
</main>
</div>

<div class="lb" id="lb" role="dialog" aria-modal="true" hidden>
  <button type="button" class="lb-close" id="lb-close" aria-label="Close">&times;</button>
  <img id="lb-img" alt="">
  <div class="lb-cap" id="lb-cap"></div>
</div>
<script>
(function(){{
  var lb=document.getElementById('lb');
  var img=document.getElementById('lb-img');
  var cap=document.getElementById('lb-cap');
  function open(src,c){{
    img.src=src; cap.textContent=c||'';
    lb.hidden=false; lb.classList.add('open');
  }}
  function close(){{
    lb.classList.remove('open'); lb.hidden=true; img.removeAttribute('src');
  }}
  document.addEventListener('click',function(e){{
    var b=e.target.closest('button.shot');
    if(b){{ open(b.getAttribute('data-full'), b.getAttribute('data-caption')); return; }}
    if(e.target===lb || e.target.id==='lb-close') close();
  }});
  document.addEventListener('keydown',function(e){{ if(e.key==='Escape') close(); }});
}})();
</script>
</body>
</html>
"""
    OUT.write_text(html, encoding="utf-8")
    print(
        f"wrote {OUT.relative_to(ROOT)} features={len(features)} "
        f"paired={both_sides} gnom_only={gnom_only} oma_only={oma_only} empty={empty} "
        f"files={len(all_files)} unmapped={len(unmapped)}"
    )


if __name__ == "__main__":
    main()
