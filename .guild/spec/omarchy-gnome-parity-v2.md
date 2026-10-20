---
type: spec
owner: orchestrator
confidence: high
source_refs:
  - .guild/explore/omarchy-gnome-parity-v2.json
  - .guild/define/omarchy-gnome-parity-v2.json
  - docs/plans/omarchy-full-parity-map-plan.html
  - features/registry.yaml
  - .guild/wiki/decisions/stock-gnome-omakase.md
created_at: 2026-10-20
updated_at: 2026-10-20
slug: omarchy-gnome-parity-v2
---

# Omarchy → stock GNOME parity wave (v2)

## Goal & outcome

Close remaining Omarchy-functional gaps under D1′: default GNOME extensions (including **user-themes**), an Omarchy-like **visual theme/background picker**, a complete port map in the feature registry, and **VM visual validation with screenshots** for every checkable surface.

## Audience / operator

gnomarchi Arch+GNOME users and the maintainer validating on the QEMU test VM (SSH `:2222`, VNC `:5901`, 9p `/mnt/gnomarchi`).

## Success criteria

- AC-1 … AC-6 from `.guild/define/omarchy-gnome-parity-v2.json` all pass.
- Overlay installs `gnome-shell-extensions` (ships `user-theme@gnome-shell-extensions.gcampax.github.com`) and enables it with appindicator + first-party chips.
- Style menu + hotkey open a carousel/list theme picker that applies packs end-to-end (not CLI-only).
- `docs/screenshots/parity-v2/` contains one screenshot per visual checklist row with pass recorded.

## Non-goals

- Quickshell / Hyprland / OWE video wallpapers.
- Vendoring Omarchy binary backgrounds, unlocks, or app marks (D7).
- ISO / gaming / Windows VM (P8/P9).
- Claiming official Omarchy affiliation.

## Constraints

- Stock GNOME Shell + GDM only (D1′).
- MIT Omarchy `colors.toml` / templates OK; no binary asset copy without CREDITS.
- Cap-6 specialists; team decision never auto-approved.
- Shell extension `shell-version` must include host (50/51).

## Autonomy policy

- May: edit registry, theme emitters, GTK picker, overlay packages, tests, docs under `docs/plans` and `docs/screenshots`.
- Confirm: team roster approve; destructive VM resets; publishing packages/keys.
- Forbidden: Hyprland packages; silent disk wipe; `--auto-approve` on team gate.

## Known risks and rollback

- user-themes + Shell CSS break on GNOME bumps → pin CSS, document disable path (`gnome-extensions disable user-theme@…`).
- Extension enable races → enable via gsettings + GDM restart; rollback disables UUIDs.
- D7 branding → keep “inspired by” provenance only.

## Assumptions vs blocking unknowns

- Assumed: `gnome-shell-extensions` is the Arch source of user-themes (verified in package file list).
- Assumed: generated wallpapers remain acceptable until CREDITS for curated stills.
- Non-blocking: exact Omarchy preview.png assets stay out; gnomarchi uses pack swatches / generated previews.

## Implementation plan (authoritative HTML)

See `docs/plans/omarchy-full-parity-map-plan.html` for the full Omarchy surface map, port matrix, lane plan, team, and VM visual checklist.
