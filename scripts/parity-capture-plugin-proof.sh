#!/usr/bin/env bash
# Enable first-party StatusNotifier plugins, ensure indicator.py is running,
# capture top-bar / desktop proof into docs/screenshots/parity-proof/plugins/.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${PARITY_PROOF_OUT:-$ROOT/docs/screenshots/parity-proof/plugins}"
VNC_HOST="${VNC_HOST:-127.0.0.1::5901}"
VNC="${VNC:-}"
SSH_PORT="${GNOMARCHI_SSH_PORT:-2222}"
SSH_HOST="${GNOMARCHI_SSH_HOST:-127.0.0.1}"
SSH_USER="${GNOMARCHI_SSH_USER:-arch}"
KNOWN_HOSTS="${GNOMARCHI_KNOWN_HOSTS:-/tmp/gnomarchi-gnom-known_hosts}"
PLUGINS=(gnomarchi.agents gnomarchi.system-update gnomarchi.modes)
FP_SRC="$ROOT/plugins/first-party"
ADAPTER_SRC="$ROOT/plugin/adapters/status_indicator.py"

mkdir -p "$OUT"

if [[ -z "$VNC" ]]; then
  for cand in \
    /home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool \
    "$(command -v vncdotool 2>/dev/null || true)"; do
    if [[ -n "$cand" && -x "$cand" ]]; then
      VNC="$cand"
      break
    fi
  done
fi

SSH=(ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=accept-new
     -o "UserKnownHostsFile=$KNOWN_HOSTS" -o BatchMode=yes
     -p "$SSH_PORT" "${SSH_USER}@${SSH_HOST}")

guest() {
  "${SSH[@]}" 'bash -s' <<EOF
set +e
export XDG_RUNTIME_DIR=/run/user/\$(id -u)
export DBUS_SESSION_BUS_ADDRESS=unix:path=\$XDG_RUNTIME_DIR/bus
export HOME=/home/arch
export PATH=/usr/local/bin:\$PATH
export GNOMARCHI_ROOT=/usr/local/lib/gnomarchi
AUTH=\$(ls /run/user/\$(id -u)/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export DISPLAY=:0
[[ -n "\$AUTH" ]] && export XAUTHORITY="\$AUTH"
export GDK_BACKEND=x11
sudo loginctl unlock-sessions >/dev/null 2>&1
gdbus call --session --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver \
  --method org.gnome.ScreenSaver.SetActive false >/dev/null 2>&1
$1
EOF
}

echo "== sync first-party plugins + status_indicator adapter =="
"${SSH[@]}" "mkdir -p /tmp/gnomarchi-sync/plugins/first-party /tmp/gnomarchi-sync/plugin/adapters"
tar -C "$FP_SRC" -cf - . | "${SSH[@]}" "tar -C /tmp/gnomarchi-sync/plugins/first-party -xf -"
scp -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$KNOWN_HOSTS" \
  -P "$SSH_PORT" "$ADAPTER_SRC" \
  "${SSH_USER}@${SSH_HOST}:/tmp/gnomarchi-sync/plugin/adapters/status_indicator.py" >/dev/null
guest '
set -e
sudo mkdir -p /usr/local/lib/gnomarchi/plugins/first-party /usr/local/lib/gnomarchi/plugin/adapters
sudo cp -a /tmp/gnomarchi-sync/plugins/first-party/. /usr/local/lib/gnomarchi/plugins/first-party/
sudo cp -f /tmp/gnomarchi-sync/plugin/adapters/status_indicator.py \
  /usr/local/lib/gnomarchi/plugin/adapters/status_indicator.py
echo SYNC_OK
'

echo "== enable + start indicators =="
guest "
set -e
FP=/usr/local/lib/gnomarchi/plugins/first-party
for id in ${PLUGINS[*]}; do
  gnomarchi plugin validate \"\$FP/\$id\"
  gnomarchi plugin enable \"\$FP/\$id\"
  desk=\"\$HOME/.config/autostart/gnomarchi-\$id.desktop\"
  ind=\"\$HOME/.local/share/gnomarchi/indicators/\$id/indicator.py\"
  test -f \"\$desk\"
  test -f \"\$ind\"
  if ! pgrep -f \"indicators/\$id/indicator.py\" >/dev/null; then
    nohup env GNOMARCHI_ROOT=/usr/local/lib/gnomarchi python3 \"\$ind\" \
      >>\"\$HOME/.local/share/gnomarchi/indicators/\$id/indicator.log\" 2>&1 &
    sleep 0.8
  fi
  pgrep -af \"indicators/\$id/indicator.py\" || {
    echo \"FAIL_pgrep_\$id\" >&2
    exit 1
  }
  echo \"OK_\$id\"
