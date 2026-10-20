# gnomarchi packaging

Custom pacman repository is the default install path (overlay + future ISO). AUR PKGBUILDs are the fallback.

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
      PKGBUILD        # stub for AUR submission
```

## Custom repo (primary)

1. Build packages (CI or local `makepkg`).
2. Place artifacts under `repo/pkgs/`.
3. Run `./packaging/repo/build-repo.sh` to refresh `gnomarchi.db.tar.gz`.
4. Host the directory over HTTPS; clients drop `pacman-gnomarchi.conf.example` into `/etc/pacman.d/` and `Include` it from `/etc/pacman.conf`.

Signing and trust checklist: owned by T6-security. This tree does **not** publish or distribute keys.

## AUR (fallback)

`aur/gnomarchi/PKGBUILD` builds from the git sources when the custom repo is unavailable. Keep version scheme aligned with repo packages.
