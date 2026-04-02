"""
Encounter Timeline Engine (Step 99).

Controls the time-based flow of encounters by scheduling and activating
discrete events at specified times.

  EventType        — enum of possible event types
  TimelineEvent    — a single scheduled event with start/end time
  EncounterTimeline— ordered list of events; advance time and fire ready ones
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class EventType(enum.Enum):
    SPAWN        = "spawn"
    PHASE_CHANGE = "phase_change"
    DOWNTIME     = "downtime"
    BUFF_APPLY   = "buff_apply"
    CUSTOM       = "custom"


@dataclass
class TimelineEvent:
    """A single scheduled encounter event."""
    event_type:  EventType
    start_time:  float
    end_time:    float = -1.0          # -1 = instantaneous
    payload:     dict  = field(default_factory=dict)
    fired:       bool  = False

    def __post_init__(self) -> None:
        if self.start_time < 0:
            raise ValueError(f"start_time must be >= 0, got {self.start_time}")
        if self.end_time != -1.0 and self.end_time < self.start_time:
            raise ValueError("end_time must be >= start_time")

    @property
    def is_instantaneous(self) -> bool:
        return self.end_time == -1.0

    @property
    def duration(self) -> float:
        if self.is_instantaneous:
            return 0.0
        return self.end_time - self.start_time


class EncounterTimeline:
    """
    Ordered collection of TimelineEvents.

    advance(time) returns all events whose start_time <= time and
    that have not yet been fired. Events are marked fired on retrieval.
    """

    def __init__(self, events: list[TimelineEvent] | None = None) -> None:
        self._events: list[TimelineEvent] = sorted(
            events or [], key=lambda e: e.start_time
        )
        self._current_time: float = 0.0

    def add_event(self, event: TimelineEvent) -> None:
        """Insert an event maintaining start_time order."""
        self._events.append(event)
        self._events.sort(key=lambda e: e.start_time)

    def advance(self, time: float) -> list[TimelineEvent]:
        """
        Advance to *time* and return all newly-fired events.

        Only events with start_time <= time that have not yet fired
        are returned. Each returned event is marked fired=True.
        """
        if time < self._current_time:
            raise ValueError(
                f"Cannot advance backward: current={self._current_time}, requested={time}"
            )
        self._current_time = time
        ready = [e for e in self._events
                 if not e.fired and e.start_time <= time]
        for e in ready:
            e.fired = True
        return ready

    def pending_events(self) -> list[TimelineEvent]:
        """Return all not-yet-fired events."""
        return [e for e in self._events if not e.fired]

    def reset(self) -> None:
        """Mark all events as unfired and reset current time."""
        for e in self._events:
            e.fired = False
        self._current_time = 0.0

    @property
    def current_time(self) -> float:
        return self._current_time

    @property
    def event_count(self) -> int:
        return len(self._events)
