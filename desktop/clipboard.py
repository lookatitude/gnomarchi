"""Clipboard history via GPaste (Arch: gpaste) with wl-clipboard fallback."""

from __future__ import annotations

import shutil
import subprocess


def _run(argv: list[str], timeout: float = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv, check=False, capture_output=True, text=True, timeout=timeout
    )


def gpaste_available() -> bool:
    return shutil.which("gpaste-client") is not None


def ensure_daemon() -> None:
    if not gpaste_available():
        return
    _run(["gpaste-client", "start"])


def history(limit: int = 20) -> list[str]:
    """Return recent clipboard entries (newest first)."""
    ensure_daemon()
    if gpaste_available():
        proc = _run(["gpaste-client", "history"])
        if proc.returncode == 0:
            lines = [ln for ln in (proc.stdout or "").splitlines() if ln.strip()]
            # gpaste-client history lines look like: "0: text..."
            cleaned: list[str] = []
            for ln in lines:
                if ": " in ln[:8]:
                    cleaned.append(ln.split(": ", 1)[1])
                else:
                    cleaned.append(ln)
            return cleaned[:limit]
    # Fallback: current selection only
    for tool, args in (
        ("wl-paste", ["wl-paste", "--no-newline"]),
        ("xclip", ["xclip", "-selection", "clipboard", "-o"]),
        ("xsel", ["xsel", "--clipboard", "--output"]),
    ):
        if shutil.which(tool):
            proc = _run(args)
            text = (proc.stdout or "").strip()
            return [text] if text else []
    raise FileNotFoundError(
        "clipboard tool missing (pacman -S gpaste, or wl-clipboard / xclip)"
    )


def select(index: int = 0) -> str:
    """Select history entry by index (0 = newest) and place on clipboard."""
    ensure_daemon()
    if gpaste_available():
        proc = _run(["gpaste-client", "select", str(index)])
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "select failed").strip())
        items = history(limit=index + 1)
        return items[index] if index < len(items) else ""
    items = history(limit=index + 1)
    if index >= len(items):
        raise IndexError(f"clipboard index out of range: {index}")
    return items[index]


def ui() -> int:
    """Open GPaste UI / applet if available."""
    if shutil.which("gpaste-client"):
        return subprocess.call(["gpaste-client", "ui"])
    subprocess.run(
        [
            "notify-send",
            "gnomarchi clipboard",
            "Install gpaste (pacman -S gpaste) for clipboard history UI",
        ],
        check=False,
    )
    return 1
