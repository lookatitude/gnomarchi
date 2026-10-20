#!/usr/bin/env bash
# Install plymouth + gnomarchi theme (assets/brand/logo.png).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/pkg.sh
source "${ROOT}/install/lib/pkg.sh"

THEME_SRC="${ROOT}/plymouth/gnomarchi"
THEME_DST="/usr/share/plymouth/themes/gnomarchi"
LOGO_SRC="${ROOT}/assets/brand/logo.png"

install_official plymouth plymouth-theme-spinner || install_official plymouth || true

[[ -d "${THEME_SRC}" ]] || { pkg_warn "missing ${THEME_SRC}"; exit 1; }
[[ -f "${LOGO_SRC}" ]] || pkg_warn "missing ${LOGO_SRC}; theme may lack logo"

sudo install -d "${THEME_DST}"
sudo cp -a "${THEME_SRC}/." "${THEME_DST}/"
if [[ -f "${LOGO_SRC}" ]]; then
  sudo install -m 0644 "${LOGO_SRC}" "${THEME_DST}/logo.png"
fi

if command -v plymouth-set-default-theme >/dev/null 2>&1; then
  sudo plymouth-set-default-theme -R gnomarchi 2>/dev/null \
    || sudo plymouth-set-default-theme gnomarchi 2>/dev/null \
    || pkg_warn "could not set default plymouth theme (rebuild initramfs after install)"
elif [[ -f /etc/plymouth/plymouthd.conf ]]; then
  sudo sed -i 's/^Theme=.*/Theme=gnomarchi/' /etc/plymouth/plymouthd.conf 2>/dev/null || true
  if ! grep -q '^Theme=' /etc/plymouth/plymouthd.conf 2>/dev/null; then
    echo 'Theme=gnomarchi' | sudo tee -a /etc/plymouth/plymouthd.conf >/dev/null
  fi
fi

# mkinitcpio hook when available
if [[ -f /etc/mkinitcpio.conf ]] && ! grep -q 'plymouth' /etc/mkinitcpio.conf 2>/dev/null; then
  pkg_warn "add 'plymouth' to HOOKS in /etc/mkinitcpio.conf and run mkinitcpio -P"
fi

pkg_log "plymouth theme gnomarchi installed → ${THEME_DST}"
