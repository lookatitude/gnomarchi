#!/usr/bin/env bash
# Optional Arch packages for Omarchy-like GNOME parity (official repos / AUR).
# No custom gnomarchi pacman repo required.
set -euo pipefail

SKIP_CONFIRM="${GNOMARCHI_SKIP_CONFIRM:-0}"

EXTRA_OFFICIAL=(
  gnome-shell-extension-caffeine
  gnome-shell-extensions
  gnome-screenshot
  tesseract
  tesseract-data-eng
  zbar
  mpv
  gpaste
  plymouth
  # Omarchy manual shell/TUI/dev parity (Arch official)
  btop
  lazygit
  fzf
  zoxide
  eza
  bat
  fd
  ripgrep
  tmux
  starship
  github-cli
  kooha
  imv
  tealdeer
  yt-dlp
  fastfetch
  cmus
  evince
  xournalpp
  pinta
  ffmpeg
  steam
  lutris
  virt-manager
  qemu-desktop
  dnsmasq
  iptables-nft
  edk2-ovmf
  libvirt
)

# dash-to-panel + PaperWM: official when present, else AUR names
AUR_HINTS=(
  gnome-shell-extension-dash-to-panel
  gnome-shell-extension-paperwm
  paperwm-git
  kooha
)

log() { printf '[gnomarchi-extras] %s\n' "$*"; }

confirm() {
  [[ "${SKIP_CONFIRM}" == "1" ]] && return 0
  printf '%s [y/N] ' "$1"
  read -r a || true
  [[ "${a}" == "y" || "${a}" == "Y" || "${a}" == "yes" ]]
}

cmd="${1:-all}"
case "${cmd}" in
  panel)
    sudo pacman -Sy --needed --noconfirm gnome-shell-extension-caffeine || true
    if pacman -Si gnome-shell-extension-dash-to-panel &>/dev/null; then
      sudo pacman -Sy --needed --noconfirm gnome-shell-extension-dash-to-panel
    elif command -v paru >/dev/null; then
      confirm "Install gnome-shell-extension-dash-to-panel via paru (AUR)?" \
        && paru -S --needed --noconfirm gnome-shell-extension-dash-to-panel
    elif command -v yay >/dev/null; then
      confirm "Install gnome-shell-extension-dash-to-panel via yay (AUR)?" \
        && yay -S --needed --noconfirm gnome-shell-extension-dash-to-panel
    else
      log "AUR: install gnome-shell-extension-dash-to-panel (yay/paru)"
    fi
    # Stock GNOME top bar stays default; dash-to-panel is opt-in.
    gnome-extensions enable caffeine@patapon.info 2>/dev/null || true
    gnome-extensions disable dash-to-panel@jderose9.github.com 2>/dev/null || true
    log "caffeine on; dash-to-panel installed but off — opt in: gnomarchi shell bar-position bottom"
    ;;
  tiling)
    if pacman -Si gnome-shell-extension-paperwm &>/dev/null; then
      sudo pacman -Sy --needed --noconfirm gnome-shell-extension-paperwm
    elif pacman -Si paperwm &>/dev/null; then
      sudo pacman -Sy --needed --noconfirm paperwm
    else
      log "PaperWM AUR: gnome-shell-extension-paperwm or paperwm-git"
      helper=""
      command -v paru >/dev/null && helper=paru
      command -v yay >/dev/null && helper=yay
      if [[ -n "${helper}" ]]; then
        confirm "Install gnome-shell-extension-paperwm via ${helper}?" \
          && "${helper}" -S --needed --noconfirm gnome-shell-extension-paperwm \
          || "${helper}" -S --needed --noconfirm paperwm-git || true
      fi
    fi
    gnome-extensions enable paperwm@paperwm.github.com 2>/dev/null || true
    ;;
  capture)
    sudo pacman -Sy --needed --noconfirm gnome-screenshot tesseract tesseract-data-eng zbar mpv gpaste
    pacman -Si kooha &>/dev/null && sudo pacman -Sy --needed --noconfirm kooha || log "optional: AUR/extra kooha for record UI"
    ;;
  shell-tools)
    # Manual chapters: shell-tools, tuis, prompt, development-tools (sans docker)
    sudo pacman -Sy --needed --noconfirm \
      btop lazygit fzf zoxide eza bat fd ripgrep tmux starship \
      github-cli kooha imv tealdeer yt-dlp fastfetch
    log "shell/TUI tools installed; docker remains optional (Install › Dev)"
    ;;
  gaming)
    sudo pacman -Sy --needed --noconfirm steam lutris
    ;;
  windows-vm)
    sudo pacman -Sy --needed --noconfirm virt-manager qemu-desktop dnsmasq iptables-nft
    sudo systemctl enable --now libvirtd.service || true
    log "Add your user to libvirt group: sudo usermod -aG libvirt \$USER"
    ;;
  plymouth)
    ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    if [[ -x "${ROOT}/install/plymouth.sh" || -f "${ROOT}/install/plymouth.sh" ]]; then
      bash "${ROOT}/install/plymouth.sh"
    else
      sudo pacman -Sy --needed --noconfirm plymouth
      if [[ -d "${ROOT}/plymouth/gnomarchi" ]]; then
        sudo cp -a "${ROOT}/plymouth/gnomarchi" /usr/share/plymouth/themes/
        if [[ -f "${ROOT}/assets/brand/logo.png" ]]; then
          sudo install -m 0644 "${ROOT}/assets/brand/logo.png" \
            /usr/share/plymouth/themes/gnomarchi/logo.png
        fi
        sudo plymouth-set-default-theme -R gnomarchi || sudo plymouth-set-default-theme gnomarchi
      fi
    fi
    ;;
  all)
    confirm "Install Arch extras for panel/tiling/capture/shell-tools/gaming/vm/plymouth?" || exit 0
    sudo pacman -Sy --needed --noconfirm "${EXTRA_OFFICIAL[@]}" || true
    "$0" panel || true
    "$0" tiling || true
    "$0" shell-tools || true
    "$0" plymouth || true
    log "AUR hints: ${AUR_HINTS[*]}"
    ;;
  *)
    echo "Usage: $0 [all|panel|tiling|capture|shell-tools|gaming|windows-vm|plymouth]"
    exit 2
    ;;
esac
