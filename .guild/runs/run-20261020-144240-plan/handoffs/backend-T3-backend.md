---
schema_version: guild.handoff_receipt.v1
task_id: T3-backend
specialist: backend
participant_id: backend-1
status: done
tier: mid
host:
  selected: cursor
  degraded: false
  independence: weak
---

# Handoff: T3-backend

## changed_files

- `bin/gnomarchi`
- `common/__init__.py`, `common/paths.py`
- `theme/__init__.py`, `theme/paths.py`, `theme/engine.py`
- `theme/packs/midnight-harbor/{theme.toml,colors.toml,gtk.css}`
- `plugin/__init__.py`, `plugin/lifecycle.py`
- `plugin/adapters/{__init__.py,overlay_app.py,menu_module.py,user_service.py}`
- `bus/{__init__.py,README.md,client.py,server.py}`
- `skills/gnomarchi-theme/SKILL.md`, `skills/gnomarchi-plugin/SKILL.md`
- `templates/theme/*`, `templates/plugin/{overlay-app,menu-module,user-service}/*`
- `tests/test_theme_validate.py`, `tests/test_plugin_validate.py`

## opens_for

- T4-frontend: menu/apps summon via bus stub + theme set CLI
- T6-security: plugin trust / confirm-on-add path still stubbed
- T7-qa: acceptance against working theme/plugin CLIs + smoke tests

## assumptions

- State dir: `GNOMARCHI_STATE_DIR` > `$XDG_CONFIG_HOME/gnomarchi` > repo `.local-state`
- Bus uses Unix-socket fallback until real session D-Bus lands
- `plugin add|enable` and menu/agent CLI groups deferred past this stub

## evidence

- `python3 -m unittest discover -s tests -v` → 8 OK
- CLI smoke: `theme list|validate|set`, `plugin scaffold|validate|list` green

## followups

- T6: confirm-on-add / no silent sudo for plugin enable
- T4: wire menu summon to `bus` Ping/SummonMenu
- Real D-Bus `org.gnomarchi.Bus` replace socket stub when desktop pieces land

```guild.handoff.v2
{
  "schema_version": "guild.handoff.v2",
  "task_id": "T3-backend",
  "tier": "mid",
  "status": "done",
  "summary": "P0–P3/P5 stubs: bin/gnomarchi theme|plugin CLIs, midnight-harbor pack, plugin adapters/scaffold, bus socket stub, skills/templates, 8 smoke tests green.",
  "artifacts": [
    "bin/gnomarchi",
    "theme/packs/midnight-harbor",
    "plugin/adapters",
    "bus/",
    "skills/gnomarchi-theme/SKILL.md",
    "skills/gnomarchi-plugin/SKILL.md",
    "tests/test_theme_validate.py",
    "tests/test_plugin_validate.py"
  ],
  "issues": [],
  "learnings": []
}
```
