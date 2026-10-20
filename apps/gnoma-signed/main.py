#!/usr/bin/env python3
"""gnoma-signed — PDF annotate / fill (Omarchy Signed → Xournal++ / Evince)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def _open(path: str | None) -> int:
    for cand in ("xournalpp", "evince", "papers"):
        if shutil.which(cand):
            cmd = [cand] if not path else [cand, path]
            subprocess.Popen(cmd, start_new_session=True)
            return 0
    print("error: install xournalpp or evince", file=sys.stderr)
    return 1


def main(argv: list[str] | None = None) -> int:
    argv = list(argv if argv is not None else sys.argv[1:])
    if argv:
        return _open(str(Path(argv[0]).expanduser()))
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gio, Gtk  # type: ignore
    except (ImportError, ValueError):
        return _open(None)

    class App(Adw.Application):
        def __init__(self) -> None:
            super().__init__(
                application_id="org.gnomarchi.Signed",
                flags=Gio.ApplicationFlags.FLAGS_NONE,
            )

        def do_activate(self) -> None:  # noqa: N802
            dialog = Gtk.FileDialog(title="Open PDF to annotate")
            filt = Gtk.FileFilter()
            filt.add_mime_type("application/pdf")
            dialog.set_default_filter(filt)

            def _done(_d, result) -> None:
                try:
                    f = dialog.open_finish(result)
                except Exception:
                    return
                if f:
                    _open(f.get_path())

            dialog.open(None, None, _done)

    return App().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
