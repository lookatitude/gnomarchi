#!/usr/bin/env bash
# Capture W3 / residual gallery shots: capture UX, notices history, share,
# custom theme, gaming/windows-vm, input, menu branches, plymouth/GDM, icons.
# Requires PARITY_CAPTURE=1. Uses VNC 5901 / SSH 2222.
set -uo pipefail
# tolerate xdotool/wmctrl misses; still fail on missing tools at top
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-proof/desktop"
CLOSE="${ROOT}/docs/screenshots/parity-proof/closeness"
ICONS="${ROOT}/docs/screenshots/parity-proof/icons"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
KEY="${KEY:-/home/miguelp/.ssh/id_rsa}"
JPG_QUALITY="${JPG_QUALITY:-82}"

if [[ "${PARITY_CAPTURE:-0}" != "1" && "${PARITY_CAPTURE:-}" != "true" ]]; then
  echo "skip: set PARITY_CAPTURE=1"
  exit 0
fi
mkdir -p "$OUT" "$CLOSE" "$ICONS"

remote() {
  timeout 90 ssh -i "$KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
    -p 2222 arch@127.0.0.1 bash -s <<EOF
set +e
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export HOME=/home/arch PATH=/usr/local/bin:\$HOME/.local/bin:\$PATH
export DISPLAY=:0 GDK_BACKEND=x11 XDG_CURRENT_DESKTOP=GNOME
export GNOMARCHI_ROOT=/usr/local/lib/gnomarchi
AUTH=\$(ls /run/user/1000/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
[[ -n \$AUTH ]] && export XAUTHORITY=\$AUTH
$1
EOF
}

shot() {
  local dest=$1 png
  png=$(mktemp --suffix=.png)
  remote 'gnomarchi notice silence >/dev/null 2>&1 || true' || true
  sleep 0.4
  timeout 18 "$VNC" -s 127.0.0.1::5901 capture "$png" >/dev/null
  magick "$png" -quality "$JPG_QUALITY" -strip "$dest"
  rm -f "$png"
  echo "OK $(basename "$dest") $(stat -c%s "$dest")b"
}

nuke() {
  remote 'gnomarchi notice silence >/dev/null 2>&1 || true
pkill -u arch -f org.gnomarchi 2>/dev/null || true
pkill -u arch -f "python3 -m menu" 2>/dev/null || true
pkill -u arch -f gnome-control-center 2>/dev/null || true
pkill -u arch -f virt-manager 2>/dev/null || true
pkill -u arch -f steam 2>/dev/null || true
pkill -u arch -f LocalSend 2>/dev/null || true
pkill -u arch -f localsend 2>/dev/null || true
pkill -u arch -f flatpak.*localsend 2>/dev/null || true
pkill -u arch -f nautilus 2>/dev/null || true
pkill -u arch -f lutris 2>/dev/null || true
for t in Capture Notices Calendar Audio Network Share Themes Command Capture Steam Virt LocalSend Settings Files Lutris; do
  wmctrl -c "$t" 2>/dev/null || true
done
sleep 0.5
echo nuked'
}

place() {
  local title=$1 x=${2:-1540} y=${3:-36} w=${4:-360} h=${5:-320}
  remote "TITLE='$title'; X=$x; Y=$y; W=$w; H=$h
for i in 1 2 3 4 5 6 7 8; do
  id=\$(xdotool search --name \"\$TITLE\" 2>/dev/null | head -1)
  [[ -n \$id ]] && break
  sleep 0.2
done
id=\$(xdotool search --name \"\$TITLE\" 2>/dev/null | head -1)
[[ -n \$id ]] && xdotool windowactivate --sync \$id windowsize \$id \$W \$H windowmove \$id \$X \$Y
echo placed"
}

center() {
  local title=$1 w=${2:-640} h=${3:-520}
  remote "N='$title'; W=$w; H=$h; X=\$(( (1920-W)/2 )); Y=\$(( (1080-H)/2 - 20 )); [[ \$Y -lt 40 ]] && Y=40
id=\$(xdotool search --name \"\$N\" 2>/dev/null | head -1)
[[ -n \$id ]] && xdotool windowactivate --sync \$id windowsize \$id \$W \$H windowmove \$id \$X \$Y
echo centered"
}

echo "=== w3-residuals START $(date -Is) ==="
nuke

# Capture menu
remote 'nohup gnomarchi capture menu >/tmp/cap-menu.log 2>&1 &'
sleep 1.2
place Capture 780 200 340 300
shot "${OUT}/capture-menu.jpg"
nuke

# Notice history (seed + UI)
remote 'gnomarchi notice time; gnomarchi notice battery; sleep 0.5
nohup gnomarchi notice history >/tmp/notice-hist.log 2>&1 &'
sleep 1.2
center Notices 440 500
shot "${OUT}/notice-history.jpg"
nuke

# Calendar under clock
remote 'nohup gnomarchi panel calendar >/tmp/cal.log 2>&1 &'
sleep 1.0
# panels.py anchors; nudge if needed
place Calendar 780 36 380 400
shot "${OUT}/panel-calendar.jpg"
nuke

# Custom theme from wallpaper (CLI proof in Ghostty)
remote 'WP=$(ls /usr/share/backgrounds/gnome/*.jpg 2>/dev/null | head -1)
WP=${WP:-/usr/share/pixmaps/archlinux-logo.png}
rm -rf ~/.config/gnomarchi/themes/from-wallpaper
gnomarchi theme new from-wallpaper --from-wallpaper "$WP" >/tmp/theme-new.log 2>&1
head -20 ~/.config/gnomarchi/themes/from-wallpaper/colors.toml >/tmp/theme-new-colors.txt
nohup ghostty -e bash -lc "clear; echo CUSTOM THEME FROM WALLPAPER; cat ~/.config/gnomarchi/themes/from-wallpaper/colors.toml; sleep 25" >/tmp/gt-theme.log 2>&1 &'
sleep 1.5
remote 'id=$(xdotool search --class ghostty 2>/dev/null | head -1)
[[ -z $id ]] && id=$(xdotool search --name Ghostty 2>/dev/null | head -1)
[[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 720 480 windowmove $id 600 200 || true'
shot "${OUT}/custom-theme.jpg" || true
nuke

# Files + papirus folder tint
remote 'export PATH="$HOME/.local/bin:$PATH" GNOMARCHI_ROOT=/usr/local/lib/gnomarchi PYTHONPATH=/usr/local/lib/gnomarchi
gnomarchi theme set tokyo-night >/dev/null
python3 - <<PY
from theme.icon_apply import apply_pack_icons, ensure_papirus_folders_bin
from pathlib import Path
ensure_papirus_folders_bin()
p = Path("/usr/local/lib/gnomarchi/theme/packs/tokyo-night")
print(apply_pack_icons(p) if p.is_dir() else "no pack")
PY
mkdir -p ~/Desktop/tint-demo/{alpha,beta,gamma}
nohup nautilus --new-window ~/Desktop/tint-demo >/tmp/nautilus.log 2>&1 &'
sleep 1.8
place Files 400 120 900 600 || true
shot "${ICONS}/papirus-tokyo-night-desktop.jpg" || true
shot "${OUT}/icons-apps.jpg" || true
nuke

# LocalSend / share
remote 'gnomarchi share nautilus >/dev/null
if ! flatpak list --app 2>/dev/null | grep -q localsend; then
  flatpak install -y flathub org.localsend.localsend_app >/tmp/localsend-install.log 2>&1 || true
fi
nohup gnomarchi share receive >/tmp/share.log 2>&1 &'
sleep 2.5
# title varies
remote 'for n in LocalSend localsend org.localsend; do
  id=$(xdotool search --name "$n" 2>/dev/null | head -1)
  [[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 720 520 windowmove $id 600 180 && break
done'
shot "${OUT}/share-localsend.jpg"
nuke

# Gaming (Steam if present; else lutris / menu Install›Gaming)
remote 'if command -v steam >/dev/null; then
  nohup steam -silent >/tmp/steam.log 2>&1 &
  sleep 3
  nohup steam >/tmp/steam2.log 2>&1 &
elif command -v lutris >/dev/null; then
  nohup lutris >/tmp/lutris.log 2>&1 &
else
  nohup ghostty -e bash -lc "echo Install›Gaming; pacman -Qi steam lutris 2>&1 | head -20; sleep 20" >/tmp/gaming.log 2>&1 &
fi'
sleep 3
remote 'for n in Steam Lutris steam lutris ghostty Ghostty; do
  id=$(xdotool search --name "$n" 2>/dev/null | head -1)
  [[ -n $id ]] && xdotool windowactivate --sync $id windowmove $id 400 100 && break
done'
shot "${OUT}/gaming.jpg"
nuke

# Windows VM / virt-manager
remote 'if command -v virt-manager >/dev/null; then
  nohup virt-manager >/tmp/virt.log 2>&1 &
else
  nohup ghostty -e bash -lc "echo Windows VM stack; pacman -Qi virt-manager qemu-desktop 2>&1 | head -20; sleep 20" >/tmp/wvm.log 2>&1 &
fi'
sleep 2.5
remote 'for n in "Virtual Machine" virt-manager Virt; do
  id=$(xdotool search --name "$n" 2>/dev/null | head -1)
  [[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 900 640 windowmove $id 400 120 && break
done'
shot "${OUT}/windows-vm.jpg"
nuke

# Input settings
remote 'nohup gnome-control-center mouse >/tmp/gcc-mouse.log 2>&1 &'
sleep 1.5
center Settings 900 640 || place Settings 400 100 900 640
shot "${OUT}/input-settings.jpg"
nuke

# Menu branches: Style / Install / Setup / Apps filter
for branch in Style Install Setup; do
  remote "pkill -u arch -f 'python3 -m menu' 2>/dev/null || true
cd /usr/local/lib/gnomarchi && nohup python3 -m menu >/tmp/menu-$branch.log 2>&1 &"
  sleep 1.0
  # type filter to dive — palette supports search; send keys via xdotool
  remote "sleep 0.3
xdotool type --delay 40 '$branch'
sleep 0.4"
  center Command 640 520 || place Command 640 200 640 520
  shot "${OUT}/menu-${branch,,}.jpg"
  nuke
done

# Dotfiles / config status
remote 'nohup ghostty -e bash -lc "clear; echo DOTFILES / CONFIG; gnomarchi config status 2>/dev/null || gnomarchi config show 2>/dev/null || ls -la ~/.config/gnomarchi | head -30; sleep 22" >/tmp/dot.log 2>&1 &'
sleep 1.5
remote 'id=$(xdotool search --class ghostty 2>/dev/null | head -1); [[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 780 520 windowmove $id 560 180'
shot "${OUT}/dotfiles.jpg"
nuke

# Plymouth / GDM branding proof (static preview when live greeter unavailable)
remote 'sudo pacman -Sy --needed --noconfirm plymouth 2>/dev/null | tail -3
gnomarchi branding plymouth status 2>/dev/null || true
gnomarchi branding gdm status 2>/dev/null || true
# Generate a simple preview PNG if branding can emit one; else show status in ghostty
nohup ghostty -e bash -lc "clear; echo PLYMOUTH / GDM BRANDING; gnomarchi branding plymouth status; echo; gnomarchi branding gdm status; ls -la /usr/share/plymouth/themes/gnomarchi 2>/dev/null | head; ls /usr/local/share/gnomarchi/gdm 2>/dev/null | head; sleep 22" >/tmp/boot.log 2>&1 &'
sleep 1.5
remote 'id=$(xdotool search --class ghostty 2>/dev/null | head -1); [[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 820 560 windowmove $id 520 160'
shot "${CLOSE}/plymouth-gdm-status.jpg"
nuke

# Shell tools collage (btop already exists; add fzf/eza proof)
remote 'nohup ghostty -e bash -lc "clear; echo SHELL TOOLS; command -v fzf eza zoxide bat fd rg; eza -la ~/.config/gnomarchi | head; sleep 20" >/tmp/shell.log 2>&1 &'
sleep 1.4
remote 'id=$(xdotool search --class ghostty 2>/dev/null | head -1); [[ -n $id ]] && xdotool windowactivate --sync $id windowsize $id 780 520 windowmove $id 560 180'
shot "${OUT}/shell-tools.jpg"
nuke

echo "=== w3-residuals DONE $(date -Is) ==="
ls -la "$OUT"/capture-menu.jpg "$OUT"/notice-history.jpg "$OUT"/share-localsend.jpg \
  "$OUT"/custom-theme.jpg "$OUT"/gaming.jpg "$OUT"/windows-vm.jpg \
  "$OUT"/input-settings.jpg "$CLOSE"/plymouth-gdm-status.jpg 2>&1 | head -20
