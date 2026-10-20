#!/usr/bin/python3
"""gnoma-calc — basic calculator (GTK4/Adwaita). Not Omarchy-branded."""

from __future__ import annotations

import argparse
import ast
import operator
import sys


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_eval(expr: str) -> float:
    """Evaluate a simple arithmetic expression (no names/calls)."""
    tree = ast.parse(expr.replace("^", "**"), mode="eval")

    def _eval(node):
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.operand))
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
        raise ValueError("unsupported expression")

    return float(_eval(tree))


def open_gtk() -> int:
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, Gtk  # type: ignore
    except (ImportError, ValueError, AttributeError):
        print("error: GTK4/Adwaita (PyGObject) required", file=sys.stderr)
        return 1

    class CalcWindow(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnoma-calc")
            self.set_default_size(320, 420)
            self._expr = ""

            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="gnoma-calc"))
            toolbar.add_top_bar(header)

            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)

            self._display = Gtk.Entry()
            self._display.set_editable(False)
            self._display.set_alignment(1.0)
            self._display.add_css_class("title-1")
            box.append(self._display)

            grid = Gtk.Grid(column_spacing=6, row_spacing=6, column_homogeneous=True, row_homogeneous=True)
            keys = [
                ("C", 0, 0),
                ("⌫", 1, 0),
                ("%", 2, 0),
                ("/", 3, 0),
                ("7", 0, 1),
                ("8", 1, 1),
                ("9", 2, 1),
                ("*", 3, 1),
                ("4", 0, 2),
                ("5", 1, 2),
                ("6", 2, 2),
                ("-", 3, 2),
                ("1", 0, 3),
                ("2", 1, 3),
                ("3", 2, 3),
                ("+", 3, 3),
                ("0", 0, 4),
                (".", 1, 4),
                ("=", 2, 4),
            ]
            for label, col, row in keys:
                btn = Gtk.Button(label=label)
                btn.set_hexpand(True)
                btn.set_vexpand(True)
                if label == "=":
                    btn.add_css_class("suggested-action")
                    grid.attach(btn, col, row, 2, 1)
                else:
                    grid.attach(btn, col, row, 1, 1)
                btn.connect("clicked", self._on_key, label)
            box.append(grid)
            toolbar.set_content(box)
            self.set_content(toolbar)

        def _refresh(self) -> None:
            self._display.set_text(self._expr or "0")

        def _on_key(self, _b, label: str) -> None:
            if label == "C":
                self._expr = ""
            elif label == "⌫":
                self._expr = self._expr[:-1]
            elif label == "=":
                try:
                    result = safe_eval(self._expr or "0")
                    if result == int(result):
                        self._expr = str(int(result))
                    else:
                        self._expr = f"{result:.10g}"
                except (ValueError, ZeroDivisionError, SyntaxError, TypeError):
                    self._expr = "Error"
            else:
                if self._expr == "Error":
                    self._expr = ""
                self._expr += label
            self._refresh()

    class CalcApp(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Calc",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:
            win = self.props.active_window
            if not win:
                win = CalcWindow(self)
            win.present()

    return int(CalcApp().run(None))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="gnoma-calc — calculator")
    parser.add_argument("expr", nargs="*", help="optional expression to evaluate (CLI)")
    args = parser.parse_args(argv)
    if args.expr:
        try:
            result = safe_eval("".join(args.expr))
            if result == int(result):
                print(int(result))
            else:
                print(f"{result:.10g}")
            return 0
        except (ValueError, ZeroDivisionError, SyntaxError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
    return open_gtk()


if __name__ == "__main__":
    raise SystemExit(main())
