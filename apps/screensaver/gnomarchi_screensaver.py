#!/usr/bin/env python3
"""Fullscreen / windowed ASCII branding viewer (Omarchy screensaver / about)."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.environ.setdefault("GNOMARCHI_ROOT", str(ROOT))


def _load_text(surface: str) -> str:
    from desktop.branding import read_surface

    return read_surface(surface)


def run_terminal(surface: str) -> int:
    text = _load_text(surface)
    print(text, end="" if text.endswith("\n") else "\n")
    return 0


def run_gtk(surface: str, *, fullscreen: bool) -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Gdk", "4.0")
        from gi.repository import Gdk, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        return run_terminal(surface)

    text = _load_text(surface)

    # About gets a brighter sweep glint; screensaver stays subtle pulse.
    glint_about = """
    @keyframes gnomarchi-glint-sweep {
      0% { opacity: 0.55; text-shadow: 0 0 0 transparent; }
      40% { opacity: 1.0; text-shadow: 0 0 12px #66ff99, 0 0 28px #33ff6688; }
      100% { opacity: 0.55; text-shadow: 0 0 0 transparent; }
    }
    label.gnomarchi-ascii.glint {
      animation: gnomarchi-glint-sweep 2.0s ease-in-out infinite;
    }
    """
    glint_screensaver = """
    @keyframes gnomarchi-glint {
      0% { opacity: 0.75; }
      50% { opacity: 1.0; }
      100% { opacity: 0.75; }
    }
    label.gnomarchi-ascii.glint {
      animation: gnomarchi-glint 2.4s ease-in-out infinite;
    }
    """
    css = f"""
    window.gnomarchi-brand {{
      background-color: #000000;
    }}
    label.gnomarchi-ascii {{
      color: #33ff66;
      font-family: monospace;
      font-size: 14pt;
      letter-spacing: 0.5px;
    }}
    {glint_about if surface == "about" else glint_screensaver}
    """

    class BrandWindow(Gtk.Window):
        def __init__(self, app: Gtk.Application) -> None:
            title = "gnomarchi screensaver" if surface == "screensaver" else "About gnomarchi"
            super().__init__(application=app, title=title)
            self.add_css_class("gnomarchi-brand")
            if fullscreen:
                self.set_default_size(960, 600)
            else:
                self.set_default_size(720, 420)

            provider = Gtk.CssProvider()
            provider.load_from_data(css.encode("utf-8"))
            display = Gdk.Display.get_default()
            if display is not None:
                Gtk.StyleContext.add_provider_for_display(
                    display, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )

            label = Gtk.Label(label=text)
            label.set_selectable(False)
            label.set_wrap(False)
            label.set_justify(Gtk.Justification.CENTER)
            label.set_halign(Gtk.Align.CENTER)
            label.set_valign(Gtk.Align.CENTER)
            label.add_css_class("gnomarchi-ascii")
            label.add_css_class("glint")
            label.set_margin_top(24)
            label.set_margin_bottom(24)
            label.set_margin_start(24)
            label.set_margin_end(24)

            scroll = Gtk.ScrolledWindow()
            scroll.set_child(label)
            scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
            self.set_child(scroll)

            key = Gtk.EventControllerKey()
            key.connect("key-pressed", self._on_key)
            self.add_controller(key)
            click = Gtk.GestureClick()
            click.connect("pressed", self._on_click)
            self.add_controller(click)

            if fullscreen:
                self.maximize()
                self.fullscreen()

        def _on_key(self, _c, keyval, _code, _state) -> bool:
            # Escape / q / space
            if keyval in (Gdk.KEY_Escape, Gdk.KEY_q, Gdk.KEY_Q, Gdk.KEY_space):
                self.close()
                return True
            return False

        def _on_click(self, *_args) -> None:
            if fullscreen:
                self.close()

    class BrandApp(Gtk.Application):
        def __init__(self) -> None:
            super().__init__(application_id="org.gnomarchi.branding")

        def do_activate(self) -> None:  # noqa: N802
            win = BrandWindow(self)
            win.present()

    app = BrandApp()
    return int(app.run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnomarchi ASCII branding viewer")
    parser.add_argument("--surface", choices=("screensaver", "about"), default="screensaver")
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--terminal", action="store_true", help="print to stdout only")
    args = parser.parse_args(argv)
    if args.terminal:
        return run_terminal(args.surface)
    return run_gtk(args.surface, fullscreen=bool(args.fullscreen))


if __name__ == "__main__":
    raise SystemExit(main())
