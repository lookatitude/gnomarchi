"""Quick-settings panels — gnome-control-center or GTK mini fallback."""

from __future__ import annotations

import shutil
import subprocess
import sys

GCC_PANELS: dict[str, str] = {
    "audio": "sound",
    "network": "wifi",
    "wifi": "wifi",
    "bluetooth": "bluetooth",
    "power": "power",
    "display": "display",
    "calendar": "datetime",
}


def _open_calendar_app() -> int | None:
    for cmd in ("gnome-calendar", "evolution"):
        found = shutil.which(cmd)
        if found:
            subprocess.Popen([found], start_new_session=True)
            return 0
    return None


def open_gcc(panel: str) -> int | None:
    gcc = shutil.which("gnome-control-center")
    if not gcc:
        return None
    return int(subprocess.call([gcc, GCC_PANELS[panel]]))


def open_gtk_mini(panel: str) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print(
            f"error: no GTK and no gnome-control-center for panel '{panel}'",
            file=sys.stderr,
        )
        return 1

    title = panel.title()

    class MiniPanel(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title=title)
            self.set_default_size(320, 220)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label=title))
            toolbar.add_top_bar(header)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_margin_top(16)
            box.set_margin_bottom(16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            box.append(Gtk.Label(label=f"Open system {panel} settings.", wrap=True))
            btn = Gtk.Button(label="Open Settings")
            btn.add_css_class("suggested-action")

            def _go(_b: Gtk.Button) -> None:
                if panel == "calendar":
                    if _open_calendar_app() is None:
                        open_gcc(panel)
                else:
                    open_gcc(panel)
                self.close()

            btn.connect("clicked", _go)
            box.append(btn)
            if panel == "calendar":
                box.append(Gtk.Calendar())
            toolbar.set_content(box)
            self.set_content(toolbar)

    class MiniApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id=f"org.gnomarchi.Panel.{panel}",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = MiniPanel(self)
            win.present()

    return int(MiniApp().run(None))


def open_panel(name: str, *, prefer_gtk: bool = False) -> int:
    key = name.strip().lower()
    if key not in GCC_PANELS:
        print(
            f"error: unknown panel '{name}'; choose from: {', '.join(GCC_PANELS)}",
            file=sys.stderr,
        )
        return 2
    if key == "audio" and shutil.which("wpctl"):
        subprocess.call(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"])
    if prefer_gtk:
        return open_gtk_mini(key)
    if key == "calendar":
        code = _open_calendar_app()
        if code is not None:
            return code
    code = open_gcc(key)
    if code is not None:
        return code
    return open_gtk_mini(key)
