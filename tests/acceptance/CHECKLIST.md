# Manual acceptance checklist (T7-qa)

Automatable subset lives under `tests/acceptance/`. This document covers VM overlay boot and Make-something only.

## A. Overlay boot (Arch VM)

Prerequisites and stages: `docs/install/vm-test.md`.

1. Snapshot guest as `pre-overlay`.
2. Dry-run: `GNOMARCHI_DRY_RUN=1 ./install/overlay.sh all`
3. Apply: `GNOMARCHI_SKIP_CONFIRM=1 GNOMARCHI_CONFIRM_DESTRUCTIVE=yes ./install/overlay.sh all`
4. Confirm: GDM enabled; `gnome-shell`, Ghostty, Neovim, Chromium installed; no Hyprland session required.
5. Reboot → GNOME (Wayland) login → open Ghostty / nvim / Chromium.
6. Confirm agent invite printed; theme seed under `~/.config/gnomarchi/themes/`.
7. On failure: revert snapshot; capture overlay stdout + `journalctl -u gdm -b`.

Pass: GNOME session usable; defaults present; wipe/destroy still refuse; no Hyprland dep.

## B. Make something (theme + plugin)

On a machine with `bin/gnomarchi` on `PATH` (or invoke via `python3 bin/gnomarchi`).

1. Theme: `gnomarchi theme validate --id midnight-harbor` then `gnomarchi theme set midnight-harbor` (or Theme picker from menu Style).
2. Menu: summon palette (`gnomarchi menu` / Super+Space per `docs/menu-super-space.md`); open Trigger → Make something….
3. Plugin skill path: scaffold overlay-app → `plugin validate` → `plugin add` (must prompt; refuse on `n`) → `plugin add --confirm` → `plugin enable`.
4. Agents window shows default-agent placeholder + Make something entries.

Pass: theme active; plugin enabled after validate+confirm; no silent add; sudo hooks rejected by validate.

## Out of scope here

- Marking release-ready (operator confirmation only).
- Public repo SigLevel tightening (T5 residual / T6 packaging-signing).
