---
type: decision
owner: architect
confidence: medium
importance: high
source_refs:
  - intake:2026-10-20
created_at: 2026-10-20
updated_at: 2026-10-20
expires_at: null
supersedes: null
sensitivity: internal
applies_to: [product]
related: [agentic-integrations, stock-gnome-omakase]
---
# ADR: Theme packs — Omarchy if licensed, else original

## Status

Accepted (2026-10-20). Intake: O3 preferred, O2 fallback.

## Decision

1. **Primary:** Vendor Omarchy theme colour packs **only if** license and branding permit redistribution and re-skinning for Gnomarchi (attribute upstream; do not imply official Omarchy).
2. **Fallback:** If vendoring is not allowed or unclear, ship **original Gnomarchi packs** whose palettes are inspired by widely known schemes (Tokyo Night, Catppuccin, etc.) without copying Omarchy files or branding.

## Gate before P1 theme ship

Confirm Omarchy theme asset license (repo LICENSE / theme AUTHORS). Document the outcome in this ADR’s update. Until then, implement the theme *engine* against a minimal original set so work is not blocked.
