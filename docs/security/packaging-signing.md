# Packaging signing and AUR trust checklist

**Lane:** T6-security · **Consumers:** T5-devops, T7-qa  
**Inputs:** `docs/architecture/module-boundaries.md` (custom repo primary, AUR fallback), `.guild/wiki/decisions/package-distribution.md`

## Goal

Users installing gnomarchi via the custom pacman repo (default) or AUR (fallback) can verify package integrity and know what trust they are granting. Publishing keys and repos requires human confirmation (spec autonomy policy).

## Custom pacman repo (primary)

### Key material

- [ ] Generate a dedicated signing key for the gnomarchi repo (or project org); do not reuse personal day-to-day keys long-term without documented separation.
- [ ] Store private key offline / HSM / CI secret with least privilege; never commit private keys or passphrases.
- [ ] Publish the public key fingerprint in install docs and on a second channel (site / signed announcement).
- [ ] Document key rotation and revocation (how users remove a compromised key from `pacman-key`).

### Repo layout

- [ ] Every package in the repo is signed (`.sig` / database signature per project pacman policy).
- [ ] `repo-add` / database updates are signed; clients verify with `SigLevel` appropriate for a third-party repo (at least `Required` for packages from this repo once published).
- [ ] Mirror / local file:// test repos used in VM procedures are labeled as **unsigned test** or use a disposable test key — never instruct users to set `SigLevel = Never` for production.

### Install UX

- [ ] Overlay / docs show the exact `pacman-key --recv-keys` / `--lsign-key` (or local import) steps and the expected fingerprint.
- [ ] First-time repo enable requires explicit user confirm (no silent append to `pacman.conf` without notice).
- [ ] `gnomarchi update` prefers the custom repo; failures fall back with a clear message, not silent unsigned AUR installs.

## AUR fallback

- [ ] PKGBUILDs live under `packaging/aur/`; source URLs pin commits or release tags where possible.
- [ ] Document that AUR trust is **user-reviewed build from source**, not the same as the signed custom repo.
- [ ] Maintainers: no `sudo` in `package()` beyond standard makepkg; no post-install hooks that escalate without pacman’s normal flow.
- [ ] CI validates PKGBUILD syntax / `namcap` (or equivalent) before publish; humans review source checksums on version bumps.
- [ ] AUR package description must not claim official Omarchy affiliation.

## Overlay / install hooks (T5)

- [ ] `install/overlay.sh` stages must not wipe disks without confirm.
- [ ] Pacman / systemd hooks shipped by gnomarchi packages must not escalate without an interactive confirm path documented for operators.
- [ ] Plugin packages in the repo still obey `docs/security/plugin-trust.md` (no sudo plugin hooks).

## Theme / branding integrity (D7)

- [ ] Shipped theme packs: original imagery or MIT config with attribution only; no vendored Omarchy backgrounds/icons without CREDITS clearance.
- [ ] Packaging metadata and repo README: product name `gnomarchi`; forbid “official Omarchy” wording.

## Pre-publish gate

Before publishing a remote repo key or production mirror: operator confirmation recorded; fingerprint published; SigLevel documented; AUR PKGBUILD checksums match tagged sources.
