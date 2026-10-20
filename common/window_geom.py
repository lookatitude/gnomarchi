"""Optional window placement for screenshot / demo layouts.

Set ``GNOMARCHI_WINDOW_GEOM=x,y,w,h`` before launching a GTK4/Adw window.
"""

from __future__ import annotations

import os
from typing import Any


def parse_geom(raw: str | None = None) -> tuple[int, int, int, int] | None:
    text = (raw if raw is not None else os.environ.get("GNOMARCHI_WINDOW_GEOM", "")).strip()
    if not text:
        return None
    parts = [p.strip() for p in text.replace("x", ",").split(",")]
    if len(parts) != 4:
        return None
    try:
        x, y, w, h = (int(p) for p in parts)
    except ValueError:
        return None
    if w < 32 or h < 32:
        return None
    return x, y, w, h


def apply_geom(window: Any) -> bool:
    """Move/resize a Gtk.Window / Adw.ApplicationWindow when env is set."""
    geom = parse_geom()
    if geom is None:
        return False
    x, y, w, h = geom
    try:
        window.set_default_size(w, h)
    except Exception:
        pass

    def _place(*_args: object) -> None:
        try:
            # GTK4: move via native surface when available (X11); Wayland may no-op.
            if hasattr(window, "move"):
                window.move(x, y)
            surface = window.get_surface() if hasattr(window, "get_surface") else None
            if surface is not None and hasattr(surface, "get_display"):
                display = surface.get_display()
                if display is not None and hasattr(window, "set_startup_id"):
                    pass
            # Prefer GdkX11 when present
            try:
                from gi.repository import GdkX11  # type: ignore

                if surface is not None and isinstance(surface, GdkX11.X11Surface):
                    import ctypes

                    # Fallback: gdk_x11_display_get_xdisplay + XMoveResizeWindow via xdotool-style
                    # is fragile; use Gtk.Window default size + present and rely on GDK_BACKEND=x11
                    # + external wmctrl when needed.
                    pass
            except Exception:
                pass
            if hasattr(window, "present_with_time"):
                window.present()
            else:
                window.present()
        except Exception:
            pass

    try:
        window.connect("map", _place)
    except Exception:
        _place()
    return True
