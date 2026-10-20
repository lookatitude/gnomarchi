#!/usr/bin/env bash
# Omarchy manual surface screenshots. Never kill qemu. Never pkill patterns that match SSH argv.
set -uo pipefail
KEY=/home/miguelp/VMs/omarchy-test/state/vm.08CB1M/id_ed25519
VNC=/home/miguelp/VMs/gnomarchi-test/venv/bin/vncdotool
OUT=/home/miguelp/Projects/gnomarchi/docs/screenshots/omarchy-manual
STATE=/home/miguelp/VMs/omarchy-test
LOG="$OUT/capture.log"
FAILS="$OUT/fails.txt"
: >"$LOG"
: >"$FAILS"
mkdir -p "$OUT" /home/miguelp/Projects/gnomarchi/docs/parity

kill_vnc() { pkill -f 'gnomarchi-test/venv/bin/vncdotool' 2>/dev/null || true; }

ssh_cmd() {
  ssh -i "$KEY" -p 2223 -o BatchMode=yes -o IdentitiesOnly=yes \
    -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
    omarchy@127.0.0.1 "$@"
}
run() { ssh_cmd "source /tmp/guest-env.sh; export OMARCHY_PATH=/usr/share/omarchy; $*"; }

vnc_key() {
  kill_vnc
  timeout 10 "$VNC" -s 127.0.0.1::5902 key "$@" >/dev/null 2>&1 || true
}

unlock_if_needed() {
  kill_vnc
  timeout 22 "$VNC" -s 127.0.0.1::5902 capture "$OUT/_lockcheck.png" >/dev/null 2>&1 || true
  if python3 - "$OUT/_lockcheck.png" <<'PY' 2>/dev/null
import sys
try:
  from PIL import Image
except ImportError:
  sys.exit(1)
im=Image.open(sys.argv[1])
# lock screen is blurred colorful with tiny center box — heuristic: very few unique-ish mid tones
# fallback: always try typing password once if file tiny/missing handled elsewhere
sys.exit(0)
PY
  then
    # Always send password once if lock UI suspected; cheap if already unlocked into focused field risk —
    # Prefer SSH check:
    locked=$(run 'omarchy-hyprland-session-locked 2>/dev/null; echo' | tr -d '\r' || true)
    if run 'omarchy-shell shell listPlugins' 2>/dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); sys.exit(0 if any(x["id"]=="omarchy.lock" and x.get("active") for x in d) else 1)' 2>/dev/null; then
      vnc_key esc
      sleep 0.2
      kill_vnc
      timeout 15 "$VNC" -s 127.0.0.1::5902 type omarchy >/dev/null 2>&1 || true
      vnc_key enter
      sleep 1.2
    fi
  fi
}

shot() {
  local name="$1"
  sleep 1.0
  kill_vnc
  if timeout 22 "$VNC" -s 127.0.0.1::5902 capture "$OUT/$name.png" >>"$LOG" 2>&1; then
    local sz
    sz=$(stat -c%s "$OUT/$name.png" 2>/dev/null || echo 0)
    if [[ "$sz" -lt 8000 ]]; then
      echo "$name tiny:$sz" >>"$FAILS"
      echo "FAIL tiny $name"
    else
      echo "OK $name ($sz)"
    fi
  else
    echo "$name capture-fail" >>"$FAILS"
    echo "FAIL capture $name"
  fi
}

close_ui() {
  run 'omarchy-menu close' || true
  vnc_key esc
  sleep 0.25
  vnc_key esc
  sleep 0.2
  run 'python3 /tmp/guest-close-all.py' || true
  sleep 0.35
}

panel_open() {
  local id="$1"
  run "omarchy-shell -q shell summon $id" || run "omarchy-shell -q shell toggle $id '{}'" || true
  sleep 1.3
}

panel_close() {
  local id="$1"
  vnc_key esc
  sleep 0.25
  run "omarchy-shell -q shell toggle $id '{}'" || true
  sleep 0.25
}

echo "=== START $(date -Is) ===" | tee -a "$LOG"

