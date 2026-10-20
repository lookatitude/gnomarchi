# Super+Space → gnomarchi menu (GNOME custom keybinding)

Summon the command palette with **Super+Space** using a **GNOME Settings custom shortcut**, not a Shell extension and not a custom panel/bar.

Architecture: `docs/architecture/module-boundaries.md` (Menu · Summon).

## Prerequisite

- `gnomarchi menu open` on `PATH` (or the absolute path to the menu launcher).
- Until the CLI lands, use the stub:

  ```bash
  env PYTHONPATH=/path/to/gnomarchi python3 -m menu --stub
  ```

  Prefer the non-stub GTK path once PyGObject Gtk4/Adw is installed (`python3 -m menu`).

## dconf snippet

Replace the binding name / command if you already use custom slots. Indices start at `custom0`.

```bash
# 1) Register a custom keybinding path
dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings \
  "['/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/']"

# 2) Name, command, Super+Space
dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/name \
  "'gnomarchi menu'"
dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/command \
  "'gnomarchi menu open'"
dconf write /org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom0/binding \
  "'<Super>space'"
```

GUI alternative: **Settings → Keyboard → Keyboard Shortcuts → View and Customize Shortcuts → Custom Shortcuts → +**.

## Conflicts

GNOME may already bind Super+Space (input source switching). Free that shortcut first, or pick another binding (e.g. `<Super><Alt>space`) in the same custom slot.

## Out of scope

- Shell extension chrome
- Replacing the GNOME top bar / panel
- Hyprland or other WM binds
