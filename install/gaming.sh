#!/usr/bin/env bash
# Install Gaming stack: Steam + Lutris (official Arch / multilib).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/pkg.sh
source "${ROOT}/install/lib/pkg.sh"

# Ensure multilib is usable for steam; do not rewrite pacman.conf silently.
if ! grep -qE '^\[multilib\]' /etc/pacman.conf 2>/dev/null; then
  pkg_warn "[multilib] not enabled in /etc/pacman.conf — enable it for Steam 32-bit libs"
fi

install_official steam lutris || {
  # steam may need multilib; still try lutris alone
  install_official lutris || true
  install_arch_or_aur steam || true
}

pkg_log "gaming packages: steam lutris"
