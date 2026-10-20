"""Runtime adapter stubs. Shell-extension is never the default enable path."""

from plugin.adapters.menu_module import MenuModuleAdapter
from plugin.adapters.overlay_app import OverlayAppAdapter
from plugin.adapters.user_service import UserServiceAdapter

ALLOWED_RUNTIMES = frozenset(
    {
        "overlay-app",
        "menu-module",
        "user-service",
        "status-indicator",
        "gnome-shell-extension",
    }
)

# Default scaffold / enable path never picks Shell extensions (D2 / P7).
DEFAULT_RUNTIME = "overlay-app"
NON_DEFAULT_RUNTIMES = frozenset({"gnome-shell-extension"})

ADAPTERS = {
    "overlay-app": OverlayAppAdapter,
    "menu-module": MenuModuleAdapter,
    "user-service": UserServiceAdapter,
}


def get_adapter(runtime: str):
    cls = ADAPTERS.get(runtime)
    if cls is None:
        return None
    return cls()
