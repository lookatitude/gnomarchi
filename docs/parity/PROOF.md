# Visual proof capture

Gallery: [visual-proof.html](visual-proof.html) · shots under `docs/screenshots/parity-proof/{theme,plugins,desktop}/`.

```bash
# Config assertions only (no VNC)
python3 scripts/parity-workflows-run.py --side gnomarchi --only theme.effect,plugin.effect

# With screenshot capture (needs guest SSH + VNC :5901)
PARITY_CAPTURE=1 ./scripts/parity-capture-theme-proof.sh
PARITY_CAPTURE=1 ./scripts/parity-capture-plugin-proof.sh
PARITY_CAPTURE=1 ./scripts/parity-capture-desktop-proof.sh

# Or gate capture steps inside catalog workflows
PARITY_CAPTURE=1 python3 scripts/parity-workflows-run.py --side gnomarchi --only theme.proof,plugin.live,desktop.proof
```

Missing jpgs = pending capture, not proven.
