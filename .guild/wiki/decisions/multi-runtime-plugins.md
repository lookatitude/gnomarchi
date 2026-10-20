---
type: decision
owner: architect
confidence: high
importance: high
source_refs:
  - docs/plans/agentic-integrations-plan.html
  - intake:2026-10-20
created_at: 2026-10-20
updated_at: 2026-10-20
expires_at: null
supersedes: null
sensitivity: internal
applies_to: [product]
related: [agentic-integrations, stock-gnome-omakase]
---
# ADR: Multi-runtime plugins (not Quickshell-only)

## Status

Accepted (2026-10-20).

## Context

Omarchy plugins are QML inside one Quickshell process. GNOME has no equivalent host.

## Decision

One `gnomarchi.plugin` manifest with runtimes: `overlay-app`, `menu-module`, `user-service`, `status-indicator`, optional `gnome-shell-extension`, plus separate `theme-pack` and `desktop-app` artifact types. Agents default to overlay-app + menu-module + service. Shell extensions are version-pinned and skill-gated.

## Consequences

- CLI `plugin enable` is runtime-aware.
- Marketplace / git-add UX can match Omarchy without sharing QML.
- Higher maintenance cost if too many first-party Shell extensions ship early — avoid that.
