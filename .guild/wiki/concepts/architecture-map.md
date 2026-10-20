---
type: concept
confidence: low
importance: medium
source_refs:
  - .guild/indexes/codebase-map.json
  - docs/plans/agentic-integrations-plan.html
labels:
  concern: architecture
---
# Architecture map (stub)

**Confidence: low** — greenfield. Cheap scan found 2 HTML design files only; no application modules, import graph, or runtime entrypoints.

## Planned shape (design-doc inferred, not observed in code)

| Layer | Planned home | Status |
| --- | --- | --- |
| CLI | `bin/gnomarchi` | not started |
| D-Bus bus | `bus/` (`gnomarchi-bus`) | not started |
| Menu UI | `menu/` (GTK palette + JSONC) | not started |
| Theme engine | `theme/` | not started |
| Plugin lifecycle + adapters | `plugin/adapters/` | not started |
| Agent skills + templates | `skills/`, `templates/` | not started |
| Overlay / ISO install | `install/`, `iso/` | not started |
| Desktop session | stock GNOME + GDM | not started |

## Observed repo layout

- `docs/omarchy-to-gnome-comparison.html` — Omarchy vs GNOME comparison
- `docs/plans/agentic-integrations-plan.html` — agentic integrations plan
- `.guild/` — Guild init (this phase)

Deep knowledge-graph and onboarding tour are **deferred** (no `--learn` / `auto_learn`).
