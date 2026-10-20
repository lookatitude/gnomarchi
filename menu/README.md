# menu — gnomarchi command palette

GTK4 + libadwaita palette when PyGObject (`gi`) with Gtk 4 / Adw 1 is installed.
Otherwise `palette.py` runs a documented **CLI stub** that loads the same JSONC tree a future GTK app will use.

## Files

| Path | Role |
| --- | --- |
| `default.jsonc` | Install / Setup / Style / Trigger skeleton |
| `jsonc.py` | JSONC → dict |
| `palette.py` | GTK window or stub; `--dump` for non-interactive list |

## Run

```bash
# from repo root
PYTHONPATH=. python -m menu --dump
PYTHONPATH=. python -m menu --stub   # interactive stub
```

Summon in a GNOME session: custom keybinding calling `gnomarchi menu open` — see `docs/menu-super-space.md`. Not a Shell extension; no custom panel/bar.

## JSONC contract

Top-level: `version`, `id`, `label`, `entries[]`. Each entry has `id`, `label`, optional `children`, or a leaf `action`:

- `{ "type": "cli", "argv": ["…"] }`
- `{ "type": "stub", "message": "…" }`
- `{ "type": "open", "path": "…" }`

Menu-module plugins merge additional JSONC fragments (backend adapter; out of scope for this package’s loader stub).
