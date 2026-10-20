"""Command palette: GTK4/libadwaita when PyGObject is present, else CLI stub.

A future GTK app loads the same JSONC tree under menu/*.jsonc. Summon via
`python -m menu` / `gnomarchi menu open` or the Super+Space custom keybinding
documented in docs/menu-super-space.md (not a Shell extension).
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from menu.jsonc import load_jsonc

HAS_GTK = False
try:
    import gi

    gi.require_version("Gtk", "4.0")
    gi.require_version("Adw", "1")
    from gi.repository import Adw, Gio, GLib, Gtk  # type: ignore

    HAS_GTK = True
except (ImportError, ValueError, AttributeError):
    Adw = Gio = GLib = Gtk = None  # type: ignore


MENU_DIR = Path(__file__).resolve().parent
DEFAULT_TREE = MENU_DIR / "default.jsonc"


def flatten_entries(
    entries: list[dict[str, Any]], prefix: str = ""
) -> list[tuple[str, dict[str, Any]]]:
    rows: list[tuple[str, dict[str, Any]]] = []
    for entry in entries:
        label = str(entry.get("label") or entry.get("id") or "?")
        path = f"{prefix} / {label}" if prefix else label
        children = entry.get("children")
        if children:
            rows.extend(flatten_entries(children, path))
        else:
            rows.append((path, entry))
    return rows


def run_action(entry: dict[str, Any]) -> int:
    action = entry.get("action") or {}
    kind = action.get("type")
    if kind == "cli":
        argv = list(action.get("argv") or [])
        if not argv:
            print("empty cli action", file=sys.stderr)
            return 1
        binary = shutil.which(argv[0]) or argv[0]
        try:
            return subprocess.call([binary, *argv[1:]])
        except FileNotFoundError:
            print(f"command not found: {argv[0]}", file=sys.stderr)
            return 127
    if kind == "stub":
        print(action.get("message") or "(stub)")
        return 0
    if kind == "open":
        path = action.get("path")
        print(f"open: {path}")
        return 0
    print(f"unknown action type: {kind!r}", file=sys.stderr)
    return 1


def open_menu_stub(tree_path: Path = DEFAULT_TREE) -> int:
    """Documented stub: print the JSONC tree and accept a numeric pick."""
    tree = load_jsonc(tree_path)
    entries = flatten_entries(list(tree.get("entries") or []))
    print(f"gnomarchi menu stub (PyGObject GTK4/Adw not available)")
    print(f"tree: {tree_path}")
    print(f"root: {tree.get('label') or tree.get('id')}")
    print()
    for i, (path, entry) in enumerate(entries, start=1):
        print(f"  {i:2d}. {path}  [{entry.get('id')}]")
    print()
    print("Pick a number and press Enter (empty = quit): ", end="", flush=True)
    try:
        line = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        print()
        return 130
    if not line:
        return 0
    try:
        idx = int(line)
    except ValueError:
        print("not a number", file=sys.stderr)
        return 1
    if idx < 1 or idx > len(entries):
        print("out of range", file=sys.stderr)
        return 1
    _, entry = entries[idx - 1]
    return run_action(entry)


def open_menu_gtk(tree_path: Path = DEFAULT_TREE) -> int:
    """GTK4 + libadwaita command palette (requires PyGObject)."""
    assert HAS_GTK and Adw is not None and Gtk is not None

    tree = load_jsonc(tree_path)
    rows = flatten_entries(list(tree.get("entries") or []))

    class PaletteWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi")
            self.set_default_size(520, 420)
            self._rows = rows

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Command palette"))
            toolbar.add_top_bar(header)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            self._search = Gtk.SearchEntry(placeholder_text="Filter…")
            self._search.connect("search-changed", self._on_filter)
            box.append(self._search)

            self._list = Gtk.ListBox()
            self._list.set_selection_mode(Gtk.SelectionMode.SINGLE)
            self._list.add_css_class("boxed-list")
            self._list.connect("row-activated", self._on_activate)
            scroll = Gtk.ScrolledWindow(vexpand=True)
            scroll.set_child(self._list)
            box.append(scroll)

            toolbar.set_content(box)
            self.set_content(toolbar)
            self._rebuild("")

        def _rebuild(self, query: str) -> None:
            while True:
                row = self._list.get_row_at_index(0)
                if row is None:
                    break
                self._list.remove(row)
            q = query.casefold()
            for path, entry in self._rows:
                hay = f"{path} {entry.get('id', '')}".casefold()
                if q and q not in hay:
                    continue
                label = Gtk.Label(label=path, xalign=0.0)
                label.set_margin_top(8)
                label.set_margin_bottom(8)
                label.set_margin_start(12)
                label.set_margin_end(12)
                row = Gtk.ListBoxRow()
                row.set_child(label)
                row._gnomarchi_entry = entry  # type: ignore[attr-defined]
                self._list.append(row)

        def _on_filter(self, entry: Gtk.SearchEntry) -> None:
            self._rebuild(entry.get_text())

        def _on_activate(self, _list: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
            entry = getattr(row, "_gnomarchi_entry", None)
            if entry:
                GLib.idle_add(self._run_and_close, entry)

        def _run_and_close(self, entry: dict[str, Any]) -> bool:
            run_action(entry)
            self.close()
            return GLib.SOURCE_REMOVE

    class PaletteApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Menu",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = PaletteWindow(self)
            win.present()

    app = PaletteApp()
    return int(app.run(None))


def open_menu(tree_path: Path | None = None) -> int:
    path = tree_path or DEFAULT_TREE
    if HAS_GTK:
        return open_menu_gtk(path)
    return open_menu_stub(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnomarchi command palette")
    parser.add_argument(
        "--tree",
        type=Path,
        default=DEFAULT_TREE,
        help="JSONC menu tree path",
    )
    parser.add_argument(
        "--stub",
        action="store_true",
        help="Force CLI stub even if GTK is available",
    )
    parser.add_argument(
        "--dump",
        action="store_true",
        help="Print flattened entries and exit (non-interactive)",
    )
    args = parser.parse_args(argv)

    if args.dump:
        tree = load_jsonc(args.tree)
        for path, entry in flatten_entries(list(tree.get("entries") or [])):
            print(f"{entry.get('id')}\t{path}")
        return 0

    if args.stub or not HAS_GTK:
        return open_menu_stub(args.tree)
    return open_menu_gtk(args.tree)


if __name__ == "__main__":
    raise SystemExit(main())
