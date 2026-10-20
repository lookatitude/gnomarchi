---
schema_version: guild.handoff_receipt.v1
task_id: T1-researcher
specialist: researcher
participant_id: researcher-1
status: done
tier: powerful
forced_floor_reason: research_always_hard
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T1-researcher

## changed_files

- `docs/research/omarchy-theme-license.md`
- `features/registry.yaml`

## opens_for

- T2-architect: D7 conditional go (MIT theme config + attribution); no-go backgrounds/icons/affiliation
- T3-backend / T4-frontend: original inspired wallpaper packs; optional MIT palette attribution only

## assumptions

- Root MIT covers software and theme config text, not image binaries without CREDITS
- Discussion #11459 does not clear wallpaper redistribution

## evidence

- https://raw.githubusercontent.com/basecamp/omarchy/dev/LICENSE
- https://omarchy.org/manual/making-your-own-theme/
- https://omarchythemes.dev/docs/publishing
- https://github.com/omacom/omarchy/discussions/11459

## followups

- Re-check CREDITS on next Omarchy release before reopening vendoring

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T1-researcher",
  "tier": "powerful",
  "status": "done",
  "summary": "D7: conditional go for MIT theme config with attribution; no-go for backgrounds, app icons, and official Omarchy affiliation. Two triage registry rows added.",
  "artifacts": [
    "docs/research/omarchy-theme-license.md",
    "features/registry.yaml"
  ],
  "issues": [],
  "learnings": [
    "Omarchy theme backgrounds lack per-theme CREDITS; do not vendor imagery"
  ]
}
```
