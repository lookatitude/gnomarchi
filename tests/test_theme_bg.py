"""theme bg cycle generates variants without Omarchy binary walls."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture()
def state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("GNOMARCHI_STATE_DIR", str(tmp_path))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    return tmp_path


def test_bg_next_after_theme_set(state: Path) -> None:
    from theme.engine import set_theme
    from theme.backgrounds import next_background, current_index, VARIANT_COUNT

    set_theme("tokyo-night")
    assert (state / "active-theme").read_text().strip() == "tokyo-night"
    p1 = next_background()
    assert p1.is_file()
    idx1 = current_index()
    assert 0 <= idx1 < VARIANT_COUNT
    p2 = next_background()
    assert p2.is_file()
    assert current_index() == (idx1 + 1) % VARIANT_COUNT
    assert p1.read_bytes() != p2.read_bytes()
