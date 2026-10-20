#!/usr/bin/python3
"""gnoma-cut — basic image crop with Pillow (GTK4/Adwaita). Not Omarchy-branded."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _require_pillow():
    try:
        from PIL import Image
    except ImportError:
        print("error: Pillow required (Arch: python-pillow)", file=sys.stderr)
        raise SystemExit(1)
    return Image


def crop_cli(src: Path, dest: Path, box: tuple[int, int, int, int]) -> int:
    Image = _require_pillow()
    img = Image.open(src)
    cropped = img.crop(box)
    dest.parent.mkdir(parents=True, exist_ok=True)
    cropped.save(dest)
    print(dest)
    return 0


def open_gtk(initial: Path | None = None) -> int:
    Image = _require_pillow()
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print("error: GTK4/Adwaita (PyGObject) required", file=sys.stderr)
        return 1

    class CutWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnoma-cut")
            self.set_default_size(780, 640)
            self._path: Path | None = initial if initial and initial.is_file() else None
            self._image = None

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="gnoma-cut"))
            open_btn = Gtk.Button(label="Open…")
            open_btn.connect("clicked", self._open)
            header.pack_start(open_btn)
            crop_btn = Gtk.Button(label="Crop & Save")
            crop_btn.add_css_class("suggested-action")
            crop_btn.connect("clicked", self._crop_save)
            header.pack_end(crop_btn)
            toolbar.add_top_bar(header)

            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            outer.set_margin_top(10)
            outer.set_margin_bottom(10)
            outer.set_margin_start(12)
            outer.set_margin_end(12)

            self._preview = Gtk.Picture()
            self._preview.set_content_fit(Gtk.ContentFit.CONTAIN)
            self._preview.set_size_request(640, 400)
            outer.append(self._preview)

            grid = Gtk.Grid(column_spacing=8, row_spacing=6)
            self._spins: dict[str, Gtk.SpinButton] = {}
            for i, key in enumerate(("left", "top", "right", "bottom")):
                grid.attach(Gtk.Label(label=key, xalign=0), 0, i, 1, 1)
                adj = Gtk.Adjustment(value=0, lower=0, upper=10000, step_increment=1)
                spin = Gtk.SpinButton(adjustment=adj, climb_rate=1, digits=0)
                self._spins[key] = spin
                grid.attach(spin, 1, i, 1, 1)
            outer.append(grid)
            hint = Gtk.Label(
                label="Set crop box (left, top, right, bottom) in pixels, then Crop & Save.",
                wrap=True,
                xalign=0,
            )
            hint.add_css_class("dim-label")
            outer.append(hint)

            scroll = Gtk.ScrolledWindow(vexpand=True)
            scroll.set_child(outer)
            toolbar.set_content(scroll)
            self.set_content(toolbar)

            if self._path:
                self._load(self._path)

        def _load(self, path: Path) -> None:
            self._path = path
            self._image = Image.open(path).convert("RGBA")
            w, h = self._image.size
            self._spins["left"].set_range(0, max(w - 1, 0))
            self._spins["top"].set_range(0, max(h - 1, 0))
            self._spins["right"].set_range(1, w)
            self._spins["bottom"].set_range(1, h)
            self._spins["left"].set_value(0)
            self._spins["top"].set_value(0)
            self._spins["right"].set_value(w)
            self._spins["bottom"].set_value(h)
            import tempfile

            tmp = Path(tempfile.gettempdir()) / "gnoma-cut-preview.png"
            self._image.save(tmp, format="PNG")
            self._preview.set_filename(str(tmp))
            self.set_title(f"gnoma-cut — {path.name} ({w}×{h})")

        def _open(self, _b) -> None:
            dialog = Gtk.FileDialog(title="Open image")
            filt = Gtk.FileFilter()
            filt.set_name("Images")
            for pat in ("*.png", "*.jpg", "*.jpeg", "*.webp", "*.bmp", "*.gif"):
                filt.add_pattern(pat)
            store = Gio.ListStore.new(Gtk.FileFilter)
            store.append(filt)
            dialog.set_filters(store)

            def _done(dlg, result) -> None:
                try:
                    f = dlg.open_finish(result)
                except GLib.Error:
                    return
                self._load(Path(f.get_path()))

            dialog.open(self, None, _done)

        def _crop_save(self, _b) -> None:
            if self._image is None or self._path is None:
                return
            left = int(self._spins["left"].get_value())
            top = int(self._spins["top"].get_value())
            right = int(self._spins["right"].get_value())
            bottom = int(self._spins["bottom"].get_value())
            if right <= left or bottom <= top:
                return
            cropped = self._image.crop((left, top, right, bottom))
            dest = self._path.with_name(self._path.stem + "-crop" + self._path.suffix)
            dialog = Gtk.FileDialog(title="Save cropped image", initial_file=Gio.File.new_for_path(str(dest)))

            def _done(dlg, result) -> None:
                try:
                    f = dlg.save_finish(result)
                except GLib.Error:
                    return
                out = Path(f.get_path())
                cropped.save(out)
                self.set_title(f"gnoma-cut — saved {out.name}")

            dialog.save(self, None, _done)

    class CutApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Cut",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = CutWindow(self)
            win.present()

    return int(CutApp().run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnoma-cut — image crop")
    parser.add_argument("file", nargs="?", help="image to open")
    parser.add_argument("--left", type=int)
    parser.add_argument("--top", type=int)
    parser.add_argument("--right", type=int)
    parser.add_argument("--bottom", type=int)
    parser.add_argument("-o", "--output", help="CLI crop output path")
    args = parser.parse_args(argv)
    if args.file and args.output and None not in (args.left, args.top, args.right, args.bottom):
        return crop_cli(
            Path(args.file).expanduser(),
            Path(args.output).expanduser(),
            (args.left, args.top, args.right, args.bottom),
        )
    path = Path(args.file).expanduser() if args.file else None
    return open_gtk(path)


if __name__ == "__main__":
    raise SystemExit(main())
