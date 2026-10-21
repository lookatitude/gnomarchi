"""Chromium --app= web apps as user .desktop launchers (Omarchy web-apps)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from common.paths import state_dir

_SAFE = re.compile(r"[^a-zA-Z0-9._-]+")


def _apps_dir() -> Path:
    home = Path.home()
    d = home / ".local" / "share" / "applications"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _registry() -> Path:
    p = state_dir() / "webapps.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load() -> dict[str, dict[str, str]]:
    import json

    path = _registry()
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def _save(data: dict[str, dict[str, str]]) -> None:
    import json

    _registry().write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _slug(name: str) -> str:
    s = _SAFE.sub("-", name.strip().lower()).strip("-")
    return s or "webapp"


def _chromium() -> str:
    for cand in ("chromium", "google-chrome-stable", "google-chrome", "brave"):
        if shutil.which(cand):
            return cand
    return "chromium"


def list_apps() -> list[dict[str, str]]:
    data = _load()
    return [{"id": k, **v} for k, v in sorted(data.items())]


def add(name: str, url: str) -> str:
    if not url.startswith(("http://", "https://")):
        raise ValueError("url must start with http:// or https://")
    sid = _slug(name)
    desktop_id = f"gnomarchi-webapp-{sid}"
    desk = _apps_dir() / f"{desktop_id}.desktop"
    browser = _chromium()
    try:
        from theme.icon_apply import icon_name_for_app, install_app_icons

        install_app_icons()
        icon = icon_name_for_app(name)
    except Exception:
        icon = "web-browser"
    desk.write_text(
        "\n".join(
            [
                "[Desktop Entry]",
                "Type=Application",
                f"Name={name}",
                f"Comment=gnomarchi web app · {url}",
                f"Exec={browser} --app={url}",
                f"Icon={icon}",
                "Terminal=false",
                "Categories=Network;WebBrowser;",
                f"StartupWMClass={sid}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    desk.chmod(0o644)
    data = _load()
    data[sid] = {"name": name, "url": url, "desktop": str(desk)}
    _save(data)
    subprocess.call(["update-desktop-database", str(_apps_dir())], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sid


def remove(app_id: str) -> bool:
    data = _load()
    row = data.pop(app_id, None)
    if row is None:
        # try slug of id
        return False
    desk = Path(row.get("desktop") or "")
    if desk.is_file():
        desk.unlink()
    _save(data)
    return True


def launch(app_id: str) -> int:
    data = _load()
    row = data.get(app_id)
    if not row:
        print(f"error: unknown webapp {app_id}", file=__import__("sys").stderr)
        return 1
    browser = _chromium()
    subprocess.Popen([browser, f"--app={row['url']}"], start_new_session=True)
    return 0


DEFAULTS = (
    ("ChatGPT", "https://chatgpt.com"),
    ("YouTube", "https://www.youtube.com"),
    ("GitHub", "https://github.com"),
)


def seed_defaults() -> list[str]:
    created: list[str] = []
    existing = _load()
    for name, url in DEFAULTS:
        sid = _slug(name)
        if sid in existing:
            continue
        created.append(add(name, url))
    return created
