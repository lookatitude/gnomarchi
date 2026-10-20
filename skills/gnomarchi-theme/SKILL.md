---
name: gnomarchi-theme
description: Create and validate gnomarchi theme packs; apply via CLI. Prefer original inspired packs; never vendor Omarchy wallpapers or claim official Omarchy.
---

# gnomarchi-theme

## When to use

Building or editing a whole-desktop theme pack for gnomarchi (GTK/CSS + colors.toml), validating it, or activating it on a machine.

## Pack layout

```
themes/<id>/
  theme.toml      # [theme] id, name, version; optional [provenance]
  colors.toml     # [colors] background, foreground, accent (+ optional)
  gtk.css         # GTK token stubs
  preview.png     # optional
```

Do **not** add `backgrounds/` without a pack-local `CREDITS` file. Never ship Omarchy wallpaper binaries. Never set `provenance.official_omarchy`.

## Commands

```bash
gnomarchi theme list
gnomarchi theme validate --id midnight-harbor
gnomarchi theme validate --path ./my-pack
gnomarchi theme set midnight-harbor
```

State lands under `$XDG_CONFIG_HOME/gnomarchi` (or `GNOMARCHI_STATE_DIR` / repo `.local-state` in tests).

## Scaffold

Copy `templates/theme/`, set `theme.id` to the directory name, fill colors, run `theme validate`, then `theme set`.

## Attribution

If a pack derives palette/config from MIT Omarchy *theme data*, note that under `[provenance]` as inspired/derived config with copyright notice — never imply partnership.
