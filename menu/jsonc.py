"""Minimal JSONC loader (// and /* */ comments, trailing commas stripped)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


_TRAILING_COMMA = re.compile(r",(\s*[}\]])")
_LINE_COMMENT = re.compile(r"(^|[^:])//.*?$", re.MULTILINE)
_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)


def strip_jsonc(text: str) -> str:
    text = _BLOCK_COMMENT.sub("", text)
    text = _LINE_COMMENT.sub(r"\1", text)
    text = _TRAILING_COMMA.sub(r"\1", text)
    return text


def load_jsonc(path: str | Path) -> Any:
    raw = Path(path).read_text(encoding="utf-8")
    return json.loads(strip_jsonc(raw))
