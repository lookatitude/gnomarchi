---
type: concept
confidence: medium
importance: high
source_refs:
  - docs/plans/agentic-integrations-plan.html
  - intake:2026-10-20
labels:
  concern: ops
---
# Install paths

## Path A — Overlay (first)

Install on existing Arch (prefer GNOME Wayland already present, or installer pulls `gnome` + GDM). Same pattern as Omarchy’s `curl | bash` after vanilla Arch. Stages share `install/` scripts used later by the ISO.

## Path B — ISO (second)

archiso-based image with offline mirror; guided disk/LUKS/user; chroot runs Path A stages. Build after overlay is proven.

## Order locked

D2: overlay before ISO.
