"""Shared StatusNotifier / AppIndicator helper for first-party plugins."""

from __future__ import annotations

import signal
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable


@dataclass
class MenuAction:
    """One tray menu row. When get_active is set, renders as a check item."""

    label: str
    action: Callable[[], None]
    get_active: Callable[[], bool] | None = None


def _themed_icon(plugin_id: str, fallback: str) -> str:
    """Prefer accent-tinted hicolor icon emitted by theme set (gnomarchi-<slug>)."""
    import os
    from pathlib import Path

    slug = plugin_id.split(".")[-1].replace("_", "-")
    name = f"gnomarchi-{slug}"
    # system-update → gnomarchi-system-update
    if plugin_id == "gnomarchi.system-update":
        name = "gnomarchi-system-update"
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    for size in ("22x22", "24x24", "32x32", "48x48"):
        cand = home / ".local" / "share" / "icons" / "hicolor" / size / "apps" / f"{name}.png"
        if cand.is_file():
            return name
    return fallback


def run_indicator(
    *,
    id: str,
    title: str,
    icon: str = "application-x-executable",
    on_activate: Callable[[], None] | None = None,
    on_secondary: Callable[[], None] | None = None,
    menu_actions: list[MenuAction] | None = None,
) -> int:
    """Run until SIGTERM. Prefers AppIndicator3, then Ayatana."""
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

    AppIndicator = None
    Gtk = None
    try:
        import gi

        gi.require_version("Gtk", "3.0")
        try:
            gi.require_version("AppIndicator3", "0.1")
            from gi.repository import AppIndicator3 as AppIndicator  # type: ignore
        except (ImportError, ValueError):
            gi.require_version("AyatanaAppIndicator3", "0.1")
            from gi.repository import AyatanaAppIndicator3 as AppIndicator  # type: ignore
        from gi.repository import Gtk  # type: ignore
    except (ImportError, ValueError) as exc:
        print(f"gnomarchi indicator {id}: AppIndicator unavailable ({exc}) — idle", flush=True)
        signal.pause()
        return 0

    icon_name = _themed_icon(id, icon)
    ind = AppIndicator.Indicator.new(
        id,
        icon_name,
        AppIndicator.IndicatorCategory.APPLICATION_STATUS,
    )
    ind.set_status(AppIndicator.IndicatorStatus.ACTIVE)
    ind.set_title(title)

    menu = Gtk.Menu()
    if menu_actions:
        check_items: list[tuple[object, MenuAction]] = []

        def _refresh_checks(*_args: object) -> None:
            for widget, spec in check_items:
                if spec.get_active is None:
                    continue
                widget.handler_block_by_func(_on_check)
                widget.set_active(bool(spec.get_active()))
                widget.handler_unblock_by_func(_on_check)

        def _on_check(widget: object, spec: MenuAction) -> None:
            spec.action()
            _refresh_checks()

        for spec in menu_actions:
            if spec.get_active is not None:
                item = Gtk.CheckMenuItem(label=spec.label)
                item.set_active(bool(spec.get_active()))
                item.connect("toggled", _on_check, spec)
                check_items.append((item, spec))
            else:
                item = Gtk.MenuItem(label=spec.label)
                item.connect("activate", lambda _w, s=spec: s.action())
            menu.append(item)
        menu.connect("show", _refresh_checks)
    else:
        item_open = Gtk.MenuItem(label=f"Open {title}")
        item_open.connect("activate", lambda *_: on_activate() if on_activate else None)
        menu.append(item_open)
        if on_secondary:
            item2 = Gtk.MenuItem(label="Secondary action")
            item2.connect("activate", lambda *_: on_secondary())
            menu.append(item2)
    item_quit = Gtk.MenuItem(label="Quit")
    item_quit.connect("activate", Gtk.main_quit)
    menu.append(item_quit)
    menu.show_all()
    ind.set_menu(menu)
    try:
        ind.connect("scroll-event", lambda *_: on_activate() if on_activate else None)
    except TypeError:
        pass
    Gtk.main()
    return 0


def spawn_cli(*args: str) -> None:
    subprocess.Popen(["gnomarchi", *args])
