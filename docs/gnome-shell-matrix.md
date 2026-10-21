# GNOME Shell extension matrix

Stock GNOME + GDM is the product identity. Extensions below are either seeded by the overlay or optional opt-ins. Exact GNOME Shell minor versions are **not pinned** in-repo.

## Validation status

| GNOME Shell | Status |
| ----------- | ------ |
| Version on the project Arch VM used for overlay / parity shots | **Validated** (primary test venue; see `docs/install/vm-test.md`) |
| Other GNOME majors / distro backports | **Untested** — treat upgrades as high risk for extensions |

Record the guest Shell version with: `gnome-shell --version`.

## Intended extensions

| Extension | UUID (typical) | Default | Notes |
| --------- | -------------- | ------- | ----- |
| User Themes | `user-theme@gnome-shell-extensions.gcampax.github.com` | On (overlay) | Required for gnomarchi GTK/Shell theme packs. |
| AppIndicator | `appindicatorsupport@rgcjonas.gmail.com` (or Ubuntu UUID) | On (overlay) | Tray / status indicators. |
| Caffeine | `caffeine@patapon.info` | On (overlay) | Inhibit sleep from the bar. |
| Dash to Panel | `dash-to-panel@jderose9.github.com` | Off (optional) | Bottom/side bar; install via Install › Desktop; enable with `gnomarchi shell bar-position bottom\|left\|right`. |
| PaperWM | `paperwm@paperwm.github.com` | Off (opt-in) | Tiling layouts; overlay offer defaults to **N**; Install › PaperWM tiling or `gnomarchi install tiling --yes`. |

## Upgrade risk

Shell extensions often break across GNOME major bumps (metadata `shell-version`, ABI). After `pacman -Syu`, a black screen, missing top bar, or “extension does not support shell” usually means an extension, not gnomarchi core.

PaperWM and dash-to-panel are the highest-churn optionals. User-themes breakage mainly drops the custom Shell theme while apps still run.

## Recovery

1. At GDM, log into a session and open a TTY if the Shell is wedged (`Ctrl+Alt+F3`).
2. Disable extensions: `gnome-extensions disable <uuid>` for each problematic UUID, or clear enabled list via `gsettings set org.gnome.shell enabled-extensions "[]"` then re-enable only what you need.
3. Reset gnomarchi theme: `gnomarchi theme set midnight-harbor` (or another seeded pack).
4. Relog / `killall -HUP gnome-shell` (Wayland: log out/in is safer).
5. If PaperWM was enabled and breaks navigation: `gnome-extensions disable paperwm@paperwm.github.com` — stock overview returns.

Do not treat extension breakage as a reason to install Hyprland; stay on GNOME and disable the failing UUID.
