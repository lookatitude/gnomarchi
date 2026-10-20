"""Clipboard history CLI (GPaste / wl-clipboard)."""

from __future__ import annotations

import sys

from desktop import clipboard as core


def history(limit: int = 20) -> int:
    try:
        items = core.history(limit=limit)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    for i, text in enumerate(items):
        one = text.replace("\n", " ")[:120]
        print(f"{i}\t{one}")
    return 0


def select(index: int) -> int:
    try:
        text = core.select(index)
    except (FileNotFoundError, RuntimeError, IndexError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


def ui() -> int:
    return int(core.ui())
