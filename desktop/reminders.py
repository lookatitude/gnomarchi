"""Lightweight reminders: JSON store + notify-send via systemd-run / sleep."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from common.paths import state_dir


@dataclass
class Reminder:
    id: str
    text: str
    due_epoch: float
    created_epoch: float
    fired: bool = False


def _path() -> Path:
    return state_dir() / "reminders.json"


def _load() -> list[Reminder]:
    path = _path()
    if not path.is_file():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out: list[Reminder] = []
    for row in raw if isinstance(raw, list) else []:
        try:
            out.append(
                Reminder(
                    id=str(row["id"]),
                    text=str(row["text"]),
                    due_epoch=float(row["due_epoch"]),
                    created_epoch=float(row["created_epoch"]),
                    fired=bool(row.get("fired", False)),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    return out


def _save(items: list[Reminder]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps([asdict(r) for r in items], indent=2) + "\n", encoding="utf-8"
    )


_DURATION = re.compile(
    r"^(?:(?P<h>\d+)h)?(?:(?P<m>\d+)m)?(?:(?P<s>\d+)s)?$", re.IGNORECASE
)


def parse_duration(spec: str) -> float:
    """Parse 10m / 1h30m / 90s into seconds."""
    text = spec.strip().lower()
    if text.isdigit():
        return float(text)
    m = _DURATION.match(text)
    if not m or not any(m.groups()):
        raise ValueError(f"bad duration: {spec} (use 10m, 1h, 90s)")
    hours = int(m.group("h") or 0)
    mins = int(m.group("m") or 0)
    secs = int(m.group("s") or 0)
    total = hours * 3600 + mins * 60 + secs
    if total <= 0:
        raise ValueError(f"duration must be positive: {spec}")
    return float(total)


def add(text: str, *, in_seconds: float | None = None, at_epoch: float | None = None) -> Reminder:
    now = time.time()
    if at_epoch is not None:
        due = float(at_epoch)
    elif in_seconds is not None:
        due = now + float(in_seconds)
    else:
        raise ValueError("provide in_seconds or at_epoch")
    rem = Reminder(
        id=uuid.uuid4().hex[:10],
        text=text.strip(),
        due_epoch=due,
        created_epoch=now,
    )
    items = _load()
    items.append(rem)
    _save(items)
    _schedule(rem)
    return rem


def list_reminders(*, include_fired: bool = False) -> list[Reminder]:
    items = _load()
    if include_fired:
        return sorted(items, key=lambda r: r.due_epoch)
    return sorted([r for r in items if not r.fired], key=lambda r: r.due_epoch)


def clear(*, reminder_id: str | None = None, all_: bool = False) -> int:
    items = _load()
    if all_:
        _save([])
        return len(items)
    if reminder_id is None:
        raise ValueError("provide reminder id or --all")
    kept = [r for r in items if r.id != reminder_id]
    removed = len(items) - len(kept)
    _save(kept)
    return removed


def _schedule(rem: Reminder) -> None:
    delay = max(0, int(rem.due_epoch - time.time()))
    notify = shutil.which("notify-send") or "notify-send"
    body = rem.text.replace("'", r"'\''")
    cmd = f"{notify} 'gnomarchi reminder' '{body}'"
    # Prefer systemd-run user transient timer
    if shutil.which("systemd-run"):
        subprocess.run(
            [
                "systemd-run",
                "--user",
                "--on-active",
                f"{delay}s",
                "--timer-property=AccuracySec=1s",
                "/bin/bash",
                "-lc",
                f"{cmd}; gnomarchi remind mark-fired {rem.id} 2>/dev/null || true",
            ],
            check=False,
            capture_output=True,
        )
        return
    # Fallback: background sleep
    subprocess.Popen(
        ["bash", "-lc", f"sleep {delay}; {cmd}"],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def mark_fired(reminder_id: str) -> bool:
    items = _load()
    found = False
    for r in items:
        if r.id == reminder_id:
            r.fired = True
            found = True
    if found:
        _save(items)
    return found


def fire_due() -> list[Reminder]:
    """Fire any overdue unfired reminders (for poll / timer hooks)."""
    now = time.time()
    fired: list[Reminder] = []
    items = _load()
    notify = shutil.which("notify-send")
    for r in items:
        if r.fired or r.due_epoch > now:
            continue
        if notify:
            subprocess.run([notify, "gnomarchi reminder", r.text], check=False)
        r.fired = True
        fired.append(r)
    if fired:
        _save(items)
    return fired
