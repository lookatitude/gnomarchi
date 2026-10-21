"""Idempotent starship init hooks for interactive zsh/bash."""

from __future__ import annotations

import os
from pathlib import Path

MARKER = "gnomarchi: starship"

_HOOKS = {
    "zsh": 'eval "$(starship init zsh)"',
    "bash": 'eval "$(starship init bash)"',
}


def _rc_path(shell: str, home: Path | None = None) -> Path:
    home = home or Path(os.environ.get("HOME", "/tmp")).expanduser()
    return home / (".zshrc" if shell == "zsh" else ".bashrc")


def hook_line(shell: str) -> str:
    if shell not in _HOOKS:
        raise ValueError(f"unsupported shell: {shell}")
    return f"# {MARKER}\n{_HOOKS[shell]}\n"


def has_starship_hook(rc: Path) -> bool:
    if not rc.is_file():
        return False
    text = rc.read_text(encoding="utf-8")
    return MARKER in text or "starship init" in text


def ensure_starship_hook(home: Path | None = None) -> dict[str, str]:
    """Append starship init to ~/.zshrc and ~/.bashrc if missing.

    Returns a map of shell → status (added|present|created).
    """
    home = home or Path(os.environ.get("HOME", "/tmp")).expanduser()
    result: dict[str, str] = {}
    for shell in ("zsh", "bash"):
        rc = _rc_path(shell, home)
        if has_starship_hook(rc):
            result[shell] = "present"
            continue
        existed = rc.is_file()
        rc.parent.mkdir(parents=True, exist_ok=True)
        with rc.open("a", encoding="utf-8") as fh:
            if existed and rc.stat().st_size > 0:
                fh.write("\n")
            fh.write(hook_line(shell))
        result[shell] = "added" if existed else "created"
    return result


def hook_status(home: Path | None = None) -> dict[str, object]:
    home = home or Path(os.environ.get("HOME", "/tmp")).expanduser()
    cfg = home / ".config" / "starship.toml"
    return {
        "zshrc": has_starship_hook(_rc_path("zsh", home)),
        "bashrc": has_starship_hook(_rc_path("bash", home)),
        "config": str(cfg) if cfg.is_file() else None,
        "binary": _which("starship"),
    }


def _which(name: str) -> str | None:
    for part in os.environ.get("PATH", "").split(os.pathsep):
        cand = Path(part) / name
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return None
