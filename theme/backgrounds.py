"""Per-theme background cycle (Omarchy Super+Ctrl+W equivalent).

Prefers stills under theme/packs/<id>/backgrounds/ (ported Omarchy graphics with
CREDITS; Omarchy logos replaced by gnomarchi brand). Falls back to generated
color-field PNGs when a pack has no backgrounds.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from theme.emitters import _write_png, emit_gsettings
from theme.palette import load_palette
from theme.paths import find_pack, state_dir

STILL_SUFFIXES = {".png", ".webp", ".jpg", ".jpeg", ".avif"}
VARIANT_COUNT = 4  # used only for generated fallback


def _active_theme_id() -> str | None:
    path = state_dir() / "active-theme"
    if not path.is_file():
        return None
    tid = path.read_text(encoding="utf-8").strip()
    return tid or None


def _variant_dir(theme_id: str) -> Path:
    return state_dir() / "wallpapers" / "variants" / theme_id


def _index_path(theme_id: str) -> Path:
    return _variant_dir(theme_id) / "index.json"


def list_pack_stills(pack: Path) -> list[Path]:
    bg = pack / "backgrounds"
    if not bg.is_dir():
        return []
    stills: list[Path] = []
    for path in sorted(bg.iterdir()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in STILL_SUFFIXES:
            continue
        # Skip nested intros dir handled only if files sit at top level
        stills.append(path)
    # Also include one-level intros stills? Omarchy intros are video — skip.
    return stills


def ensure_variants(theme_id: str | None = None) -> list[Path]:
    """Return ordered background candidates for the theme."""
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme; run gnomarchi theme set first")
    pack = find_pack(tid)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {tid}")
    stills = list_pack_stills(pack)
    if stills:
        return stills
    # Generated fallback
    colors = load_palette(pack)
    dest = _variant_dir(tid)
    dest.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(VARIANT_COUNT):
        shifted = dict(colors)
        if i == 1:
            shifted["accent"], shifted["surface"] = (
                colors.get("surface", "#121a2b"),
                colors.get("accent", "#3d8bfd"),
            )
        elif i == 2:
            shifted["background"] = colors.get("surface", "#121a2b")
            shifted["surface"] = colors.get("background", "#0b1220")
        elif i == 3:
            shifted["accent"] = colors.get("foreground", "#e8eef7")
        out = dest / f"{i:02d}.png"
        _write_png(out, 1920, 1080, shifted)
        paths.append(out)
    return paths


def current_index(theme_id: str | None = None) -> int:
    tid = theme_id or _active_theme_id()
    if not tid:
        return 0
    variants = ensure_variants(tid)
    n = max(len(variants), 1)
    meta = _index_path(tid)
    if not meta.is_file():
        return 0
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
        return int(data.get("index", 0)) % n
    except (json.JSONDecodeError, TypeError, ValueError):
        return 0


def _activate(chosen: Path, pack: Path, tid: str, idx: int) -> Path:
    dest_dir = state_dir() / "wallpapers"
    dest_dir.mkdir(parents=True, exist_ok=True)
    active = dest_dir / f"active{chosen.suffix.lower()}"
    # Clear other actives
    for old in dest_dir.glob("active.*"):
        if old != active:
            old.unlink(missing_ok=True)
    shutil.copy2(chosen, active)
    # Also keep active.png alias when source is png for older callers
    if active.suffix.lower() == ".png":
        pass
    elif chosen.suffix.lower() == ".png":
        shutil.copy2(chosen, dest_dir / "active.png")
    _index_path(tid).parent.mkdir(parents=True, exist_ok=True)
    _index_path(tid).write_text(
        json.dumps({"index": idx, "theme": tid, "path": str(chosen)}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    emit_gsettings(active, load_palette(pack))
    return active


def set_background(index: int, theme_id: str | None = None) -> Path:
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme")
    pack = find_pack(tid)
    if pack is None:
        raise FileNotFoundError(f"theme pack not found: {tid}")
    variants = ensure_variants(tid)
    idx = index % len(variants)
    return _activate(variants[idx], pack, tid, idx)


def next_background(theme_id: str | None = None) -> Path:
    tid = theme_id or _active_theme_id()
    if not tid:
        raise FileNotFoundError("no active theme")
    return set_background(current_index(tid) + 1, tid)


def first_background(theme_id: str | None = None) -> Path:
    return set_background(0, theme_id)


def list_backgrounds(theme_id: str | None = None) -> list[tuple[int, Path]]:
    """Indexed stills / generated variants for the active (or given) theme."""
    variants = ensure_variants(theme_id)
    return list(enumerate(variants))


def pick_background_cli(theme_id: str | None = None) -> Path | None:
    """List pack backgrounds and apply the chosen index (stdin)."""
    import sys

    rows = list_backgrounds(theme_id)
    if not rows:
        print("no backgrounds", file=sys.stderr)
        return None
    cur = current_index(theme_id)
    print("# backgrounds")
    for idx, path in rows:
        mark = "*" if idx == cur else " "
        print(f"{mark} {idx:2d}. {path.name}\t{path}")
    print("Enter index (empty = quit): ", end="", flush=True)
    try:
        choice = sys.stdin.readline().strip()
    except KeyboardInterrupt:
        print()
        return None
    if not choice:
        return None
    try:
        index = int(choice)
    except ValueError:
        print("not a number", file=sys.stderr)
        return None
    return set_background(index, theme_id)


def pick_background_gtk(theme_id: str | None = None) -> int:
    """GTK grid of pack backgrounds; apply on activate."""
    import sys

    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, GdkPixbuf, Gio, GLib, Gtk, Pango  # type: ignore
    except (ImportError, ValueError, AttributeError):
        path = pick_background_cli(theme_id)
        if path is None:
            return 1
        print(f"background → {path}")
        return 0

    try:
        rows = list_backgrounds(theme_id)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not rows:
        print("no backgrounds", file=sys.stderr)
        return 1

    TILE_W, TILE_H = 160, 90

    class BgPicker(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnomarchi Backgrounds")
            self.set_default_size(720, 520)
            self._rows = rows
            toolbar = Adw.ToolbarView()
            header = Adw.HeaderBar()
            header.set_title_widget(Gtk.Label(label="Background"))
            toolbar.add_top_bar(header)
            outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            outer.set_margin_top(12)
            outer.set_margin_bottom(12)
            outer.set_margin_start(16)
            outer.set_margin_end(16)
            self._hint = Gtk.Label(label="Click a still to apply · Esc closes", xalign=0)
            self._hint.add_css_class("dim-label")
            outer.append(self._hint)
            flow = Gtk.FlowBox()
            flow.set_max_children_per_line(3)
            flow.set_min_children_per_line(2)
            flow.set_selection_mode(Gtk.SelectionMode.SINGLE)
            flow.set_activate_on_single_click(True)
            flow.connect("child-activated", self._on_activate)
            for idx, path in rows:
                child = self._make_tile(idx, path)
                flow.append(child)
            scroller = Gtk.ScrolledWindow(vexpand=True)
            scroller.set_child(flow)
            outer.append(scroller)
            toolbar.set_content(outer)
            self.set_content(toolbar)

        def _make_tile(self, index: int, path: Path) -> Gtk.FlowBoxChild:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            picture = Gtk.Picture()
            picture.set_content_fit(Gtk.ContentFit.COVER)
            picture.set_size_request(TILE_W, TILE_H)
            try:
                pix = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    str(path), TILE_W * 2, TILE_H * 2, False
                )
                picture.set_pixbuf(pix)
            except Exception:
                pass
            name = Gtk.Label(label=f"{index}. {path.name}", xalign=0)
            name.set_ellipsize(Pango.EllipsizeMode.END)
            box.append(picture)
            box.append(name)
            child = Gtk.FlowBoxChild()
            child.set_child(box)
            child._bg_index = index  # type: ignore[attr-defined]
            return child

        def _on_activate(self, _flow: Gtk.FlowBox, child: Gtk.FlowBoxChild) -> None:
            idx = int(getattr(child, "_bg_index", 0))

            def _apply() -> bool:
                try:
                    dest = set_background(idx, theme_id)
                    self._hint.set_label(f"Applied {dest.name}")
                except (FileNotFoundError, ValueError) as exc:
                    self._hint.set_label(f"Failed: {exc}")
                return False

            GLib.idle_add(_apply)

    class App(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.BgPicker",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:  # noqa: N802
            win = BgPicker(self)
            win.present()

    return int(App().run(None))
