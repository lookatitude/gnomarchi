# gnomarchi packaging

**Supported beta path:** GitHub Releases source tarball + AUR `PKGBUILD` with pinned `sha256sums`. Arch official packages remain the default for system updates (`features/registry.yaml` `operator_note`).

A custom pacman repository is **optional** and must be signed (packages + database `.sig`, client `SigLevel = Required`) before any public use. See `docs/security/packaging-signing.md`.

## Layout

```
packaging/
  README.md           # this file
  repo/
    pacman-gnomarchi.conf.example
    build-repo.sh     # stub: repo-add workflow
    pkgs/             # drop built .pkg.tar.zst here (gitignored in real use)
  aur/
    gnomarchi/
      PKGBUILD        # AUR submission; pinned release tarball checksums
```

## AUR / GitHub Releases (supported beta)

1. Tag and publish via `.github/workflows/release.yml` (builds `gnomarchi-<VERSION>.tar.gz` + `.sha256`).
2. Refresh PKGBUILD checksums: `./scripts/update-pkgbuild-checksums.sh` (reads `VERSION`, downloads the release asset, rewrites `sha256sums`).
3. Keep `pkgver` / `_tagver` / git tag aligned (e.g. `pkgver=0.0.1beta4`, `_tagver=0.0.1-beta.4`, tag `v0.0.1-beta.4`).
4. Live ISO `gnomarchi-<VERSION>-x86_64.iso` is built in the Release workflow and uploaded beside the source tarball.
5. PKGBUILD must install the full CLI runtime tree (`theme`/`plugin`/`common`/`apps`/…), not only `bin`+`desktop`.

## Custom repo (optional, must be signed)

1. Build packages (CI or local `makepkg`).
2. Place artifacts under `repo/pkgs/`.
3. Run `./packaging/repo/build-repo.sh` to refresh `gnomarchi.db.tar.gz`.
4. Sign packages and the database; host `.sig` files beside them.
5. Clients use `pacman-gnomarchi.conf.example` (`SigLevel = Required TrustedOnly`) after importing the operator key.

This tree does **not** publish or distribute private keys.
