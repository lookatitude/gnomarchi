# Plugin trust model

**Lane:** T6-security · **Consumers:** T3-backend, T4-frontend, T7-qa  
**Inputs:** `docs/architecture/module-boundaries.md`, `.guild/spec/gnomarchi-v1.md` (forbid sudo install hooks), D7 theme rules

## For users (short)

Plugins are **arbitrary code** in your session. Before install:

1. `gnomarchi plugin add <path>` prints id, source, runtime, permissions, and hooks, then asks **Add this plugin? [y/N]** (default no). Use `--confirm` only after you have seen that summary (agents/scripts).
2. `gnomarchi plugin enable` always re-validates; it refuses unsafe hooks and Shell-extension runtimes unless the manifest opts in.
3. Themes are data; plugins are not — never expect silent plugin install from the menu or bus.

Full rules below. gnomarchi is not official Omarchy / Basecamp.

## Threat posture

Plugins run **unsandboxed** in the user session (overlay apps, menu helpers, systemd `--user` units, optional Shell extensions). Treat every third-party plugin as arbitrary code with the user’s privileges. Themes are data-only and may auto-apply after validate; plugins must not.

gnomarchi is **not** official Omarchy / Basecamp. Do not imply partnership in trust prompts or plugin metadata.

## Required controls (non-negotiable)

### 1. Confirm-on-add

`gnomarchi plugin add` (clone / copy / install-from-path) MUST:

1. Show plugin `id`, source path/URL, `runtime`, `permissions[]`, and any declared `hooks`.
2. Require an explicit interactive yes (or `--confirm` for scripted agents after the same summary is printed).
3. Refuse silent add from agents, menus, or bus signals.

Default answer is **no**. Never weaken this prompt to “Y to continue” defaults or skip-on-CI flags that ship to users.

### 2. Validate before enable

`gnomarchi plugin enable` MUST call `plugin validate` first and abort on any error.

Validate MUST enforce:

- Known `runtime` only (`overlay-app` | `menu-module` | `user-service` | `status-indicator` | `gnome-shell-extension`).
- `permissions[]` and `hooks` present and well-typed.
- Adapter artifact checks (desktop entry, unit, menu fragment, etc.).
- `gnome-shell-extension` never on the default enable path (P7; requires explicit opt-in fields).

Scaffold / list without enable is fine; enable is the privilege boundary.

### 3. No-sudo hooks

Plugin manifests MUST NOT declare install/enable hooks that escalate to root.

Refuse (validate error) any hook that:

- Invokes `sudo`, `pkexec`, or polkit privilege prompts.
- Writes under `/etc`, `/usr`, or other system paths.
- Installs pacman hooks, sudoers fragments, or system-wide systemd units.
- Runs package managers as root.

Allowed: user-scoped actions after confirm (`systemctl --user`, XDG autostart, menu merge under `$XDG_CONFIG_HOME/gnomarchi`).

Agent / Make-something skills follow the same rule: no silent sudo.

## Trust split vs themes

| Artifact | Apply path | User confirm |
| --- | --- | --- |
| Theme pack (data + CSS/GSettings) | `theme validate` then `theme set` | Not required for trusted local packs; still no Omarchy binary assets without D7 clearance |
| Plugin (code) | confirm-on-add → validate → enable | Required on add; enable blocked if validate fails |

## First-party ids

Reserve `gnomarchi.*` plugin ids for first-party packages from the signed custom repo. Third-party plugins must not claim that prefix.

## Review checklist (T3 / T7)

- [ ] `plugin add` prints summary and requires confirm
- [ ] `plugin enable` refuses invalid manifests
- [ ] Validate rejects sudo / system-path / pacman-hook declarations
- [ ] Shell-extension runtime off by default
- [ ] Trust UX copy never says “official Omarchy”
