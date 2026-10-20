"""Plugin manifest validate / scaffold / list / add / enable."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from plugin.adapters import (
    ALLOWED_RUNTIMES,
    DEFAULT_RUNTIME,
    NON_DEFAULT_RUNTIMES,
    get_adapter,
)
from common.paths import REPO_ROOT, state_dir

REQUIRED_MANIFEST_KEYS = ("id", "name", "version", "runtime", "permissions", "hooks")

# Escalating / system-wide patterns refused in hooks (docs/security/plugin-trust.md).
_HOOK_DENY = re.compile(
    r"(?i)\b(sudo|pkexec|polkit)|"
    r"(^|[\s:=])/etc(/|$)|"
    r"(^|[\s:=])/usr(/|$)|"
    r"pacman\.d/hooks|sudoers|/etc/systemd/system|"
    r"\bpacman\b|\bapt(-get)?\b|\bdnf\b|\brpm\b"
)


def _manifest_path(plugin_dir: Path) -> Path:
    return plugin_dir / "manifest.json"


def _load_manifest(plugin_dir: Path) -> tuple[dict | None, list[str]]:
    path = _manifest_path(plugin_dir)
    if not path.is_file():
        return None, ["missing manifest.json"]
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"manifest.json: {exc}"]
    if not isinstance(manifest, dict):
        return None, ["manifest.json: root must be an object"]
    return manifest, []


def _hook_values(hooks: dict) -> list[str]:
    values: list[str] = []
    for val in hooks.values():
        if isinstance(val, str):
            values.append(val)
        elif isinstance(val, list):
            values.extend(str(v) for v in val)
        elif isinstance(val, dict):
            values.extend(_hook_values(val))
        else:
            values.append(str(val))
    return values


def check_hooks_no_sudo(hooks: dict) -> list[str]:
    errors: list[str] = []
    for raw in _hook_values(hooks):
        if _HOOK_DENY.search(raw):
            errors.append(f"hooks refuse escalating/system action: {raw!r}")
    return errors


def validate_plugin(plugin_dir: str | Path) -> list[str]:
    root = Path(plugin_dir).expanduser().resolve()
    manifest, errors = _load_manifest(root)
    if manifest is None:
        return errors

    for key in REQUIRED_MANIFEST_KEYS:
        if key not in manifest:
            errors.append(f"manifest.{key} required")

    runtime = manifest.get("runtime")
    if runtime is not None and runtime not in ALLOWED_RUNTIMES:
        errors.append(f"unknown runtime {runtime!r}; allowed: {sorted(ALLOWED_RUNTIMES)}")

    if not isinstance(manifest.get("permissions", []), list):
        errors.append("manifest.permissions must be an array")
    hooks = manifest.get("hooks", {})
    if not isinstance(hooks, dict):
        errors.append("manifest.hooks must be an object")
    else:
        errors.extend(check_hooks_no_sudo(hooks))

    if manifest.get("id") and manifest["id"] != root.name:
        errors.append(
            f"manifest.id {manifest['id']!r} must match directory name {root.name!r}"
        )

    if runtime == "gnome-shell-extension":
        if not manifest.get("explicit_shell_extension"):
            errors.append(
                "gnome-shell-extension requires explicit_shell_extension=true "
                "(never default enable path)"
            )

    adapter = get_adapter(runtime) if runtime else None
    if adapter is not None and not errors:
        errors.extend(adapter.validate_artifacts(root, manifest))

    return errors


def summarize_plugin(plugin_dir: str | Path) -> dict[str, object]:
    root = Path(plugin_dir).expanduser().resolve()
    manifest, errors = _load_manifest(root)
    if manifest is None:
        raise ValueError("; ".join(errors))
    return {
        "id": manifest.get("id", root.name),
        "name": manifest.get("name", root.name),
        "runtime": manifest.get("runtime"),
        "permissions": manifest.get("permissions", []),
        "hooks": manifest.get("hooks", {}),
        "source": str(root),
    }


def add_plugin(
    source: str | Path,
    *,
    confirm: bool = False,
    prompt_confirm=None,
    dest_root: str | Path | None = None,
) -> Path:
    """Copy plugin into state after interactive or --confirm approval."""
    src = Path(source).expanduser().resolve()
    if not src.is_dir():
        raise FileNotFoundError(f"plugin source not a directory: {src}")

    summary = summarize_plugin(src)
    print("plugin add summary:")
    print(f"  id:          {summary['id']}")
    print(f"  name:        {summary['name']}")
    print(f"  runtime:     {summary['runtime']}")
    print(f"  permissions: {summary['permissions']}")
    print(f"  hooks:       {summary['hooks']}")
    print(f"  source:      {summary['source']}")

    approved = bool(confirm)
    if not approved:
        ask = prompt_confirm or (lambda: input("Add this plugin? [y/N] ").strip().lower())
        answer = ask()
        approved = answer in ("y", "yes")
    if not approved:
        raise PermissionError("refused: confirm-on-add required (default no)")

    errors = validate_plugin(src)
    if errors:
        raise ValueError("validate failed: " + "; ".join(errors))

    plugin_id = str(summary["id"])
    base = Path(dest_root) if dest_root else state_dir() / "plugins"
    base.mkdir(parents=True, exist_ok=True)
    target = base / plugin_id
    if target.exists():
        raise FileExistsError(f"plugin already installed: {target}")
    shutil.copytree(src, target)
    return target


def enable_plugin(plugin_dir: str | Path) -> str:
    """Validate then invoke adapter enable. Shell extensions need explicit flag."""
    root = Path(plugin_dir).expanduser().resolve()
    errors = validate_plugin(root)
    if errors:
        raise ValueError("validate failed: " + "; ".join(errors))

    manifest, load_errors = _load_manifest(root)
    if manifest is None:
        raise ValueError("; ".join(load_errors))

    runtime = manifest.get("runtime")
    if runtime in NON_DEFAULT_RUNTIMES and not manifest.get("explicit_shell_extension"):
        raise PermissionError(
            "refusing to enable gnome-shell-extension without explicit_shell_extension=true"
        )

    adapter = get_adapter(runtime)
    if adapter is None:
        raise ValueError(f"no enable adapter for runtime {runtime!r}")
    if hasattr(adapter, "enable"):
        return adapter.enable(root, manifest)
    return adapter.enable_stub(root, manifest)


def list_plugins() -> list[dict[str, str]]:
    roots = [
        REPO_ROOT / "plugins" / "first-party",
        REPO_ROOT / "plugin" / "installed",
        state_dir() / "plugins",
    ]
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for root in roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name in seen:
                continue
            manifest = _manifest_path(child)
            if not manifest.is_file():
                continue
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                data = {}
            pid = str(data.get("id") or child.name)
            seen.add(pid)
            out.append(
                {
                    "id": pid,
                    "name": str(data.get("name") or pid),
                    "runtime": str(data.get("runtime") or ""),
                    "path": str(child),
                }
            )
    return out


def scaffold_plugin(
    plugin_id: str,
    runtime: str = DEFAULT_RUNTIME,
    dest_root: str | Path | None = None,
    *,
    explicit_shell_extension: bool = False,
) -> Path:
    if runtime not in ALLOWED_RUNTIMES:
        raise ValueError(f"unknown runtime: {runtime}")
    if runtime in NON_DEFAULT_RUNTIMES and not explicit_shell_extension:
        raise ValueError(
            "refusing to scaffold gnome-shell-extension without "
            "explicit_shell_extension=True"
        )

    template = REPO_ROOT / "templates" / "plugin" / runtime
    if not template.is_dir():
        raise FileNotFoundError(f"missing template for runtime: {runtime}")

    base = Path(dest_root) if dest_root else state_dir() / "plugins"
    target = base / plugin_id
    if target.exists():
        raise FileExistsError(f"plugin already exists: {target}")

    shutil.copytree(template, target)
    manifest_path = target / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["id"] = plugin_id
    manifest["name"] = plugin_id.replace("-", " ").title()
    manifest["runtime"] = runtime
    if runtime == "gnome-shell-extension":
        manifest["explicit_shell_extension"] = True
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    unit = target / "gnomarchi-plugin.service"
    if unit.is_file():
        text = unit.read_text(encoding="utf-8").replace("PLUGIN_ID", plugin_id)
        unit.write_text(text, encoding="utf-8")

    desktop = target / "app.desktop"
    if desktop.is_file():
        text = desktop.read_text(encoding="utf-8").replace("PLUGIN_ID", plugin_id)
        desktop.write_text(text, encoding="utf-8")

    meta = target / "metadata.json"
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        data["uuid"] = f"{plugin_id}@gnomarchi"
        data["name"] = plugin_id
        meta.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    return target


def clone_plugin(plugin_id: str, dest_root: str | Path | None = None) -> Path:
    """Copy a first-party plugin into the user plugins tree for customization."""
    src = REPO_ROOT / "plugins" / "first-party" / plugin_id
    if not src.is_dir():
        raise FileNotFoundError(f"first-party plugin not found: {plugin_id}")
    base = Path(dest_root) if dest_root else state_dir() / "plugins"
    # User-owned id: keep original id in manifest but place under user.$name if collision
    target = base / plugin_id
    if target.exists():
        raise FileExistsError(f"plugin already installed: {target}")
    base.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target)
    return target

