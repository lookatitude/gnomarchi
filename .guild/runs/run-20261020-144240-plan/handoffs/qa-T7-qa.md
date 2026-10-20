---
schema_version: guild.handoff_receipt.v1
task_id: T7-qa
specialist: qa
participant_id: qa-1
status: done
tier: mid
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T7-qa

## changed_files

- `tests/acceptance/__init__.py`
- `tests/acceptance/_helpers.py`
- `tests/acceptance/test_registry_completeness.py`
- `tests/acceptance/test_theme_cli.py`
- `tests/acceptance/test_plugin_lifecycle.py`
- `tests/acceptance/test_overlay.py`
- `tests/acceptance/test_menu.py`
- `tests/acceptance/CHECKLIST.md`

## opens_for

- operator: manual VM overlay boot + Make-something via CHECKLIST.md (not release-ready)
- T5/ops: SigLevel Optional TrustAll residual before public mirror

## assumptions

- Registry parsed without PyYAML (line-oriented subset of features/registry.yaml)
- `python -m unittest discover -s tests` imports acceptance as package under start dir
- Manual VM steps remain operator-gated; automatable subset only in unittest

## evidence

- `python3 -m unittest discover -s tests -v` → Ran 20 tests, OK (9 acceptance + 11 prior unit)
- Registry completeness asserts every feature row has status+phase in allowed set
- Overlay wipe/destroy non-zero; bash -n; no hyprland in GNOME_PKGS/DEFAULT_APP_PKGS

## followups

- Operator: run CHECKLIST.md A/B on Arch VM before any release narrative
- Do not mark release-ready from this lane

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T7-qa",
  "tier": "mid",
  "status": "done",
  "summary": "Acceptance harness: 9 tests under tests/acceptance/ (registry, theme CLI, plugin lifecycle, overlay, menu) + CHECKLIST.md; discover -s tests → 20 OK.",
  "artifacts": [
    "tests/acceptance/",
    "tests/acceptance/CHECKLIST.md"
  ],
  "issues": [],
  "learnings": []
}
```
