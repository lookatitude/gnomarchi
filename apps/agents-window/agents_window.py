#!/usr/bin/env python3
"""Agents window placeholder — lists default-agent + Make something entries.

GTK4/libadwaita window when PyGObject is available; otherwise prints the same
catalog (for headless / CI). Real agent invoke is owned by the backend CLI
(`gnomarchi agent …`).
"""

from __future__ import annotations

import argparse
import sys

ENTRIES = [
    {
        "id": "default-agent",
        "label": "Default agent",
        "description": "Session coding agent (mise + skills). Placeholder until bus wires Agents window open.",
        "action": ["gnomarchi", "agent", "default"],
    },
    {
        "id": "make-theme",
        "label": "Make something — Theme",
        "description": "Scaffold a theme pack via gnomarchi-theme skill.",
        "action": ["gnomarchi", "agent", "make-something", "theme"],
    },
    {
        "id": "make-plugin",
        "label": "Make something — Plugin",
        "description": "Scaffold a multi-runtime plugin via gnomarchi-plugin skill.",
        "action": ["gnomarchi", "agent", "make-something", "plugin"],
    },
    {
        "id": "make-app",
        "label": "Make something — App",
        "description": "Scaffold an overlay-app from templates/.",
        "action": ["gnomarchi", "agent", "make-something", "app"],
    },
]


def print_catalog() -> None:
    print("gnomarchi Agents window (placeholder)")
    print()
    for e in ENTRIES:
        print(f"  • {e['label']}  [{e['id']}]")
        print(f"    {e['description']}")
        print(f"    → {' '.join(e['action'])}")
        print()


def open_gtk() -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print_catalog()
        print("(GTK unavailable — catalog printed)", file=sys.stderr)
        return 0

    class AgentsWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi Agents")
            self.set_default_size(480, 360)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Agents"))
            toolbar.add_top_bar(header)

            listbox = Gtk.ListBox()
            listbox.add_css_class("boxed-list")
            for e in ENTRIES:
                row = Adw.ActionRow()
                row.set_title(e["label"])
                row.set_subtitle(e["description"])
                listbox.append(row)

            scroll = Gtk.ScrolledWindow(vexpand=True)
            scroll.set_child(listbox)
            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            outer.set_margin_top(12)
            outer.set_margin_bottom(12)
            outer.set_margin_start(12)
            outer.set_margin_end(12)
            outer.append(scroll)
            toolbar.set_content(outer)
            self.set_content(toolbar)

    class AgentsApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Agents",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = AgentsWindow(self)
            win.present()

    return int(AgentsApp().run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnomarchi Agents window placeholder")
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print catalog only (no GTK)",
    )
    args = parser.parse_args(argv)
    if args.list:
        print_catalog()
        return 0
    return open_gtk()


if __name__ == "__main__":
    raise SystemExit(main())
