---
type: decision
owner: architect
confidence: high
importance: high
source_refs:
  - intake:2026-10-20
created_at: 2026-10-20
updated_at: 2026-10-20
expires_at: null
supersedes: null
sensitivity: internal
applies_to: [product, ops]
related: [install-paths]
---
# ADR: Package distribution — repo + AUR

## Status

Accepted (2026-10-20). Intake O3.

## Decision

Ship a **custom pacman repository** as the default path for overlay and ISO installs. Also publish **AUR** PKGBUILDs as a fallback for users who prefer building from source or do not add the repo.

## Consequences

- ISO/offline mirror and `gnomarchi update` target the custom repo first.
- AUR packages must stay compatible with the same version scheme; CI should build both or at least validate PKGBUILDs.
