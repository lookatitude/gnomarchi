#!/usr/bin/env python3
"""gnoma-hype — media / video launcher (Omarchy Hype parity)."""

from __future__ import annotations

import shutil
import subprocess
import sys


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    player = next((c for c in ("mpv", "vlc", "totem") if shutil.which(c)), None)
    if player is None:
        print("error: install mpv (or vlc)", file=sys.stderr)
        return 1
    if argv:
        return subprocess.call([player, *argv])
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gtk  # type: ignore
    except (ImportError, ValueError):
        print("usage: gnoma-hype [url-or-file…]", file=sys.stderr)
        return 2

    class Win(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnoma Hype")
            self.set_default_size(420, 160)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_margin_top(16)
            box.set_margin_bottom(16)
            box.set_margin_start(16)
            box.set_margin_end(16)
            self.entry = Gtk.Entry(placeholder_text="YouTube URL or file path")
            self.entry.set_hexpand(True)
            btn = Gtk.Button(label="Play")
            btn.add_css_class("suggested-action")
            btn.connect("clicked", self._play)
            self.entry.connect("activate", self._play)
            box.append(self.entry)
            box.append(btn)
            self.set_content(box)

        def _play(self, *_args) -> None:
            target = self.entry.get_text().strip()
            if not target:
                return
            subprocess.Popen([player, target], start_new_session=True)
            self.close()

    class App(Adw.Application):
        def __init__(self) -> None:
            super().__init__(application_id="org.gnomarchi.Hype")

        def do_activate(self) -> None:  # noqa: N802
            Win(self).present()

    return App().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
