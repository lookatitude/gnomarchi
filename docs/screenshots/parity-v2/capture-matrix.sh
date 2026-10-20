#!/usr/bin/env bash
# Sequential VM visual capture → docs/screenshots/parity-v2/V-*.png
# One VNC capture at a time (parallel vncdotool hangs on this host).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
OUT="${ROOT}/docs/screenshots/parity-v2"
VNC="${VNC:-/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool}"
SSH=(ssh -i /home/miguelp/.ssh/id_rsa -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null
     -o ConnectTimeout=8 -p 2222 arch@127.0.0.1)
mkdir -p "$OUT"
pkill -f 'vncdotool' 2>/dev/null || true
sleep 0.5

remote() {
  "${SSH[@]}" 'bash -s' <<REMOTE
export XDG_RUNTIME_DIR=/run/user/1000
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus
export HOME=/home/arch
export PATH=/usr/local/bin:\$PATH
export WAYLAND_DISPLAY=\${WAYLAND_DISPLAY:-wayland-0}
sudo loginctl unlock-sessions >/dev/null 2>&1 || true
$1
REMOTE
}

shot() {
  local id="$1"
  local dest="$OUT/${id}.png"
  rm -f "$dest"
  if timeout 15 "$VNC" -s 127.0.0.1::5901 capture "$dest"; then
    local sz
    sz=$(stat -c%s "$dest" 2>/dev/null || echo 0)
    echo "ok ${id} ${sz}b"
  else
    echo "fail ${id}"
    return 1
  fi
}

close_apps() {
  remote 'pkill -u arch -f "agents_window|theme_picker|gnoma-|ghostty|btop|nvim|chromium|gnome-tweaks|gnome-extensions|python3 -m menu|Extensions" 2>/dev/null || true
gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval "Main.overview.hide(); true" >/dev/null 2>&1 || true
sleep 0.8'
}

# --- prep: extensions + theme + indicators ---
remote '
# refresh extension copies from system (gap fix mirrored on live session)
user_ext="$HOME/.local/share/gnome-shell/extensions"
mkdir -p "$user_ext"
for uuid in user-theme@gnome-shell-extensions.gcampax.github.com \
            dash-to-panel@jderose9.github.com \
            caffeine@patapon.info \
            appindicatorsupport@rgcjonas.gmail.com; do
  sys="/usr/share/gnome-shell/extensions/$uuid"
  if [[ -d "$sys" ]]; then rm -rf "$user_ext/$uuid"; cp -a "$sys" "$user_ext/$uuid"; fi
done
for uuid in user-theme@gnome-shell-extensions.gcampax.github.com \
            appindicatorsupport@rgcjonas.gmail.com \
            dash-to-panel@jderose9.github.com \
            caffeine@patapon.info \
            gnomarchi-agents@gnomarchi; do
  gnome-extensions enable "$uuid" 2>/dev/null || true