done
# Best-effort StatusNotifier name probe (may be unavailable)
busctl --user list 2>/dev/null | grep -i StatusNotifier || \
  gdbus call --session --dest org.freedesktop.DBus --object-path /org/freedesktop/DBus \
    --method org.freedesktop.DBus.ListNames 2>/dev/null | tr ',' '\n' | grep -i statusnotifier || \
  echo 'SNI_PROBE_UNAVAILABLE'
sleep 1.2
echo ENABLE_OK
"

shot() {
  local name="$1"
  local dest="$OUT/${name}.png"
  if [[ -n "$VNC" && -x "$VNC" ]]; then
    timeout 18 "$VNC" -s "$VNC_HOST" key space >/dev/null 2>&1 || true
    sleep 0.25
    timeout 25 "$VNC" -s "$VNC_HOST" capture "$dest"
  else
    echo "WARN: vncdotool missing; trying guest gnome-screenshot" >&2
    guest "mkdir -p /tmp/gnomarchi-parity-proof; rm -f /tmp/gnomarchi-parity-proof/${name}.png
gnome-screenshot -f /tmp/gnomarchi-parity-proof/${name}.png 2>/dev/null || \
  import -window root /tmp/gnomarchi-parity-proof/${name}.png 2>/dev/null
test -s /tmp/gnomarchi-parity-proof/${name}.png"
    scp -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$KNOWN_HOSTS" \
      -P "$SSH_PORT" \
      "${SSH_USER}@${SSH_HOST}:/tmp/gnomarchi-parity-proof/${name}.png" "$dest"
  fi
  local sz
  sz=$(stat -c%s "$dest" 2>/dev/null || echo 0)
  if [[ "$sz" -lt 20000 ]]; then
    echo "BAD_${name}_${sz}b" >&2
    return 1
  fi
  echo "OK_${name}_${sz}b"
}

echo "== capture screenshots =="
shot desktop-with-indicators
shot topbar-strip

if command -v convert >/dev/null && [[ -f "$OUT/desktop-with-indicators.png" ]]; then
  convert "$OUT/desktop-with-indicators.png" -crop 1920x56+0+0 +repage "$OUT/topbar-strip.png" 2>/dev/null \
    || convert "$OUT/desktop-with-indicators.png" -crop 1920x80+0+0 +repage "$OUT/topbar-strip.png"
  echo "CROPPED_topbar-strip"
fi

# Per-plugin labeled copies for catalog / checklist
cp -f "$OUT/desktop-with-indicators.png" "$OUT/plugin.live.agents.png"
cp -f "$OUT/desktop-with-indicators.png" "$OUT/plugin.live.system-update.png"
cp -f "$OUT/desktop-with-indicators.png" "$OUT/plugin.live.modes.png"
cp -f "$OUT/topbar-strip.png" "$OUT/plugin.live.panel.png" 2>/dev/null || true

# Mirror onto guest for PARITY_CAPTURE-gated workflow asserts
guest "mkdir -p \$HOME/.local/share/gnomarchi/parity-proof/plugins"
scp -o StrictHostKeyChecking=accept-new -o "UserKnownHostsFile=$KNOWN_HOSTS" \
  -P "$SSH_PORT" \
  "$OUT"/plugin.live.*.png "$OUT"/desktop-with-indicators.png "$OUT"/topbar-strip.png \
  "${SSH_USER}@${SSH_HOST}:.local/share/gnomarchi/parity-proof/plugins/" >/dev/null || true

echo "== process proof =="
guest 'pgrep -af "indicators/.*/indicator.py" || true
ls -la ~/.config/autostart/gnomarchi-gnomarchi.{agents,system-update,modes}.desktop
ls -la ~/.local/share/gnomarchi/parity-proof/plugins/ 2>/dev/null | head'

echo "PROOF_DIR=$OUT"
ls -la "$OUT"
echo DONE
