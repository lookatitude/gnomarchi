#!/usr/bin/env bash
# Capture GTK desktop proofs after theme set on the gnomarchi guest.
#
# Env:
#   PARITY_CAPTURE=1   — workflows (theme.proof.*) capture + assert host JPEGs when set;
#                        this script always captures when invoked directly.
#   GNOMARCHI_SSH_HOST — default 127.0.0.1
#   GNOMARCHI_SSH_PORT — default 2222
#   GNOMARCHI_SSH_USER — default arch
#   GNOMARCHI_VNC      — vncdotool -s target, default 127.0.0.1::5901
#   VNC_TOOL           — vncdotool binary (default: PATH, then gnomarchi-test venv)
#   SETTLE_SEC         — seconds after theme set before shot (default 2)
#
# Usage (host):
#   ./scripts/parity-capture-theme-proof.sh
#   ./scripts/parity-capture-theme-proof.sh tokyo-night nord
#   PARITY_CAPTURE=1 python3 scripts/parity-workflows-run.py --only theme.proof --side gnomarchi
#
# Without PARITY_CAPTURE, workflows still assert guest gtk.css + gsettings (CI-safe).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-proof/theme"
SSH_HOST="${GNOMARCHI_SSH_HOST:-127.0.0.1}"
SSH_PORT="${GNOMARCHI_SSH_PORT:-2222}"
SSH_USER="${GNOMARCHI_SSH_USER:-arch}"
VNC_TARGET="${GNOMARCHI_VNC:-127.0.0.1::5901}"
SETTLE_SEC="${SETTLE_SEC:-2}"
KNOWN_HOSTS="${GNOMARCHI_KNOWN_HOSTS:-/tmp/gnomarchi-gnom-known_hosts}"

DEFAULT_THEMES=(tokyo-night nord gruvbox catppuccin-latte)
THEMES=("$@")
if [[ ${#THEMES[@]} -eq 0 ]]; then
  THEMES=("${DEFAULT_THEMES[@]}")
fi

mkdir -p "$OUT"

resolve_vnc() {
  if [[ -n "${VNC_TOOL:-}" && -x "${VNC_TOOL}" ]]; then
    echo "$VNC_TOOL"
    return
  fi
  if command -v vncdotool >/dev/null 2>&1; then
    command -v vncdotool
    return
  fi
  local cand=/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool
  if [[ -x "$cand" ]]; then
    echo "$cand"
    return
  fi
  echo ""
}

VNC_BIN="$(resolve_vnc)"

SSH=(ssh -p "$SSH_PORT"
  -o StrictHostKeyChecking=accept-new
  -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o BatchMode=yes
  -o ConnectTimeout=8
  "${SSH_USER}@${SSH_HOST}")

SCP=(scp -P "$SSH_PORT"
  -o StrictHostKeyChecking=accept-new
  -o "UserKnownHostsFile=$KNOWN_HOSTS"
  -o BatchMode=yes
  -o ConnectTimeout=8)

remote() {
  "${SSH[@]}" 'bash -s' <<REMOTE
export DISPLAY=\${DISPLAY:-:0}
export DBUS_SESSION_BUS_ADDRESS=\${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/\$(id -u)/bus}
export XDG_RUNTIME_DIR=\${XDG_RUNTIME_DIR:-/run/user/\$(id -u)}
set -euo pipefail
$1
REMOTE
}

compress_jpeg() {
  local src="$1" dest="$2"
  if command -v magick >/dev/null 2>&1; then
    magick "$src" -quality 85 -strip "$dest"
  elif command -v convert >/dev/null 2>&1; then
    convert "$src" -quality 85 -strip "$dest"
  else
    cp "$src" "$dest"
  fi
  local sz
  sz=$(stat -c%s "$dest" 2>/dev/null || echo 0)
  # Re-compress if still huge (>1.5MB)
  if [[ "$sz" -gt 1572864 ]] && command -v magick >/dev/null 2>&1; then
    magick "$dest" -quality 70 -resize '1920x1080>' -strip "$dest"
  fi
}

capture_one() {
  local theme="$1"
  local raw png jpg guest_tmp
  raw="${OUT}/.raw-${theme}.png"
  png="${OUT}/theme-${theme}.png"
  jpg="${OUT}/theme-${theme}.jpg"
  guest_tmp="/tmp/gnomarchi-theme-proof-${theme}.png"

  echo "== theme set: ${theme}"
  remote "gnomarchi theme set ${theme}"
  sleep "$SETTLE_SEC"

  rm -f "$raw" "$png" "$jpg"
  if [[ -n "$VNC_BIN" ]]; then
    echo "capture via vncdotool ${VNC_TARGET}"
    pkill -f 'vncdotool' 2>/dev/null || true
    sleep 0.3
    timeout 20 "$VNC_BIN" -s "$VNC_TARGET" capture "$raw"
  else
    echo "vncdotool missing; guest gnome-screenshot → scp"
    remote "rm -f ${guest_tmp}; gnome-screenshot -f ${guest_tmp} || import -window root ${guest_tmp}"
    "${SCP[@]}" "${SSH_USER}@${SSH_HOST}:${guest_tmp}" "$raw"
    remote "rm -f ${guest_tmp}" || true
  fi

  local sz
  sz=$(stat -c%s "$raw" 2>/dev/null || echo 0)
  if [[ "$sz" -lt 1000 ]]; then
    echo "ERROR: capture too small (${sz}b) for ${theme}" >&2
    return 1
  fi

  compress_jpeg "$raw" "$jpg"
  # Keep a PNG sibling only if JPEG path failed oddly; prefer JPEG as proof artifact
  if [[ ! -f "$jpg" ]]; then
    cp "$raw" "$png"
  fi
  rm -f "$raw"
  echo "ok theme-${theme}.jpg ($(stat -c%s "$jpg")b)"
}

for t in "${THEMES[@]}"; do
  capture_one "$t"
done

echo "proofs under ${OUT}"
ls -la "$OUT"/theme-*.jpg 2>/dev/null || ls -la "$OUT"/theme-*.png
