# VM test procedure — gnomarchi overlay

Validates Path A (`install/overlay.sh`) on Arch + stock GNOME. Consumed by T7-qa.

## Prerequisites

- Hypervisor: QEMU/KVM, VirtualBox, or cloud Arch image
- Guest: fresh Arch install (or archiso live with installed root), network, sudo
- Host checkout of this repo mounted or cloned inside the guest at e.g. `/src/gnomarchi`
- Snapshot the VM before running the overlay

## Forbidden checks

- Overlay must not pull Hyprland, SDDM, or UWSM as dependencies
- Overlay must not wipe disks; `wipe` / `destroy` subcommands refuse
- Do not publish or inject repo signing keys in this procedure (T6 owns trust)

## Procedure

1. Boot the Arch guest; confirm `ID=arch` in `/etc/os-release`.
2. Snapshot: name it `pre-overlay`.
3. Dry run:

   ```bash
   cd /src/gnomarchi
   GNOMARCHI_DRY_RUN=1 ./install/overlay.sh all
   ```

4. Install (interactive confirms, or automation):

   ```bash
   GNOMARCHI_SKIP_CONFIRM=1 GNOMARCHI_CONFIRM_DESTRUCTIVE=yes ./install/overlay.sh all
   ```

5. Verify packages: `pacman -Q gdm gnome-shell ghostty neovim chromium`
6. Verify GDM: `systemctl is-enabled gdm.service` → `enabled`
7. Verify seed: `test -f ~/.config/gnomarchi/defaults.toml` and `~/.config/gnomarchi/themes/midnight-harbor/theme.toml`
8. Reboot; at GDM choose **GNOME** (Wayland preferred); log in
9. Smoke: open Ghostty, nvim, Chromium; confirm no Hyprland session is required
10. Optional repo path: drop `packaging/repo/pacman-gnomarchi.conf.example` pointing at a local HTTP mirror of `packaging/repo/pkgs`, then re-run `./install/overlay.sh gnomarchi`

## Pass criteria

- GDM enabled; GNOME session usable after reboot
- Default app packages installed; theme pack and defaults.toml seeded
- Agent invite printed at end of overlay
- No disk wipe; no Hyprland requirement

## Fail / rollback

Revert to snapshot `pre-overlay`. Capture `journalctl -u gdm -b` and overlay stdout on failure for T7.
