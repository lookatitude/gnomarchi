"""Idle / lock / screensaver toggles (Omarchy idle chapter → GNOME)."""

from __future__ import annotations

import shutil
import subprocess
import sys

from desktop import modes


def lock_now() -> int:
    for argv in (
        ["loginctl", "lock-session"],
        ["gnome-screensaver-command", "-l"],
        ["dbus-send", "--session", "--dest=org.gnome.ScreenSaver",
         "--type=method_call", "/org/gnome/ScreenSaver",
         "org.gnome.ScreenSaver.Lock"],
    ):
        if shutil.which(argv[0]):
            return subprocess.call(argv)
    print("error: no lock helper", file=sys.stderr)
    return 1


def stay_awake(on: bool | None = None) -> int:
    if on is None:
        on = not modes.stay_awake_enabled()
    modes.set_stay_awake(bool(on))
    print("stay-awake", "on" if on else "off")
    return 0


def inhibit_sleep(seconds: int = 3600) -> int:
    if not shutil.which("systemd-inhibit"):
        return stay_awake(True)
    subprocess.Popen(
        [
            "systemd-inhibit",
            "--what=idle:sleep",
            "--who=gnomarchi",
            "--why=manual inhibit",
            "sleep",
            str(seconds),
        ],
        start_new_session=True,
    )
    print(f"inhibit idle/sleep for {seconds}s")
    return 0


def status() -> int:
    for line in modes.status_lines():
        print(line)
    return 0
