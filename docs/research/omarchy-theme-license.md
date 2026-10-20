# Omarchy theme / branding license findings (D7)

**Lane:** T1-researcher · **Date:** 2026-10-20 · **Sources:** [basecamp/omarchy LICENSE](https://github.com/basecamp/omarchy/blob/dev/LICENSE) (MIT), [Making your own theme](https://omarchy.org/manual/making-your-own-theme/), [Theme publishing docs](https://omarchythemes.dev/docs/publishing), [Discussion #11459](https://github.com/omacom/omarchy/discussions/11459) (background/icon provenance).

## Verdict (D7 go/no-go)

| Asset class | Go/no-go | Rule for gnomarchi |
| --- | --- | --- |
| Repo software + theme *config* (`colors.toml`, btop/chromium/helix token maps, etc.) under MIT | **Conditional go** | May vendor with copyright + MIT notice retained; no “official Omarchy” claim. |
| Bundled **backgrounds** / wallpapers in `themes/*/backgrounds/` | **No-go until CREDITS** | No per-theme LICENSE/CREDITS in tree; community discussion flags unclear artist terms. Do **not** ship these binaries. |
| Third-party **application icons** under Omarchy tree | **No-go** | Product marks; no redistribution clearance. Use GNOME/app icons or original art. |
| Community theme repos (`omarchy-*-theme`) | **Per-repo** | Require each repo’s LICENSE + background credits before optional install-from-URL; never assume MIT covers images. |
| Branding / name | **No-go for affiliation** | Public name remains `gnomarchi`; forbid “official Omarchy” or Basecamp endorsement. |

**Operational D7:** Prefer **original inspired packs** for wallpapers and GTK chrome. Optionally vendor **palette/config** derived from MIT-licensed Omarchy theme *data* with attribution. Install flows may later fetch community themes at user request after license check — not as default shipped packs.

## Branding constraints

- Keep MIT notice when redistributing Software portions.
- Theme picker copy: “inspired by Omarchy palettes” only when a pack actually derives from vendored MIT config; never imply partnership.
- Drop executable/theme-side code patterns Omarchy strips on install (`.lua`, terminal configs, `vscode.json`) — gnomarchi theme packs are data + CSS/GSettings only.

## Registry gaps vs this review

Confirmed inventoried rows cover theme system at `omarchy.theme.system`. Added triage rows for background/icon provenance (see `features/registry.yaml`). No silent drop of a major Omarchy capability category vs 2026-10-20 inventory; release-notes delta check still owed at each upstream bump (sync process in consolidated plan).
