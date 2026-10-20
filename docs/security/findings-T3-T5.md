# Findings: T3 / T5 vs plugin trust controls

**Lane:** T6-security · **Date:** 2026-10-20 · **Against:** T3 tree + T5 install/packaging  
**Remediation:** F1–F3 closed 2026-10-20 post-T6 (orchestrator follow-up)

## Summary

| ID | Status | Notes |
| --- | --- | --- |
| F1 confirm-on-add | **closed** | `gnomarchi plugin add` + summary; default no; `--confirm` after print |
| F2 no-sudo hooks | **closed** | `check_hooks_no_sudo` in validate |
| F3 enable-after-validate | **closed** | `plugin enable` validates first; Shell-extension refused |
| F4 T5 packaging/overlay | **partial** | Overlay confirms + wipe refuse landed; SigLevel Optional TrustAll still weak for prod |

## F1 — T3: confirm-on-add (closed)

- Implemented: `plugin/lifecycle.py` `add_plugin`, CLI `plugin add`.

## F2 — T3: no-sudo / dangerous-hook reject (closed)

- Implemented: validate errors on sudo/pkexec/system paths/package managers in hooks.

## F3 — T3: enable-after-validate (closed)

- Implemented: `enable_plugin` → validate then adapter `enable_stub`; Shell-extension blocked.

## F4 — T5: packaging / overlay trust surface (partial)

- Closed: `install/overlay.sh` confirm gates; wipe/destroy refused; no Hyprland; packaging stubs without key publish.
- Residual: `packaging/repo/pacman-gnomarchi.conf.example` uses `SigLevel = Optional TrustAll` — tighten to required signatures before public repo (see `docs/security/packaging-signing.md`).

## Opens

- T5/ops: tighten SigLevel before publishing a public mirror
- T7: acceptance for refuse-without-confirm, refuse-sudo-hook, overlay wipe refuse, registry completeness
