#!/usr/bin/env bash
# Unlock session, then capture each V-* with a distinct on-screen feature.
set -u
OUT="$(cd "$(dirname "$0")" && pwd)"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
SSH=(ssh -o ConnectTimeout=8 -i /home/miguelp/.ssh/id_rsa
     -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -p 2222 arch@127.0.0.1)
pkill -f vncdotool 2>/dev/null || true
sleep 0.3

guest() {
  "${SSH[@]}" 'bash -s' <<EOF
set +e
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export HOME=/home/arch PATH=/usr/local/bin:\$PATH
AUTH=\$(ls /run/user/1000/.mutter-Xwaylandauth.* 2>/dev/null | head -1)
export DISPLAY=:0 XAUTHORITY="\$AUTH" GDK_BACKEND=x11
sudo loginctl unlock-sessions >/dev/null 2>&1
gdbus call --session --dest org.gnome.ScreenSaver --object-path /org/gnome/ScreenSaver --method org.gnome.ScreenSaver.SetActive false >/dev/null 2>&1
$1
EOF
}

shot() {
  local id="$1"
  timeout 18 "$VNC" -s 127.0.0.1::5901 key space >/dev/null 2>&1 || true
  sleep 0.2
  timeout 20 "$VNC" -s 127.0.0.1::5901 capture "$OUT/${id}.png"
  local sz
  sz=$(stat -c%s "$OUT/${id}.png" 2>/dev/null || echo 0)
  if [[ "$sz" -lt 80000 ]]; then
    echo "BAD_${id}_${sz}b"
    return 1
  fi
  echo "OK_${id}_${sz}b"
}

kill_apps() {
  guest 'pkill -u arch -f "agents_window|theme_picker|ghostty|nautilus|python3 -m menu|chromium|gnome-tweaks|gnoma-|nvim|btop|gnome-extensions prefs" 2>/dev/null; sleep 0.6'
}

# Prep
guest '
python3 - <<"PY"
import dbus
bus=dbus.SessionBus(); dc=bus.get_object("org.gnome.Mutter.DisplayConfig","/org/gnome/Mutter/DisplayConfig")
iface=dbus.Interface(dc,"org.gnome.Mutter.DisplayConfig")
serial,monitors,_,_=iface.GetCurrentState()
conn=mode=None
for m in monitors:
  meta,modes=m[0],m[1]; conn=str(meta[0])
  for mt in modes:
    if int(mt[1])==1920 and int(mt[2])==1080 and "60" in str(mt[0]):
      mode=str(mt[0]); break
  if mode: break
