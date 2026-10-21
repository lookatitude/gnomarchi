# gnomarchi ISO (archiso)

**Status: WIP / experimental — not shipped on GitHub Releases for v0.0.1-beta.2.**

The supported install path for that release is **overlay + release tarball**
(`install/overlay.sh` / curl|bash), not a published live ISO asset.

Guided Arch live ISO (when built locally). After base install, the live session
runs `install/overlay.sh` (same stages as curl|bash overlay). System updates use
official Arch only: `gnomarchi update` → `sudo pacman -Syu` (no custom
`[gnomarchi]` repo required).

## Build (experimental)

Requires root, `archiso`, and a full `mkarchiso` run. Not part of CI.

```bash
sudo pacman -S --needed archiso
sudo ./iso/build.sh
```

`build.sh` copies archiso `releng`, appends `iso/packages.x86_64`, embeds this
repo under `/root/gnomarchi-src`, and writes `/root/gnomarchi-install.sh` which
exports `GNOMARCHI_ROOT` and runs `install/overlay.sh all`.

Output: `iso/out/gnomarchi-*.iso`

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
