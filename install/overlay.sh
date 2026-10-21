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
  gnome-shell-extensions
  xdg-desktop-portal-gnome
  xdg-user-dirs
)
DEFAULT_APP_PKGS=(
  ghostty
  neovim
  chromium
  starship
  zsh
)
AGENT_APP_PKGS=(
  mise
  libappindicator-gtk3
  gnome-shell-extension-appindicator
  pacman-contrib
  gnome-shell-extension-caffeine
  gnome-screenshot
  tesseract
  tesseract-data-eng
  zbar
  mpv
  gpaste
  papirus-icon-theme
)
# Shell UUIDs enabled after GNOME session tools exist (user-themes ships in gnome-shell-extensions).
DEFAULT_SHELL_EXTENSIONS=(
  user-theme@gnome-shell-extensions.gcampax.github.com
  appindicatorsupport@rgcjonas.gmail.com
  caffeine@patapon.info
)
# Optional panel / tiling (Arch official + AUR). Installed by stage_panel; not required for stock GNOME.
PANEL_PKGS=(
  gnome-shell-extension-caffeine
  gnome-shell-extension-dash-to-panel
)
TILING_PKGS=(
  gnome-shell-extension-paperwm
)
PANEL_SHELL_EXTENSIONS=(
  dash-to-panel@jderose9.github.com
  caffeine@patapon.info
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

# Soft opt-in: default N, never aborts the overlay. Non-interactive (SKIP_CONFIRM)
# stays off unless GNOMARCHI_ENABLE_PAPERWM=1 (explicit).
offer_opt_in() {
  local prompt="$1"
  if [[ "${SKIP_CONFIRM}" == "1" ]]; then
    [[ "${GNOMARCHI_ENABLE_PAPERWM:-0}" == "1" ]] && return 0
    return 1
  fi
  printf '%s [y/N] ' "${prompt}"
  local ans
  read -r ans || true
  [[ "${ans}" == "y" || "${ans}" == "Y" || "${ans}" == "yes" ]]
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
  local lib_dest="${dest}/lib/gnomarchi"
  mkdir -p "${GNOMARCHI_CONFIG}"

  if [[ -f "${bin_src}" ]]; then
    confirm "Install gnomarchi CLI + libs to ${dest} (sudo)?"
    run sudo install -d "${dest}/bin" "${lib_dest}"
    # Python packages the CLI imports.
    local pkg
    for pkg in theme plugin common bus menu apps agent config desktop; do
      if [[ -d "${GNOMARCHI_ROOT}/${pkg}" ]]; then
        run sudo rm -rf "${lib_dest}/${pkg}"
        run sudo cp -a "${GNOMARCHI_ROOT}/${pkg}" "${lib_dest}/"
      fi
    done
    if [[ -d "${GNOMARCHI_ROOT}/plugins" ]]; then
      run sudo rm -rf "${lib_dest}/plugins"
      run sudo cp -a "${GNOMARCHI_ROOT}/plugins" "${lib_dest}/"
    fi
    # Drop bytecode caches from the 9p/host tree copy.
    run sudo find "${lib_dest}" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
    run sudo install -m 0755 "${bin_src}" "${dest}/bin/gnomarchi"
    # App menu entries (gnoma-write / cut / calc)
    if [[ -d "${GNOMARCHI_ROOT}/applications" ]]; then
      local apps_share="${dest}/share/applications"
      run sudo install -d "${apps_share}"
      local desk
      for desk in "${GNOMARCHI_ROOT}"/applications/org.gnomarchi.*.desktop; do
        [[ -f "${desk}" ]] || continue
        run sudo install -m 0644 "${desk}" "${apps_share}/"
      done
      run mkdir -p "${HOME}/.local/share/applications"
      for desk in "${GNOMARCHI_ROOT}"/applications/org.gnomarchi.*.desktop; do
        [[ -f "${desk}" ]] || continue
        run install -m 0644 "${desk}" "${HOME}/.local/share/applications/"
      done
    fi
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
  log "stage: seed default apps (Ghostty + nvim + Chromium + starship + agent deps)"
  confirm "Install default apps: ghostty neovim chromium starship (+ mise, appindicator, pacman-contrib)?"
  run sudo pacman -Sy --needed --noconfirm "${DEFAULT_APP_PKGS[@]}"
  local pkg
  for pkg in "${AGENT_APP_PKGS[@]}"; do
    run sudo pacman -Sy --needed --noconfirm "${pkg}" || warn "optional package ${pkg} not installed"
  done

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
packages = ["ghostty", "neovim", "chromium", "starship"]
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

stage_icons() {
  # Omarchy packs name Yaru-*; Arch has Papirus. theme set maps Yaru→Papirus+folders.
  # Also installs applications/icons into ~/.local/share/icons/hicolor for launchers.
  log "stage: icon theme + app icons (Papirus; Yaru not in Arch repos)"
  if ! pacman -Q papirus-icon-theme &>/dev/null; then
    confirm "Install papirus-icon-theme (Omarchy Yaru substitute on Arch)?"
    run sudo pacman -Sy --needed --noconfirm papirus-icon-theme || warn "papirus-icon-theme install failed"
  fi
  # papirus-folders: AUR helper, else download upstream script into ~/.local/bin
  if ! command -v papirus-folders >/dev/null 2>&1; then
    if command -v yay >/dev/null 2>&1; then
      run yay -S --needed --noconfirm papirus-folders || warn "papirus-folders AUR install failed"
    elif command -v paru >/dev/null 2>&1; then
      run paru -S --needed --noconfirm papirus-folders || warn "papirus-folders AUR install failed"
    fi
  fi
  if [[ -x "${GNOMARCHI_ROOT}/bin/gnomarchi" ]] || command -v gnomarchi >/dev/null 2>&1; then
    run env PYTHONPATH="${GNOMARCHI_ROOT}${PYTHONPATH:+:$PYTHONPATH}" \
      python3 -c "from theme.icon_apply import install_app_icons, apply_pack_icons, ensure_papirus_folders_bin; from pathlib import Path; ensure_papirus_folders_bin(); install_app_icons(); p=Path('${GNOMARCHI_ROOT}/theme/packs/tokyo-night'); apply_pack_icons(p) if p.is_dir() else None" \
      || warn "icon apply skipped"
  fi
}

stage_agents() {
  log "stage: agent stack + panel widgets"
  # mise + wrappers + skills
  if command -v gnomarchi >/dev/null 2>&1; then
    run gnomarchi agent setup || warn "agent setup failed"
  elif [[ -x "${GNOMARCHI_ROOT}/bin/gnomarchi" ]]; then
    run env GNOMARCHI_ROOT="${GNOMARCHI_ROOT}" python3 "${GNOMARCHI_ROOT}/bin/gnomarchi" agent setup || warn "agent setup failed"
  fi

  # Shell aliases (Omarchy muscle memory)
  local alias_file="${GNOMARCHI_CONFIG}/shell-aliases.sh"
  cat > "${alias_file}" <<'ALIASES'
# gnomarchi agent aliases
alias a='gnomarchi agent launch'
alias cy='gnomarchi agent launch claude'
alias cx='gnomarchi agent launch codex'
alias c='gnomarchi agent launch opencode'
ALIASES
  for rc in "${HOME}/.zshrc" "${HOME}/.bashrc"; do
    if [[ -f "${rc}" ]] || [[ "${SKIP_CONFIRM}" == "1" ]]; then
      touch "${rc}"
      if ! grep -q 'gnomarchi/shell-aliases.sh' "${rc}" 2>/dev/null; then
        echo "source ${alias_file}" >> "${rc}"
      fi
    fi
  done

  # Starship prompt hook (G1 / manual.prompt) — idempotent
  ensure_starship_rc() {
    local shell="$1" rc="$2" line
    line="eval \"\$(starship init ${shell})\""
    if [[ -f "${rc}" ]] || [[ "${SKIP_CONFIRM}" == "1" ]]; then
      touch "${rc}"
      if ! grep -qE 'starship init|gnomarchi: starship' "${rc}" 2>/dev/null; then
        printf '\n# gnomarchi: starship\n%s\n' "${line}" >> "${rc}"
        log "appended starship init to ${rc}"
      else
        log "starship init already present in ${rc}"
      fi
    fi
  }
  ensure_starship_rc zsh "${HOME}/.zshrc"
  ensure_starship_rc bash "${HOME}/.bashrc"

  # Enable first-party indicators + crash capture + agents panel when CLI works
  if command -v gnomarchi >/dev/null 2>&1 || [[ -x "${GNOMARCHI_ROOT}/bin/gnomarchi" ]]; then
    local gnom
    gnom="$(command -v gnomarchi || true)"
    [[ -n "${gnom}" ]] || gnom="python3 ${GNOMARCHI_ROOT}/bin/gnomarchi"
    for pid in gnomarchi.agents gnomarchi.weather gnomarchi.system-update gnomarchi.crash-capture gnomarchi.agents-panel gnomarchi.modes; do
      run bash -c "GNOMARCHI_ROOT=${GNOMARCHI_ROOT} ${gnom} plugin enable --id ${pid}" || warn "enable ${pid} skipped"
    done
  fi

  # Enable default Shell extensions (user-themes + AppIndicator + caffeine).
  # Stock GNOME top bar is the default; dash-to-panel is optional via stage_panel
  # / `gnomarchi shell bar-position bottom|left|right`.
  # Copy system extensions into ~/.local so Shell discovers them after first
  # install without a second GDM cycle (Arch ships under /usr/share/...).
  local user_ext="${HOME}/.local/share/gnome-shell/extensions"
  run mkdir -p "${user_ext}"
  local copy_uuid
  for copy_uuid in \
    "user-theme@gnome-shell-extensions.gcampax.github.com" \
    "caffeine@patapon.info" \
    "appindicatorsupport@rgcjonas.gmail.com"
  do
    local copy_sys="/usr/share/gnome-shell/extensions/${copy_uuid}"
    if [[ -d "${copy_sys}" ]]; then
      run rm -rf "${user_ext}/${copy_uuid}"
      run cp -a "${copy_sys}" "${user_ext}/${copy_uuid}"
    fi
  done
  if command -v gnome-extensions >/dev/null 2>&1 || command -v gsettings >/dev/null 2>&1; then
    for uuid in "${DEFAULT_SHELL_EXTENSIONS[@]}"; do
      run gnome-extensions enable "${uuid}" 2>/dev/null || true
    done
    # Ensure dash-to-panel stays off unless the user opts into a bottom/side bar.
    run gnome-extensions disable "dash-to-panel@jderose9.github.com" 2>/dev/null || true
    # Merge into gsettings so enable survives GDM restart races
    if command -v gsettings >/dev/null 2>&1 && command -v python3 >/dev/null 2>&1; then
      run python3 - <<'PY'
import ast, subprocess
raw = subprocess.check_output(
    ["gsettings", "get", "org.gnome.shell", "enabled-extensions"], text=True
).strip()
text = raw[4:] if raw.startswith("@as ") else raw
try:
    lst = list(ast.literal_eval(text))
except Exception:
    lst = []
want = (
    "user-theme@gnome-shell-extensions.gcampax.github.com",
    "appindicatorsupport@rgcjonas.gmail.com",
    "ubuntu-appindicators@ubuntu.com",
    "caffeine@patapon.info",
    "gnomarchi-agents@gnomarchi",
)
drop = {"dash-to-panel@jderose9.github.com"}
lst = [u for u in lst if u not in drop]
for uuid in want:
    if uuid not in lst:
        lst.append(uuid)
subprocess.check_call(
    ["gsettings", "set", "org.gnome.shell", "enabled-extensions", str(lst)]
)
print("enabled-extensions:", lst)
PY
    fi
    run gsettings set org.gnome.shell.extensions.user-theme name gnomarchi 2>/dev/null || true
  fi

  # Usage refresh timer
  local unit_dir="${XDG_CONFIG_HOME}/systemd/user"
  mkdir -p "${unit_dir}"
  cat > "${unit_dir}/gnomarchi-agent-usage.service" <<EOF
[Unit]
Description=gnomarchi agent usage refresh
[Service]
Type=oneshot
ExecStart=${GNOMARCHI_PREFIX:-/usr/local}/bin/gnomarchi agent usage-update
EOF
  cat > "${unit_dir}/gnomarchi-agent-usage.timer" <<'EOF'
[Unit]
Description=Refresh gnomarchi agent usage every 15m
[Timer]
OnBootSec=2m
OnUnitActiveSec=15m
Persistent=true
[Install]
WantedBy=timers.target
EOF
  if command -v systemctl >/dev/null 2>&1; then
    run systemctl --user daemon-reload || true
    run systemctl --user enable --now gnomarchi-agent-usage.timer || warn "usage timer not enabled"
  fi

  # Hotkeys mirrored from https://omarchy.org/manual/hotkeys/ + the-top-bar/
  # (GNOME adapters: Quick Settings panels via `gnomarchi panel`, Style via theme).
  if command -v gsettings >/dev/null 2>&1; then
    local kb_paths=(
      gnomarchi-menu gnomarchi-agent gnomarchi-theme gnomarchi-bg
      gnomarchi-panel-audio gnomarchi-panel-network gnomarchi-panel-bluetooth
      gnomarchi-panel-display gnomarchi-panel-power
      gnomarchi-clipboard gnomarchi-terminal gnomarchi-browser gnomarchi-btop
      gnomarchi-notice-time gnomarchi-notice-battery gnomarchi-notice-weather
      gnomarchi-mode-dnd gnomarchi-mode-night gnomarchi-calc gnomarchi-write
      gnomarchi-remind gnomarchi-capture-shot gnomarchi-capture-ocr
      gnomarchi-nvim gnomarchi-herdr gnomarchi-lock gnomarchi-files
      gnomarchi-panel-calendar gnomarchi-share gnomarchi-capture-menu
      gnomarchi-notice-history
    )
    local listed="'/"
    listed+="org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/${kb_paths[0]}/'"
    local p
    for p in "${kb_paths[@]:1}"; do
      listed+=",'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/${p}/'"
    done
    run gsettings set org.gnome.settings-daemon.plugins.media-keys custom-keybindings "[${listed}]" || true
    local base="org.gnome.settings-daemon.plugins.media-keys.custom-keybinding"
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-menu/" name 'gnomarchi menu' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-menu/" command 'gnomarchi menu open' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-menu/" binding '<Super>space' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-agent/" name 'gnomarchi default agent' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-agent/" command 'gnomarchi agent launch' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-agent/" binding '<Super><Shift><Control>a' || true
    # Omarchy Style: Super+Ctrl+Shift+Space theme · Super+Ctrl+Space background
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-theme/" name 'gnomarchi theme picker' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-theme/" command 'gnomarchi theme pick' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-theme/" binding '<Super><Control><Shift>space' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-bg/" name 'gnomarchi next background' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-bg/" command 'gnomarchi theme bg next' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-bg/" binding '<Super><Control>space' || true
    # Omarchy top-bar panel hotkeys → gnomarchi panel adapters
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-audio/" name 'gnomarchi audio panel' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-audio/" command 'gnomarchi panel audio' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-audio/" binding '<Super><Control>a' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-network/" name 'gnomarchi network panel' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-network/" command 'gnomarchi panel network' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-network/" binding '<Super><Control>w' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-bluetooth/" name 'gnomarchi bluetooth panel' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-bluetooth/" command 'gnomarchi panel bluetooth' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-bluetooth/" binding '<Super><Control>b' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-display/" name 'gnomarchi display panel' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-display/" command 'gnomarchi panel display' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-display/" binding '<Super><Control>d' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-power/" name 'gnomarchi power panel' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-power/" command 'gnomarchi panel power' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-power/" binding '<Super><Control>p' || true
    # Clipboard / launchers / notices / modes (Omarchy hotkeys, GNOME-safe subset)
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-clipboard/" name 'gnomarchi clipboard' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-clipboard/" command 'gnomarchi clipboard ui' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-clipboard/" binding '<Super><Control>v' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-terminal/" name 'gnomarchi terminal' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-terminal/" command 'ghostty' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-terminal/" binding '<Super>Return' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-browser/" name 'gnomarchi browser' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-browser/" command 'chromium' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-browser/" binding '<Super><Shift>Return' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-btop/" name 'gnomarchi btop' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-btop/" command 'ghostty -e btop' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-btop/" binding '<Super><Control>t' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-time/" name 'gnomarchi notice time' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-time/" command 'gnomarchi notice time' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-time/" binding '<Super><Control>period' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-battery/" name 'gnomarchi notice battery' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-battery/" command 'gnomarchi notice battery' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-battery/" binding '<Super><Control>comma' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-weather/" name 'gnomarchi notice weather' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-weather/" command 'gnomarchi notice weather' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-weather/" binding '<Super><Control>slash' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-dnd/" name 'gnomarchi DND toggle' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-dnd/" command 'gnomarchi mode dnd' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-dnd/" binding '<Super><Control>i' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-night/" name 'gnomarchi night light' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-night/" command 'gnomarchi mode night-light' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-mode-night/" binding '<Super><Control>n' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-calc/" name 'gnomarchi calc' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-calc/" command 'gnomarchi app calc' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-calc/" binding '<Super><Control>q' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-write/" name 'gnomarchi write' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-write/" command 'gnomarchi app write' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-write/" binding '<Super><Shift>w' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-remind/" name 'gnomarchi remind list' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-remind/" command 'gnomarchi remind list' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-remind/" binding '<Super><Control>r' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-shot/" name 'gnomarchi screenshot' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-shot/" command 'gnomarchi capture shot' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-shot/" binding '<Super><Shift>Print' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-ocr/" name 'gnomarchi OCR' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-ocr/" command 'gnomarchi capture ocr' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-ocr/" binding '<Super><Control>Print' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-nvim/" name 'gnomarchi nvim' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-nvim/" command 'ghostty -e nvim' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-nvim/" binding '<Super><Shift>n' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-herdr/" name 'gnomarchi herdr' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-herdr/" command 'gnomarchi herdr attach' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-herdr/" binding '<Super><Control>Return' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-lock/" name 'gnomarchi lock' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-lock/" command 'gnomarchi idle lock' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-lock/" binding '<Super><Control>l' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-files/" name 'gnomarchi files' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-files/" command 'nautilus' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-files/" binding '<Super><Shift>f' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-calendar/" name 'gnomarchi calendar' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-calendar/" command 'gnomarchi panel calendar' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-panel-calendar/" binding '<Super><Control><Alt>d' || true
    # Omarchy Super+Ctrl+S share / LocalSend receive
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-share/" name 'gnomarchi share' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-share/" command 'gnomarchi share receive' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-share/" binding '<Super><Control>s' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-menu/" name 'gnomarchi capture menu' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-menu/" command 'gnomarchi capture menu' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-capture-menu/" binding '<Super><Shift><Control>Print' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-history/" name 'gnomarchi notice history' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-history/" command 'gnomarchi notice history' || true
    run gsettings set "${base}:/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/gnomarchi-notice-history/" binding '<Super><Control><Shift>period' || true
  fi
}

stage_panel() {
  log "stage: optional dash-to-panel (bottom/side bar; Arch/AUR)"
  local extras="${GNOMARCHI_ROOT}/install/arch-extras.sh"
  if [[ -f "${extras}" ]]; then
    confirm "Install dash-to-panel package (optional bottom/side bar; stock top bar stays default)?"
    run env GNOMARCHI_SKIP_CONFIRM="${SKIP_CONFIRM}" bash "${extras}" panel || warn "panel extras failed; Install › Desktop › panel later"
    run env GNOMARCHI_SKIP_CONFIRM=1 bash "${extras}" shell-tools || warn "shell-tools extras failed"
  else
    [[ -f "${GNOMARCHI_ROOT}/install/panel.sh" ]] && run bash "${GNOMARCHI_ROOT}/install/panel.sh" || true
  fi
  # Install only — do not enable dash-to-panel. Opt in with:
  #   gnomarchi shell bar-position bottom
  log "stock GNOME top bar remains default; enable bottom bar via gnomarchi shell bar-position bottom"
}

# F3: PaperWM is opt-in (default N). Stock GNOME overview stays the default session feel.
stage_tiling_offer() {
  log "stage: PaperWM tiling offer (opt-in, default N)"
  cat <<'NOTE'

  PaperWM is optional GNOME tiling (Omarchy dwindle/scroll substitute).
  Default is stock GNOME overview — PaperWM is never force-enabled.

NOTE
  if offer_opt_in "Enable PaperWM tiling now?"; then
    local extras="${GNOMARCHI_ROOT}/install/arch-extras.sh"
    if [[ -f "${extras}" ]]; then
      run env GNOMARCHI_SKIP_CONFIRM=1 bash "${extras}" tiling || warn "PaperWM install failed; retry: Install › PaperWM tiling"
    elif [[ -f "${GNOMARCHI_ROOT}/install/tiling.sh" ]]; then
      run bash "${GNOMARCHI_ROOT}/install/tiling.sh" || warn "tiling.sh failed"
    else
      warn "tiling helpers missing; Install › PaperWM tiling later"
    fi
  else
    log "PaperWM skipped (default). Opt in later: Install › PaperWM tiling, or: gnomarchi install tiling --yes"
  fi
}

stage_plymouth() {
  log "stage: plymouth theme (assets/brand/logo.png)"
  local extras="${GNOMARCHI_ROOT}/install/arch-extras.sh"
  confirm "Install plymouth boot theme with gnomarchi logo?"
  if [[ -f "${extras}" ]]; then
    run env GNOMARCHI_SKIP_CONFIRM="${SKIP_CONFIRM}" bash "${extras}" plymouth || warn "plymouth extras failed"
  elif [[ -f "${GNOMARCHI_ROOT}/install/plymouth.sh" ]]; then
    run bash "${GNOMARCHI_ROOT}/install/plymouth.sh" || warn "plymouth.sh failed"
  else
    warn "plymouth install helpers missing; skip"
  fi
}

stage_agent_invite() {
  log "stage: agent invite"
  cat <<'INVITE'

────────────────────────────────────────────────────────────
  gnomarchi overlay complete (stock GNOME + GDM + agents).

  Next:
    1. Reboot and select the GNOME session at GDM.
    2. gnomarchi theme set midnight-harbor
    3. gnomarchi default agent claude   # or: codex, opencode, grok, …
    4. Super+Space menu · Agents indicator · Make something
    5. gnomarchi update                 # sudo pacman -Syu (official Arch)
    6. Optional PaperWM: Install › PaperWM tiling
       (or: gnomarchi install tiling --yes / GNOMARCHI_ENABLE_PAPERWM=1)

  Defaults: Ghostty · Neovim · Chromium · mise agents · stock GNOME overview
  Docs:     docs/install/vm-test.md · docs/apps/substitutes.md · docs/gnome-shell-matrix.md
────────────────────────────────────────────────────────────

INVITE
}

# Explicit destructive helpers — never called by default stages.
wipe_disk() {
  die "disk wipe is not part of the overlay; use a manual installer. Refusing."
}

usage() {
  cat <<EOF
Usage: $(basename "$0") [all|detect|gnome|gdm|gnomarchi|defaults|theme|agents|panel|tiling|plymouth|invite]

Env:
  GNOMARCHI_DRY_RUN=1              print actions only
  GNOMARCHI_SKIP_CONFIRM=1         non-interactive (CI/VM automation only)
  GNOMARCHI_CONFIRM_DESTRUCTIVE=yes  allow steps that disable other DMs
  GNOMARCHI_ENABLE_PAPERWM=1        with SKIP_CONFIRM, opt into PaperWM (else skipped)
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
      stage_icons
      ;;
    icons) stage_detect; stage_icons ;;
    agents) stage_detect; stage_agents ;;
    panel) stage_detect; stage_panel ;;
    tiling) stage_detect; stage_tiling_offer ;;
    plymouth) stage_detect; stage_plymouth ;;
    invite) stage_agent_invite ;;
    all)
      stage_detect
      stage_refuse_forbidden
      stage_packages_gnome
      stage_enable_gdm
      stage_install_gnomarchi
      stage_defaults
      stage_theme_seed
      stage_icons
      stage_agents
      stage_panel
      stage_tiling_offer
      stage_plymouth
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
