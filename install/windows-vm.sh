#!/usr/bin/env bash
# Windows VM helpers: virt-manager + QEMU/KVM (official Arch).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# shellcheck source=lib/pkg.sh
source "${ROOT}/install/lib/pkg.sh"

install_official \
  qemu-desktop \
  libvirt \
  virt-manager \
  dnsmasq \
  edk2-ovmf \
  iptables-nft || true

if command -v systemctl >/dev/null 2>&1; then
  sudo systemctl enable --now libvirtd.service 2>/dev/null || true
  sudo systemctl enable --now virtlogd.service 2>/dev/null || true
fi

# Allow current user to manage VMs without root when possible.
if getent group libvirt >/dev/null 2>&1; then
  sudo usermod -aG libvirt "${USER}" 2>/dev/null || true
fi

pkg_log "Windows VM stack: virt-manager qemu-desktop libvirt (open virt-manager to create a Windows guest)"
