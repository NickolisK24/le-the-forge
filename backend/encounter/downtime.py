"""
Downtime Simulation System (Step 102).

Simulates forced downtime windows (movement, invulnerability, phase gaps)
during which skills cannot be cast.

  DowntimeWindow   — a named period of unavailability with start/end time
  DowntimeTracker  — accumulates windows; query whether current time is
                     inside any active downtime period
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DowntimeWindow:
    """A single forced-downtime period."""
    name:       str
    start_time: float
    end_time:   float
    reason:     str = ""

    def __post_init__(self) -> None:
        if self.end_time <= self.start_time:
            raise ValueError(
                f"end_time must be > start_time, got [{self.start_time}, {self.end_time}]"
            )

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

    def is_active(self, time: float) -> bool:
        return self.start_time <= time < self.end_time


class DowntimeTracker:
    """
    Tracks downtime windows and reports whether a given time is blocked.

    Usage:
        tracker = DowntimeTracker()
        tracker.add_window(DowntimeWindow("move", 10.0, 13.0))
        tracker.is_downtime(11.0)   # True
        tracker.is_downtime(14.0)   # False
    """

    def __init__(self) -> None:
        self._windows: list[DowntimeWindow] = []

    def add_window(self, window: DowntimeWindow) -> None:
        self._windows.append(window)

    def is_downtime(self, time: float) -> bool:
        """Return True if *time* falls inside any registered window."""
        return any(w.is_active(time) for w in self._windows)

    def active_window(self, time: float) -> DowntimeWindow | None:
        """Return the first active DowntimeWindow at *time*, or None."""
        for w in self._windows:
            if w.is_active(time):
                return w
        return None

    def total_downtime(self) -> float:
        """Sum of all window durations (overlapping windows counted once each)."""
        if not self._windows:
            return 0.0
        # Merge overlapping windows
        sorted_windows = sorted(self._windows, key=lambda w: w.start_time)
        merged_start = sorted_windows[0].start_time
        merged_end   = sorted_windows[0].end_time
        total = 0.0
        for w in sorted_windows[1:]:
            if w.start_time < merged_end:
                merged_end = max(merged_end, w.end_time)
            else:
                total += merged_end - merged_start
                merged_start = w.start_time
                merged_end   = w.end_time
        total += merged_end - merged_start
        return total

    def uptime_fraction(self, fight_duration: float) -> float:
        """Fraction of fight_duration that is NOT downtime (0–1)."""
        if fight_duration <= 0:
            return 0.0
        dt = min(self.total_downtime(), fight_duration)
        return (fight_duration - dt) / fight_duration

    def window_count(self) -> int:
        return len(self._windows)

    def clear(self) -> None:
        self._windows.clear()
