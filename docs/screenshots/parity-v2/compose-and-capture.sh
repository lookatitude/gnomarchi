#!/usr/bin/env bash
# 1080p composite + matrix: stock GNOME top bar, windows spread with no overlap.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-v2"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
SSH=(ssh -i /home/miguelp/.ssh/id_rsa -o StrictHostKeyChecking=no
     -o UserKnownHostsFile=/dev/null -o ConnectTimeout=8 -p 2222 arch@127.0.0.1)
mkdir -p "$OUT"
pkill -f vncdotool 2>/dev/null || true
sleep 0.3

shot() {
  local id="$1"
  timeout 25 "$VNC" -s 127.0.0.1::5901 capture "$OUT/${id}.png"
  echo "ok ${id} $(identify -format '%wx%h' "$OUT/${id}.png" 2>/dev/null || echo '?')"
}

# Sync + layout on guest
"${SSH[@]}" 'bash -s' <<'GUEST'
set -e
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export HOME=/home/arch
export PATH=/usr/local/bin:$PATH
sudo loginctl unlock-sessions >/dev/null 2>&1 || true

# Sync from 9p
if [[ -d /mnt/gnomarchi ]]; then
  sudo cp -a /mnt/gnomarchi/theme/emitters.py /usr/local/lib/gnomarchi/theme/emitters.py
  sudo cp -a /mnt/gnomarchi/common/window_geom.py /usr/local/lib/gnomarchi/common/window_geom.py
  sudo cp -a /mnt/gnomarchi/common/bar_position.py /usr/local/lib/gnomarchi/common/bar_position.py
  sudo cp -a /mnt/gnomarchi/apps/theme-picker/gnomarchi_theme_picker.py \
    /usr/local/lib/gnomarchi/apps/theme-picker/gnomarchi_theme_picker.py
  sudo cp -a /mnt/gnomarchi/apps/agents-window/agents_window.py \
    /usr/local/lib/gnomarchi/apps/agents-window/agents_window.py
  sudo cp -a /mnt/gnomarchi/bin/gnomarchi /usr/local/bin/gnomarchi
fi

# Persist 1920x1080
python3 - <<'PY'
import dbus
bus = dbus.SessionBus()
dc = bus.get_object("org.gnome.Mutter.DisplayConfig", "/org/gnome/Mutter/DisplayConfig")
iface = dbus.Interface(dc, "org.gnome.Mutter.DisplayConfig")
serial, monitors, logical, props = iface.GetCurrentState()
conn = mode_id = None
for m in monitors:
    meta, modes = m[0], m[1]
    conn = str(meta[0])
    for mode in modes:
        if int(mode[1]) == 1920 and int(mode[2]) == 1080 and "60" in str(mode[0]):
            mode_id = str(mode[0]); break
    if mode_id: break
iface.ApplyMonitorsConfig(serial, 2,
    [(dbus.Int32(0), dbus.Int32(0), dbus.Double(1.0), dbus.UInt32(0), True, [(conn, mode_id, {})])], {})
print("display", mode_id)
PY

# Stock Omarchy-like top bar (not dash-to-panel)
gnome-extensions disable dash-to-panel@jderose9.github.com 2>/dev/null || true
gnomarchi shell bar-position top >/dev/null
gnomarchi theme set tokyo-night >/dev/null

AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11

pkill -u arch -f 'agents_window|theme_picker|ghostty|nautilus|gnome-tweaks|python3 -m menu|gnoma-|chromium|btop|nvim' 2>/dev/null || true
sleep 1

