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


def _extensions_dir() -> Path:
    from common.paths import state_dir

    return state_dir() / "extensions"


def load_menu_tree(tree_path: Path = DEFAULT_TREE) -> dict[str, Any]:
    """Load default JSONC and merge ~/.config/gnomarchi/extensions/*.jsonc children."""
    tree = load_jsonc(tree_path)
    ext_dir = _extensions_dir()
    if not ext_dir.is_dir():
        return tree
    entries = list(tree.get("entries") or [])
    # Map top-level id → entry for append into children
    by_id = {str(e.get("id")): e for e in entries if isinstance(e, dict)}
    for frag_path in sorted(ext_dir.glob("*.jsonc")):
        try:
            frag = load_jsonc(frag_path)
        except Exception:
            continue
        # Fragment may be a single entry or {entries:[...]} or {path, command}
        if "entries" in frag:
            for e in frag["entries"]:
                entries.append(e)
        elif "path" in frag and "command" in frag:
            # Omarchy-style menu module: path: ["Install","AI","X"]
            path = list(frag.get("path") or [])
            if not path:
                continue
            top = by_id.get(path[0].lower()) or by_id.get(path[0])
            # Prefer matching label under install/setup/style/trigger
            target = None
            for e in entries:
                if str(e.get("label", "")).lower() == str(path[0]).lower() or str(e.get("id")) == path[0]:
                    target = e
                    break
            if target is None:
                continue
            node = target
            for part in path[1:-1]:
                children = node.setdefault("children", [])
                found = None
                for c in children:
                    if str(c.get("label")) == part or str(c.get("id")) == part:
                        found = c
                        break
                if found is None:
                    found = {"id": part.lower().replace(" ", "-"), "label": part, "children": []}
                    children.append(found)
                node = found
            leaf = {
                "id": str(frag.get("id") or path[-1]),
                "label": path[-1],
                "action": {"type": "cli", "argv": str(frag["command"]).split()},
            }
            node.setdefault("children", []).append(leaf)
        elif "id" in frag:
            entries.append(frag)
    tree["entries"] = entries
    return tree


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
    """Print the JSONC tree and accept a numeric pick (no GTK)."""
    tree = load_menu_tree(tree_path)
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
    """GTK4 + libadwaita command palette (requires PyGObject).

    Default: hierarchical drill-down (root categories → children, Back).
    Non-empty filter search flattens the tree (secondary mode).
    """
    assert HAS_GTK and Adw is not None and Gtk is not None

    tree = load_menu_tree(tree_path)
    root_entries = list(tree.get("entries") or [])
    flat_rows = flatten_entries(root_entries)

    class PaletteWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi")
            self.set_default_size(520, 420)
            self._stack: list[tuple[str, list[dict[str, Any]]]] = [
                (str(tree.get("label") or "Menu"), root_entries)
            ]
            self._flat_rows = flat_rows

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            self._title = Gtk.Label(label="Command palette")
            header.set_title_widget(self._title)
            self._back = Gtk.Button(label="Back")
            self._back.connect("clicked", self._on_back)
            header.pack_start(self._back)
            toolbar.add_top_bar(header)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            self._search = Gtk.SearchEntry(placeholder_text="Filter (flattens)…")
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

            key = Gtk.EventControllerKey()
            key.connect("key-pressed", self._on_key)
            self.add_controller(key)

            self._rebuild("")

        def _query(self) -> str:
            return (self._search.get_text() or "").strip()

        def _rebuild(self, query: str) -> None:
            while True:
                row = self._list.get_row_at_index(0)
                if row is None:
                    break
                self._list.remove(row)
            q = query.casefold()
            if q:
                self._back.set_sensitive(False)
                self._title.set_label("Search")
                for path, entry in self._flat_rows:
                    hay = f"{path} {entry.get('id', '')}".casefold()
                    if q not in hay:
                        continue
                    self._append_row(path, entry, drill=None)
                return
            title, entries = self._stack[-1]
            self._title.set_label(title)
            self._back.set_sensitive(len(self._stack) > 1)
            for entry in entries:
                label = str(entry.get("label") or entry.get("id") or "?")
                children = entry.get("children") or []
                if children:
                    self._append_row(f"{label} ›", entry, drill=list(children))
                else:
                    self._append_row(label, entry, drill=None)

        def _append_row(
            self,
            label: str,
            entry: dict[str, Any],
            drill: list[dict[str, Any]] | None,
        ) -> None:
            lab = Gtk.Label(label=label, xalign=0.0)
            lab.set_margin_top(8)
            lab.set_margin_bottom(8)
            lab.set_margin_start(12)
            lab.set_margin_end(12)
            row = Gtk.ListBoxRow()
            row.set_child(lab)
            row._gnomarchi_entry = entry  # type: ignore[attr-defined]
            row._gnomarchi_drill = drill  # type: ignore[attr-defined]
            self._list.append(row)

        def _on_filter(self, entry: Gtk.SearchEntry) -> None:
            self._rebuild(entry.get_text())

        def _on_back(self, *_args: Any) -> None:
            if len(self._stack) > 1:
                self._stack.pop()
                self._search.set_text("")
                self._rebuild("")

        def _on_key(self, _ctrl: Any, keyval: int, *_rest: Any) -> bool:
            from gi.repository import Gdk  # type: ignore

            if keyval == Gdk.KEY_Escape:
                if self._query():
                    self._search.set_text("")
                    self._rebuild("")
                    return True
                if len(self._stack) > 1:
                    self._on_back()
                    return True
                self.close()
                return True
            return False

        def _on_activate(self, _list: Gtk.ListBox, row: Gtk.ListBoxRow) -> None:
            drill = getattr(row, "_gnomarchi_drill", None)
            entry = getattr(row, "_gnomarchi_entry", None)
            if drill is not None and entry is not None:
                label = str(entry.get("label") or entry.get("id") or "?")
                self._stack.append((label, drill))
                self._search.set_text("")
                self._rebuild("")
                return
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
        tree = load_menu_tree(args.tree)
        for path, entry in flatten_entries(list(tree.get("entries") or [])):
            print(f"{entry.get('id')}\t{path}")
        return 0

    if args.stub or not HAS_GTK:
        return open_menu_stub(args.tree)
    return open_menu_gtk(args.tree)


if __name__ == "__main__":
    raise SystemExit(main())
