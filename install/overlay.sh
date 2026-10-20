#!/usr/bin/env bash
# gnomarchi overlay installer — Arch Linux + stock GNOME (GDM)
# Stages: detect → packages → GNOME/GDM → gnomarchi → defaults → theme seed → agent invite
# Safe defaults: never wipe disks; destructive steps require explicit confirm.
# Forbidden: Hyprland packages; publishing repo keys; silent destructive disk ops.
set -euo pipefail

GNOMARCHI_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
XDG_CONFIG_HOME="${XDG_CONFIG_HOME:-${HOME}/.config}"
GNOMARCHI_CONFIG="${XDG_CONFIG_HOME}/gnomarchi"
CONFIRM_DESTRUCTIVE="${GNOMARCHI_CONFIRM_DESTRUCTIVE:-}"
SKIP_CONFIRM="${GNOMARCHI_SKIP_CONFIRM:-0}"
DRY_RUN="${GNOMARCHI_DRY_RUN:-0}"

# Official Arch packages (extra). ghostty is in official repos as of 2024+.
GNOME_PKGS=(
  gnome
  gdm
  gnome-tweaks
  xdg-desktop-portal-gnome
  xdg-user-dirs
)
DEFAULT_APP_PKGS=(
  ghostty
  neovim
  chromium
)
# Never install these (D1 / plan forbidden).
FORBIDDEN_PKGS=(hyprland hyprland-git sddm uwsm)

log()  { printf '[gnomarchi-overlay] %s\n' "$*"; }
warn() { printf '[gnomarchi-overlay] WARN: %s\n' "$*" >&2; }
die()  { printf '[gnomarchi-overlay] ERROR: %s\n' "$*" >&2; exit 1; }

run() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    log "DRY-RUN: $*"
    return 0
  fi
  "$@"
}

confirm() {
  local prompt="$1"
  if [[ "${SKIP_CONFIRM}" == "1" ]]; then
    return 0
  fi
  if [[ -n "${CONFIRM_DESTRUCTIVE}" ]]; then
    [[ "${CONFIRM_DESTRUCTIVE}" == "yes" ]] || die "destructive step declined (GNOMARCHI_CONFIRM_DESTRUCTIVE!=yes)"
    return 0
  fi
  printf '%s [y/N] ' "${prompt}"
  local ans
  read -r ans || true
  [[ "${ans}" == "y" || "${ans}" == "Y" || "${ans}" == "yes" ]] || die "aborted by user"
}

stage_detect() {
  log "stage: detect Arch"
  [[ -f /etc/os-release ]] || die "/etc/os-release missing"
  # shellcheck disable=SC1091
  . /etc/os-release
  [[ "${ID:-}" == "arch" || "${ID_LIKE:-}" == *"arch"* ]] || die "not Arch Linux (ID=${ID:-unknown}); overlay targets Arch only"
  command -v pacman >/dev/null 2>&1 || die "pacman not found"
  command -v systemctl >/dev/null 2>&1 || die "systemctl not found"
  log "detected ${PRETTY_NAME:-Arch Linux}"
}

stage_refuse_forbidden() {
  local pkg
  for pkg in "${FORBIDDEN_PKGS[@]}"; do
    if pacman -Q "${pkg}" &>/dev/null; then
      warn "installed package '${pkg}' is outside gnomarchi identity (stock GNOME); not removing"
    fi
  done
}

stage_packages_gnome() {
  log "stage: install GNOME + GDM packages"
  confirm "Install GNOME/GDM packages via pacman (requires sudo)?"
  run sudo pacman -Sy --needed --noconfirm "${GNOME_PKGS[@]}"
}

stage_enable_gdm() {
  log "stage: enable GDM"
  confirm "Enable and (on next reboot) use GDM as display manager?"
  if systemctl is-enabled gdm.service &>/dev/null; then
    log "gdm.service already enabled"
  else
    # Disabling another DM can strand a machine; require confirm.
    local other
    for other in sddm lightdm ly; do
      if systemctl is-enabled "${other}.service" &>/dev/null; then
        confirm "Disable ${other}.service before enabling gdm?"
        run sudo systemctl disable "${other}.service"
      fi
    done
    run sudo systemctl enable gdm.service
  fi
  log "GNOME session packages present; login via GDM after reboot"
}

