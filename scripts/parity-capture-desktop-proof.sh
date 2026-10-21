#!/usr/bin/env bash
# Capture F4 desktop visual proofs with Omarchy-like framing:
# overview OFF, notifications cleared, single centered window, dark theme.
#
# Env:
#   PARITY_CAPTURE=1   required to write shots (no-op exit 0 otherwise)
#   VNC                vncdotool binary (default: gnomarchi-test venv)
#   VNC_ADDR           default 127.0.0.1::5901
#   SSH_PORT           default 2222
#   KNOWN_HOSTS        default /tmp/gnomarchi-gnom-known_hosts
#
# Without PARITY_CAPTURE: exits 0 and prints skip (CI-safe).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-proof/desktop"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
VNC_ADDR="${VNC_ADDR:-127.0.0.1::5901}"
SSH_PORT="${SSH_PORT:-2222}"
KNOWN_HOSTS="${KNOWN_HOSTS:-/tmp/gnomarchi-gnom-known_hosts}"
JPG_QUALITY="${JPG_QUALITY:-82}"

SSH=(ssh -p "$SSH_PORT"
  -o StrictHostKeyChecking=accept-new
  -o "UserKnownHostsFile=${KNOWN_HOSTS}"
  -o BatchMode=yes
  -o ConnectTimeout=8
  arch@127.0.0.1)

if [[ "${PARITY_CAPTURE:-0}" != "1" && "${PARITY_CAPTURE:-}" != "true" && "${PARITY_CAPTURE:-}" != "yes" ]]; then
  echo "skip: set PARITY_CAPTURE=1 to capture under ${OUT}"
  exit 0
fi

mkdir -p "$OUT"
pkill -f 'vncdotool' 2>/dev/null || true
sleep 0.3

