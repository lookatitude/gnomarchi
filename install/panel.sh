#!/usr/bin/env bash
# Install dash-to-panel + caffeine packages (Arch official / AUR).
# Default UI stays stock GNOME top bar. Opt into a bottom/side bar with:
#   gnomarchi shell bar-position bottom|left|right
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/pkg.sh
source "${ROOT}/install/lib/pkg.sh"

# Official: gnome-shell-extension-caffeine (extra).
# AUR: gnome-shell-extension-dash-to-panel.
install_arch_or_aur gnome-shell-extension-caffeine || true
install_arch_or_aur gnome-shell-extension-dash-to-panel || true

# Copy into ~/.local so Shell can discover them when the user opts in.
user_ext="${HOME}/.local/share/gnome-shell/extensions"
mkdir -p "${user_ext}"
for uuid in dash-to-panel@jderose9.github.com caffeine@patapon.info; do
  sys="/usr/share/gnome-shell/extensions/${uuid}"
  if [[ -d "${sys}" ]]; then
    rm -rf "${user_ext}/${uuid}"
    cp -a "${sys}" "${user_ext}/${uuid}"
  fi
done

# Caffeine is a default amenity (does not replace the top bar).
if command -v gnome-extensions >/dev/null 2>&1; then
  gnome-extensions enable "caffeine@patapon.info" 2>/dev/null || true
  # Leave dash-to-panel disabled until bar-position opts in.
  gnome-extensions disable "dash-to-panel@jderose9.github.com" 2>/dev/null || true
fi

pkg_log "panel packages installed (dash-to-panel optional; stock GNOME top bar default)"