scp -i "$KEY" -P 2223 -o BatchMode=yes -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  "$STATE/guest-env.sh" "$STATE/guest-close-all.py" omarchy@127.0.0.1:/tmp/ >/dev/null

# prepare session
run 'omarchy-toggle-idle >/tmp/idle.log 2>&1 || true' || true
# ensure stay-awake / screensaver off if toggle flipped wrong — force on stay awake path
run 'omarchy-toggle-enabled idle >/dev/null 2>&1; true' || true
unlock_if_needed
close_ui
# dismiss first-run notices for cleaner shots when possible
run 'omarchy-shell -q notifications dismissAll' || true
sleep 0.4

# M-01 desktop / top bar
shot M-01-topbar

# Top bar widgets
for pair in \
  "M-02-audio:omarchy.audio" \
  "M-03-network:omarchy.network" \
  "M-04-bluetooth:omarchy.bluetooth" \
  "M-05-power:omarchy.power" \
  "M-06-clock:omarchy.clock"
do
  name="${pair%%:*}"; id="${pair##*:}"
  close_ui
  panel_open "$id"
  shot "$name"
  panel_close "$id"
done

# Hotkey cheatsheet
close_ui
run 'nohup omarchy-menu-keybindings >/tmp/keybind.log 2>&1 </dev/null &'
sleep 1.6
shot M-07-keybindings
close_ui

# Menu branches
close_ui
run 'omarchy-menu summon root'
sleep 1.3
shot M-08-menu-root

for pair in \
  "M-09-menu-apps:apps" \
  "M-10-menu-style:style" \
  "M-11-menu-setup:setup" \
  "M-12-menu-install:install" \
  "M-12b-menu-learn:learn" \
  "M-12c-menu-trigger:trigger" \
  "M-12d-menu-system:system"
do
  name="${pair%%:*}"; route="${pair##*:}"
  run 'omarchy-menu close' || true
  sleep 0.2
  run "omarchy-menu summon $route"
  sleep 1.2
  shot "$name"
done
run 'omarchy-menu close' || true

# About
close_ui
run 'nohup omarchy-launch-about >/tmp/about.log 2>&1 </dev/null &'
sleep 2.0
shot M-13-about
close_ui

# Theme switcher — browse all themes with Right
close_ui
run 'nohup omarchy theme switcher >/tmp/theme-sw.log 2>&1 </dev/null &'
sleep 2.3
shot M-14-theme-switcher
for _ in $(seq 1 12); do
  kill_vnc
  timeout 8 "$VNC" -s 127.0.0.1::5902 key Right >/dev/null 2>&1 || true
  sleep 0.35
done
shot M-14b-theme-switcher-mid
for _ in $(seq 1 12); do
  kill_vnc
  timeout 8 "$VNC" -s 127.0.0.1::5902 key Right >/dev/null 2>&1 || true
  sleep 0.35
done
shot M-14c-theme-switcher-end
vnc_key esc
sleep 0.4
# close without matching SSH argv: kill binary name only
run 'pids=$(pgrep -f /usr/share/omarchy/bin/omarchy-theme-switcher || true); [[ -n ${pids:-} ]] && kill $pids || true' || true
run 'omarchy-menu close' || true

# Background switcher
close_ui
run 'nohup omarchy theme bg-switcher >/tmp/bg-sw.log 2>&1 </dev/null &'
sleep 2.3
shot M-15-bg-switcher
vnc_key esc
run 'pids=$(pgrep -f /usr/share/omarchy/bin/omarchy-theme-bg-switcher || true); [[ -n ${pids:-} ]] && kill $pids || true' || true

# Unlock art / plymouth switcher
close_ui
run 'nohup omarchy-plymouth-switcher >/tmp/ply.log 2>&1 </dev/null &'
sleep 2.3
shot M-16-unlock-art
vnc_key esc
run 'pids=$(pgrep -f /usr/share/omarchy/bin/omarchy-plymouth-switcher || true); [[ -n ${pids:-} ]] && kill $pids || true' || true

# Clipboard
close_ui
run 'echo "clipboard-seed-$(date +%s)" | wl-copy; nohup omarchy-menu-clipboard >/tmp/clip.log 2>&1 </dev/null &'
sleep 1.0
run 'omarchy-shell -q shell summon omarchy.clipboard' || true
sleep 1.0
shot M-17-clipboard
panel_close omarchy.clipboard
close_ui

