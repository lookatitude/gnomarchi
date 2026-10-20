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

`gnome-shell-extension` requires `explicit_shell_extension: true` and is **not** offered by `plugin scaffold`.

## Commands

```bash
gnomarchi plugin scaffold my-tool --runtime overlay-app
gnomarchi plugin validate ~/.config/gnomarchi/plugins/my-tool
gnomarchi plugin list
```

## Artifacts by runtime

| Runtime | Required artifact |
| --- | --- |
| overlay-app | `app.desktop` |
| menu-module | `menu.jsonc` |
| user-service | `gnomarchi-plugin.service` |

Templates live under `templates/plugin/<runtime>/`.
