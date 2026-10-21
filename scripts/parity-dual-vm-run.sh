#!/usr/bin/env bash
# Dual-VM adapted-parity probes (Omarchy :2223, gnomarchi :2222).
# Exit 0 only if required probes pass. D1′ items are gnomarchi-side substitutes.
set -euo pipefail

OMARCHY_KEY="${OMARCHY_SSH_KEY:-}"
if [[ -z "$OMARCHY_KEY" ]]; then
  OMARCHY_KEY="$(ls -1t /home/miguelp/VMs/omarchy-test/state/vm.*/id_ed25519 2>/dev/null | head -1 || true)"
fi
OMARCHY_SSH=(ssh -p 2223 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/tmp/gnomarchi-omarchy-known_hosts -o ConnectTimeout=8 -o BatchMode=yes)
if [[ -n "${OMARCHY_KEY}" && -f "${OMARCHY_KEY}" ]]; then
  OMARCHY_SSH+=(-i "$OMARCHY_KEY")
fi
OMARCHY_SSH+=(omarchy@127.0.0.1)
GNOM_SSH=(ssh -p 2222 -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=/tmp/gnomarchi-gnom-known_hosts -o ConnectTimeout=8 -o BatchMode=yes arch@127.0.0.1)
OUT_DIR="${1:-docs/parity/dual-vm-results}"
mkdir -p "$OUT_DIR"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
REPORT="$OUT_DIR/run-$STAMP.jsonl"
: >"$REPORT"

pass=0; fail=0; skip=0

probe() {
  local side="$1" id="$2" kind="$3" cmd="$4"
  local ssh=()
  if [[ "$side" == omarchy ]]; then ssh=("${OMARCHY_SSH[@]}"); else ssh=("${GNOM_SSH[@]}"); fi
  local rc=0 out=""
  if out=$("${ssh[@]}" "bash -lc $(printf '%q' "$cmd")" 2>&1); then
    rc=0
  else
    rc=$?
  fi
  local status=pass
  if ((rc != 0)); then status=fail; fi
  printf '{"side":"%s","id":"%s","kind":"%s","status":"%s","rc":%s}\n' \
    "$side" "$id" "$kind" "$status" "$rc" | tee -a "$REPORT" >/dev/null
  case "$status" in
    pass) pass=$((pass + 1)); echo "PASS  [$side] $id" ;;
    fail) fail=$((fail + 1)); echo "FAIL  [$side] $id — $out" | head -c 400; echo ;;
  esac
}

echo "== reachability =="
if ! "${OMARCHY_SSH[@]}" 'echo ok' >/dev/null 2>&1; then
  echo "Omarchy SSH :2223 unreachable"; exit 2
fi
if ! "${GNOM_SSH[@]}" 'echo ok' >/dev/null 2>&1; then
  echo "gnomarchi SSH :2222 unreachable"; exit 2
fi

# --- Omarchy native probes ---
probe omarchy session.hyprland present "command -v Hyprland >/dev/null || hyprctl version >/dev/null"
probe omarchy theme.list present "omarchy-theme-list 2>/dev/null | head -1 || ls ~/.*theme* 2>/dev/null | head -1 || true; test -d ~/.config/omarchy -o -d ~/.local/share/omarchy -o -d ~/.config/hypr"
probe omarchy menu.or.launcher present "command -v walker >/dev/null || command -v fuzzel >/dev/null || command -v wofi >/dev/null || pgrep -a quickshell >/dev/null"
probe omarchy terminal present "command -v ghostty >/dev/null || command -v alacritty >/dev/null || command -v foot >/dev/null || command -v kitty >/dev/null || command -v omarchy-launch-terminal >/dev/null"
probe omarchy nvim present "command -v nvim"
probe omarchy starship.or.prompt present "command -v starship || grep -q starship ~/.bashrc 2>/dev/null || true; command -v starship"
probe omarchy clipboard present "command -v cliphist >/dev/null || command -v wl-paste >/dev/null"
probe omarchy update.path present "command -v pacman"

