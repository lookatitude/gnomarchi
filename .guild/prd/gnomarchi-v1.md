---
type: prd
spec: .guild/spec/gnomarchi-v1.md
team: .guild/team/gnomarchi-v1.plan.yaml
right_size_trigger: multi-feature
created_at: 2026-10-20
run_id: run-20261020-144240-plan
---

# PRD: gnomarchi v1

## Product

**gnomarchi** — Arch Linux desktop that ports Omarchy’s omakase and agentic workflows onto stock GNOME (slightly omakase’d).

## Locked decisions (D1–D7)

1. Stock GNOME, slightly omakase’d (not tiling-first).
2. Multi-runtime plugins; Shell extensions last.
3. Overlay install before ISO.
4. Custom pacman repo + AUR fallback.
5. Public name `gnomarchi`.
6. Defaults: Ghostty + Neovim + Chromium.
7. Themes: vendor Omarchy packs if licensed; else original inspired packs.

## Features (rolled up)

| Area | Outcome |
| --- | --- |
| Feature registry | Every inventoried Omarchy capability tracked (native/port/adapt/rebuild/defer) + upstream sync process |
| Theme engine | `gnomarchi theme set` fans out; agent skill can author packs |
| Menu | GTK command palette + JSONC; Install/Setup/Style/Trigger |
| Plugins | add/clone/validate/enable for overlay-app, menu-module, user-service |
| Agents | mise CLIs, default agent, Make something, crash→diagnose, Agents window |
| Overlay | Install on Arch+GNOME to usable desktop with defaults |
| Packaging | Repo path for updates; AUR PKGBUILDs |

## User-facing success

- Overlay → GNOME session + Ghostty/nvim/Chromium + CLI + theme + agent invite.
- Agent creates theme and overlay-app plugin end-to-end.
- Registry maps Omarchy release notes without silent drops.
- Consolidated plan remains planning source of truth: `docs/plans/gnomarchi-consolidated-plan.html`.

## Non-goals

Quickshell/Hyprland session; PaperWM as v1 identity; official Omarchy affiliation; auto-convert Quickshell plugins; full marketplace in v1.

## Lane split rationale

Research unlocks D7 before theme vendoring. Architect spines contracts. Backend/frontend/devops/security implement in parallel after architect. QA gates overlay + agent flows.
