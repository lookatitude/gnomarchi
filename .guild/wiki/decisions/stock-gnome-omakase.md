---
type: decision
owner: architect
confidence: high
importance: high
source_refs:
  - intake:2026-10-20
  - docs/omarchy-to-gnome-comparison.html
  - docs/plans/omarchy-parity-gaps-plan.html
created_at: 2026-10-20
updated_at: 2026-10-20
expires_at: null
supersedes: null
sensitivity: internal
applies_to: [product]
related: [agentic-integrations, install-paths]
---
# ADR: Stock GNOME, slightly omakase’d (D1′)

## Status

Accepted (2026-10-20). Soft-revised same day to **D1′** after parity-gap review.

## Context

Q1 asked whether the default feel should be Omarchy-like Super chords on PaperWM or softer stock GNOME. Screenshots then showed empty chrome because bar widgets and agents were deferred under a strict reading of “no custom bar.”

## Decision

**D1′ — Stock GNOME chrome as the bar host, omakase content in and around it.**

- Keep GNOME Shell + GDM + Quick Settings (audio/net/bt/power).
- Ship **StatusNotifier / AppIndicator** first-party widgets (agents, weather, updates, tailscale).
- Ship an optional version-pinned **Shell extension** for the agents panel chip (`gnomarchi.agents-panel`).
- Configure indicator order via `~/.config/gnomarchi/shell.toml`.
- Do **not** replace GNOME’s top bar with Quickshell, Hyprland, or a full custom bar engine.

## Consequences

- PaperWM/Forge remain optional profiles, not identity.
- “Bar drag to any edge” is not a first-party Quickshell feature; use GNOME extension prefs if needed.
- Agents, mise CLIs, usage meters, and Make something are required product surface — not optional stubs.
