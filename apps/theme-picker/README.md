# apps/theme-picker

CLI-backed picker that applies a pack with `gnomarchi theme set <id>`.

When PyGObject GTK4/Adw is present later, this entry can grow a small Adw window; the apply path stays the CLI (privileged edge under `$XDG_CONFIG_HOME/gnomarchi`).

## Run

```bash
# list
python3 apps/theme-picker/gnomarchi_theme_picker.py --list

# apply
python3 apps/theme-picker/gnomarchi_theme_picker.py midnight-harbor
```

If `gnomarchi` is not on `PATH`, the script falls back to in-repo `theme.engine` for list/set during development.

## D7 copy

Do not claim official Omarchy / Basecamp affiliation. Use “inspired by Omarchy palettes” only when a pack’s provenance actually derives from vendored MIT Omarchy theme *config*.
