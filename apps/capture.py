"""Screenshot / OCR / QR / screen-record CLI wrappers (Arch + stock GNOME)."""

from __future__ import annotations

import sys

from desktop import capture as core


def shot(*, area: bool = False) -> int:
    try:
        path = core.shot(area=area, interactive=not area)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


def ocr() -> int:
    try:
        text = core.ocr()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(text, end="" if text.endswith("\n") else text + "\n")
    return 0


def qr() -> int:
    try:
        text = core.qr()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


def record() -> int:
    try:
        return int(core.record())
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


def menu() -> int:
    """GTK capture chooser (shot / area / OCR / QR / record)."""
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print("shot | area | ocr | qr | record", file=sys.stderr)
        return 1

    class CaptureWin(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="Capture")
            self.set_default_size(320, 280)
            self.set_resizable(False)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Capture"))
            toolbar.add_top_bar(header)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(14)
            box.set_margin_bottom(14)
            box.set_margin_start(16)
            box.set_margin_end(16)

            def _run(fn) -> None:
                self.close()
                GLib.idle_add(lambda: fn() or False)

            actions = [
                ("Screenshot", lambda: shot(area=False)),
                ("Area shot", lambda: shot(area=True)),
                ("OCR selection", ocr),
                ("QR scan", qr),
                ("Screen record", record),
            ]
            for label, fn in actions:
                btn = Gtk.Button(label=label)
                btn.connect("clicked", lambda _b, f=fn: _run(f))
                box.append(btn)
            toolbar.set_content(box)
            self.set_content(toolbar)

    class CaptureApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Capture",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = CaptureWin(self)
            win.present()

    return int(CaptureApp().run(None))
