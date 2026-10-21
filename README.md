# gnomarchi

<p align="center">
  <img src="docs/brand/logo.png" alt="gnomarchi" width="280">
</p>

<p align="center"><strong>v0.0.1-beta.3</strong> · stock GNOME omakase for Arch</p>

**Experimental.** gnomarchi ports [Omarchy](https://omarchy.org)’s omakase Arch desktop — themes, menu, plugins, agents, and overlay install — onto **stock GNOME** instead of Hyprland/Quickshell.

**Not affiliated with Omarchy, Basecamp, or DHH.** Inspired by Omarchy’s product shape; we do not claim partnership or endorsement.

## Screenshots

<p align="center">
  <img src="docs/screenshots/readme/01-desktop.jpg" alt="gnomarchi desktop composite" width="800">
</p>

<p align="center">
  <img src="docs/screenshots/readme/02-themes.jpg" alt="Theme picker — all 24 packs" width="800">
</p>

<p align="center">
  <img src="docs/screenshots/readme/03-agents.jpg" alt="Agents window" width="390">
  <img src="docs/screenshots/readme/04-menu.jpg" alt="Super+Space menu" width="390">
</p>

<p align="center">
  <img src="docs/screenshots/readme/05-ghostty.jpg" alt="Ghostty themed terminal" width="390">
  <img src="docs/screenshots/readme/06-panel-optional.jpg" alt="Optional dash-to-panel" width="390">
</p>

More validation shots: [`docs/screenshots/parity-v2/`](docs/screenshots/parity-v2/) · Omarchy originals: [`docs/screenshots/omarchy-manual/`](docs/screenshots/omarchy-manual/) · parity map: [`docs/omarchy-manual-parity.html`](docs/omarchy-manual-parity.html)

## Quick start

On Arch with GNOME already installed:

```bash
git clone https://github.com/lookatitude/gnomarchi.git
cd gnomarchi
./install/overlay.sh
```

CLI: `gnomarchi` (`theme`, `menu`, `agent`, `notice`, `webapp`, `share`, `install`, …).

```bash
gnomarchi theme pick          # all theme packs
gnomarchi theme set tokyo-night
Super+Space                   # unified menu
```

## Install channels

**Beta.** Prefer overlay or a release tarball. Packaging and ISO paths are experimental; do not treat them as a signed production distro yet. Gaps: [`docs/parity/gaps-and-improvements.html`](docs/parity/gaps-and-improvements.html) · app substitutes: [`docs/apps/substitutes.md`](docs/apps/substitutes.md) · Shell matrix: [`docs/gnome-shell-matrix.md`](docs/gnome-shell-matrix.md).

| Channel | How |
| --- | --- |
| **Overlay** (dev / existing Arch+GNOME) | `./install/overlay.sh` |
| **Release tarball** | GitHub Releases → `gnomarchi-0.0.1-beta.3.tar.gz` |
| **AUR-style PKGBUILD** | `packaging/aur/gnomarchi/` (`makepkg -si`) — uses pinned `sha256sums` when a release asset checksum is available |
| **Custom pacman repo** | `packaging/repo/` — build pkgs, `./packaging/repo/build-repo.sh`, host mirror |
| **ISO builder** | Release asset `gnomarchi-iso-builder-0.0.1-beta.3.tar.gz` → `sudo ./build-iso.sh` (needs `archiso`); or `sudo ./scripts/build-iso.sh` from a checkout |

```bash
# From a release tag
./scripts/build-release.sh          # source archive + checksums under dist/
sudo ./scripts/build-iso.sh         # guided live ISO under iso/out/ (archiso + root)
# Optional Arch package
cd packaging/aur/gnomarchi && makepkg -si
```

## Status (v0.0.1-beta.3)

Feature gap map vs Omarchy manual: **43/43 done** on the GNOME adaptation path (Hyprland/Quickshell replaced by GNOME Shell + GDM by design). `status=done` is adaptation tracking; product readiness uses `maturity` (`adapted` \| `shipped` \| `proven`) in `features/registry.yaml`. Tracker: `features/registry.yaml` · `docs/parity/gnomarchi-gap-map.json` · honesty notes: [`docs/parity/gaps-and-improvements.html`](docs/parity/gaps-and-improvements.html).

```bash
python3 -m unittest discover -s tests
# Dual-VM adapted-parity workflows (agents/themes/panels/apps/…):
#   docs/parity/workflows-catalog.html
#   python3 scripts/parity-workflows-run.py --side both
#   python3 scripts/parity-workflows-run.py --only theme.effect,plugin.effect
#   PARITY_CAPTURE=1 ./scripts/parity-capture-theme-proof.sh   # + plugin/desktop
#   PARITY_CAPTURE=1 python3 scripts/parity-workflows-run.py --only theme.proof,plugin.live,desktop.proof
#   ./scripts/parity-dual-vm-run.sh
# Plugin Hypr→GTK plan: docs/parity/plugin-migration-plan.html
# Visual proof gallery: docs/parity/visual-proof.html
# Capture runbook: docs/parity/PROOF.md
```

## License

MIT — see [LICENSE](LICENSE). Theme pack assets keep their own credits under `theme/packs/*/CREDITS` where present.
