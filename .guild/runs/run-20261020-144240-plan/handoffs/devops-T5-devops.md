---
schema_version: guild.handoff_receipt.v1
task_id: T5-devops
specialist: devops
participant_id: devops-1
status: done
tier: mid
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T5-devops

## changed_files

- `install/overlay.sh`
- `packaging/README.md`
- `packaging/repo/pacman-gnomarchi.conf.example`
- `packaging/repo/build-repo.sh`
- `packaging/aur/gnomarchi/PKGBUILD`
- `packaging/aur/gnomarchi/.SRCINFO`
- `iso/README.md`
- `docs/install/vm-test.md`

## opens_for

- T7-qa: run `docs/install/vm-test.md` against overlay + packaging layout
- T6-security: signing/trust checklist for custom repo (SigLevel currently Optional TrustAll in example only)
- T3-backend: `bin/gnomarchi` so overlay install stage can place a real CLI

## assumptions

- Package names `ghostty`, `neovim`, `chromium`, group `gnome`, and `gdm` resolve on current Arch extra
- Theme seed pack id `midnight-harbor` exists under `theme/packs/` (present at write time)
- Full pacman install not executed here; evidence is dry-run detect + wipe refuse + bash -n

## evidence

- `GNOMARCHI_DRY_RUN=1 … overlay.sh detect` → Arch detected
- `overlay.sh wipe` → exit 1 refuse (no disk wipe)
- `bash -n install/overlay.sh` and `packaging/repo/build-repo.sh` → syntax_ok
- Files on disk under `install/`, `packaging/`, `iso/`, `docs/install/`

## followups

- T6: replace example SigLevel before any public mirror
- T7: live VM acceptance once guest snapshot available
- No Hyprland packages referenced; ISO build deferred to P8 per `iso/README.md`

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T5-devops",
  "tier": "mid",
  "status": "done",
  "summary": "Overlay, packaging stubs, ISO deferral, and VM test procedure landed for T7.",
  "artifacts": [
    "install/overlay.sh",
    "packaging/README.md",
    "packaging/repo/pacman-gnomarchi.conf.example",
    "packaging/repo/build-repo.sh",
    "packaging/aur/gnomarchi/PKGBUILD",
    "packaging/aur/gnomarchi/.SRCINFO",
    "iso/README.md",
    "docs/install/vm-test.md"
  ],
  "issues": [],
  "learnings": []
}
```