# Reminders
close_ui
run 'omarchy-reminder clear >/dev/null 2>&1 || true; omarchy-reminder 60 "QA reminder screenshot" >/dev/null 2>&1 || true'
run 'omarchy-shell -q shell summon omarchy.reminders' || true
run 'nohup omarchy-reminder show >/tmp/rem.log 2>&1 </dev/null &'
sleep 1.5
shot M-18-reminders
close_ui

# Notices
close_ui
run 'omarchy-notification-send "QA notice" "Omarchy manual screenshot coverage" >/dev/null 2>&1 || true'
sleep 1.0
shot M-19-notice-toast
run 'omarchy-shell -q notifications showHistory' || true
sleep 1.2
shot M-19b-notice-history
vnc_key esc
run 'omarchy-shell -q notifications dismissAll' || true
close_ui

# Screensaver (force) then escape — do NOT leave locked
close_ui
run 'nohup omarchy-launch-screensaver force >/tmp/ss.log 2>&1 </dev/null &'
sleep 2.8
shot M-20-screensaver
vnc_key esc
sleep 0.6
vnc_key esc
sleep 0.4
run 'pids=$(pgrep -f org.omarchy.screensaver || true); [[ -n ${pids:-} ]] && kill $pids || true' || true
run 'pids=$(pgrep -f /usr/share/omarchy/bin/omarchy-screensaver || true); [[ -n ${pids:-} ]] && kill $pids || true' || true
unlock_if_needed
close_ui

# Agents
close_ui
run 'nohup omarchy agent --pick >/tmp/agent.log 2>&1 </dev/null &'
sleep 2.3
shot M-21-agents
close_ui

# Apps
close_ui
run 'nohup foot >/tmp/foot.log 2>&1 </dev/null &'
sleep 1.7
shot M-22-foot
close_ui

run 'nohup foot -e nvim /usr/share/omarchy/logo.txt >/tmp/nvim.log 2>&1 </dev/null &'
sleep 1.9
shot M-23-nvim
close_ui

run 'nohup foot -e btop >/tmp/btop.log 2>&1 </dev/null &'
sleep 1.9
shot M-24-btop
close_ui

run 'nohup chromium --no-first-run about:blank >/tmp/chromium.log 2>&1 </dev/null &'
sleep 3.8
shot M-25-chromium
close_ui

run 'nohup omacalc >/tmp/omacalc.log 2>&1 </dev/null &'
sleep 1.9
shot M-26-omacalc
close_ui

run 'nohup omawrite >/tmp/omawrite.log 2>&1 </dev/null &'
sleep 1.9
shot M-27-omawrite
close_ui

run 'nohup omacut >/tmp/omacut.log 2>&1 </dev/null &'
sleep 1.9
shot M-28-omacut
close_ui

run 'nohup nautilus "$HOME" >/tmp/nautilus.log 2>&1 </dev/null &'
sleep 2.2
shot M-29-files
close_ui

# Extra installed Apps-menu GUIs
for pair in \
  "M-30-obsidian:obsidian" \
  "M-31-localsend:localsend" \
  "M-32-pinta:pinta" \
  "M-33-evince:evince"
do
  name="${pair%%:*}"; bin="${pair##*:}"
  if run "command -v $bin >/dev/null"; then
    close_ui
    run "nohup $bin >/tmp/$bin.log 2>&1 </dev/null &"
    sleep 2.5
    shot "$name"
    close_ui
  else
    echo "$name missing:$bin" >>"$FAILS"
  fi
done

# Install TUI branch
close_ui
run 'omarchy-menu summon install.tui'
sleep 1.3
shot M-35-menu-install-tui
run 'omarchy-menu close' || true

close_ui
shot M-37-desktop-clean

echo "=== DONE $(date -Is) ===" | tee -a "$LOG"
echo "--- FAILS ---"
cat "$FAILS" || true
ls "$OUT"/M-*.png 2>/dev/null | wc -l
