"""Branding store: ASCII screensaver/about + logo path (Omarchy branding → GNOME)."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from common.paths import REPO_ROOT, state_dir

SURFACES = ("screensaver", "about")
_DEFAULT_DIR = REPO_ROOT / "assets" / "brand"
_FALLBACK_ASCII = """\
                                            _     _
  __ _ _ __   ___  _ __ ___   __ _ _ __ ___| |__ (_)
 / _` | '_ \\ / _ \\| '_ ` _ \\ / _` | '__/ __| '_ \\| |
| (_| | | | | (_) | | | | | | (_| | | | (__| | | | |
 \\__, |_| |_|\\___/|_| |_| |_|\\__,_|_|  \\___|_| |_|_|
 |___/
"""


def branding_dir() -> Path:
    return state_dir() / "branding"


def surface_path(surface: str) -> Path:
    if surface not in SURFACES:
        raise ValueError(f"unknown surface: {surface}")
    return branding_dir() / f"{surface}.txt"


def logo_path() -> Path:
    return branding_dir() / "logo.png"


def _shipped_default(surface: str) -> str:
    candidate = _DEFAULT_DIR / f"{surface}.txt"
    if candidate.is_file():
        return candidate.read_text(encoding="utf-8")
    text = _FALLBACK_ASCII
    if surface == "about":
        ver = _version_line()
        text = f"{text.rstrip()}\n\n{ver}\n"
    return text


def _version_line() -> str:
    ver_file = REPO_ROOT / "VERSION"
    ver = ver_file.read_text(encoding="utf-8").strip() if ver_file.is_file() else "dev"
    return f"gnomarchi {ver} — stock GNOME omakase (not affiliated with Omarchy)"


def _figlet_text(phrase: str) -> str | None:
    if not shutil.which("figlet"):
        return None
    proc = subprocess.run(
        ["figlet", "-f", "standard", phrase],
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.rstrip() + "\n"


def ensure_store() -> Path:
    """Create branding dir + seed missing screensaver/about/logo from assets."""
    root = branding_dir()
    root.mkdir(parents=True, exist_ok=True)
    for surface in SURFACES:
        path = surface_path(surface)
        if not path.is_file():
            path.write_text(_shipped_default(surface), encoding="utf-8")
    logo = logo_path()
    if not logo.is_file():
        for src in (
            _DEFAULT_DIR / "logo.png",
            REPO_ROOT / "docs" / "brand" / "logo.png",
            REPO_ROOT / "icon.png",
        ):
            if src.is_file():
                shutil.copy2(src, logo)
                break
    return root


def read_surface(surface: str) -> str:
    ensure_store()
    path = surface_path(surface)
    return path.read_text(encoding="utf-8")


def write_surface(surface: str, text: str) -> Path:
    ensure_store()
    path = surface_path(surface)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text, encoding="utf-8")
    return path


def reset_surface(surface: str) -> Path:
    ensure_store()
    path = surface_path(surface)
    path.write_text(_shipped_default(surface), encoding="utf-8")
    return path


def set_text(surface: str, phrase: str | None = None) -> Path:
    """Set surface from FIGlet phrase (default: gnomarchi) or fallback ASCII."""
    phrase = (phrase or "gnomarchi").strip() or "gnomarchi"
    art = _figlet_text(phrase)
    if art is None:
        art = _FALLBACK_ASCII if phrase == "gnomarchi" else f"{phrase}\n"
    if surface == "about":
        art = art.rstrip() + "\n\n" + _version_line() + "\n"
    return write_surface(surface, art)


def image_to_ascii(image_path: Path, *, width: int = 80) -> str | None:
    """Crude Pillow luminance ASCII. Returns None if Pillow unavailable."""
    try:
        from PIL import Image  # type: ignore
    except ImportError:
        return None
    chars = " .:-=+*#%@"
    img = Image.open(image_path).convert("L")
    w, h = img.size
    if w <= 0 or h <= 0:
        return None
    new_w = max(8, min(width, w))
    new_h = max(4, int(h * (new_w / w) * 0.45))
    img = img.resize((new_w, new_h))
    pixels = list(img.getdata())
    lines: list[str] = []
    for y in range(new_h):
        row = pixels[y * new_w : (y + 1) * new_w]
        lines.append("".join(chars[min(len(chars) - 1, p * len(chars) // 256)] for p in row))
    return "\n".join(lines) + "\n"


def set_from_image(surface: str, image_path: Path) -> tuple[Path | None, str]:
    """
    Convert image → ASCII when Pillow is present.
    Returns (path, message). path is None on soft failure (stub path).
    """
    ensure_store()
    image_path = image_path.expanduser().resolve()
    if not image_path.is_file():
        return None, f"error: image not found: {image_path}"
    art = image_to_ascii(image_path)
    if art is None:
        note = branding_dir() / f"{surface}.image-todo.txt"
        note.write_text(
            f"TODO: install python-pillow (PIL) to convert images to ASCII.\n"
            f"source: {image_path}\n",
            encoding="utf-8",
        )
        return None, (
            f"Pillow not installed — skipped image→ASCII. "
            f"Noted path in {note}. Install python-pillow, then retry."
        )
    if surface == "about":
        art = art.rstrip() + "\n\n" + _version_line() + "\n"
    path = write_surface(surface, art)
    return path, f"{surface} ← ascii from {image_path}"


def logo_status() -> dict[str, str]:
    ensure_store()
    logo = logo_path()
    plymouth_theme = Path("/usr/share/plymouth/themes/gnomarchi/logo.png")
    return {
        "branding_logo": str(logo) if logo.is_file() else "(missing)",
        "branding_logo_exists": "yes" if logo.is_file() else "no",
        "plymouth_logo": str(plymouth_theme) if plymouth_theme.is_file() else "(not installed)",
        "plymouth_logo_exists": "yes" if plymouth_theme.is_file() else "no",
        "hint": "gnomarchi install plymouth  # bootsplash theme",
    }


def print_logo_status() -> int:
    for key, val in logo_status().items():
        print(f"{key}\t{val}")
    return 0


def render_boot_preview() -> Path:
    """Composite plymouth logo + GDM unlock bg into a review PNG (no reboot)."""
    ensure_store()
    from theme.unlock import unlock_path

    out = branding_dir() / "boot-login-preview.png"
    bg = unlock_path()
    if not bg.is_file():
        bg = gdm_staged_bg()
    logo = Path("/usr/share/plymouth/themes/gnomarchi/logo.png")
    if not logo.is_file():
        logo = logo_path()
    # Prefer magick; fall back to copy unlock art
    if shutil.which("magick") and bg.is_file():
        argv = [
            "magick",
            str(bg),
            "-resize",
            "1920x1080^",
            "-gravity",
            "center",
            "-extent",
            "1920x1080",
            "-fill",
            "rgba(0,0,0,0.45)",
            "-draw",
            "rectangle 0,0 1920,1080",
        ]
        if logo.is_file():
            argv.extend(
                [
                    "(",
                    str(logo),
                    "-resize",
                    "320x320",
                    ")",
                    "-gravity",
                    "center",
                    "-compose",
                    "over",
                    "-composite",
                ]
            )
        argv.extend(
            [
                "-fill",
                "white",
                "-pointsize",
                "28",
                "-gravity",
                "south",
                "-annotate",
                "+0+80",
                "gnomarchi · plymouth / GDM preview",
                str(out),
            ]
        )
        subprocess.run(argv, check=False, timeout=30)
        if out.is_file():
            return out
    if bg.is_file():
        shutil.copy2(bg, out)
        return out
    raise FileNotFoundError("no unlock/GDM background to preview")


def launch_viewer(surface: str, *, fullscreen: bool | None = None) -> int:
    """Open GTK ASCII viewer (screensaver fullscreen; about windowed)."""
    ensure_store()
    app = REPO_ROOT / "apps" / "screensaver" / "gnomarchi_screensaver.py"
    if not app.is_file():
        text = read_surface(surface)
        print(text, end="" if text.endswith("\n") else "\n")
        return 0
    fs = fullscreen if fullscreen is not None else surface == "screensaver"
    argv = [sys.executable, str(app), "--surface", surface]
    if fs:
        argv.append("--fullscreen")
    return int(subprocess.call(argv))


# --- GDM greeter background (GNOME — not SDDM) ---

GDM_SYSTEM_DIR = Path("/usr/local/share/gnomarchi/gdm")
GDM_SYSTEM_BG = GDM_SYSTEM_DIR / "background.png"


def gdm_staged_bg() -> Path:
    return branding_dir() / "gdm-background.png"


def gdm_apply(*, use_sudo: bool = True) -> int:
    """Stage unlock art for GDM; install under /usr/local/share when root/sudo -n.

    Safe when GDM dirs need root: always stages user-local files and prints the
    install command if escalation is unavailable.
    """
    import os

    from theme.unlock import apply_unlock, unlock_path

    ensure_store()
    src = unlock_path()
    if not src.is_file():
        applied = apply_unlock()
        src = applied if applied is not None else unlock_path()
    if not src.is_file():
        print(
            "error: no unlock art; run: gnomarchi theme unlock set <pack-id>",
            file=sys.stderr,
        )
        return 1

    staged = gdm_staged_bg()
    shutil.copy2(src, staged)
    note = branding_dir() / "GDM.txt"
    note.write_text(
        "gnomarchi GDM greeter background (GNOME — not SDDM)\n"
        f"staged: {staged}\n"
        f"system: {GDM_SYSTEM_BG}\n"
        "\n"
        "Install (root):\n"
        f"  sudo mkdir -p {GDM_SYSTEM_DIR}\n"
        f"  sudo cp {staged} {GDM_SYSTEM_BG}\n"
        "\n"
        "Point the greeter (as gdm user, when dbus allows):\n"
        "  sudo -u gdm dbus-run-session gsettings set \\\n"
        "    org.gnome.desktop.screensaver picture-uri \\\n"
        f"    'file://{GDM_SYSTEM_BG}'\n"
        "\n"
        "GDM CSS under /usr/share/gnome-shell/theme/ is distro-owned;\n"
        "this command only stages the background path safely.\n",
        encoding="utf-8",
    )
    print(f"gdm background staged → {staged}")
    print(f"notes → {note}")

    if os.geteuid() == 0:
        GDM_SYSTEM_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copy2(staged, GDM_SYSTEM_BG)
        print(f"gdm background installed → {GDM_SYSTEM_BG}")
        return 0

    if not use_sudo:
        print(f"run as root to install: sudo cp {staged} {GDM_SYSTEM_BG}")
        return 0

    try:
        proc = subprocess.run(
            ["sudo", "-n", "mkdir", "-p", str(GDM_SYSTEM_DIR)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc.returncode != 0:
            print(
                f"sudo unavailable (need root once): sudo cp {staged} {GDM_SYSTEM_BG}"
            )
            return 0
        proc2 = subprocess.run(
            ["sudo", "-n", "cp", str(staged), str(GDM_SYSTEM_BG)],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if proc2.returncode == 0:
            print(f"gdm background installed → {GDM_SYSTEM_BG}")
        else:
            print(
                f"sudo cp failed; install manually: sudo cp {staged} {GDM_SYSTEM_BG}"
            )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print(f"install manually: sudo cp {staged} {GDM_SYSTEM_BG}")
    return 0
