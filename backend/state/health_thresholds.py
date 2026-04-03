"""
H10 — Health Threshold Logic

HealthThresholdTracker monitors a health value (player or target) across
simulation ticks and fires callbacks the first time a threshold is crossed
downward (or upward, for recovery checks).

Thresholds are expressed as fractions (0.0–1.0). Each threshold fires at
most once per simulation unless reset() is called.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass
class HealthThreshold:
    """
    threshold_pct   — the HP fraction at which this fires (e.g. 0.5 = 50 %)
    direction       — "below" fires when HP falls under the threshold;
                      "above" fires when HP rises above it
    callback        — callable(threshold_pct: float, actual_pct: float) → None
    fired           — True once the threshold has triggered; prevents re-firing
    """
    threshold_pct: float
    direction:     str = "below"
    callback:      Callable[[float, float], None] = field(repr=False, default=lambda *_: None)
    fired:         bool = field(default=False, init=False)

    def __post_init__(self) -> None:
        if not (0.0 <= self.threshold_pct <= 1.0):
            raise ValueError("threshold_pct must be 0.0–1.0")
        if self.direction not in ("below", "above"):
            raise ValueError("direction must be 'below' or 'above'")


class HealthThresholdTracker:
    """
    Tracks health transitions and fires thresholds exactly once.

    Usage::
        tracker = HealthThresholdTracker()
        tracker.add_threshold(HealthThreshold(0.5, "below", on_half_health))
        tracker.update(current_pct=0.45)   # fires on_half_health once
        tracker.update(current_pct=0.30)   # already fired — no-op
    """

    def __init__(self) -> None:
        self._thresholds: list[HealthThreshold] = []

    def add_threshold(self, threshold: HealthThreshold) -> None:
        self._thresholds.append(threshold)

    def update(self, current_pct: float) -> list[float]:
        """
        Check all un-fired thresholds against *current_pct*.
        Fires and marks any that are crossed.
        Returns list of threshold_pct values that fired this update.
        """
        if not (0.0 <= current_pct <= 1.0):
            raise ValueError("current_pct must be 0.0–1.0")
        fired: list[float] = []
        for t in self._thresholds:
            if t.fired:
                continue
            crossed = (
                (t.direction == "below" and current_pct <= t.threshold_pct) or
                (t.direction == "above" and current_pct >= t.threshold_pct)
            )
            if crossed:
                t.callback(t.threshold_pct, current_pct)
                t.fired = True
                fired.append(t.threshold_pct)
        return fired

    def reset(self) -> None:
        """Allow all thresholds to fire again (e.g. new fight)."""
        for t in self._thresholds:
            t.fired = False

    def all_fired(self) -> bool:
        return all(t.fired for t in self._thresholds)
