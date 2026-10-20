---
type: plan
spec: .guild/spec/gnomarchi-v1.md
team: .guild/team/gnomarchi-v1.plan.yaml
backend: subagent
created_at: 2026-10-20
approved: true
approved_at: 2026-10-20T14:56:00Z
approved_by: user:miguelp
run_id: run-20261020-144240-plan
---

# Plan: gnomarchi v1

PRD: `.guild/prd/gnomarchi-v1.md`

Product plan (feature matrix + D1–D7): `docs/plans/gnomarchi-consolidated-plan.html`

## Lane: researcher

- task-id: T1-researcher
- owner: researcher
- participant-id: researcher-1
- depends-on: []
- spine: true
- consumed-contract:
  - `docs/research/omarchy-theme-license.md` D7 go/no-go — pulled by T2-architect
  - Registry triage gap list (or confirmed none) — pulled by T2-architect
- complexity_score: 3
- tier: powerful
- scope: Confirm Omarchy theme/plugin asset license and branding constraints (D7); note any features missing from `features/registry.yaml` vs latest Omarchy release notes. Research floor: always powerful.
- success-criteria:
  - Written finding under `docs/research/omarchy-theme-license.md` with go/no-go for vendoring.
  - Registry gaps listed as new `triage` rows or confirmed none.
- autonomy-policy:
  - may act without asking: read public Omarchy/GitHub LICENSE and docs; update registry triage rows.
  - requires confirmation: committing vendored theme binary assets.
  - forbidden: claiming official Omarchy partnership.

## Lane: architect

- task-id: T2-architect
- owner: architect
- participant-id: architect-1
- depends-on: [T1-researcher]
- spine: true
- consumed-contract:
  - `docs/architecture/module-boundaries.md` — pulled by T3-backend, T4-frontend, T5-devops, T6-security
  - `features/registry.yaml` status/phase rules — pulled by T3-backend, T7-qa
  - D7 go/no-go folded into architecture — pulled by T3-backend (theme packs), T4-frontend (picker content)
- complexity_score: 3
- tier: powerful
- scope: Author module boundaries and IPC/contracts for CLI, bus, menu, theme, plugin adapters, install stages; keep registry complete vs consolidated matrix.
- success-criteria:
  - `docs/architecture/module-boundaries.md` committed with interfaces named for dependents.
  - Registry has no inventoried Omarchy row without status+phase.
- autonomy-policy:
  - may act without asking: write architecture docs under `docs/architecture/`; expand registry metadata.
  - requires confirmation: changing D1–D7 meaning.
  - forbidden: implementing production packages in this lane.

## Lane: backend

- task-id: T3-backend
- owner: backend
- participant-id: backend-1
- depends-on: [T2-architect]
- spine: true
- consumed-contract:
  - Working `bin/gnomarchi` theme/plugin CLIs + skills — pulled by T7-qa
  - Manifest validate smoke tests — pulled by T7-qa
- complexity_score: 3
- tier: mid
- scope: Implement P0–P3/P5 core — `bin/gnomarchi`, `bus/`, `plugin/` adapters, `theme/` engine stubs, skills/templates, registry sync helpers — against T2 contracts.
- success-criteria:
  - `gnomarchi theme validate|set` and `gnomarchi plugin validate|scaffold` work on a dev machine.
  - Skills `gnomarchi-theme` and `gnomarchi-plugin` present and symlinkable.
  - Unit/smoke tests for manifest validate green.
- autonomy-policy:
  - may act without asking: create files under `bin/`, `bus/`, `plugin/`, `theme/`, `skills/`, `templates/`, `features/`.
  - requires confirmation: new system-wide sudoers or pacman hooks.
  - forbidden: enabling Shell-extension runtime by default.

## Lane: frontend

- task-id: T4-frontend
- owner: frontend
- participant-id: frontend-1
- depends-on: [T2-architect]
- spine: true
- consumed-contract:
  - Menu + theme picker + Agents window runnable via bus — pulled by T7-qa
- Super+Space summon hook docs — pulled by T7-qa
- complexity_score: 2
- tier: mid
- scope: GTK4/libadwaita command palette (menu JSONC), theme picker UI, Agents window shell; summon via gnomarchi-bus.
- success-criteria:
  - Menu opens from CLI/`Super+Space` binding hook documented.
  - Theme picker can apply a pack via backend CLI.
  - Agents window shows default-agent placeholder + Make something entries.
- autonomy-policy:
  - may act without asking: create `menu/`, `apps/` GTK projects.
  - requires confirmation: Shell extension chrome.
  - forbidden: replacing GNOME panel with a custom bar.

## Lane: devops

- task-id: T5-devops
- owner: devops
- participant-id: devops-1
- depends-on: [T2-architect]
- spine: true
- consumed-contract:
  - `install/overlay.sh` + VM procedure — pulled by T7-qa
  - `packaging/` repo+AUR layout — pulled by T7-qa
- complexity_score: 3
- tier: mid
- scope: `install/overlay.sh` stages for Arch+GNOME, package lists, pacman repo + AUR packaging stubs, Ghostty/nvim/Chromium defaults (D6); ISO scaffold deferred but stubbed.
- success-criteria:
  - Overlay script installs/enables GDM+GNOME and gnomarchi packages from a local/repo path in a documented test VM procedure.
  - Packaging layout for custom repo + AUR documented under `packaging/`.
- autonomy-policy:
  - may act without asking: write `install/`, `packaging/`, `iso/` stubs.
  - requires confirmation: publishing repo keys or destroying disks.
  - forbidden: requiring Hyprland packages.

## Lane: security

- task-id: T6-security
- owner: security
- participant-id: security-1
- depends-on: [T2-architect]
- complexity_score: 2
- tier: powerful
- scope: Threat notes for unsandboxed plugins, theme attribution, packaging integrity; review plugin add confirm/validate path. Tier pinned powerful for correctness sensitivity.
- success-criteria:
  - `docs/security/plugin-trust.md` and packaging/signing checklist committed.
  - Findings filed against T3/T5 if confirm-on-add or no-sudo-hook rules are missing.
- autonomy-policy:
  - may act without asking: write security docs; comment on PRs/lanes.
  - requires confirmation: changing crypto/signing implementation choices.
  - forbidden: weakening plugin trust prompts.

## Lane: qa

- task-id: T7-qa
- owner: qa
- participant-id: qa-1
- depends-on: [T3-backend, T4-frontend, T5-devops]
- complexity_score: 2
- tier: mid
- scope: Acceptance harness for overlay boot, registry completeness, theme set, plugin scaffold, Make-something smoke.
- success-criteria:
  - `tests/acceptance/` (or documented checklist + automatable subset) covers spec success criteria.
  - Failures block `/guild:build` completion narrative.
- autonomy-policy:
  - may act without asking: add tests under `tests/`.
  - requires confirmation: marking release-ready.
  - forbidden: skipping registry completeness check.