stage_install_gnomarchi() {
  log "stage: install/copy gnomarchi"
  local dest="${GNOMARCHI_PREFIX:-/usr/local}"
  local bin_src="${GNOMARCHI_ROOT}/bin/gnomarchi"
  mkdir -p "${GNOMARCHI_CONFIG}"

  if [[ -f "${bin_src}" ]]; then
    confirm "Install gnomarchi CLI to ${dest}/bin (sudo)?"
    run sudo install -d "${dest}/bin"
    run sudo install -m 0755 "${bin_src}" "${dest}/bin/gnomarchi"
  else
    warn "bin/gnomarchi not present yet; seeding config and PATH hint only"
    local local_bin="${HOME}/.local/bin"
    run mkdir -p "${local_bin}"
    if [[ ! -e "${local_bin}/gnomarchi" ]]; then
      cat > "${local_bin}/gnomarchi" <<'WRAPPER'
#!/usr/bin/env bash
echo "gnomarchi CLI not built yet; see repo bin/ once T3 lands" >&2
exit 1
WRAPPER
      chmod +x "${local_bin}/gnomarchi"
    fi
  fi

  # Prefer custom repo package when configured; else tree copy of theme/skills.
  if [[ -f /etc/pacman.d/gnomarchi.conf ]] || grep -q '\[gnomarchi\]' /etc/pacman.conf 2>/dev/null; then
    log "gnomarchi pacman repo detected; attempting package install"
    confirm "Install gnomarchi from pacman repo?"
    run sudo pacman -Sy --needed --noconfirm gnomarchi || warn "pacman gnomarchi install failed; continuing with tree seed"
  fi

  run mkdir -p "${GNOMARCHI_CONFIG}/themes"
  if [[ -d "${GNOMARCHI_ROOT}/theme/packs" ]]; then
    run cp -a "${GNOMARCHI_ROOT}/theme/packs/." "${GNOMARCHI_CONFIG}/themes/"
  fi
  if [[ -d "${GNOMARCHI_ROOT}/skills" ]]; then
    run mkdir -p "${GNOMARCHI_CONFIG}/skills"
    run cp -a "${GNOMARCHI_ROOT}/skills/." "${GNOMARCHI_CONFIG}/skills/" 2>/dev/null || true
  fi
}

stage_defaults() {
  log "stage: seed default apps (Ghostty + nvim + Chromium)"
  confirm "Install default apps: ghostty neovim chromium?"
  run sudo pacman -Sy --needed --noconfirm "${DEFAULT_APP_PKGS[@]}"

  # Soft defaults via xdg / GSettings when session tools exist (no force).
  if command -v xdg-settings >/dev/null 2>&1; then
    run xdg-settings set default-web-browser chromium.desktop 2>/dev/null || true
  fi
  mkdir -p "${XDG_CONFIG_HOME}/xdg-terminals.list.d" 2>/dev/null || true
  printf 'ghostty.desktop\n' > "${XDG_CONFIG_HOME}/xdg-terminals.list" 2>/dev/null || true

  cat > "${GNOMARCHI_CONFIG}/defaults.toml" <<EOF
# Seeded by install/overlay.sh — D6 defaults
terminal = "ghostty"
editor = "neovim"
browser = "chromium"
packages = ["ghostty", "neovim", "chromium"]
EOF
  log "wrote ${GNOMARCHI_CONFIG}/defaults.toml"
}

stage_theme_seed() {
  log "stage: theme seed"
  local pack_id="midnight-harbor"
  local pack_src="${GNOMARCHI_ROOT}/theme/packs/${pack_id}"
  local pack_dst="${GNOMARCHI_CONFIG}/themes/${pack_id}"

  if [[ -d "${pack_src}" ]]; then
    run mkdir -p "${pack_dst}"
    run cp -a "${pack_src}/." "${pack_dst}/"
  fi

  cat > "${GNOMARCHI_CONFIG}/active-theme" <<EOF
${pack_id}
EOF

  if command -v gnomarchi >/dev/null 2>&1; then
    run gnomarchi theme set "${pack_id}" 2>/dev/null || warn "gnomarchi theme set skipped (CLI incomplete)"
  else
    log "theme pack '${pack_id}' seeded under ${GNOMARCHI_CONFIG}/themes; apply via 'gnomarchi theme set' when CLI is available"
  fi
}

stage_agent_invite() {
  log "stage: agent invite"
  cat <<'INVITE'

────────────────────────────────────────────────────────────
  gnomarchi overlay complete (stock GNOME + GDM path).

  Next:
    1. Reboot and select the GNOME session at GDM.
    2. Run:  gnomarchi theme list
    3. Agents / Make-something:  gnomarchi agent
       (skills under ~/.config/gnomarchi/skills when present)

  Defaults: Ghostty · Neovim · Chromium
  Docs:     docs/install/vm-test.md
────────────────────────────────────────────────────────────

INVITE
}

# Explicit destructive helpers — never called by default stages.
wipe_disk() {
  die "disk wipe is not part of the overlay; use a manual installer. Refusing."
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [all|detect|gnome|gdm|gnomarchi|defaults|theme|invite]

Env:
  GNOMARCHI_DRY_RUN=1              print actions only
  GNOMARCHI_SKIP_CONFIRM=1         non-interactive (CI/VM automation only)
  GNOMARCHI_CONFIRM_DESTRUCTIVE=yes  allow steps that disable other DMs
  GNOMARCHI_PREFIX=/usr/local      CLI install prefix
EOF
}

main() {
  local cmd="${1:-all}"
  case "${cmd}" in
    -h|--help) usage; exit 0 ;;
    detect) stage_detect ;;
    gnome)
      stage_detect
      stage_refuse_forbidden
      stage_packages_gnome
      ;;
    gdm)
      stage_detect
      stage_enable_gdm
      ;;
    gnomarchi)
      stage_detect
      stage_install_gnomarchi
      ;;
    defaults)
      stage_detect
      stage_defaults
      ;;
    theme)
      stage_detect
      stage_theme_seed
      ;;
    invite) stage_agent_invite ;;
    all)
      stage_detect
      stage_refuse_forbidden
      stage_packages_gnome
      stage_enable_gdm
      stage_install_gnomarchi
      stage_defaults
      stage_theme_seed
      stage_agent_invite
      ;;
    wipe|destroy)
      wipe_disk
      ;;
    *)
      usage
      die "unknown stage: ${cmd}"
      ;;
  esac
}

main "$@"
