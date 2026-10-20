"""Screenshot / OCR / QR / screen-record CLI wrappers (Arch + stock GNOME)."""

from __future__ import annotations

import sys

from desktop import capture as core


def shot(*, area: bool = False) -> int:
    try:
        path = core.shot(area=area, interactive=not area)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(path)
    return 0


def ocr() -> int:
    try:
        text = core.ocr()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(text, end="" if text.endswith("\n") else text + "\n")
    return 0


def qr() -> int:
    try:
        text = core.qr()
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(text)
    return 0


def record() -> int:
    try:
        return int(core.record())
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
