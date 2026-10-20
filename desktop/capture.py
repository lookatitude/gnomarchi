"""Screenshot / OCR / QR / screen-record wrappers over Arch packages.

Tools: gnome-screenshot (or grim+slurp fallback), tesseract, zbarimg, kooha
(or gnome-shell ScreenCast D-Bus / wf-recorder).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from common.paths import state_dir


def _run(argv: list[str], timeout: float | None = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, check=False, capture_output=True, text=True, timeout=timeout
    )


def _shots_dir() -> Path:
    dest = state_dir() / "captures"
    dest.mkdir(parents=True, exist_ok=True)
    return dest


def _stamp(suffix: str) -> Path:
    return _shots_dir() / f"gnomarchi-{time.strftime('%Y%m%d-%H%M%S')}{suffix}"


def _which(*names: str) -> str | None:
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def shot(*, interactive: bool = True, area: bool = False) -> Path:
    """Take a screenshot. Returns path to PNG."""
    out = _stamp(".png")
    gs = _which("gnome-screenshot")
    if gs:
        argv = [gs, "-f", str(out)]
        if area:
            argv.append("-a")
        elif interactive:
            argv.append("-i")
        proc = _run(argv, timeout=300)
        if proc.returncode == 0 and out.is_file():
            return out
    # Wayland portal / grim fallback
    grim = _which("grim")
    if grim:
        if area and _which("slurp"):
            region = _run(["slurp"])
            if region.returncode == 0 and region.stdout.strip():
                proc = _run([grim, "-g", region.stdout.strip(), str(out)])
                if proc.returncode == 0 and out.is_file():
                    return out
        proc = _run([grim, str(out)])
        if proc.returncode == 0 and out.is_file():
            return out
    # Import (ImageMagick) last resort — full display when DISPLAY set
    convert = _which("import")
    if convert and os.environ.get("DISPLAY"):
        proc = _run([convert, "-window", "root", str(out)])
        if proc.returncode == 0 and out.is_file():
            return out
    raise FileNotFoundError(
        "no screenshot tool found (install gnome-screenshot, or grim+slurp)"
    )


def ocr(*, lang: str = "eng") -> str:
    """Area screenshot → tesseract OCR → stdout text."""
    tess = _which("tesseract")
    if not tess:
        raise FileNotFoundError("tesseract not found (pacman -S tesseract tesseract-data-eng)")
    img = shot(area=True, interactive=False)
    with tempfile.TemporaryDirectory(prefix="gnomarchi-ocr-") as tmp:
        base = Path(tmp) / "out"
        proc = _run([tess, str(img), str(base), "-l", lang])
        text_path = Path(str(base) + ".txt")
        if proc.returncode != 0 or not text_path.is_file():
            err = (proc.stderr or proc.stdout or "tesseract failed").strip()
            raise RuntimeError(err)
        return text_path.read_text(encoding="utf-8", errors="replace")


def qr() -> str:
    """Area screenshot → zbarimg QR/barcode decode."""
    zbar = _which("zbarimg")
    if not zbar:
        raise FileNotFoundError("zbarimg not found (pacman -S zbar)")
    img = shot(area=True, interactive=False)
    proc = _run([zbar, "--quiet", "--raw", str(img)])
    text = (proc.stdout or "").strip()
    if proc.returncode != 0 or not text:
        raise RuntimeError((proc.stderr or "no barcode detected").strip())
    return text


def record() -> int:
    """Launch screen recorder (kooha preferred; else notify with hint)."""
    kooha = _which("kooha")
    if kooha:
        return subprocess.call([kooha])
    # GNOME 42+ built-in screencast via dbus (non-interactive start is limited)
    if shutil.which("gdbus"):
        # Open overview hint — user uses Super+Alt+R on stock GNOME
        subprocess.run(
            [
                "notify-send",
                "gnomarchi capture record",
                "Install kooha, or press Super+Alt+R for GNOME screencast",
            ],
            check=False,
        )
        return 0
    raise FileNotFoundError("kooha not found (pacman -S kooha)")
