---
type: goals
source_refs:
  - intake:2026-10-20
  - docs/omarchy-to-gnome-comparison.html
  - docs/plans/agentic-integrations-plan.html
---
# Goals

1. Ship an Arch-based desktop that feels stock GNOME with light omakase defaults (keybinds, apps, themes, menu), not a Hyprland clone on GNOME.
2. Preserve Omarchy’s **integration shape**: agent skills → typed artifacts (theme / plugin / app / menu module) → CLI lifecycle → “Make something” starters.
3. Make the system **installable** first as an overlay on existing Arch (+GNOME), then as an ISO that reuses the same install stages.
4. Keep theme-as-data vs plugin-as-code trust split (themes auto-apply; plugins confirm + validate).

## Non-goals (v1)

- Reimplementing Quickshell or running it beside GNOME Shell.
- 1:1 Hyprland tiling semantics (PaperWM/Forge are optional later, not the default feel).
- Auto-migrating Omarchy Quickshell plugins to Gnomarchi.
