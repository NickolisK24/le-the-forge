"""
H7 — Event Trigger System

An EventTrigger fires a callback when a named game event occurs.
The TriggerRegistry manages all registered triggers and dispatches
events in priority order (lower number = fires first).

Supported trigger events:
    on_hit          — a skill lands on a target
    on_crit         — a hit is a critical strike
    on_kill         — target HP drops to 0
    on_buff_expire  — a buff's duration runs out
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Any

VALID_EVENTS = frozenset({"on_hit", "on_crit", "on_kill", "on_buff_expire"})


@dataclass
class EventTrigger:
    """
    A single registered trigger.

    trigger_id  — unique identifier
    event       — one of VALID_EVENTS
    callback    — callable(context: dict) → None
                  context keys depend on the event type
    priority    — lower = fires earlier among same-event triggers
    """
    trigger_id: str
    event:      str
    callback:   Callable[[dict], None]
    priority:   int = 10

    def __post_init__(self) -> None:
        if self.event not in VALID_EVENTS:
            raise ValueError(
                f"Invalid event {self.event!r}. Must be one of: {sorted(VALID_EVENTS)}"
            )
        if self.priority < 1:
            raise ValueError("priority must be >= 1")


class TriggerRegistry:
    """
    Central registry for event triggers.

    register(trigger)          — add a trigger
    unregister(trigger_id)     — remove by id
    fire(event, context)       — dispatch to all triggers registered for event,
                                 in priority order; returns list of fired ids
    """

    def __init__(self) -> None:
        self._triggers: dict[str, EventTrigger] = {}

    def register(self, trigger: EventTrigger) -> None:
        self._triggers[trigger.trigger_id] = trigger

    def unregister(self, trigger_id: str) -> None:
        self._triggers.pop(trigger_id, None)

    def fire(self, event: str, context: dict | None = None) -> list[str]:
        """
        Fire all triggers registered for *event*, sorted by priority.
        Returns the list of trigger_ids that were invoked.
        """
        if event not in VALID_EVENTS:
            raise ValueError(f"Unknown event: {event!r}")
        ctx = context or {}
        matching = sorted(
            (t for t in self._triggers.values() if t.event == event),
            key=lambda t: t.priority,
        )
        fired: list[str] = []
        for trigger in matching:
            trigger.callback(ctx)
            fired.append(trigger.trigger_id)
        return fired

    def triggers_for(self, event: str) -> list[EventTrigger]:
        """Return triggers registered for *event*, sorted by priority."""
        return sorted(
            (t for t in self._triggers.values() if t.event == event),
            key=lambda t: t.priority,
        )

    def clear(self) -> None:
        self._triggers.clear()
