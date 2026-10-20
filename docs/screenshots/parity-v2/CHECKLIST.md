# parity-v2 visual validation (re-audited)

Method: unique MD5 + open each frame for the intended feature. Venue 1920×1080, stock GNOME top bar (bottom bar only for V-27).

| ID | Verdict | Shows intended feature? | Notes |
|---|---|---|---|
| V-00 | pass | yes | Files + Ghostty + Themes + Agents under top bar |
| V-01 | pass | yes | Clean GNOME desktop, top bar, wallpaper |
| V-02 | pass* | partial | Same frame as V-01; tray cluster visible, no dedicated tray callout |
| V-03 | pass | yes | User Themes prefs; `gnomarchi` selectable |
| V-04 | fail | no | Top-bar crop only; no identifiable agents StatusNotifier glyph |
| V-05 | fail | no | Top-bar crop; weather chip not identifiable |
| V-06 | fail | no | Top-bar crop; update chip not identifiable |
| V-07 | fail | no | Top-bar crop; tailscale chip not identifiable |
| V-08 | fail | no | Opens on Install/AI list, not menu root categories |
| V-09 | pass | yes | Theme carousel Tokyo Night 22/24 |
| V-10 | pass* | partial | Same bytes as V-09 (carousel); GTK chrome change not isolated |
| V-11 | pass | yes | Ghostty alone, themed terminal |
| V-12 | pass | yes | Catppuccin 1/24 carousel (theme B) |
| V-13 | pass | yes | Desktop wallpaper for theme A |
| V-14 | pass | yes | Distinct wallpaper after `theme bg next` (hash ≠ V-22) |
| V-15 | fail | no | Same bytes as V-13; no A-vs-B panel tint compare |
| V-16 | pass | yes | Agents window alone |
| V-17 | pass | yes | Menu filtered to Install / … |
| V-18 | pass | yes | nvim editing gnomarchi README |
| V-19 | pass | yes | btop (or btop_missing terminal) |
| V-20 | pass | yes | Chromium about:blank |
| V-21 | pass* | partial | Same bytes as V-09 (picker = hotkey target) |
| V-22 | pass | yes | Second bg after another `bg next` (≠ V-14) |
| V-23 | pass | yes | GNOME Tweaks |
| V-24 | pass | yes | Terminal showing no hyprland / GNOME desktop |
| V-25 | pass | yes | gnoma-calc |
| V-26 | pass | yes | gnoma-write |
| V-27 | pass | yes | dash-to-panel bottom bar enabled (optional path) |

\* Shared frame with another ID that already proves the UI; not a silent copy of an unrelated shot.

## Dup summary (after re-capture)

- Unique files: most IDs
- Remaining shared: V-01≡V-02; V-09≡V-10≡V-21; V-13≡V-15
- Hard fails needing new evidence: V-04…V-07 (indicator glyphs), V-08 (menu root), V-15 (panel CSS A vs B)

## Next capture fixes

1. V-08: open menu with empty filter / root tree only  
2. V-04–V-07: click each StatusNotifier icon so a popup labels agents/weather/update/tailscale  
3. V-15: shot theme A panel, then theme B panel, side-by-side or sequential distinct hashes  
