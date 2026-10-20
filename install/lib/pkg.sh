#!/usr/bin/env bash
# Shared pacman + AUR install helpers for overlay and menu Install modules.
# Official Arch packages first; AUR via yay/paru when pacman cannot resolve.
set -euo pipefail

pkg_log() { printf '[gnomarchi-pkg] %s\n' "$*"; }
pkg_warn() { printf '[gnomarchi-pkg] WARN: %s\n' "$*" >&2; }

# Install packages available in sync DBs (extra/core/community/multilib).
install_official() {
  local pkgs=("$@")
  [[ ${#pkgs[@]} -gt 0 ]] || return 0
  pkg_log "pacman: ${pkgs[*]}"
  sudo pacman -Sy --needed --noconfirm "${pkgs[@]}"
}

# Try pacman; if a name is missing, fall through to AUR helper for that name only.
install_arch_or_aur() {
  local pkg="$1"
  if pacman -Si "${pkg}" &>/dev/null || pacman -Q "${pkg}" &>/dev/null; then
    install_official "${pkg}"
    return 0
  fi
  local helper=""
  if command -v yay >/dev/null 2>&1; then
    helper=yay
  elif command -v paru >/dev/null 2>&1; then
    helper=paru
  fi
  if [[ -z "${helper}" ]]; then
    pkg_warn "package '${pkg}' not in pacman DBs and no yay/paru; install from AUR manually"
    return 1
  fi
  pkg_log "AUR (${helper}): ${pkg}"
  "${helper}" -S --needed --noconfirm "${pkg}"
}
