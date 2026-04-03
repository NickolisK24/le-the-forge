"""
H11 — Time Window Conditions

A TimeWindow is a half-open interval [start, end) on the simulation
clock. Conditions can reference a window to restrict their activation
to specific fight phases.

TimeWindowTracker manages a set of named windows and can answer whether
a given time falls inside any window, or check a specific one.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeWindow:
    """
    A named time interval [start, end) in seconds.

    window_id — unique name (e.g. "opener", "burn_phase")
    start     — inclusive start time (>= 0)
    end       — exclusive end time (> start); None = open-ended
    """
    window_id: str
    start:     float
    end:       float | None = None

    def __post_init__(self) -> None:
        if self.start < 0:
            raise ValueError("start must be >= 0")
        if self.end is not None and self.end <= self.start:
            raise ValueError("end must be > start")

    def is_active(self, now: float) -> bool:
        """True when *now* falls within [start, end)."""
        if now < self.start:
            return False
        if self.end is None:
            return True
        return now < self.end

    @property
    def duration(self) -> float | None:
        """Length of the window in seconds, or None if open-ended."""
        if self.end is None:
            return None
        return self.end - self.start

    def to_dict(self) -> dict:
        return {"window_id": self.window_id, "start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, d: dict) -> "TimeWindow":
        return cls(window_id=d["window_id"], start=d["start"], end=d.get("end"))


class TimeWindowTracker:
    """
    Manages a collection of TimeWindow objects.

    register(window)                — add a window
    is_any_active(now)              — True when now falls in at least one window
    is_window_active(id, now)       — True when the named window is active
    active_windows(now)             — list of active window_ids
    """

    def __init__(self) -> None:
        self._windows: dict[str, TimeWindow] = {}

    def register(self, window: TimeWindow) -> None:
        self._windows[window.window_id] = window

    def is_window_active(self, window_id: str, now: float) -> bool:
        w = self._windows.get(window_id)
        return w.is_active(now) if w else False

    def is_any_active(self, now: float) -> bool:
        return any(w.is_active(now) for w in self._windows.values())

    def active_windows(self, now: float) -> list[str]:
        return sorted(w.window_id for w in self._windows.values() if w.is_active(now))

    def overlapping_at(self, now: float) -> list[TimeWindow]:
        return [w for w in self._windows.values() if w.is_active(now)]
