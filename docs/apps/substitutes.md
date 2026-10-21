# Omarchy-like apps → gnomarchi substitutes

gnomarchi keeps Omarchy muscle-memory names in places, but the backends are Arch/GNOME-friendly substitutes — not the Omarchy apps themselves. See Trigger menu labels (they say “substitute”).

| Omarchy-like name | gnomarchi substitute | Expectation gap |
| ----------------- | -------------------- | --------------- |
| Hype | mpv (via `gnomarchi app hype` / gnoma-hype) | URL/file launcher around mpv; not Hype’s full media UI or playlist chrome. |
| Signed | Xournal++ (`xournalpp`; Evince for plain PDF) | Annotation/fill via Xournal++; not Signed’s exact workflow or branding. |
| Herdr | tmux (`gnomarchi herdr attach`) | Agent session attach over tmux; not a dedicated Herdr TUI or Omarchy layout pack. |
| Cliamp | cmus (`gnomarchi cliamp`) | Terminal music player wrapper; not Cliamp’s Omarchy-integrated player UX. |
| Monologue | whisper and/or ffmpeg (`gnomarchi app monologue`) | Dictation notepad with optional whisper; falls back to mic→WAV for later transcription — not always live Omarchy Monologue parity. |

Install paths for packages: Install › GUI (Xournal++), Install › Dev › Shell/TUI tools (tmux), or overlay defaults (mpv). Details: `docs/gnome-shell-matrix.md` for Shell extensions only.
