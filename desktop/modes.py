"""Center-bar mode toggles: Do Not Disturb, Night Light, Stay Awake (caffeine).

Uses gsettings for DND / Night Light. Stay Awake prefers the Arch package
gnome-shell-extension-caffeine (UUID caffeine@patapon.info); falls back to
gnome-session-inhibit when the extension is unavailable.
"""

from __future__ import annotations

import ast
import shutil
import subprocess
from dataclasses import dataclass


CAFFEINE_UUID = "caffeine@patapon.info"
_INHIBIT_PROC: subprocess.Popen[bytes] | None = None


def _run(argv: list[str], timeout: float = 10) -> subprocess.CompletedProcess[str] | None:
    try:
        return subprocess.run(
            argv, check=False, capture_output=True, text=True, timeout=timeout
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


def _gsettings_get(schema: str, key: str) -> str | None:
    if not shutil.which("gsettings"):
        return None
    proc = _run(["gsettings", "get", schema, key])
    if proc is None or proc.returncode != 0:
        return None
    return (proc.stdout or "").strip()


def _gsettings_set(schema: str, key: str, value: str) -> bool:
    if not shutil.which("gsettings"):
        return False
    proc = _run(["gsettings", "set", schema, key, value])
    return proc is not None and proc.returncode == 0


def dnd_enabled() -> bool:
    """True when notification banners are suppressed (GNOME DND equivalent)."""
    raw = _gsettings_get("org.gnome.desktop.notifications", "show-banners")
    if raw is None:
        return False
    return raw.lower() in ("false", "0")


def set_dnd(on: bool) -> bool:
    # show-banners=false ≈ Do Not Disturb
    return _gsettings_set(
        "org.gnome.desktop.notifications",
        "show-banners",
        "false" if on else "true",
    )


def toggle_dnd() -> bool:
    on = not dnd_enabled()
    set_dnd(on)
    return on


def night_light_enabled() -> bool:
    raw = _gsettings_get(
        "org.gnome.settings-daemon.plugins.color", "night-light-enabled"
    )
    if raw is None:
        return False
    return raw.lower() in ("true", "1")


def set_night_light(on: bool) -> bool:
    return _gsettings_set(
        "org.gnome.settings-daemon.plugins.color",
        "night-light-enabled",
        "true" if on else "false",
    )


def toggle_night_light() -> bool:
    on = not night_light_enabled()
    set_night_light(on)
    return on


def _enabled_extensions() -> list[str]:
    raw = _gsettings_get("org.gnome.shell", "enabled-extensions")
    if not raw:
        return []
    text = raw[4:] if raw.startswith("@as ") else raw
    try:
        return list(ast.literal_eval(text))
    except (SyntaxError, ValueError):
        return []


def caffeine_extension_available() -> bool:
    if shutil.which("gnome-extensions"):
        proc = _run(["gnome-extensions", "info", CAFFEINE_UUID])
        if proc is not None and proc.returncode == 0:
            return True
    # Installed under user or system share
    from pathlib import Path
    import os

    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    for base in (
        home / ".local" / "share" / "gnome-shell" / "extensions",
        Path("/usr/share/gnome-shell/extensions"),
    ):
        if (base / CAFFEINE_UUID).is_dir():
            return True
    return False


def ensure_caffeine_enabled() -> bool:
    """Enable caffeine Shell extension when present. Returns True if enabled."""
    if not caffeine_extension_available():
        return False
    if CAFFEINE_UUID not in _enabled_extensions():
        _run(["gnome-extensions", "enable", CAFFEINE_UUID])
        enabled = _enabled_extensions()
        if CAFFEINE_UUID not in enabled:
            enabled.append(CAFFEINE_UUID)
            _gsettings_set(
                "org.gnome.shell",
                "enabled-extensions",
                str(enabled),
            )
    # Caffeine schema: toggle user-configured "always on"
    schema = "org.gnome.shell.extensions.caffeine"
    if _gsettings_get(schema, "user-enabled") is not None:
        return _gsettings_set(schema, "user-enabled", "true")
    if _gsettings_get(schema, "toggle-state") is not None:
        return _gsettings_set(schema, "toggle-state", "true")
    return True


def _set_caffeine_extension(on: bool) -> bool:
    if not ensure_caffeine_enabled() and on:
        return False
    schema = "org.gnome.shell.extensions.caffeine"
    if _gsettings_get(schema, "user-enabled") is not None:
        return _gsettings_set(schema, "user-enabled", "true" if on else "false")
    if _gsettings_get(schema, "toggle-state") is not None:
        return _gsettings_set(schema, "toggle-state", "true" if on else "false")
    if not on:
        _run(["gnome-extensions", "disable", CAFFEINE_UUID])
        return True
    return caffeine_extension_available()


def stay_awake_enabled() -> bool:
    global _INHIBIT_PROC
    schema = "org.gnome.shell.extensions.caffeine"
    for key in ("user-enabled", "toggle-state"):
        raw = _gsettings_get(schema, key)
        if raw is not None:
            return raw.lower() in ("true", "1")
    if _INHIBIT_PROC is not None and _INHIBIT_PROC.poll() is None:
        return True
    return False


def set_stay_awake(on: bool) -> bool:
    """Inhibit idle/sleep. Prefer caffeine extension; else gnome-session-inhibit."""
    global _INHIBIT_PROC
    if caffeine_extension_available() or (
        shutil.which("gnome-extensions") and _run(["gnome-extensions", "list"])
    ):
        if _set_caffeine_extension(on):
            if not on and _INHIBIT_PROC is not None:
                _INHIBIT_PROC.terminate()
                _INHIBIT_PROC = None
            return True
    if on:
        if _INHIBIT_PROC is not None and _INHIBIT_PROC.poll() is None:
            return True
        inhibit = shutil.which("gnome-session-inhibit")
        if not inhibit:
            return False
        _INHIBIT_PROC = subprocess.Popen(
            [
                inhibit,
                "--inhibit",
                "idle:sleep",
                "--reason",
                "gnomarchi Stay Awake",
                "sleep",
                "infinity",
            ]
        )
        return True
    if _INHIBIT_PROC is not None:
        _INHIBIT_PROC.terminate()
        try:
            _INHIBIT_PROC.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _INHIBIT_PROC.kill()
        _INHIBIT_PROC = None
    return True


def toggle_stay_awake() -> bool:
    on = not stay_awake_enabled()
    set_stay_awake(on)
    return on


@dataclass
class ModeSnapshot:
    dnd: bool
    night_light: bool
    stay_awake: bool


def snapshot() -> ModeSnapshot:
    return ModeSnapshot(
        dnd=dnd_enabled(),
        night_light=night_light_enabled(),
        stay_awake=stay_awake_enabled(),
    )


def status_lines() -> list[str]:
    s = snapshot()
    return [
        f"dnd={'on' if s.dnd else 'off'}",
        f"night-light={'on' if s.night_light else 'off'}",
        f"stay-awake={'on' if s.stay_awake else 'off'}",
    ]
