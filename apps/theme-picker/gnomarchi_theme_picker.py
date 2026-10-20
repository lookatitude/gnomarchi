#!/usr/bin/env python3
"""CLI-backed theme picker. Applies packs via `gnomarchi theme set <id>`.

D7: copy never claims official Omarchy affiliation. If a pack's theme.toml
provenance notes Omarchy-derived MIT config, the list line may say
"inspired by Omarchy palettes"; shipped default packs are original-inspired.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def _run(argv: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        argv,
        check=check,
        text=True,
        capture_output=True,
    )


def resolve_gnomarchi() -> list[str]:
    """Return argv prefix for the gnomarchi CLI."""
    found = shutil.which("gnomarchi")
    if found:
        return [found]
    # Repo checkout: bin/gnomarchi next to apps/
    repo_bin = Path(__file__).resolve().parents[2] / "bin" / "gnomarchi"
    if repo_bin.is_file():
        return [str(repo_bin)]
    return ["gnomarchi"]


def list_via_cli(prefix: list[str]) -> list[dict[str, str]] | None:
    for extra in (["--json"], []):
        proc = _run([*prefix, "theme", "list", *extra])
        if proc.returncode != 0:
            continue
        text = (proc.stdout or "").strip()
        if not text:
            continue
        if extra == ["--json"] or text.startswith("["):
            try:
                data = json.loads(text)
                if isinstance(data, list):
                    return [
                        {
                            "id": str(item.get("id", "")),
                            "name": str(item.get("name") or item.get("id", "")),
                            "note": str(item.get("note") or ""),
                        }
                        for item in data
                        if isinstance(item, dict) and item.get("id")
                    ]
            except json.JSONDecodeError:
                pass
        # Plain lines: "id\tname" or "id"
        rows: list[dict[str, str]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t") if "\t" in line else line.split(None, 1)
            tid = parts[0]
            name = parts[1] if len(parts) > 1 else tid
            rows.append({"id": tid, "name": name, "note": ""})
        if rows:
            return rows
    return None


def list_via_engine() -> list[dict[str, str]]:
    """Fallback when CLI is missing: import in-repo theme.engine."""
    repo = Path(__file__).resolve().parents[2]
    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    from theme.engine import list_themes  # noqa: WPS433

    out: list[dict[str, str]] = []
    for item in list_themes():
        note = ""
        pack = Path(item["path"])
        toml = pack / "theme.toml"
        if toml.is_file() and "omarchy" in toml.read_text(encoding="utf-8").casefold():
            note = "inspired by Omarchy palettes"
        out.append({"id": item["id"], "name": item["name"], "note": note})
    return out


def set_via_cli(prefix: list[str], theme_id: str) -> int:
    proc = _run([*prefix, "theme", "set", theme_id])
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    if proc.returncode == 0:
        return 0
    # Fallback: engine when CLI absent
    if prefix == ["gnomarchi"] and shutil.which("gnomarchi") is None:
        repo = Path(__file__).resolve().parents[2]
        if str(repo) not in sys.path:
            sys.path.insert(0, str(repo))
        from theme.engine import set_theme  # noqa: WPS433

        try:
            path = set_theme(theme_id)
        except (FileNotFoundError, ValueError) as exc:
            print(exc, file=sys.stderr)
            return 1
        print(f"active theme → {path}")
        return 0
    return proc.returncode or 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Pick a gnomarchi theme pack and apply it via gnomarchi theme set"
    )
    parser.add_argument("theme_id", nargs="?", help="Apply this id non-interactively")
    parser.add_argument(
        "--list",
        action="store_true",
        help="List packs and exit",
    )
    args = parser.parse_args(argv)

    prefix = resolve_gnomarchi()
    themes = list_via_cli(prefix)
    used_cli_list = themes is not None
    if themes is None:
        try:
            themes = list_via_engine()
        except Exception as exc:  # noqa: BLE001 — surface import/path errors
            print(f"cannot list themes: {exc}", file=sys.stderr)
            return 1

    if args.list or args.theme_id is None:
        source = "gnomarchi theme list" if used_cli_list else "theme.engine (CLI missing)"
        print(f"# themes ({source})")
        for i, t in enumerate(themes, start=1):
            note = f"  — {t['note']}" if t.get("note") else ""
            print(f"  {i:2d}. {t['id']}\t{t['name']}{note}")
        if args.list:
            return 0
        if not themes:
            print("no theme packs found", file=sys.stderr)
            return 1
        print()
        print("Enter number or theme id (empty = quit): ", end="", flush=True)
        try:
            choice = sys.stdin.readline().strip()
        except KeyboardInterrupt:
            print()
            return 130
        if not choice:
            return 0
        if choice.isdigit():
            idx = int(choice)
            if idx < 1 or idx > len(themes):
                print("out of range", file=sys.stderr)
                return 1
            theme_id = themes[idx - 1]["id"]
        else:
            theme_id = choice
    else:
        theme_id = args.theme_id

    return set_via_cli(prefix, theme_id)


if __name__ == "__main__":
    raise SystemExit(main())
