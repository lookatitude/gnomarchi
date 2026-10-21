#!/usr/bin/env bash
# Optional PaperWM tiling (AUR: gnome-shell-extension-paperwm).
# Opt-in only: stock GNOME overview remains the default. Called when the user
# accepts the overlay PaperWM offer, or runs Install › PaperWM / `gnomarchi install tiling`.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/pkg.sh
source "${ROOT}/install/lib/pkg.sh"

install_arch_or_aur gnome-shell-extension-paperwm || true

if command -v gnome-extensions >/dev/null 2>&1; then
  gnome-extensions enable paperwm@paperwm.github.com 2>/dev/null || true
fi

pkg_log "PaperWM enabled (optional tiling; disable anytime via gnome-extensions disable paperwm@paperwm.github.com)"
