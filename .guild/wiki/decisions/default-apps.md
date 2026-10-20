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
applies_to: [product]
related: [stock-gnome-omakase]
---
# ADR: Default apps — Ghostty, Neovim, Chromium

## Status

Accepted (2026-10-20). Intake O3.

## Decision

Omakase defaults: **Ghostty** (terminal), **Neovim** (editor), **Chromium** (browser). GNOME Console / Text Editor / Epiphany remain installable; they are not the system defaults.

## Consequences

- Theme emitters and hotkeys target Ghostty + nvim + Chromium first.
- `xdg-terminal-exec` / GSettings default terminal → Ghostty.
- Agent and tmux/herdr integrations assume a capable terminal (Ghostty).
