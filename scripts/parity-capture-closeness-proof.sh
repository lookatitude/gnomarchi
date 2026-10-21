#!/usr/bin/env bash
# Capture closeness-plan proof shots (prompt, unlock, branding, menu, panels, bg).
# Requires PARITY_CAPTURE=1. Uses VNC 5901 / SSH 2222.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-proof/closeness"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
KEY="${KEY:-/home/miguelp/.ssh/id_rsa}"
JPG_QUALITY="${JPG_QUALITY:-82}"

if [[ "${PARITY_CAPTURE:-0}" != "1" && "${PARITY_CAPTURE:-}" != "true" ]]; then
  echo "skip: set PARITY_CAPTURE=1"
  exit 0
fi
mkdir -p "$OUT"

remote() {
  timeout 40 ssh -i "$KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -p 2222 arch@127.0.0.1 bash -s <<EOF
set +e
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export HOME=/home/arch PATH=/usr/local/bin:\$PATH
export DISPLAY=:0 GDK_BACKEND=x11 XDG_CURRENT_DESKTOP=GNOME
AUTH=\$(ls /run/user/1000/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
[[ -n \$AUTH ]] && export XAUTHORITY=\$AUTH
$1
EOF
}

shot() {
  local name=$1 png
  png=$(mktemp --suffix=.png)
  remote 'gnomarchi notice silence >/dev/null 2>&1 || true' || true
  sleep 0.35
  timeout 18 "$VNC" -s 127.0.0.1::5901 capture "$png" >/dev/null
  magick "$png" -quality "$JPG_QUALITY" -strip "${OUT}/${name}.jpg"
  rm -f "$png"
  echo "OK ${name} $(stat -c%s "${OUT}/${name}.jpg")b"
}

nuke() {
  remote 'gnomarchi notice silence >/dev/null 2>&1 || true
pkill -u arch -f org.gnomarchi.Panel 2>/dev/null || true
pkill -u arch -f gnomarchi_screensaver 2>/dev/null || true
pkill -u arch -f "python3 -m menu" 2>/dev/null || true
pkill -u arch -f theme_picker 2>/dev/null || true
pkill -u arch -f ghostty 2>/dev/null || true
for t in Audio Network Bluetooth Power Display Calendar Screensaver About Themes Command gnomarchi ghostty Ghostty; do
  wmctrl -c "$t" 2>/dev/null || true
done
sleep 0.5
echo nuked'
}

place_tr() {
  local title=$1
  remote "TITLE='$title'
for i in 1 2 3 4 5 6 7 8; do
  id=\$(xdotool search --name \"\$TITLE\" 2>/dev/null | head -1)
  [[ -n \$id ]] && break
  sleep 0.2
done
id=\$(xdotool search --name \"\$TITLE\" 2>/dev/null | head -1)
[[ -n \$id ]] && xdotool windowactivate --sync \$id windowsize \$id 360 320 windowmove \$id 1540 36
wmctrl -l -G | head -8
echo placed"
}

center() {
  local title=$1 w=${2:-720} h=${3:-640}
  remote "N='$title'; W=$w; H=$h; X=\$(( (1920-W)/2 )); Y=\$(( (1080-H)/2 - 20 )); [[ \$Y -lt 40 ]] && Y=40
id=\$(xdotool search --name \"\$N\" 2>/dev/null | head -1)
[[ -n \$id ]] && xdotool windowactivate --sync \$id windowsize \$id \$W \$H windowmove \$id \$X \$Y
echo centered"
}

echo "=== closeness-proof START $(date -Is) ==="
remote 'gnomarchi shell ensure >/dev/null
gnomarchi theme set tokyo-night >/dev/null
gnomarchi theme unlock set tokyo-night >/dev/null
gsettings set org.gnome.desktop.interface color-scheme prefer-dark
echo prep_ok'

nuke

# 1) Themed prompt in Ghostty
remote 'nohup ghostty -e zsh -lc "clear; echo TOKYO-NIGHT prompt; starship prompt 2>/dev/null; pwd; echo; echo themed session; sleep 45" >/tmp/gt-prompt.log 2>&1 &
sleep 2; wmctrl -l'
center ghostty 1000 560
center Ghostty 1000 560
shot prompt-tokyo-night
nuke

# 2) Unlock art applied — open Files on branding dir + show unlock.png preview if possible
remote 'nohup eog ~/.config/gnomarchi/branding/unlock.png >/tmp/eog.log 2>&1 || nohup papers ~/.config/gnomarchi/branding/unlock.png >/tmp/eog.log 2>&1 || nohup imv ~/.config/gnomarchi/branding/unlock.png >/tmp/eog.log 2>&1 &
sleep 1.5; wmctrl -l'
center unlock 900 700
center Image 900 700
center imv 900 700
shot unlock-art
nuke

# 3) Screensaver branding
remote 'nohup gnomarchi branding screensaver show >/tmp/ss.log 2>&1 &
sleep 1.8; wmctrl -l'
shot branding-screensaver
nuke

# 4) About branding
remote 'nohup gnomarchi branding about show >/tmp/ab.log 2>&1 &
sleep 1.5; wmctrl -l'
center About 640 520
center about 640 520
center gnomarchi 640 520
shot branding-about
nuke

# 5) Menu root (hierarchical)
remote 'nohup gnomarchi menu open >/tmp/menu.log 2>&1 &
sleep 1.5; wmctrl -l'
center Command 520 560
center gnomarchi 520 560
shot menu-root
nuke

# 6) Interactive tray panels
for panel in audio network bluetooth; do
  nuke
  remote "nohup gnomarchi panel $panel >/tmp/p-$panel.log 2>&1 & sleep 1.5; wmctrl -l"
  place_tr "${panel^}"
  # title-case via bash
  case $panel in
    audio) place_tr Audio ;;
    network) place_tr Network ;;
    bluetooth) place_tr Bluetooth ;;
  esac
  shot "panel-${panel}"
done
nuke

# 7) Theme bg pick
remote 'nohup gnomarchi theme bg pick >/tmp/bg.log 2>&1 &
sleep 2; wmctrl -l'
center Background 900 700
center background 900 700
center Themes 900 700
center gnomarchi 900 700
shot theme-bg-pick
nuke

# 8) Desktop clean baseline
shot desktop-clean

echo "=== closeness-proof DONE ==="
ls -la "$OUT"/*.jpg