iface.ApplyMonitorsConfig(serial,2,[(dbus.Int32(0),dbus.Int32(0),dbus.Double(1.0),dbus.UInt32(0),True,[(conn,mode,{})])],{})
print("res",mode)
PY
gnome-extensions disable dash-to-panel@jderose9.github.com 2>/dev/null
gnomarchi shell bar-position top >/dev/null
gnomarchi theme set tokyo-night >/dev/null
for d in "$HOME"/.local/share/gnomarchi/indicators/*/indicator.py; do
  [[ -f "$d" ]] || continue
  base=$(basename "$(dirname "$d")")
  pgrep -f "indicators/$base/indicator" >/dev/null || nohup python3 "$d" >/dev/null 2>&1 &
done
echo PREP
'

kill_apps
sleep 1
shot V-01-desktop-overview || true
shot V-02-panel-tray || true

# V-03 user-themes prefs
guest 'nohup env GDK_BACKEND=x11 gnome-extensions prefs user-theme@gnome-shell-extensions.gcampax.github.com >/tmp/ut.log 2>&1 & sleep 2.5
xdotool search --name "User Themes" windowmove 250 50 windowsize 900 700 2>/dev/null
wmctrl -l | head'
shot V-03-ext-user-themes || true

# Panel indicators: clean desktop (close prefs) — then crop tops later
guest 'pkill -u arch -f "gnome-extensions prefs" 2>/dev/null; sleep 0.5'
shot V-04-panel-agents-chip || true
shot V-05-panel-weather || true
shot V-06-panel-update || true
shot V-07-panel-tailscale || true

# Crop top-right panel strips so V-04..07 are visually distinct files
if command -v convert >/dev/null; then
  # full bar strip
  convert "$OUT/V-04-panel-agents-chip.png" -crop 1920x48+0+0 +repage "$OUT/V-04-panel-agents-chip.png"
  convert "$OUT/V-05-panel-weather.png" -crop 700x48+1220+0 +repage "$OUT/V-05-panel-weather.png"
  convert "$OUT/V-06-panel-update.png" -crop 500x48+1420+0 +repage "$OUT/V-06-panel-update.png"
  convert "$OUT/V-07-panel-tailscale.png" -crop 400x48+1520+0 +repage "$OUT/V-07-panel-tailscale.png"
  echo CROPPED_PANEL
fi

# V-08 menu root — need top-level items. Clear filter.
guest 'pkill -u arch -f "python3 -m menu" 2>/dev/null; cd /usr/local/lib/gnomarchi && nohup env GDK_BACKEND=x11 python3 -m menu >/tmp/menu.log 2>&1 & sleep 1.8
wmctrl -l | head'
shot V-08-menu-root || true

# V-17 Install
timeout 8 "$VNC" -s 127.0.0.1::5901 type Install >/dev/null 2>&1 || true
sleep 0.4
shot V-17-menu-branches || true

# V-09 / V-10 / V-21 theme A carousel
guest 'pkill -u arch -f "python3 -m menu" 2>/dev/null
gnomarchi theme set tokyo-night >/dev/null
nohup env GDK_BACKEND=x11 gnomarchi theme pick >/tmp/pick.log 2>&1 & sleep 2
xdotool search --name Themes windowmove 300 60 windowsize 820 900 2>/dev/null
wmctrl -l | head'
shot V-09-style-theme-carousel || true
shot V-10-theme-a-gtk || true
shot V-21-hotkey-theme || true

# V-13 wallpaper + V-15 panel (close picker)
guest 'pkill -u arch -f theme_picker 2>/dev/null; sleep 0.8'
shot V-13-theme-a-wallpaper || true
shot V-15-shell-css-panel || true

# V-11 ghostty
guest 'nohup env GDK_BACKEND=x11 ghostty >/tmp/g.log 2>&1 & sleep 2
xdotool search --name "~" windowmove 120 50 windowsize 1600 960 2>/dev/null'
shot V-11-theme-a-ghostty || true

# V-16 agents
guest 'pkill -u arch -f ghostty 2>/dev/null
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/agents-window/agents_window.py >/tmp/a.log 2>&1 & sleep 2
xdotool search --name Agents windowmove 500 100 windowsize 720 820 2>/dev/null'
shot V-16-agents-window || true

# V-12 theme B
guest 'pkill -u arch -f agents_window 2>/dev/null
gnomarchi theme set catppuccin >/dev/null
nohup env GDK_BACKEND=x11 gnomarchi theme pick >/tmp/pickb.log 2>&1 & sleep 2
xdotool search --name Themes windowmove 300 60 windowsize 820 900 2>/dev/null
cat ~/.config/gnomarchi/active-theme'
shot V-12-theme-b-gtk || true

# V-14 / V-22 bg cycle — two different indices
guest 'pkill -u arch -f theme_picker 2>/dev/null
gnomarchi theme set tokyo-night >/dev/null
# cycle twice to force visible change
gnomarchi theme bg next >/dev/null; sleep 0.5
gnomarchi theme bg next >/dev/null; sleep 1
md5sum ~/.config/gnomarchi/wallpapers/active.webp 2>/dev/null || true'
shot V-14-bg-cycle || true
guest 'gnomarchi theme bg next >/dev/null; sleep 1
md5sum ~/.config/gnomarchi/wallpapers/active.webp 2>/dev/null || true'
shot V-22-hotkey-bg || true

# V-18 nvim
guest 'pkill -u arch -f "theme_picker|ghostty" 2>/dev/null
nohup env GDK_BACKEND=x11 ghostty -e nvim /usr/local/lib/gnomarchi/README.md >/tmp/nvim.log 2>&1 & sleep 2.2
xdotool search --name nvim windowmove 100 50 windowsize 1600 960 2>/dev/null || xdotool search --name "~" windowmove 100 50 windowsize 1600 960 2>/dev/null'
shot V-18-theme-nvim || true

# V-19 btop
guest 'pkill -u arch -f "ghostty|nvim" 2>/dev/null
if command -v btop >/dev/null; then
  nohup env GDK_BACKEND=x11 ghostty -e btop >/tmp/btop.log 2>&1 &
else
  nohup env GDK_BACKEND=x11 ghostty -e bash -c "echo btop_not_installed; sleep 30" >/tmp/btop.log 2>&1 &
fi
sleep 2.2
xdotool search --name "~" windowmove 100 50 windowsize 1600 960 2>/dev/null'
shot V-19-theme-btop || true

# V-20 chromium
guest 'pkill -u arch -f ghostty 2>/dev/null
nohup env GDK_BACKEND=x11 chromium --no-first-run about:blank >/tmp/chr.log 2>&1 & sleep 3.5
xdotool search --name Chrom windowmove 40 40 windowsize 1800 1000 2>/dev/null'
shot V-20-theme-chromium || true

# V-23 tweaks
guest 'pkill -u arch -f chromium 2>/dev/null
nohup env GDK_BACKEND=x11 gnome-tweaks >/tmp/t.log 2>&1 & sleep 2
xdotool search --name Tweaks windowmove 200 50 windowsize 1400 950 2>/dev/null'
shot V-23-tweaks || true

# V-24 no hyprland
guest 'pkill -u arch -f gnome-tweaks 2>/dev/null
pacman -Q hyprland >/tmp/nh.txt 2>&1 || true
echo "XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP" >>/tmp/nh.txt
nohup env GDK_BACKEND=x11 ghostty -e bash -c "cat /tmp/nh.txt; sleep 25" >/tmp/nh.log 2>&1 & sleep 2
xdotool search --name "~" windowmove 200 80 windowsize 1400 800 2>/dev/null'
shot V-24-no-hyprland || true

# V-25 / V-26
guest 'pkill -u arch -f ghostty 2>/dev/null
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/gnoma-calc/main.py >/tmp/c.log 2>&1 & sleep 1.6
xdotool search --name calc windowmove 400 150 windowsize 480 560 2>/dev/null'
shot V-25-gnoma-calc || true
guest 'pkill -u arch -f gnoma-calc 2>/dev/null
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/gnoma-write/main.py >/tmp/w.log 2>&1 & sleep 1.6
xdotool search --name write windowmove 250 60 windowsize 1200 900 2>/dev/null'
shot V-26-gnoma-write || true

# V-27 bottom bar optional
guest 'pkill -u arch -f gnoma 2>/dev/null
gnomarchi shell bar-position bottom
sleep 2.5
gnome-extensions list --enabled | grep dash || true'
shot V-27-dash-to-panel-optional || true
guest 'gnomarchi shell bar-position top; sleep 1; gnomarchi theme set tokyo-night >/dev/null'

# V-00 composite
guest 'pkill -u arch -f "agents_window|theme_picker|ghostty|nautilus|menu|gnoma|prefs|tweaks|chromium" 2>/dev/null; sleep 0.8
nohup env GDK_BACKEND=x11 nautilus --new-window /home/arch >/dev/null 2>&1 & sleep 1.5
nohup env GDK_BACKEND=x11 ghostty >/dev/null 2>&1 & sleep 1.5
nohup env GDK_BACKEND=x11 gnomarchi theme pick >/dev/null 2>&1 & sleep 1.5
nohup env GDK_BACKEND=x11 python3 /usr/local/lib/gnomarchi/apps/agents-window/agents_window.py >/dev/null 2>&1 & sleep 1.5
xdotool search --name Home windowmove 10 24 windowsize 880 1000
xdotool search --name "~" windowmove 470 24 windowsize 900 460
xdotool search --name Themes windowmove 470 268
xdotool search --name Agents windowmove 760 268 windowsize 400 480
wmctrl -lG'
shot V-00-composite-desktop || true

echo '=== AUDIT ==='
md5sum "$OUT"/V-*.png | awk '{h=$1;n=$2;sub(".*/","",n);c[h]++;f[h]=f[h]" "n} END{for(h in c) print c[h], f[h]}' | sort -n
echo DONE
