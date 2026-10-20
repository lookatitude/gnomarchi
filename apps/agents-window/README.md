# apps/agents-window

Placeholder Agents window for gnomarchi.

## Entries

| Id | Label |
| --- | --- |
| `default-agent` | Default agent |
| `make-theme` | Make something — Theme |
| `make-plugin` | Make something — Plugin |
| `make-app` | Make something — App |

## Run

```bash
python3 apps/agents-window/agents_window.py --list
python3 apps/agents-window/agents_window.py          # GTK if PyGObject present
```

Invoke paths call into `gnomarchi agent …` (backend). Opening via bus (`org.gnomarchi.Bus`) is a later wire-up; this shell only presents the catalog.
