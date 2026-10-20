"""gnomarchi command palette (GTK4/libadwaita when available)."""

from menu.jsonc import load_jsonc
from menu.palette import HAS_GTK, main, open_menu

__all__ = ["HAS_GTK", "load_jsonc", "main", "open_menu"]
