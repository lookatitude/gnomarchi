#!/usr/bin/env python3
"""Visual theme grid (Omarchy Style > Theme / Super+Ctrl+Shift+Space).

Shows every pack with a preview thumbnail. Applies on select via
`gnomarchi theme set <id>`. D7: never claims official Omarchy.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("GNOMARCHI_ROOT", str(ROOT))

_PREVIEW_NAMES = (
    "preview.png",
    "preview.jpg",
    "preview-unlock.png",
    "wallpaper.webp",
    "wallpaper.png",
    "wallpaper.jpg",
)
_BG_GLOBS = ("*.webp", "*.png", "*.jpg", "*.jpeg")


def resolve_gnomarchi() -> list[str]:
    found = shutil.which("gnomarchi")
    if found:
        return [found]
    repo_bin = ROOT / "bin" / "gnomarchi"
    if repo_bin.is_file():
        return [sys.executable, str(repo_bin)]
    return ["gnomarchi"]


def list_themes() -> list[dict[str, str]]:
    prefix = resolve_gnomarchi()
    proc = subprocess.run(
        [*prefix, "theme", "list"],
        check=False,
        text=True,
        capture_output=True,
    )
    rows: list[dict[str, str]] = []
    if proc.returncode == 0 and proc.stdout.strip():
        for line in proc.stdout.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("("):
                continue
            parts = line.split("\t")
            tid = parts[0]
            name = parts[1] if len(parts) > 1 else tid
            rows.append({"id": tid, "name": name, "note": ""})
        if rows:
            return rows
    from theme.engine import list_themes as engine_list

    return [
        {"id": t["id"], "name": t["name"], "note": ""}
        for t in engine_list()
    ]


def active_theme_id() -> str | None:
    from theme.paths import state_dir

    p = state_dir() / "active-theme"
    if p.is_file():
        return p.read_text(encoding="utf-8").strip() or None
    return None


def apply_theme(theme_id: str) -> int:
    prefix = resolve_gnomarchi()
    proc = subprocess.run([*prefix, "theme", "set", theme_id], check=False)
    return proc.returncode


def preview_path_for(theme_id: str) -> Path | None:
    """Resolve pack preview: preview.png → wallpaper.* → backgrounds still."""
    try:
        from theme.paths import find_pack
    except Exception:
        return None
    pack = find_pack(theme_id)
    if pack is None:
        return None
    for name in _PREVIEW_NAMES:
        candidate = pack / name
        if candidate.is_file():
            return candidate
    backgrounds = pack / "backgrounds"
    if backgrounds.is_dir():
        for pattern in _BG_GLOBS:
            for candidate in sorted(backgrounds.glob(pattern)):
                if candidate.is_file():
                    return candidate
    return None


def open_gtk() -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gdk, GdkPixbuf, GLib, Gtk, Pango  # type: ignore
    except (ImportError, ValueError, AttributeError):
        return open_cli()

    themes = list_themes()
    if not themes:
        print("no theme packs found", file=sys.stderr)
        return 1

    TILE_W, TILE_H = 140, 78

    class ThemePicker(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi Themes")
            # Tall enough for 4×6 = 24 tiles without scrolling on 1080p
            self.set_default_size(980, 980)
            self._themes = themes
            self._applying = False
            self._syncing = False
            active = active_theme_id()
            self._index = 0
            for i, t in enumerate(themes):
                if t["id"] == active:
                    self._index = i
                    break

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Theme"))
            toolbar.add_top_bar(header)

            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            outer.set_margin_top(12)
            outer.set_margin_bottom(12)
            outer.set_margin_start(16)
            outer.set_margin_end(16)

            self._status = Gtk.Label(xalign=0)
            self._status.add_css_class("title-2")
            outer.append(self._status)
            self._hint = Gtk.Label(
                label="Arrow keys move · selection applies · Esc closes",
                xalign=0,
            )
            self._hint.add_css_class("dim-label")
            outer.append(self._hint)

            self._flow = Gtk.FlowBox()
            self._flow.set_valign(Gtk.Align.START)
            self._flow.set_max_children_per_line(4)
            self._flow.set_min_children_per_line(4)
            self._flow.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self._flow.set_homogeneous(True)
            self._flow.set_row_spacing(10)
            self._flow.set_column_spacing(10)
            self._flow.set_activate_on_single_click(True)
            self._flow.connect("child-activated", self._on_child_activated)

            self._tiles: list[Gtk.FlowBoxChild] = []
            for i, t in enumerate(themes):
                child = self._make_tile(i, t)
                self._flow.append(child)
                self._tiles.append(child)

            scroller = Gtk.ScrolledWindow()
            scroller.set_vexpand(True)
            scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroller.set_child(self._flow)
            outer.append(scroller)

            toolbar.set_content(outer)
            self.set_content(toolbar)

            key = Gtk.EventControllerKey()
            key.connect("key-pressed", self._on_key)
            self.add_controller(key)

            GLib.idle_add(self._select_index, self._index, False)

        def _make_tile(self, index: int, theme: dict[str, str]) -> Gtk.FlowBoxChild:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            box.set_margin_top(4)
            box.set_margin_bottom(4)
            box.set_margin_start(4)
            box.set_margin_end(4)

            picture = Gtk.Picture()
            picture.set_content_fit(Gtk.ContentFit.COVER)
            picture.set_size_request(TILE_W, TILE_H)
            picture.set_can_shrink(True)
            pix = self._tile_pixbuf(theme["id"])
            if pix is not None:
                picture.set_pixbuf(pix)

            name = Gtk.Label(label=theme["name"], xalign=0)
            name.add_css_class("heading")
            name.set_ellipsize(Pango.EllipsizeMode.END)
            tid = Gtk.Label(label=theme["id"], xalign=0)
            tid.add_css_class("dim-label")
            tid.set_ellipsize(Pango.EllipsizeMode.END)

            box.append(picture)
            box.append(name)
            box.append(tid)

            child = Gtk.FlowBoxChild()
            child.set_child(box)
            child._theme_index = index  # type: ignore[attr-defined]
            return child

        def _tile_pixbuf(self, theme_id: str):
            path = preview_path_for(theme_id)
            if path is not None:
                try:
                    return GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        str(path), TILE_W * 2, TILE_H * 2, False
                    )
                except Exception:
                    pass
            return self._swatch_pixbuf(theme_id)

        def _swatch_pixbuf(self, theme_id: str):
            pal = self._palette(theme_id)

            def parse(hex_color: str) -> tuple[int, int, int]:
                v = hex_color.lstrip("#")
                if len(v) != 6:
                    return 11, 18, 32
                return int(v[0:2], 16), int(v[2:4], 16), int(v[4:6], 16)

            bg = parse(pal.get("background", "#0b1220"))
            accent = parse(pal.get("accent", "#3d8bfd"))
            surface = parse(pal.get("surface", "#121a2b"))
            raw = bytearray(TILE_W * TILE_H * 3)
            for y in range(TILE_H):
                for x in range(TILE_W):
                    if y < TILE_H * 0.22:
                        c = surface
                    elif x > TILE_W * 0.7 and TILE_H * 0.35 < y < TILE_H * 0.8:
                        c = accent
                    else:
                        c = bg
                    i = (y * TILE_W + x) * 3
                    raw[i], raw[i + 1], raw[i + 2] = c
            # Keep buffer alive for the Pixbuf lifetime
            buf = bytes(raw)
            if not hasattr(self, "_swatch_bufs"):
                self._swatch_bufs = []
            self._swatch_bufs.append(buf)
            return GdkPixbuf.Pixbuf.new_from_data(
                buf,
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                TILE_W,
                TILE_H,
                TILE_W * 3,
            )

        def _palette(self, theme_id: str) -> dict[str, str]:
            try:
                from theme.paths import find_pack
                from theme.palette import load_palette

                pack = find_pack(theme_id)
                if pack:
                    return load_palette(pack)
            except Exception:
                pass
            return {
                "background": "#0b1220",
                "foreground": "#e8eef7",
                "accent": "#3d8bfd",
                "surface": "#121a2b",
            }

        def _select_index(self, index: int, do_apply: bool) -> bool:
            if index < 0 or index >= len(self._themes):
                return False
            self._syncing = True
            self._index = index
            child = self._tiles[index]
            self._flow.select_child(child)
            try:
                self._flow.get_child_at_index(index).grab_focus()
            except Exception:
                child.grab_focus()
            t = self._themes[index]
            self._status.set_label(
                f"{t['name']}  ·  {index + 1} / {len(self._themes)}"
            )
            self._syncing = False
            if do_apply:
                self._apply_current()
            return False

        def _apply_current(self) -> None:
            if self._applying or self._syncing:
                return
            tid = self._themes[self._index]["id"]
            self._applying = True
            self._hint.set_label(f"Applying {tid}…")

            def _run() -> bool:
                code = apply_theme(tid)
                if code == 0:
                    self._hint.set_label(
                        f"Applied {tid} · arrows move · Esc closes"
                    )
                else:
                    self._hint.set_label(f"Failed to apply {tid}")
                self._applying = False
                return False

            GLib.idle_add(_run)

        def _on_child_activated(self, _flow, child) -> None:
            idx = int(getattr(child, "_theme_index", 0))
            self._select_index(idx, True)

        def _step(self, delta: int) -> None:
            # Browse only; Enter / click applies (Omarchy carousel browse ≠ apply).
            nxt = (self._index + delta) % len(self._themes)
            self._select_index(nxt, False)

        def _on_key(self, _ctrl, keyval, _keycode, _state) -> bool:
            if keyval in (Gdk.KEY_Right, Gdk.KEY_l):
                self._step(1)
                return True
            if keyval in (Gdk.KEY_Left, Gdk.KEY_h):
                self._step(-1)
                return True
            cols = 4
            if keyval in (Gdk.KEY_Down, Gdk.KEY_j):
                self._step(cols)
                return True
            if keyval in (Gdk.KEY_Up, Gdk.KEY_k):
                self._step(-cols)
                return True
            if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
                self._apply_current()
                return True
            if keyval == Gdk.KEY_Escape:
                self.close()
                return True
            return False

    class App(Adw.Application):
        def __init__(self) -> None:
            super().__init__(application_id="org.gnomarchi.ThemePicker")

        def do_activate(self) -> None:  # noqa: N802
            from common.window_geom import apply_geom

            win = ThemePicker(self)
            apply_geom(win)
            win.present()

    return App().run(None)


def open_cli(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnomarchi theme picker")
    parser.add_argument("theme_id", nargs="?", help="Apply this id non-interactively")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--gui", action="store_true", help="Force GTK carousel")
    args = parser.parse_args(argv)

    if args.gui:
        return open_gtk()

    themes = list_themes()
    if args.list or args.theme_id is None:
        print("# themes")
        for i, t in enumerate(themes, start=1):
            print(f"  {i:2d}. {t['id']}\t{t['name']}")
        if args.list:
            return 0
        if not themes:
            return 1
        print("Enter number or theme id (empty = quit): ", end="", flush=True)
        try:
            choice = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print()
            return 130
        if not choice:
            return 0
        if choice.isdigit():
            idx = int(choice)
            if idx < 1 or idx > len(themes):
                return 1
            theme_id = themes[idx - 1]["id"]
        else:
            theme_id = choice
    else:
        theme_id = args.theme_id
    return apply_theme(theme_id)


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args or args == ["--gui"]:
        return open_gtk()
    return open_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
