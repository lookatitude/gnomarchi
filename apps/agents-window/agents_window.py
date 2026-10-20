#!/usr/bin/env python3
"""Agents window — usage meters, default agent, Make something."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("GNOMARCHI_ROOT", str(ROOT))

from agent.catalog import AGENTS  # noqa: E402
from agent.default_agent import get_default_agent, set_default_agent  # noqa: E402
from agent.make import STARTERS  # noqa: E402
from agent.usage import read_usage, update_usage  # noqa: E402


def _cli(*args: str) -> None:
    cli = ROOT / "bin" / "gnomarchi"
    subprocess.Popen([sys.executable, str(cli), *args])


def print_catalog() -> None:
    default = get_default_agent()
    usage = read_usage()
    print("gnomarchi Agents")
    print(f"default: {default or '(none)'}")
    print()
    print("usage:")
    print(json.dumps(usage.get("providers", {}), indent=2))
    print()
    print("agents:")
    for aid, spec in AGENTS.items():
        mark = "*" if aid == default else " "
        print(f"  {mark} {aid} — {spec.label}")
    print()
    print("Make something:")
    for kind in STARTERS:
        print(f"  • {kind}")


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

    update_usage()
    usage = read_usage()

    class AgentsWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi Agents")
            self.set_default_size(520, 560)
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Agents"))
            toolbar.add_top_bar(header)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            default = get_default_agent()
            box.append(Gtk.Label(label=f"Default: {default or 'not set'}", xalign=0))

            usage_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            usage_box.append(Gtk.Label(label="Usage", xalign=0))
            for provider, meta in (usage.get("providers") or {}).items():
                session = meta.get("session_pct")
                weekly = meta.get("weekly_pct")
                avail = meta.get("available")
                line = f"{provider}: "
                if avail and (session is not None or weekly is not None):
                    line += f"session={session}% weekly={weekly}%"
                else:
                    line += meta.get("message") or "no data — sign in"
                usage_box.append(Gtk.Label(label=line, xalign=0))
            box.append(usage_box)

            agents_list = Gtk.ListBox()
            agents_list.add_css_class("boxed-list")
            for aid, spec in AGENTS.items():
                row = Adw.ActionRow()
                row.set_title(spec.label)
                row.set_subtitle(aid + (" (default)" if aid == default else ""))
                btn_default = Gtk.Button(label="Set default")
                btn_default.connect(
                    "clicked",
                    lambda _b, a=aid: (set_default_agent(a, install=False), self.close(), _cli("agent", "window")),
                )
                btn_launch = Gtk.Button(label="Launch")
                btn_launch.connect("clicked", lambda _b, a=aid: _cli("agent", "launch", a))
                row.add_suffix(btn_default)
                row.add_suffix(btn_launch)
                agents_list.append(row)
            box.append(agents_list)

            make = Gtk.ListBox()
            make.add_css_class("boxed-list")
            for kind in STARTERS:
                row = Adw.ActionRow()
                row.set_title(f"Make something — {kind.title()}")
                row.set_subtitle(STARTERS[kind][0])
                btn = Gtk.Button(label="Run")
                btn.connect(
                    "clicked",
                    lambda _b, k=kind: _cli("agent", "make-something", k),
                )
                row.add_suffix(btn)
                make.append(row)
            box.append(Gtk.Label(label="Make something", xalign=0))
            box.append(make)

            scroll = Gtk.ScrolledWindow(vexpand=True)
            scroll.set_child(box)
            toolbar.set_content(scroll)
            self.set_content(toolbar)

    class AgentsApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Agents",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            from common.window_geom import apply_geom

            win = self.props.active_window
            if not win:
                win = AgentsWindow(self)
            apply_geom(win)
            win.present()

    return int(AgentsApp().run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnomarchi Agents window")
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args(argv)
    if args.list:
        print_catalog()
        return 0
    return open_gtk()


if __name__ == "__main__":
    raise SystemExit(main())
