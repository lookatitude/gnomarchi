# gnomarchi ISO (archiso)

**Status (v0.0.1-beta.3):** ISO **builder** ships on GitHub Releases as
`gnomarchi-iso-builder-<VERSION>.tar.gz`. A pre-built `.iso` binary is not
uploaded (large, Arch-host build). Supported install remains overlay + source
tarball; use this builder when you want a guided live USB.

Guided Arch live ISO. After base install, the live session runs
`install/overlay.sh` (same stages as curl|bash overlay). System updates use
official Arch only: `gnomarchi update` → `sudo pacman -Syu` (no custom
`[gnomarchi]` repo required).

## Build

Requires root, `archiso`, and a full `mkarchiso` run. Not part of default CI
(validate-only: `.github/workflows/iso-validate.yml`).

From a checkout:

```bash
sudo pacman -S --needed archiso
sudo ./scripts/build-iso.sh
# or: sudo ./iso/build.sh
```

From the release asset `gnomarchi-iso-builder-*.tar.gz`:

```bash
tar xf gnomarchi-iso-builder-*.tar.gz && cd gnomarchi-iso-builder-*
sudo pacman -S --needed archiso
sudo ./build-iso.sh
```

`iso/build.sh` copies archiso `releng`, appends `iso/packages.x86_64`, embeds this
repo under `/root/gnomarchi-src`, and writes `/root/gnomarchi-install.sh` which
exports `GNOMARCHI_ROOT` and runs `install/overlay.sh all`.

Output: `iso/out/gnomarchi-*.iso` — write to USB with `dd` / Ventoy / balenaEtcher.

```bash
sudo rm -rf iso/mkarchiso-tmp iso/work-releng
```

Optional alternate seed (keeps a durable `iso/profile/` tree):

```bash
./iso/bootstrap-from-releng.sh
sudo mkarchiso -v -w /tmp/gnomarchi-iso-work -o out/ iso/profile
```

## Guided install (live)

1. Boot the ISO (UEFI recommended).
2. Install a base Arch root (`archinstall` or pacstrap into `/mnt`).
3. On the live system (or in chroot with the tree available):

```bash
/root/gnomarchi-install.sh
# or: GNOMARCHI_ISO_AUTO=1 gnomarchi-guided-install /mnt
```

## Packages

`iso/packages.x86_64` lists official Arch packages merged into releng (GNOME, GDM,
plymouth, …). AUR-only names (e.g. some Shell extensions) install after first boot
via `gnomarchi install panel|tiling` / Install menu.