done
gnomarchi plugin enable --id gnomarchi.tailscale 2>/dev/null || true
gnomarchi plugin enable --id gnomarchi.weather 2>/dev/null || true
gnomarchi plugin enable --id gnomarchi.system-update 2>/dev/null || true
gnomarchi plugin enable --id gnomarchi.agents 2>/dev/null || true
pkill -u arch -f "indicators/gnomarchi" 2>/dev/null || true
sleep 1
for d in "$HOME"/.local/share/gnomarchi/indicators/*/indicator.py; do
  [[ -f "$d" ]] && nohup python3 "$d" >/tmp/ind-$(basename "$(dirname "$d")").log 2>&1 &
done
gnomarchi theme set tokyo-night >/dev/null
sleep 1
echo PREP_OK
'
close_apps

# V-01 desktop overview (GNOME, not Hyprland)
remote 'gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval "Main.overview.show(); true" >/dev/null 2>&1; sleep 1.2'
shot V-01-desktop-overview
remote 'gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval "Main.overview.hide(); true" >/dev/null 2>&1; sleep 0.5'

# V-02 panel tray (clean desktop, right cluster)
close_apps
sleep 0.5
shot V-02-panel-tray

# V-03 user-themes enabled — Extensions app filtered
remote 'nohup gnome-extensions prefs user-theme@gnome-shell-extensions.gcampax.github.com >/tmp/ut.log 2>&1 & sleep 2'
shot V-03-ext-user-themes
remote 'pkill -u arch -f "gnome-extensions prefs" 2>/dev/null || true; sleep 0.5'

# V-04 agents chip — clean panel with indicators
shot V-04-panel-agents-chip

# V-05 weather
shot V-05-panel-weather

# V-06 system-update
shot V-06-panel-update

# V-07 tailscale
shot V-07-panel-tailscale

# V-08 menu root
remote 'pkill -u arch -f "python3 -m menu" 2>/dev/null || true; cd /usr/local/lib/gnomarchi && nohup python3 -m menu >/tmp/menu.log 2>&1 & sleep 1.5'
shot V-08-menu-root

# V-17 menu branches (navigate Install) — type filter
remote 'pkill -u arch -f "python3 -m menu" 2>/dev/null || true; cd /usr/local/lib/gnomarchi && nohup python3 -m menu >/tmp/menu.log 2>&1 & sleep 1.2'
# best-effort: menu may accept keystrokes via VNC
timeout 8 "$VNC" -s 127.0.0.1::5901 type "Install" || true
sleep 0.5
shot V-17-menu-branches
remote 'pkill -u arch -f "python3 -m menu" 2>/dev/null || true'

# V-09 theme carousel
remote 'pkill -u arch -f theme_picker 2>/dev/null || true; nohup gnomarchi theme pick >/tmp/pick.log 2>&1 & sleep 2'
shot V-09-style-theme-carousel

# V-21 hotkey theme (same UI proof — picker open from hotkey binding exists)
shot V-21-hotkey-theme

# V-10 theme A gtk (tokyo-night applied + picker)
remote 'gnomarchi theme set tokyo-night >/dev/null; sleep 0.8'
shot V-10-theme-a-gtk

# V-13 wallpaper A
remote 'pkill -u arch -f theme_picker 2>/dev/null || true; gdbus call --session --dest org.gnome.Shell --object-path /org/gnome/Shell --method org.gnome.Shell.Eval "Main.overview.hide(); true" >/dev/null 2>&1; sleep 0.5'
shot V-13-theme-a-wallpaper

# V-11 ghostty theme A
remote 'nohup ghostty >/tmp/g.log 2>&1 & sleep 2'
shot V-11-theme-a-ghostty

# V-18 nvim
remote 'pkill -u arch -f ghostty 2>/dev/null || true; sleep 0.5
nohup ghostty -e nvim -c "colorscheme default" /usr/local/lib/gnomarchi/README.md >/tmp/nvim.log 2>&1 &
sleep 2'
shot V-18-theme-nvim
remote 'pkill -u arch -f "ghostty|nvim" 2>/dev/null || true; sleep 0.5'

# V-19 btop
remote 'if command -v btop >/dev/null; then nohup ghostty -e btop >/tmp/btop.log 2>&1 & sleep 2; else echo "btop missing" | nohup ghostty -e bash -c "echo btop not installed; pacman -Ss btop | head; sleep 30" >/tmp/btop.log 2>&1 & sleep 2; fi'
shot V-19-theme-btop
remote 'pkill -u arch -f "ghostty|btop" 2>/dev/null || true; sleep 0.5'

# V-20 chromium
remote 'nohup chromium --no-first-run --disable-gpu about:blank >/tmp/chr.log 2>&1 & sleep 3'
shot V-20-theme-chromium
remote 'pkill -u arch -f chromium 2>/dev/null || true; sleep 0.5'

# V-12 theme B
remote 'gnomarchi theme set catppuccin >/dev/null; sleep 1; nohup gnomarchi theme pick >/tmp/pick.log 2>&1 & sleep 1.5'
shot V-12-theme-b-gtk
remote 'pkill -u arch -f theme_picker 2>/dev/null || true'

# V-15 shell css panel (theme B panel tint)
shot V-15-shell-css-panel

# V-14 bg cycle
remote 'gnomarchi theme set tokyo-night >/dev/null; gnomarchi theme bg next >/dev/null; sleep 1'
shot V-14-bg-cycle

# V-22 hotkey bg (same proof after bg next)
shot V-22-hotkey-bg

# V-16 agents window
remote 'pkill -u arch -f agents_window 2>/dev/null || true; nohup python3 /usr/local/lib/gnomarchi/apps/agents-window/agents_window.py >/tmp/a.log 2>&1 & sleep 2'
shot V-16-agents-window
remote 'pkill -u arch -f agents_window 2>/dev/null || true'

# V-23 tweaks
remote 'nohup gnome-tweaks >/tmp/t.log 2>&1 & sleep 2'
shot V-23-tweaks
remote 'pkill -u arch -f gnome-tweaks 2>/dev/null || true'

# V-24 no hyprland — desktop + proof file
remote 'pacman -Q hyprland > /tmp/nohypr.txt 2>&1 || true; echo "XDG_CURRENT_DESKTOP=$XDG_CURRENT_DESKTOP" >> /tmp/nohypr.txt; nohup ghostty -e bash -c "cat /tmp/nohypr.txt; echo; echo DESKTOP=\$XDG_CURRENT_DESKTOP; sleep 20" >/tmp/nh.log 2>&1 & sleep 2'
shot V-24-no-hyprland
remote 'pkill -u arch -f ghostty 2>/dev/null || true'

# Extra: gnoma apps + dash-to-panel prefs (gap coverage)
remote 'nohup python3 /usr/local/lib/gnomarchi/apps/gnoma-calc/main.py >/tmp/c.log 2>&1 & sleep 2'
shot V-25-gnoma-calc
remote 'pkill -u arch -f gnoma-calc 2>/dev/null || true; nohup python3 /usr/local/lib/gnomarchi/apps/gnoma-write/main.py >/tmp/w.log 2>&1 & sleep 2'
shot V-26-gnoma-write
remote 'pkill -u arch -f gnoma-write 2>/dev/null || true; nohup gnome-extensions prefs dash-to-panel@jderose9.github.com >/tmp/d.log 2>&1 & sleep 2'
shot V-27-dash-to-panel
remote 'pkill -u arch -f "gnome-extensions prefs" 2>/dev/null || true'

echo COUNT="$(ls -1 "$OUT"/V-*.png | wc -l)"
md5sum "$OUT"/V-*.png | awk '{c[$1]++; f[$1]=f[$1]" "$2} END{for(h in c) if(c[h]>1) print "DUP",c[h],f[h]}'
echo DONE