guest() {
  "${SSH[@]}" 'bash -s' <<EOF
set +e
export XDG_RUNTIME_DIR=\${XDG_RUNTIME_DIR:-/run/user/\$(id -u)}
export DBUS_SESSION_BUS_ADDRESS=\${DBUS_SESSION_BUS_ADDRESS:-unix:path=/run/user/\$(id -u)/bus}
export HOME=/home/arch
export PATH=/usr/local/bin:\$PATH
export XDG_CURRENT_DESKTOP=GNOME
export GNOME_DESKTOP_SESSION_ID=this-is-deprecated
AUTH=\$(ls /run/user/\$(id -u)/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export DISPLAY=:0
[[ -n "\$AUTH" ]] && export XAUTHORITY="\$AUTH"
export GDK_BACKEND=x11
export WAYLAND_DISPLAY=\${WAYLAND_DISPLAY:-wayland-0}
sudo loginctl unlock-sessions >/dev/null 2>&1 || true
gdbus call --session --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver \
  --method org.gnome.ScreenSaver.SetActive false >/dev/null 2>&1 || true
$1
EOF
}

# Escape overview + clear banners via VNC (reliable when Shell.Eval is locked).
vnc_escape() {
  timeout 12 "$VNC" -s "$VNC_ADDR" key esc pause 0.35 key esc pause 0.25 >/dev/null 2>&1 || true
}

prep_desktop() {
  guest 'gnomarchi theme set tokyo-night >/tmp/parity-theme.log 2>&1 || true
gsettings set org.gnome.desktop.interface color-scheme prefer-dark 2>/dev/null || true
gsettings set org.gnome.desktop.screensaver lock-enabled false
gsettings set org.gnome.desktop.session idle-delay 0
# Hide overview / clear tray banners (best-effort; may be denied)
gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell \
  --method org.gnome.Shell.Eval "try{Main.overview.hide();}catch(e){}; try{Main.messageTray._banner?.destroy();}catch(e){}; true" >/dev/null 2>&1 || true
# Close leftover windows (killall by binary — avoid pkill -f matching this SSH cmdline)
killall -u arch -q papers evince chromium ghostty nautilus gnome-control-center gnome-tweaks 2>/dev/null || true
pkill -u arch -f "/usr/local/lib/gnomarchi/apps/" 2>/dev/null || true
pkill -u arch -f "python3 -m menu" 2>/dev/null || true
sleep 0.6'
  vnc_escape
}

close_ui() {
  guest 'killall -u arch -q papers evince chromium ghostty nautilus gnome-control-center gnome-tweaks 2>/dev/null || true
pkill -u arch -f "/usr/local/lib/gnomarchi/apps/" 2>/dev/null || true
pkill -u arch -f "python3 -m menu" 2>/dev/null || true
gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell \
  --method org.gnome.Shell.Eval "try{Main.overview.hide();}catch(e){}; try{Main.messageTray.getQueue().forEach(n=>n.destroy());}catch(e){}; try{Main.messageTray._banner?.destroy();}catch(e){}; true" >/dev/null 2>&1 || true
wmctrl -c Agents 2>/dev/null || true
wmctrl -c Settings 2>/dev/null || true
wmctrl -c gnoma 2>/dev/null || true
sleep 0.5'
  vnc_escape
}

# Center a window by substring match; fallback: first matching class.
center_win() {
  local needle="$1"
  local w="${2:-720}"
  local h="${3:-640}"
  guest "W=${w}; H=${h}; NEEDLE='${needle}'
SW=\$(xdpyinfo 2>/dev/null | awk '/dimensions/{print \$2}' | cut -dx -f1)
SH=\$(xdpyinfo 2>/dev/null | awk '/dimensions/{print \$2}' | cut -dx -f2)
SW=\${SW:-1920}; SH=\${SH:-1080}
X=\$(( (SW - W) / 2 )); Y=\$(( (SH - H) / 2 - 20 )); [[ \$Y -lt 40 ]] && Y=40
# Prefer exact name match, then class
IDS=\$(xdotool search --name \"\$NEEDLE\" 2>/dev/null)
[[ -z \"\$IDS\" ]] && IDS=\$(xdotool search --classname \"\$NEEDLE\" 2>/dev/null)
[[ -z \"\$IDS\" ]] && IDS=\$(xdotool search --class \"\$NEEDLE\" 2>/dev/null)
for id in \$IDS; do
  xdotool windowactivate --sync \$id 2>/dev/null || true
  xdotool windowsize \$id \$W \$H 2>/dev/null || true
  xdotool windowmove \$id \$X \$Y 2>/dev/null || true
  break
done
# Also try wmctrl -r
wmctrl -r \"\$NEEDLE\" -e 0,\$X,\$Y,\$W,\$H 2>/dev/null || true
sleep 0.35"
}

shot_jpg() {
  local name="$1"
  local png jpg
  png="$(mktemp --suffix=.png)"
  jpg="${OUT}/${name}.jpg"
  pkill -f 'vncdotool' 2>/dev/null || true
  # Kill sticky toasts before every frame (never Escape — dismisses GTK dialogs).
  guest 'gnomarchi notice silence >/dev/null 2>&1 || true' || true
  sleep 0.25
  if ! timeout 22 "$VNC" -s "$VNC_ADDR" capture "$png" >/dev/null 2>&1; then
    echo "FAIL capture ${name}"
    rm -f "$png"
    return 1
  fi
  local sz
  sz=$(stat -c%s "$png" 2>/dev/null || echo 0)
  if [[ "$sz" -lt 8000 ]]; then
    echo "FAIL tiny ${name} ${sz}b"
    rm -f "$png"
    return 1
  fi
  if command -v magick >/dev/null; then
    magick "$png" -quality "$JPG_QUALITY" -strip "$jpg"
  elif command -v convert >/dev/null; then
    convert "$png" -quality "$JPG_QUALITY" -strip "$jpg"
  elif command -v ffmpeg >/dev/null; then
    ffmpeg -y -loglevel error -i "$png" -q:v 3 "$jpg"
  else
    cp "$png" "${OUT}/${name}.png"
    echo "WARN no magick/convert; left ${name}.png"
    rm -f "$png"
    return 0
  fi
  rm -f "$png"
  sz=$(stat -c%s "$jpg" 2>/dev/null || echo 0)
  echo "OK ${name}.jpg ${sz}b"
}

echo "=== desktop-proof START $(date -Is) → ${OUT} ==="
prep_desktop

# 0) Clean desktop baseline (for branding / navigation)
shot_jpg desktop-clean || true

# 1) Agents window — centered, alone
close_ui
guest 'nohup env GDK_BACKEND=x11 gnomarchi agent window >/tmp/parity-agents.log 2>&1 &
sleep 1.8'
center_win "Agents" 720 820
shot_jpg agents-window || true
close_ui

# 2) Tray popups top-right (Omarchy-comparable) — NOT full Settings windows
for panel in audio network bluetooth power display calendar; do
  close_ui
  guest "nohup env GDK_BACKEND=x11 gnomarchi panel ${panel} >/tmp/parity-panel-${panel}.log 2>&1 &
sleep 1.5
TITLE=$(python3 -c \"print('${panel}'.title())\")
# 1920 logical top-right under GNOME bar
id=\$(xdotool search --name \"\$TITLE\" 2>/dev/null | head -1)
[[ -n \$id ]] && xdotool windowactivate --sync \$id windowsize \$id 340 300 windowmove \$id 1572 36 2>/dev/null || true"
  # do not Escape before shot — dismisses panel
  shot_jpg "panel-${panel}" || true
  close_ui
done

# 3) First-party apps — one window, centered
close_ui
guest 'nohup env GDK_BACKEND=x11 gnomarchi app write >/tmp/parity-write.log 2>&1 &
sleep 1.8'
center_win "write" 1100 780
center_win "gnoma-write" 1100 780
shot_jpg app-write || true
close_ui

guest 'nohup env GDK_BACKEND=x11 gnomarchi app calc >/tmp/parity-calc.log 2>&1 &
sleep 1.6'
center_win "calc" 420 520
center_win "gnoma-calc" 420 520
shot_jpg app-calc || true
close_ui

guest 'nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/gnoma-cut/main.py >/tmp/parity-cut.log 2>&1 &
sleep 1.6'
center_win "cut" 900 700
center_win "gnoma-cut" 900 700
shot_jpg app-cut || true
close_ui

# 4) Menu root (must be root Go… list, not a deep branch)
close_ui
guest 'pkill -u arch -f "python3 -m menu|gnomarchi menu" 2>/dev/null || true
nohup env GDK_BACKEND=x11 gnomarchi menu open >/tmp/parity-menu.log 2>&1 &
sleep 1.6'
center_win "Command" 420 560
center_win "menu" 420 560
center_win "Go" 420 560
shot_jpg menu-root || true
close_ui

# 5) Notice time toast — capture quickly while banner visible
close_ui
guest 'gnomarchi notice time >/tmp/parity-notice.log 2>&1'
sleep 0.45
# do NOT escape (would dismiss); capture immediately
png="$(mktemp --suffix=.png)"
jpg="${OUT}/notice-time.jpg"
if timeout 22 "$VNC" -s "$VNC_ADDR" capture "$png" >/dev/null 2>&1; then
  if command -v magick >/dev/null; then magick "$png" -quality "$JPG_QUALITY" -strip "$jpg"
  elif command -v convert >/dev/null; then convert "$png" -quality "$JPG_QUALITY" -strip "$jpg"
  else cp "$png" "$jpg"; fi
  echo "OK notice-time.jpg $(stat -c%s "$jpg")b"
fi
rm -f "$png"
close_ui

# 6) Terminal / neovim / btop / files / browser / pdf / clipboard / theme picker
close_ui
guest 'nohup ghostty -e bash -lc "clear; echo gnomarchi / ghostty; cat ~/.config/gnomarchi/active-theme; exec bash" >/tmp/parity-gt.log 2>&1 &
sleep 1.5'
center_win "ghostty" 1000 640
center_win "Ghostty" 1000 640
shot_jpg terminal-ghostty || true
close_ui

guest 'nohup ghostty -e bash -lc "nvim -c \"echo \\\"gnomarchi nvim\\\"\" -c \"sleep 30\"" >/tmp/parity-nvim.log 2>&1 &
sleep 2.0'
center_win "ghostty" 1100 720
shot_jpg neovim || true
close_ui

guest 'nohup ghostty -e bash -lc "btop" >/tmp/parity-btop.log 2>&1 &
sleep 1.8'
center_win "ghostty" 1100 720
shot_jpg tui-btop || true
close_ui

guest 'nohup nautilus --new-window >/tmp/parity-files.log 2>&1 &
sleep 1.8'
center_win "Files" 1000 700
center_win "Home" 1000 700
shot_jpg files || true
close_ui

guest 'nohup chromium --new-window about:blank >/tmp/parity-chrome.log 2>&1 &
sleep 2.5'
center_win "Chromium" 1200 800
center_win "Chrome" 1200 800
shot_jpg browser-chromium || true
close_ui

guest 'echo "%PDF-1.4
1 0 obj<<>>endobj
trailer<<>>
%%EOF" > /tmp/parity-sample.pdf
nohup papers /tmp/parity-sample.pdf >/tmp/parity-pdf.log 2>&1 || nohup evince /tmp/parity-sample.pdf >/tmp/parity-pdf.log 2>&1 &
sleep 1.8'
center_win "Papers" 900 700
center_win "Document" 900 700
center_win "Evince" 900 700
shot_jpg pdf-viewer || true
close_ui

guest 'nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/clipboard.py >/tmp/parity-clip.log 2>&1 &
sleep 1.4
# fallback CLI
nohup env GDK_BACKEND=x11 gnomarchi clipboard >/tmp/parity-clip2.log 2>&1 &
sleep 0.8'
center_win "clipboard" 640 480
center_win "Clipboard" 640 480
shot_jpg clipboard || true
close_ui

guest 'nohup env GDK_BACKEND=x11 gnomarchi theme pick >/tmp/parity-tp.log 2>&1 &
sleep 2.0'
center_win "Theme" 900 700
center_win "theme" 900 700
shot_jpg theme-picker || true
close_ui

guest 'nohup env GDK_BACKEND=x11 gnomarchi remind >/tmp/parity-remind.log 2>&1 &
sleep 1.4'
center_win "remind" 640 480
center_win "Remind" 640 480
shot_jpg reminders || true
close_ui

# Keybindings cheatsheet if present
guest 'KB=$(ls ~/.config/gnomarchi/*keybind* /usr/local/share/gnomarchi/*keybind* 2>/dev/null | head -1)
if [[ -n "$KB" ]]; then
  nohup papers "$KB" >/tmp/parity-kb.log 2>&1 || nohup xdg-open "$KB" >/tmp/parity-kb.log 2>&1 &
  sleep 1.5
fi
# else open Settings keyboard
nohup env GDK_BACKEND=x11 XDG_CURRENT_DESKTOP=GNOME gnome-control-center keyboard >/tmp/parity-kb2.log 2>&1 &
sleep 2.0'
center_win "Settings" 980 720
center_win "Keyboard" 980 720
shot_jpg keybindings || true
close_ui

# Icons proof — files + calc side by side, icons visible in dock when overview briefly? Prefer desktop with nautilus icons
guest 'nohup nautilus --new-window >/tmp/parity-icons-f.log 2>&1 &
sleep 1.2
nohup env GDK_BACKEND=x11 gnomarchi app calc >/tmp/parity-icons-c.log 2>&1 &
sleep 1.4
# place files left, calc right (not overview)
SW=$(xdpyinfo 2>/dev/null | awk "/dimensions/{print \$2}" | cut -dx -f1); SW=${SW:-1920}
FID=$(xdotool search --name Files 2>/dev/null | head -1)
CID=$(xdotool search --name calc 2>/dev/null | head -1)
[[ -n "$FID" ]] && xdotool windowsize "$FID" 780 640 windowmove "$FID" 80 80
[[ -n "$CID" ]] && xdotool windowsize "$CID" 400 500 windowmove "$CID" $((SW - 460)) 100
sleep 0.4'
shot_jpg icons-apps || true
close_ui

echo "=== desktop-proof DONE ==="
ls -la "$OUT"/*.jpg 2>/dev/null || ls -la "$OUT"/
