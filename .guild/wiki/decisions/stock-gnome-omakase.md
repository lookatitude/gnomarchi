---
type: decision
owner: architect
confidence: high
importance: high
source_refs:
  - intake:2026-10-20
  - docs/omarchy-to-gnome-comparison.html
created_at: 2026-10-20
updated_at: 2026-10-20
expires_at: null
supersedes: null
sensitivity: internal
applies_to: [product]
related: [agentic-integrations, install-paths]
---
# ADR: Stock GNOME, slightly omakase’d

## Status

Accepted (2026-10-20).

## Context

Q1 from the Omarchy→GNOME comparison asked whether the default feel should be Omarchy-like Super chords on PaperWM or softer stock GNOME.

## Decision

**Stock GNOME slightly omakase’d.** Use GNOME Shell chrome and Settings/Quick Settings; add curated defaults (apps, themes, menu, agent stack). Do not make aggressive tiling the identity.

## Consequences

- PaperWM/Forge are optional profiles, not the v1 default metaphor.
- Custom bar/Quickshell clones are out of scope; StatusNotifier + GTK overlays instead.
- Hotkey table should not fight Shell’s Super conventions aggressively.
