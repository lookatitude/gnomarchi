# gnomarchi module boundaries

**Lane:** T2-architect · **Consumers:** T3-backend, T4-frontend, T5-devops, T6-security, T7-qa  
**Inputs:** `.guild/spec/gnomarchi-v1.md`, `docs/plans/gnomarchi-consolidated-plan.html`, T1 `docs/research/omarchy-theme-license.md` (D7)

## Identity constraints (non-negotiable)

- D1: stock GNOME session (GDM); no custom bar, no tiling-first identity.
- D2: multi-runtime plugins; Shell extensions last / version-pinned.
- D7: theme **config** may follow MIT Omarchy data with attribution; **no** vendored Omarchy backgrounds/icons; no official affiliation.

## Tree

```
gnomarchi/
  bin/gnomarchi              # CLI entry (theme|plugin|menu|install|update|agent)
  bus/                       # gnomarchi-bus D-Bus service + client lib
  menu/                      # GTK4/libadwaita palette; JSONC menu defs
  theme/                     # pack schema, validate, emitters (GSettings/CSS/apps)
  plugin/adapters/           # overlay-app | menu-module | user-service | status-indicator | gnome-shell-extension
  apps/                      # Agents window, theme picker shells
  skills/ + templates/       # agent skills + Make-something scaffolds
  features/registry.yaml     # parity tracker (native|port|adapt|rebuild|defer|triage|done)
  install/                   # overlay.sh stages
  packaging/                 # custom pacman repo + AUR
  iso/                       # deferred P8
  tests/acceptance/
```

## Interfaces dependents implement against

### `gnomarchi` CLI (`bin/`)

| Command group | Contract | Owner lane |
| --- | --- | --- |
| `theme validate \| set \| list` | Pack dir + `theme.toml` / `colors.toml`; emitters idempotent | T3 |
| `plugin validate \| scaffold \| add \| enable \| list` | Manifest JSON schema; confirm-on-add; no default Shell-extension runtime | T3 |
| `menu open \| reload` | Talks to bus → menu process | T3 + T4 |
| `bus` / status | Session bus name `org.gnomarchi.Bus` (provisional) | T3 |
| `install` / overlay helpers | Invokes `install/overlay.sh` stages; no disk wipe without confirm | T5 |
| `agent` / Make-something hooks | Invokes skills via mise; no silent sudo | T3 |

### `gnomarchi-bus` (`bus/`)

- **Purpose:** summon menu, theme apply events, plugin enable signals, Agents window open.
- **Transport:** session D-Bus; JSON payloads for non-primitive args.
- **Rule:** UI never shells out with user secrets; CLI is the privileged edge for pack writes under `$XDG_CONFIG_HOME/gnomarchi`.

### Menu (`menu/`)

- GTK4 + libadwaita command palette.
- Menu tree from JSONC (`menu/*.jsonc`); modules register via `menu-module` adapter.
- Summon: CLI + documented `Super+Space` GNOME custom keybinding hook (Settings deep link / dconf snippet — not a Shell extension in P2).

### Theme engine (`theme/`)

- Pack layout: `themes/<id>/{theme.toml,colors.toml,gtk.css,preview.png,...}`.
- Emitters: GNOME Shell/GTK, Ghostty, nvim colorscheme stub, Chromium theme hint where feasible.
- **D7:** ship original inspired packs for imagery; optional `provenance.omarchy_palette` attribution when config derives from MIT Omarchy theme data.

### Plugin adapters (`plugin/adapters/`)

| Runtime | Artifact | Enable path |
| --- | --- | --- |
| overlay-app | Desktop entry + binary/script | XDG apps + optional autostart |
| menu-module | JSONC fragment + optional helper | Merged into menu tree |
| user-service | systemd `--user` unit | `systemctl --user enable` after validate |
| status-indicator | StatusNotifierItem / AppIndicator | optional |
| gnome-shell-extension | UUID + metadata | **P7 only**; off by default |

Manifest must declare `runtime`, `permissions[]`, `hooks`, and refuse unknown runtimes.

### Install / packaging (`install/`, `packaging/`)

- Overlay stages: packages → GNOME session → gnomarchi packages → defaults (Ghostty, nvim, Chromium) → theme seed → agent invite.
- Custom pacman repo primary; AUR PKGBUILD fallback.
- Signing / trust checklist owned by T6; hooks must not escalate without confirm (T3/T5).

## Registry rules

- Every inventoried Omarchy capability has `status` + `phase` in `features/registry.yaml`.
- Allowed status: `native|port|adapt|rebuild|defer|triage|done`.
- Sync process: consolidated plan §Future improvements; no silent drops on upstream release notes.

## Spine contracts (for execute-plan verify)

Pulled by dependents:

1. This file — T3, T4, T5, T6
2. `features/registry.yaml` status/phase rules — T3, T7
3. D7 decision from T1 research — T3 (packs), T4 (picker copy/content)
