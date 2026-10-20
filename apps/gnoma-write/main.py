#!/usr/bin/python3
"""gnoma-write — simple Markdown notes (GTK4/Adwaita). Not Omarchy-branded."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

NOTES_DIR = Path.home() / "Documents" / "gnoma-write"


def notes_dir() -> Path:
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    return NOTES_DIR


def default_note() -> Path:
    return notes_dir() / "scratch.md"


def open_gtk(path: Path | None = None) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print("error: GTK4/Adwaita (PyGObject) required", file=sys.stderr)
        return 1

    note_path = path or default_note()
    if not note_path.is_file():
        note_path.write_text("# Notes\n\n", encoding="utf-8")

    class WriteWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnoma-write")
            self.set_default_size(720, 560)
            self._path = note_path

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="gnoma-write"))
            save_btn = Gtk.Button(label="Save")
            save_btn.add_css_class("suggested-action")
            save_btn.connect("clicked", self._save)
            header.pack_end(save_btn)
            open_btn = Gtk.Button(label="Open…")
            open_btn.connect("clicked", self._open_dialog)
            header.pack_start(open_btn)
            toolbar.add_top_bar(header)

            self._buf = Gtk.TextBuffer()
            self._buf.set_text(self._path.read_text(encoding="utf-8"), -1)
            view = Gtk.TextView(buffer=self._buf)
            view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            view.set_monospace(True)
            view.set_top_margin(12)
            view.set_bottom_margin(12)
            view.set_left_margin(14)
            view.set_right_margin(14)
            scroll = Gtk.ScrolledWindow(vexpand=True, hexpand=True)
            scroll.set_child(view)
            toolbar.set_content(scroll)
            self.set_content(toolbar)

            ctrl = Gtk.EventControllerKey()
            ctrl.connect("key-pressed", self._on_key)
            self.add_controller(ctrl)

        def _on_key(self, _c, keyval, _code, state) -> bool:
            from gi.repository import Gdk  # type: ignore

            ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
            if ctrl and keyval in (Gdk.KEY_s, Gdk.KEY_S):
                self._save(None)
                return True
            return False

        def _save(self, _b) -> None:
            start = self._buf.get_start_iter()
            end = self._buf.get_end_iter()
            text = self._buf.get_text(start, end, True)
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(text, encoding="utf-8")
            self.set_title(f"gnoma-write — {self._path.name}")

        def _open_dialog(self, _b) -> None:
            dialog = Gtk.FileDialog(title="Open Markdown")
            filt = Gtk.FileFilter()
            filt.set_name("Markdown")
            filt.add_pattern("*.md")
            filt.add_pattern("*.txt")
            store = Gio.ListStore.new(Gtk.FileFilter)
            store.append(filt)
            dialog.set_filters(store)

            def _done(dlg, result) -> None:
                try:
                    f = dlg.open_finish(result)
                except GLib.Error:
                    return
                p = Path(f.get_path())
                self._path = p
                self._buf.set_text(p.read_text(encoding="utf-8"), -1)
                self.set_title(f"gnoma-write — {p.name}")

            dialog.open(self, None, _done)

    class WriteApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Write",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = WriteWindow(self)
            win.present()

    return int(WriteApp().run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnoma-write — Markdown notes")
    parser.add_argument("file", nargs="?", help="note file to open")
    args = parser.parse_args(argv)
    path = Path(args.file).expanduser() if args.file else None
    return open_gtk(path)


if __name__ == "__main__":
    raise SystemExit(main())
