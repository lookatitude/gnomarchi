"""Reminders CLI store + notify scheduling."""

from __future__ import annotations

from desktop import reminders as core


def add(text: str, due_epoch: int | None = None, in_spec: str | None = None) -> dict:
    if in_spec:
        seconds = core.parse_duration(in_spec)
        rem = core.add(text, in_seconds=seconds)
    elif due_epoch is not None:
        rem = core.add(text, at_epoch=float(due_epoch))
    else:
        rem = core.add(text, in_seconds=60.0)
    return {
        "id": rem.id,
        "text": rem.text,
        "due": int(rem.due_epoch),
        "created": int(rem.created_epoch),
        "done": rem.fired,
    }


def list_items(*, include_done: bool = False) -> list[dict]:
    return [
        {
            "id": r.id,
            "text": r.text,
            "due": int(r.due_epoch),
            "created": int(r.created_epoch),
            "done": r.fired,
        }
        for r in core.list_reminders(include_fired=include_done)
    ]


def due_now() -> list[dict]:
    fired = core.fire_due()
    return [
        {
            "id": r.id,
            "text": r.text,
            "due": int(r.due_epoch),
            "created": int(r.created_epoch),
            "done": r.fired,
        }
        for r in fired
    ]


def complete(item_id: str | int) -> bool:
    return core.mark_fired(str(item_id))


def clear_all() -> int:
    return core.clear(all_=True)
