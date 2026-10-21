"""Omarchy-style notices: time / battery / weather + history + dismiss."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from common.paths import state_dir

_HISTORY_LIMIT = 80


def _history_path() -> Path:
    path = state_dir() / "notices.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _append_history(title: str, body: str, *, nid: int | None = None) -> None:
    row = {
        "ts": time.time(),
        "iso": datetime.now().isoformat(timespec="seconds"),
        "title": title,
        "body": body,
        "id": nid,
    }
    path = _history_path()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    # Trim
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) > _HISTORY_LIMIT:
        path.write_text("\n".join(lines[-_HISTORY_LIMIT:]) + "\n", encoding="utf-8")


def load_history(limit: int = 40) -> list[dict]:
    path = _history_path()
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _notify(title: str, body: str, *, icon: str | None = None) -> int:
    if not shutil.which("notify-send"):
        print(f"{title}: {body}")
        _append_history(title, body)
        return 0
    cmd = ["notify-send", "-p", "-a", "gnomarchi", "--urgency=low", title, body]
    if icon:
        cmd.extend(["-i", icon])
    # Transient + short TTL so banners do not linger into unrelated proof shots.
    cmd.extend(
        [
            "-e",
            "-t",
            "2500",
            "-h",
            "string:x-gnome-privacy-scope:transient",
            "-h",
            "boolean:transient:true",
        ]
    )
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    nid: int | None = None
    out = (proc.stdout or "").strip()
    if out.isdigit():
        nid = int(out)
    _append_history(title, body, nid=nid)
    return int(proc.returncode)


def notice_time() -> int:
    now = datetime.now().strftime("%A %-d %B · %H:%M")
    return _notify("Time", now, icon="appointment-soon-symbolic")


def _battery_text() -> str:
    base = Path("/sys/class/power_supply")
    if not base.is_dir():
        return "No battery detected"
    lines: list[str] = []
    for bat in sorted(base.glob("BAT*")):
        cap = bat / "capacity"
        status = bat / "status"
        pct = cap.read_text(encoding="utf-8").strip() if cap.is_file() else "?"
        st = status.read_text(encoding="utf-8").strip() if status.is_file() else "?"
        lines.append(f"{bat.name}: {pct}% ({st})")
    return "\n".join(lines) if lines else "No battery detected"


def notice_battery() -> int:
    return _notify("Battery", _battery_text(), icon="battery-symbolic")


def notice_weather() -> int:
    try:
        import urllib.request

        with urllib.request.urlopen("https://wttr.in/?format=%l:+%c+%t+%h", timeout=8) as resp:
            text = resp.read().decode("utf-8", errors="replace").strip()
    except Exception as exc:
        text = f"unavailable ({exc})"
    return _notify("Weather", text or "unavailable", icon="weather-few-clouds-symbolic")


def _close_notification(nid: int) -> None:
    try:
        subprocess.run(
            [
                "gdbus",
                "call",
                "--session",
                "--dest",
                "org.freedesktop.Notifications",
                "--object-path",
                "/org/freedesktop/Notifications",
                "--method",
                "org.freedesktop.Notifications.CloseNotification",
                str(int(nid)),
            ],
            check=False,
            capture_output=True,
            timeout=1,
        )
    except (ValueError, FileNotFoundError, subprocess.TimeoutExpired):
        pass


def dismiss_all() -> int:
    """Close tracked + recent notification IDs; hide banners for a clean desktop."""
    for row in load_history(limit=_HISTORY_LIMIT):
        nid = row.get("id")
        if nid is not None:
            try:
                _close_notification(int(nid))
            except (TypeError, ValueError):
                pass
    # Sweep a wide ID range — GNOME keeps banners after our tracked IDs expire.
    for nid in range(1, 256):
        _close_notification(nid)
    if shutil.which("gsettings"):
        subprocess.run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.notifications",
                "show-banners",
                "false",
            ],
            check=False,
            capture_output=True,
            timeout=2,
        )
    return 0


def capture_silence(*, restore_banners: bool = False) -> int:
    """Call before screenshot proofs so stale toasts cannot appear in the frame."""
    dismiss_all()
    if restore_banners and shutil.which("gsettings"):
        subprocess.run(
            [
                "gsettings",
                "set",
                "org.gnome.desktop.notifications",
                "show-banners",
                "true",
            ],
            check=False,
            capture_output=True,
            timeout=2,
        )
    return 0


def clear_history() -> int:
    path = _history_path()
    if path.is_file():
        path.write_text("", encoding="utf-8")
    return 0


def open_history_ui() -> int:
    """GTK history window (Omarchy M-19b analogue)."""
    rows = load_history(limit=40)
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        for row in rows:
            print(f"{row.get('iso', '?')}\t{row.get('title')}\t{row.get('body')}")
        return 0 if rows else 1

    class HistoryWin(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="Notices")
            self.set_default_size(420, 480)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Notice history"))
            clear_btn = Gtk.Button(label="Clear")
            clear_btn.connect("clicked", lambda _b: (clear_history(), self.close()))
            dismiss_btn = Gtk.Button(label="Dismiss toasts")
            dismiss_btn.connect("clicked", lambda _b: dismiss_all())
            header.pack_end(clear_btn)
            header.pack_start(dismiss_btn)
            toolbar.add_top_bar(header)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            box.set_margin_top(10)
            box.set_margin_bottom(10)
            box.set_margin_start(12)
            box.set_margin_end(12)
            if not rows:
                box.append(Gtk.Label(label="No notices yet", xalign=0.0))
            else:
                for row in reversed(rows):
                    title = str(row.get("title") or "")
                    body = str(row.get("body") or "")
                    iso = str(row.get("iso") or "")
                    lab = Gtk.Label(
                        label=f"{iso}\n{title}\n{body}",
                        xalign=0.0,
                        wrap=True,
                    )
                    lab.add_css_class("card")
                    frame = Gtk.Frame()
                    frame.set_child(lab)
                    frame.set_margin_bottom(4)
                    box.append(frame)
            scroll = Gtk.ScrolledWindow()
            scroll.set_child(box)
            scroll.set_vexpand(True)
            toolbar.set_content(scroll)
            self.set_content(toolbar)

    class HistoryApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.NoticeHistory",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = HistoryWin(self)
            win.present()

    return int(HistoryApp().run(None))


def run(kind: str) -> int:
    table = {
        "time": notice_time,
        "battery": notice_battery,
        "weather": notice_weather,
        "history": open_history_ui,
        "dismiss": dismiss_all,
        "clear": clear_history,
        "silence": capture_silence,
    }
    fn = table.get(kind)
    if fn is None:
        print(
            f"error: unknown notice {kind} (time|battery|weather|history|dismiss|clear|silence)",
            file=__import__("sys").stderr,
        )
        return 2
    return fn()


def demo_all() -> int:
    """Fire all three (spaced) for screenshot / QA."""
    rc = 0
    for kind in ("time", "battery", "weather"):
        rc = run(kind) or rc
        time.sleep(0.4)
    return rc
