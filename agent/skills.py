"""Symlink gnomarchi skills into every agent harness path (Omarchy parity)."""

from __future__ import annotations

import os
from pathlib import Path

from common.paths import REPO_ROOT, state_dir

HARNESS_SKILL_DIRS = (
    "~/.claude/skills",
    "~/.codex/skills",
    "~/.pi/agent/skills",
    "~/.gemini/config/skills",
    "~/.hermes/skills",
    "~/.agents/skills",
)


def skills_source() -> Path:
    cfg = state_dir() / "skills"
    if cfg.is_dir():
        return cfg
    return REPO_ROOT / "skills"


def install_skills() -> list[str]:
    src = skills_source()
    if not src.is_dir():
        return []
    linked: list[str] = []
    home = Path(os.environ.get("HOME", "/tmp")).expanduser()
    for rel in HARNESS_SKILL_DIRS:
        dest_root = Path(rel).expanduser() if rel.startswith("~") else home / rel
        # expanduser on "~/.claude/skills" works
        dest_root = Path(os.path.expanduser(rel))
        dest_root.mkdir(parents=True, exist_ok=True)
        for skill_dir in sorted(src.iterdir()):
            if not skill_dir.is_dir():
                continue
            target = dest_root / skill_dir.name
            if target.is_symlink() or target.exists():
                if target.is_symlink() and target.resolve() == skill_dir.resolve():
                    linked.append(str(target))
                    continue
                if target.is_symlink():
                    target.unlink()
                elif target.is_dir():
                    continue  # do not clobber real dirs
            try:
                target.symlink_to(skill_dir.resolve(), target_is_directory=True)
                linked.append(str(target))
            except OSError:
                continue
    return linked
