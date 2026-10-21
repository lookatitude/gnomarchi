"""Shared paths for acceptance tests."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CLI = REPO / "bin" / "gnomarchi"
REGISTRY = REPO / "features" / "registry.yaml"
OVERLAY = REPO / "install" / "overlay.sh"
MENU_DEFAULT = REPO / "menu" / "default.jsonc"

ALLOWED_STATUS = frozenset(
    {"native", "port", "adapt", "rebuild", "defer", "triage", "done"}
)
ALLOWED_MATURITY = frozenset({"adapted", "shipped", "proven"})