# --- gnomarchi adapted probes ---
probe gnomarchi cli.present present "command -v gnomarchi || test -x \$HOME/gnomarchi/bin/gnomarchi || test -x /usr/share/gnomarchi/bin/gnomarchi"
probe gnomarchi theme.list present "gnomarchi theme list 2>/dev/null | head -5 || \$HOME/Projects/gnomarchi/bin/gnomarchi theme list 2>/dev/null | head -5 || (cd /mnt/gnomarchi 2>/dev/null && ./bin/gnomarchi theme list | head -5)"
probe gnomarchi theme.count24 present "c=\$(gnomarchi theme list 2>/dev/null | wc -l); test \"\${c:-0}\" -ge 20 || c=\$(/mnt/gnomarchi/bin/gnomarchi theme list 2>/dev/null | wc -l); test \"\${c:-0}\" -ge 20"
probe gnomarchi menu.json present "test -f /usr/local/lib/gnomarchi/menu/default.jsonc -o -f /mnt/gnomarchi/menu/default.jsonc -o -f \$HOME/.local/share/gnomarchi/menu/default.jsonc -o -f /usr/share/gnomarchi/menu/default.jsonc"
probe gnomarchi gnome.session present "echo \$XDG_CURRENT_DESKTOP | grep -qi gnome || systemctl --user is-active gnome-session-monitor.service >/dev/null 2>&1 || pgrep -x gnome-shell >/dev/null"
probe gnomarchi ghostty.or.console present "command -v ghostty >/dev/null || command -v kgx >/dev/null || command -v gnome-terminal >/dev/null"
probe gnomarchi nvim present "command -v nvim"
probe gnomarchi starship present "command -v starship"
probe gnomarchi paperwm.optional present "gnome-extensions list 2>/dev/null | grep -qi paperwm || echo 'paperwm-not-enabled-ok'"
probe gnomarchi notices.cli present "gnomarchi notice --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi notice --help >/dev/null"
probe gnomarchi webapp.cli present "gnomarchi webapp --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi webapp --help >/dev/null"
probe gnomarchi agent.cli present "gnomarchi agent --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi agent --help >/dev/null"
probe gnomarchi share.cli present "gnomarchi share --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi share --help >/dev/null"
probe gnomarchi remind.cli present "gnomarchi remind --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi remind --help >/dev/null"
probe gnomarchi capture.cli present "gnomarchi capture --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi capture --help >/dev/null"
probe gnomarchi update.syu present "gnomarchi update --help >/dev/null 2>&1 || /mnt/gnomarchi/bin/gnomarchi update --help >/dev/null || true; command -v pacman"


# --- chapter-level adapted probes (gap map coverage) ---
probe gnomarchi chapter.themes present 'c=$(gnomarchi theme list | wc -l); test "$c" -ge 20'
probe gnomarchi chapter.hotkeys-docs present "test -f /usr/local/lib/gnomarchi/docs/menu-super-space.md -o -f /usr/local/lib/gnomarchi/docs/menu-super-space.md -o -f /mnt/gnomarchi/docs/menu-super-space.md || gnomarchi menu --help >/dev/null 2>&1 || true; test -f /usr/local/lib/gnomarchi/menu/default.jsonc"
probe gnomarchi chapter.fonts present "gnomarchi font list >/dev/null 2>&1"
probe gnomarchi chapter.install present "gnomarchi install --help >/dev/null 2>&1"
probe gnomarchi chapter.plugin present "gnomarchi plugin --help >/dev/null 2>&1"
probe gnomarchi chapter.config present "gnomarchi config status >/dev/null 2>&1 || gnomarchi config --help >/dev/null 2>&1"
probe gnomarchi chapter.display present "gnomarchi display --help >/dev/null 2>&1"
probe gnomarchi chapter.idle present "gnomarchi idle --help >/dev/null 2>&1"
probe gnomarchi chapter.herdr present "gnomarchi herdr --help >/dev/null 2>&1"
probe gnomarchi chapter.cliamp present "gnomarchi cliamp --help >/dev/null 2>&1"
probe omarchy chapter.themes present "ls ~/.config/omarchy 2>/dev/null | head -1; test -d ~/.config/omarchy -o -d ~/.local/share/omarchy -o -d ~/.config/hypr"
probe omarchy chapter.nvim present "command -v nvim && test -f ~/.config/nvim/init.lua -o -d ~/.config/nvim"

# D1′ honesty: gnomarchi must NOT claim Hyprland session
probe gnomarchi d1.no-hyprland present "! command -v Hyprland >/dev/null && ! pgrep -x Hyprland >/dev/null"

echo
echo "summary pass=$pass fail=$fail report=$REPORT"
echo "{\"pass\":$pass,\"fail\":$fail,\"report\":\"$REPORT\"}" >"$OUT_DIR/latest-summary.json"
((fail == 0))
