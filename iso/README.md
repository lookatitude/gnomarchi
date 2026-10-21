# gnomarchi ISO (archiso)

**Status (v0.0.1-beta.4):** Release workflow builds and uploads
`gnomarchi-<VERSION>-x86_64.iso` on each `v*` tag. Local builds still work with
`archiso` + root.

Guided Arch live ISO. After base install, the live session runs
`install/overlay.sh` (same stages as curl|bash overlay). System updates use
official Arch only: `gnomarchi update` → `sudo pacman -Syu`.

## Build (local)

```bash
sudo pacman -S --needed archiso
sudo ./scripts/build-iso.sh
# or: sudo ./iso/build.sh
```

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
plymouth, …). AUR-only names install after first boot via
`gnomarchi install panel|tiling` / Install menu.
