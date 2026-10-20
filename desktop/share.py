"""Share helpers — LocalSend when available, else xdg-open / notify fallback."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def _localsend() -> str | None:
    for cand in ("localsend", "localsend_app", "LocalSend"):
        if shutil.which(cand):
            return cand
    # Flatpak
    if shutil.which("flatpak"):
        proc = subprocess.run(
            ["flatpak", "list", "--app", "--columns=application"],
            capture_output=True,
            text=True,
            check=False,
        )
        if "org.localsend.localsend_app" in (proc.stdout or ""):
            return "flatpak"
    return None


def _launch_localsend(extra: list[str] | None = None) -> int:
    bin_ = _localsend()
    if bin_ is None:
        print(
            "error: LocalSend not installed. Install › Share › LocalSend "
            "or: flatpak install flathub org.localsend.localsend_app",
            file=__import__("sys").stderr,
        )
        return 1
    if bin_ == "flatpak":
        cmd = ["flatpak", "run", "org.localsend.localsend_app", *(extra or [])]
    else:
        cmd = [bin_, *(extra or [])]
    subprocess.Popen(cmd, start_new_session=True)
    return 0


def share_file(path: str) -> int:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        print(f"error: missing path {p}", file=__import__("sys").stderr)
        return 1
    # LocalSend CLI args vary by build; open GUI with path hint via xdg
    return _launch_localsend([str(p)])


def share_folder(path: str) -> int:
    return share_file(path)


def share_clipboard() -> int:
    # Prefer wl-paste / xclip → temp file → share
    text = ""
    if shutil.which("wl-paste"):
        text = subprocess.getoutput("wl-paste -n")
    elif shutil.which("xclip"):
        text = subprocess.getoutput("xclip -selection clipboard -o")
    if not text:
        return _launch_localsend()
    tmp = Path.home() / ".cache" / "gnomarchi" / "clipboard-share.txt"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(text, encoding="utf-8")
    return share_file(str(tmp))


def receive() -> int:
    return _launch_localsend()


def install_hint() -> str:
    return (
        "LocalSend: flatpak install -y flathub org.localsend.localsend_app\n"
        "Or AUR: localsend-bin"
    )
