#!/usr/bin/env python3
"""gnoma-monologue — dictation notepad (Omarchy Monologue parity).

Uses whisper.cpp / openai-whisper / vosk when present; otherwise a notepad
with mic-record → WAV via ffmpeg for offline transcription later.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def _transcribe(wav: Path) -> str:
    if shutil.which("whisper"):
        out = subprocess.run(
            ["whisper", str(wav), "--model", "base", "--output_format", "txt", "--output_dir", str(wav.parent)],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        txt = wav.with_suffix(".txt")
        if txt.is_file():
            return txt.read_text(encoding="utf-8").strip()
        return (out.stdout or "").strip()
    if shutil.which("whisper-cpp") or shutil.which("main"):
        bin_ = shutil.which("whisper-cpp") or "main"
        out = subprocess.run(
            [bin_, "-f", str(wav)],
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
        )
        return (out.stdout or "").strip()
    return ""


def _record_seconds(seconds: int = 8) -> Path | None:
    if not shutil.which("ffmpeg"):
        return None
    dest = Path(tempfile.mkdtemp(prefix="gnoma-mono-")) / "take.wav"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "pulse",
            "-i",
            "default",
            "-t",
            str(seconds),
            str(dest),
        ],
        capture_output=True,
        check=False,
        timeout=seconds + 15,
    )
    return dest if dest.is_file() else None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    try:
        import gi

        gi.require_version("Gtk", "4.0")
        gi.require_version("Adw", "1")
        from gi.repository import Adw, Gdk, Gtk  # type: ignore
    except (ImportError, ValueError):
        print("gnoma-monologue needs GTK4/Adw", file=sys.stderr)
        return 2

    class Win(Adw.ApplicationWindow):
        def __init__(self, app: Adw.Application) -> None:
            super().__init__(application=app, title="gnoma Monologue")
            self.set_default_size(520, 360)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            for m in (12, 12, 12, 12):
                pass
            box.set_margin_top(12)
            box.set_margin_bottom(12)
            box.set_margin_start(12)
            box.set_margin_end(12)
            self.buf = Gtk.TextBuffer()
            view = Gtk.TextView(buffer=self.buf)
            view.set_vexpand(True)
            view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            scroll = Gtk.ScrolledWindow()
            scroll.set_child(view)
            row = Gtk.Box(spacing=8)
            rec = Gtk.Button(label="Record 8s → text")
            rec.add_css_class("suggested-action")
            rec.connect("clicked", self._record)
            copy = Gtk.Button(label="Copy all")
            copy.connect("clicked", self._copy)
            row.append(rec)
            row.append(copy)
            hint = Gtk.Label(
                label="Uses whisper or ffmpeg+pulse. Install whisper for STT.",
                xalign=0,
            )
            hint.add_css_class("dim-label")
            box.append(scroll)
            box.append(row)
            box.append(hint)
            self.set_content(box)

        def _append(self, text: str) -> None:
            end = self.buf.get_end_iter()
            self.buf.insert(end, text + ("\n" if text and not text.endswith("\n") else ""))

        def _record(self, *_a) -> None:
            wav = _record_seconds(8)
            if wav is None:
                self._append("[record failed — need ffmpeg + pulse]")
                return
            text = _transcribe(wav)
            if text:
                self._append(text)
            else:
                self._append(f"[saved {wav} — install whisper to transcribe]")

        def _copy(self, *_a) -> None:
            start, end = self.buf.get_bounds()
            text = self.buf.get_text(start, end, True)
            display = Gdk.Display.get_default()
            if display:
                display.get_clipboard().set(text)

    class App(Adw.Application):
        def __init__(self) -> None:
            super().__init__(application_id="org.gnomarchi.Monologue")

        def do_activate(self) -> None:  # noqa: N802
            Win(self).present()

    return App().run(None)


if __name__ == "__main__":
    raise SystemExit(main())
