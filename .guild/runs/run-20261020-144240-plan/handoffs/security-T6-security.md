---
schema_version: guild.handoff_receipt.v1
task_id: T6-security
specialist: security
participant_id: security-1
status: done
tier: powerful
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T6-security

## changed_files

- `docs/security/plugin-trust.md`
- `docs/security/packaging-signing.md`
- `docs/security/findings-T3-T5.md`

## opens_for

- T3-backend: F1–F3 — confirm-on-add, no-sudo hook reject in validate, enable-after-validate
- T5-devops: F4 — overlay/repo signing UX per packaging checklist
- T7-qa: acceptance for refuse-without-confirm and refuse-sudo-hook

## assumptions

- T3 partial stubs (`plugin/lifecycle.py`) are in-flight; findings target current tree, not a finished handoff
- T5 directories exist but have no install/packaging bodies yet
- Signing crypto choices left as checklist items; no key generation in this lane

## evidence

- `docs/architecture/module-boundaries.md` plugin confirm-on-add / no silent sudo
- `.guild/spec/gnomarchi-v1.md` forbid sudo install hooks; no official Omarchy claim
- `docs/research/omarchy-theme-license.md` D7
- Grep/read: `plugin/lifecycle.py` lacks add/enable + hook policy; `bin/` `install/` empty; packaging dirs empty
- No T3/T5 handoff receipts in this run yet

## followups

- Re-review after T3 ships `plugin add|enable` and after T5 lands `install/overlay.sh` + repo key docs
- Do not weaken trust prompts in later UX polish

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T6-security",
  "tier": "powerful",
  "status": "done",
  "summary": "Plugin-trust and packaging-signing docs landed; T3/T5 findings filed for missing confirm-on-add and no-sudo hooks.",
  "artifacts": [
    "docs/security/plugin-trust.md",
    "docs/security/packaging-signing.md",
    "docs/security/findings-T3-T5.md"
  ],
  "issues": [
    "F1: plugin add confirm-on-add not implemented",
    "F2: validate does not reject sudo/escalating hooks",
    "F3: enable-after-validate incomplete",
    "F4: T5 install/packaging bodies empty"
  ],
  "learnings": [
    "Lane small: docs + gap findings only; no crypto implementation chosen"
  ]
}
```
