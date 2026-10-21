# Media weight policy (release vs working tree)

## Keep in-tree (and in the release tarball)

- `docs/screenshots/readme/*.jpg` — curated README/docs shots; ship these.

## Evidence (git OK; excluded from release tarball)

- `docs/screenshots/parity-v2/` — parity capture evidence
- `docs/screenshots/omarchy-manual/` — manual/checklist captures

These may remain tracked for development. `scripts/build-release.sh` excludes them from `dist/gnomarchi-*.tar.gz` so the distribution archive stays slim.

Also excluded from the tarball (local dumps, often gitignored): `omarchy-v1`, `parity-v1`, `parity`.

## Theme intro MP4s (optional heavy assets)

- Paths: `theme/packs/*/backgrounds/intros/*.mp4` (~90MB total)
- Keep in the working tree for overlay/theme preview.
- Do **not** ship in the release archive.
- `scripts/build-release.sh` excludes/strips `**/backgrounds/intros/*.mp4` from the staging tree before packing.
- Helper for ad-hoc staging trees: `scripts/strip-theme-intros-for-release.sh <staging-root>`

## CI

PR/push to `main` runs `python3 -m unittest discover -s tests -v` via `.github/workflows/ci.yml`.
