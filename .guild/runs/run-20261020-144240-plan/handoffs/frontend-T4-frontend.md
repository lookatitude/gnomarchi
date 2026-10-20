---
schema_version: guild.handoff_receipt.v1
task_id: T4-frontend
specialist: frontend
participant_id: frontend-1
status: done
tier: mid
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T4-frontend

## changed_files

- `menu/default.jsonc`
- `menu/jsonc.py`
- `menu/palette.py`
- `menu/__init__.py`
- `menu/__main__.py`
- `menu/README.md`
- `apps/theme-picker/gnomarchi_theme_picker.py`
- `apps/theme-picker/README.md`
- `apps/theme-picker/__main__.py`
- `apps/agents-window/agents_window.py`
- `apps/agents-window/README.md`
- `docs/menu-super-space.md`

## opens_for

- T3-backend: wire `gnomarchi menu open|reload` → palette / bus; keep theme list/set contract used by picker
- T7-qa: acceptance for menu dump, theme-picker apply, agents `--list`, Super+Space doc presence

## assumptions

- PyGObject Gtk4/Adw absent on this host → stub path is the verified runtime; GTK branches unexecuted here
- D7: picker/docs avoid official Omarchy affiliation; default pack is original-inspired

## evidence

- `PYTHONPATH=. python3 -m menu --dump` → Install/Setup/Style/Trigger leaf ids
- `python3 apps/theme-picker/gnomarchi_theme_picker.py --list` → midnight-harbor; `.py midnight-harbor` → active-theme written
- `python3 apps/agents-window/agents_window.py --list` → default-agent + Make something entries
- `HAS_GTK False` on verify host

## followups

- T3: `menu` CLI group not yet in `bin/gnomarchi` (only theme|plugin at verify time)
- Bus open for Agents window / menu summon still provisional (`org.gnomarchi.Bus`)

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T4-frontend",
  "tier": "mid",
  "status": "done",
  "summary": "Menu JSONC+stub palette, theme-picker via theme set, agents placeholder, Super+Space dconf docs shipped.",
  "artifacts": [
    "menu/",
    "apps/theme-picker/",
    "apps/agents-window/",
    "docs/menu-super-space.md"
  ],
  "issues": [],
  "learnings": [
    "PyGObject missing → stub+JSONC is the shippable P2 path; GTK code gated on HAS_GTK"
  ]
}
```