# Indicators
for d in "$HOME"/.local/share/gnomarchi/indicators/*/indicator.py; do
  id=$(basename "$(dirname "$d")")
  pgrep -u arch -f "indicators/$id/indicator" >/dev/null || nohup python3 "$d" >/dev/null 2>&1 &
done

place() {
  # place <title-regex> x y w h
  local re="$1" x="$2" y="$3" w="$4" h="$5"
  local id
  for _ in $(seq 1 25); do
    id=$(wmctrl -l | awk -v re="$re" 'BEGIN{IGNORECASE=1} $0 ~ re {print $1; exit}')
    [[ -n "$id" ]] && break
    sleep 0.2
  done
  [[ -n "$id" ]] || { echo "missing $re"; return 1; }
  wmctrl -i -r "$id" -b remove,maximized_vert,maximized_horz
  wmctrl -i -r "$id" -e "0,$x,$y,$w,$h"
  echo "placed $re -> $x,$y ${w}x${h}"
}

# 2x2 grid under top bar (y starts ~40)
# TL Files | TR Ghostty
# BL Theme | BR Agents
nohup env GDK_BACKEND=x11 nautilus --new-window /home/arch >/tmp/nau.log 2>&1 &
sleep 1.5
place 'Home|Files|arch' 16 44 944 1012 || true

nohup env GDK_BACKEND=x11 ghostty >/tmp/g.log 2>&1 &
sleep 1.5
place 'ghostty|Ghostty|arch@' 976 44 928 492 || true

nohup env GDK_BACKEND=x11 GNOMARCHI_WINDOW_GEOM=976,552,448,504 \
  gnomarchi theme pick >/tmp/pick.log 2>&1 &
sleep 1.8
place 'Theme' 976 552 448 504 || true

nohup env GDK_BACKEND=x11 GNOMARCHI_WINDOW_GEOM=1440,552,464,504 \
  python3 /usr/local/lib/gnomarchi/apps/agents-window/agents_window.py >/tmp/a.log 2>&1 &
sleep 1.8
place 'Agents' 1440 552 464 504 || true

wmctrl -l || true
echo COMPOSITE_READY
GUEST

shot V-00-composite-desktop
shot V-01-desktop-overview
shot V-02-panel-tray
shot V-04-panel-agents-chip
shot V-05-panel-weather
shot V-06-panel-update
shot V-07-panel-tailscale
shot V-09-style-theme-carousel
shot V-10-theme-a-gtk
shot V-13-theme-a-wallpaper
shot V-15-shell-css-panel
shot V-16-agents-window
shot V-21-hotkey-theme

# Ghostty alone (keep top bar proof)
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH"
pkill -u arch -f 'agents_window|theme_picker|nautilus' 2>/dev/null || true
sleep 0.5
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /ghostty|Ghostty|arch@/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,200,80,1520,920
GUEST
shot V-11-theme-a-ghostty

# Menu
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f 'ghostty|python3 -m menu' 2>/dev/null || true
cd /usr/local/lib/gnomarchi && nohup env GDK_BACKEND=x11 python3 -m menu >/tmp/menu.log 2>&1 &
sleep 1.5
GUEST
shot V-08-menu-root
timeout 8 "$VNC" -s 127.0.0.1::5901 type Install || true
sleep 0.3
shot V-17-menu-branches

# Theme B
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f 'python3 -m menu' 2>/dev/null || true
gnomarchi theme set catppuccin >/dev/null
nohup env GDK_BACKEND=x11 gnomarchi theme pick >/tmp/pick.log 2>&1 &
sleep 1.5
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /Theme/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,600,120,720,800
GUEST
shot V-12-theme-b-gtk

# bg cycle
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
pkill -u arch -f theme_picker 2>/dev/null || true
gnomarchi theme set tokyo-night >/dev/null
gnomarchi theme bg next >/dev/null
sleep 1
GUEST
shot V-14-bg-cycle
shot V-22-hotkey-bg

# user-themes
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
nohup env GDK_BACKEND=x11 gnome-extensions prefs user-theme@gnome-shell-extensions.gcampax.github.com >/dev/null 2>&1 &
sleep 2
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /Extensions|User Themes|prefs/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,400,80,1100,900
GUEST
shot V-03-ext-user-themes

# nvim / btop / chromium / tweaks / no-hypr / optional bottom / gnoma
run_app_shot() {
  local remote="$1" id="$2"
  "${SSH[@]}" "bash -s" <<<"$remote"
  shot "$id"
}

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f 'gnome-extensions prefs' 2>/dev/null || true
nohup env GDK_BACKEND=x11 ghostty -e nvim /usr/local/lib/gnomarchi/README.md >/tmp/nvim.log 2>&1 &
sleep 2
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /nvim|ghostty|README/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,160,60,1600,960
GUEST
shot V-18-theme-nvim

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f 'ghostty|nvim' 2>/dev/null || true
if command -v btop >/dev/null; then nohup env GDK_BACKEND=x11 ghostty -e btop >/tmp/btop.log 2>&1 &
else nohup env GDK_BACKEND=x11 ghostty -e bash -c 'echo btop_missing; sleep 30' >/tmp/btop.log 2>&1 & fi
sleep 2
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /btop|ghostty/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,160,60,1600,960
GUEST
shot V-19-theme-btop

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f 'ghostty|btop' 2>/dev/null || true
nohup env GDK_BACKEND=x11 chromium --no-first-run about:blank >/tmp/chr.log 2>&1 &
sleep 3.5
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /chrom/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,80,48,1760,1000
GUEST
shot V-20-theme-chromium

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f chromium 2>/dev/null || true
nohup env GDK_BACKEND=x11 gnome-tweaks >/tmp/t.log 2>&1 &
sleep 2
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /Tweaks/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,360,80,1200,900
GUEST
shot V-23-tweaks

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f gnome-tweaks 2>/dev/null || true
pacman -Q hyprland >/tmp/nohypr.txt 2>&1 || true
echo "XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP" >>/tmp/nohypr.txt
echo "bar=stock_GNOME_top (Omarchy default position)" >>/tmp/nohypr.txt
nohup env GDK_BACKEND=x11 ghostty -e bash -c 'cat /tmp/nohypr.txt; sleep 25' >/tmp/nh.log 2>&1 &
sleep 2
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /ghostty|arch@/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,240,100,1440,800
GUEST
shot V-24-no-hyprland

# Optional bottom bar (Omarchy allows bar position bottom)
"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
pkill -u arch -f ghostty 2>/dev/null || true
gnomarchi shell bar-position bottom
sleep 2
GUEST
shot V-27-dash-to-panel-optional

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
gnomarchi shell bar-position top
sleep 1.2
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/gnoma-calc/main.py >/tmp/c.log 2>&1 &
sleep 1.5
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /calc|gnoma/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,720,200,480,560
GUEST
shot V-25-gnoma-calc

"${SSH[@]}" 'bash -s' <<'GUEST'
export XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus HOME=/home/arch PATH=/usr/local/bin:$PATH
AUTH=$(ls /run/user/1000/.mutter-Xwaylandauth.* | head -1)
export DISPLAY=:0 XAUTHORITY="$AUTH" GDK_BACKEND=x11
pkill -u arch -f gnoma-calc 2>/dev/null || true
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/gnoma-write/main.py >/tmp/w.log 2>&1 &
sleep 1.5
id=$(wmctrl -l | awk 'BEGIN{IGNORECASE=1} /write|gnoma/ {print $1; exit}')
[[ -n "$id" ]] && wmctrl -i -r "$id" -e 0,400,80,1120,900
GUEST
shot V-26-gnoma-write

echo '---'
for f in "$OUT"/V-*.png; do
  printf '%10s %s\n' "$(identify -format '%wx%h' "$f" 2>/dev/null)" "$(basename "$f")"
done | sort -k2
md5sum "$OUT"/V-*.png | awk '{h=$1;n=$2;sub(".*/","",n);c[h]++;f[h]=f[h]" "n} END{for(h in c) if(c[h]>1) print "DUP",c[h],f[h]}'
echo DONE
