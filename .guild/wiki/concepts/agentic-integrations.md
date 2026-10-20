---
type: concept
confidence: high
importance: high
source_refs:
  - docs/plans/agentic-integrations-plan.html
  - intake:2026-10-20
labels:
  concern: architecture
---
# Agentic integrations

Gnomarchi keeps Omarchy’s loop: **skills → default agent → typed artifact → CLI lifecycle → Make something**, not Quickshell QML.

## Surfaces

- **Themes** — data only (`colors.toml` + emitters); fan-out via `gnomarchi theme set`.
- **Plugins** — multi-runtime manifest; prefer overlay-app + menu-module + user-service; Shell extensions last.
- **Apps** — `gnomarchi-app` skill (GTK4/libadwaita preferred); theme watcher on state dir.
- **Menu modules** — JSONC fragments agents can append safely.
- **Skills** — `gnomarchi-os`, `-theme`, `-plugin`, `-app`, `-menu`, `-diagnose-crash`, `-extension-gnome`.

## Trust

Themes filtered. Plugins unsandboxed: confirm on add, validate, no install hooks, no sudo. Reserved `gnomarchi.*` ids for first-party.
