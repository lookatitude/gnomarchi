---
type: spec
owner: orchestrator
confidence: high
source_refs:
  - intake:2026-10-20
  - docs/omarchy-to-gnome-comparison.html
  - docs/plans/agentic-integrations-plan.html
  - docs/plans/gnomarchi-consolidated-plan.html
  - .guild/wiki/decisions/
created_at: 2026-10-20
updated_at: 2026-10-20
run_id: run-20261020-143729-ideate
approved: true
approved_at: 2026-10-20
approved_by: user@chat
---

# gnomarchi v1 — Omarchy feature port on stock GNOME

## Goal & outcome

Ship **gnomarchi**: an Arch Linux desktop product that ports Omarchy’s omakase, agentic, and installable workflows onto **stock GNOME (slightly omakase’d)**. End users get a guided overlay (then ISO), a unified menu/CLI, whole-desktop themes, coding-agent integration with “Make something” (themes/plugins/apps), and a **complete feature registry** so every Omarchy capability is either ported, natively covered, adapted, or explicitly deferred with a future path.

## Audience / operator

- Primary: developers who like Omarchy’s agentic Arch experience but want GNOME’s desktop model.
- Operator: project maintainer building packages (custom pacman repo + AUR) and the overlay/ISO.

## Success criteria

- Feature registry covers **100% of inventoried Omarchy product surfaces** with status ∈ {native, port, adapt, rebuild, defer} and an owner phase.
- Overlay install on Arch+GNOME reaches: GNOME session, Ghostty/Neovim/Chromium defaults, `gnomarchi` CLI, theme set, menu, agent invite.
- Agent with `gnomarchi-theme` / `gnomarchi-plugin` skills can create and enable a theme and an overlay-app plugin end-to-end.
- Upstream Omarchy release notes can be mapped into registry rows via a documented process (`features/registry` + sync notes).
- Consolidated plan HTML is the single planning artifact (decisions inlined; wiki ADRs remain audit trail only).

## Non-goals

- Replacing GNOME Shell with Quickshell or Hyprland.
- PaperWM/Forge as v1 identity (optional later profile only).
- Claiming official Omarchy affiliation.
- Auto-converting existing Omarchy Quickshell plugins.
- Full marketplace (plugins.gnomarchi.org) in v1 (git-add + validate is enough).

## Constraints

- stack: Arch, GNOME Wayland, GDM; Ghostty + Neovim + Chromium defaults.
- packaging: custom pacman repo (default) + AUR fallback.
- branding: public name `gnomarchi`.
- themes: vendor Omarchy packs iff license/branding OK; else original inspired packs.
- plugins: multi-runtime; Shell extensions last.
- install: overlay before ISO.
- legal: attribute upstream; confirm theme license before vendoring.

## Autonomy policy

- may act without asking: scaffold under agreed layout; update registry statuses; theme engine against minimal original packs; write docs/plans HTML.
- requires confirmation: publishing remote/repo keys; vendoring Omarchy theme assets after license read; enabling Shell-extension runtime in defaults; destructive disk/ISO tests on real hardware.
- forbidden: implying Omarchy official status; running Quickshell beside GNOME Shell; silent overwrite of user `~/.config` without backup; sudo install hooks in plugins.

## Risks & rollback

- Omarchy theme license blocks vendoring → fall back to O2 original packs (already decided).
- GNOME Shell API churn for extensions → keep extensions optional; prefer overlay-apps.
- Feature parity pressure vs stock-GNOME feel → registry `defer` rows with rationale, not silent drop.
- Rollback: `gnomarchi reinstall configs`; overlay uninstall restores dconf backup; packages removable via pacman.

## Assumptions (from brainstorm)

- User explicitly agreed Q1–Q7 (stock GNOME, multi-runtime plugins, overlay→ISO, repo+AUR, name gnomarchi, Ghostty/nvim/Chromium, themes O3→O2).
- “Port all features” means **account for every inventoried feature** in the registry (native/adapt/defer allowed), not bit-identical Hyprland UX.
- Future Omarchy improvements are tracked by registry sync against release notes, not by continuous rebase of their shell.

## Locked decisions (canonical copy — also in consolidated plan)

1. Stock GNOME, slightly omakase’d.
2. Multi-runtime plugins; Shell extensions last.
3. Overlay install before ISO.
4. Custom pacman repo + AUR fallback.
5. Public name `gnomarchi`.
6. Defaults: Ghostty + Neovim + Chromium.
7. Themes: vendor Omarchy if licensed; else original inspired packs.

## Deliverable pointer

Executable consolidated plan (feature matrix, phases, improvement mapping): `docs/plans/gnomarchi-consolidated-plan.html`.
