---
name: gnomarchi-plugin
description: Scaffold and validate gnomarchi multi-runtime plugins. Default runtimes are overlay-app, menu-module, user-service. Shell extensions are never the default.
---

# gnomarchi-plugin

## When to use

Creating a new plugin, validating a `manifest.json`, or choosing an adapter runtime.

## Manifest

Required keys: `id`, `name`, `version`, `runtime`, `permissions` (array), `hooks` (object).

Allowed runtimes: `overlay-app` | `menu-module` | `user-service` | `status-indicator` | `gnome-shell-extension`.

`gnome-shell-extension` requires `explicit_shell_extension: true` and CLI flag `--explicit-shell-extension`.

## Commands

```bash
gnomarchi plugin scaffold my-tool --runtime overlay-app
gnomarchi plugin scaffold my-ind --runtime status-indicator
gnomarchi plugin scaffold my-ext --runtime gnome-shell-extension --explicit-shell-extension
gnomarchi plugin clone gnomarchi.agents
gnomarchi plugin validate ~/.config/gnomarchi/plugins/my-tool
gnomarchi plugin enable --id gnomarchi.weather
gnomarchi plugin list
```

## Artifacts by runtime

| Runtime | Required artifact |
| --- | --- |
| overlay-app | `app.desktop` |
| menu-module | `menu.jsonc` |
| user-service | `gnomarchi-plugin.service` |
| status-indicator | `indicator.py` + `autostart.desktop` |
| gnome-shell-extension | `metadata.json` + `extension.js` + explicit flag |

Templates live under `templates/plugin/<runtime>/`. First-party widgets live under `plugins/first-party/`.
