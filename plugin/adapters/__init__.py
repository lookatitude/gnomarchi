"""Runtime adapters. Shell-extension enable requires explicit_shell_extension."""

from plugin.adapters.gnome_shell_extension import GnomeShellExtensionAdapter
from plugin.adapters.menu_module import MenuModuleAdapter
from plugin.adapters.overlay_app import OverlayAppAdapter
from plugin.adapters.status_indicator import StatusIndicatorAdapter
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

DEFAULT_RUNTIME = "overlay-app"
# Scaffold of Shell extensions requires --explicit-shell-extension on CLI.
NON_DEFAULT_RUNTIMES = frozenset({"gnome-shell-extension"})

ADAPTERS = {
    "overlay-app": OverlayAppAdapter,
    "menu-module": MenuModuleAdapter,
    "user-service": UserServiceAdapter,
    "status-indicator": StatusIndicatorAdapter,
    "gnome-shell-extension": GnomeShellExtensionAdapter,
}


def get_adapter(runtime: str):
    cls = ADAPTERS.get(runtime)
    if cls is None:
        return None
    return cls()
