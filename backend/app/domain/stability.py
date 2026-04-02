"""
Long-Fight Stability Hardening (Step 70).

Provides utilities that prevent numerical drift and out-of-bounds values
during long-duration simulations (300s+). Floating-point accumulation
errors can cause timers to drift, resources to go slightly negative, or
damage to compound in unexpected ways.

Utilities:
  clamp(value, lo, hi)          — generic clamp
  safe_subtract(a, b)           — a - b, floored at 0 (no negatives)
  safe_tick(remaining, delta)   — advance a timer, floor at 0
  accumulate(total, amount)     — add damage, reject negative additions
  normalise_pct(value)          — clamp a percentage to [0, 100]
  stable_divide(numerator, denominator, fallback=0.0) — safe division
  SimStats                      — running stats tracker for a simulation
      tracks min/max/sum/count; reports mean and drift detection
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Pure utility functions
# ---------------------------------------------------------------------------

def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* to [lo, hi]. Raises ValueError if lo > hi."""
    if lo > hi:
        raise ValueError(f"lo ({lo}) must be <= hi ({hi})")
    return max(lo, min(hi, value))


def safe_subtract(a: float, b: float) -> float:
    """Return max(0, a - b). Prevents floating-point underflow below zero."""
    return max(0.0, a - b)


def safe_tick(remaining: float, delta: float) -> float:
    """
    Decrement *remaining* by *delta*, floored at 0.

    Equivalent to safe_subtract but named for timer contexts.
    Raises ValueError if delta < 0.
    """
    if delta < 0:
        raise ValueError(f"delta must be >= 0, got {delta}")
    return max(0.0, remaining - delta)


def accumulate(total: float, amount: float) -> float:
    """
    Add *amount* to *total*. Rejects negative amounts (returns total unchanged).

    Prevents accidental negative contributions from corrupting running totals.
    """
    if amount < 0:
        return total
    return total + amount


def normalise_pct(value: float) -> float:
    """Clamp *value* to [0.0, 100.0]."""
    return clamp(value, 0.0, 100.0)


def stable_divide(numerator: float, denominator: float, fallback: float = 0.0) -> float:
    """
    Return numerator / denominator, or *fallback* if denominator is zero
    or very close to zero (abs < 1e-12).
    """
    if abs(denominator) < 1e-12:
        return fallback
    return numerator / denominator


# ---------------------------------------------------------------------------
# SimStats — running statistics tracker
# ---------------------------------------------------------------------------

@dataclass
class SimStats:
    """
    Accumulates per-tick damage values and detects unusual drift.

    Usage::

        stats = SimStats()
        for tick_damage in tick_values:
            stats.record(tick_damage)
        print(stats.mean, stats.max_value)
    """

    _count: int   = field(default=0, init=False, repr=False)
    _total: float = field(default=0.0, init=False, repr=False)
    _min:   float = field(default=float("inf"),  init=False, repr=False)
    _max:   float = field(default=float("-inf"), init=False, repr=False)

    def record(self, value: float) -> None:
        """Record one observation. Ignores NaN and negative values."""
        if value != value:   # NaN check
            return
        if value < 0:
            return
        self._count += 1
        self._total += value
        if value < self._min:
            self._min = value
        if value > self._max:
            self._max = value

    @property
    def count(self) -> int:
        return self._count

    @property
    def total(self) -> float:
        return self._total

    @property
    def mean(self) -> float:
        return stable_divide(self._total, float(self._count))

    @property
    def min_value(self) -> float:
        return self._min if self._count > 0 else 0.0

    @property
    def max_value(self) -> float:
        return self._max if self._count > 0 else 0.0

    @property
    def range_value(self) -> float:
        """max - min. 0.0 if no observations."""
        if self._count == 0:
            return 0.0
        return self._max - self._min

    def is_stable(self, max_relative_drift: float = 0.01) -> bool:
        """
        Return True if the range of observed values is within
        *max_relative_drift* of the mean.

        A simulation is considered stable if tick-to-tick variation
        stays within a small percentage of the average — large spikes
        indicate a numerical instability.

        Returns True if count == 0 (no data = trivially stable).
        """
        if self._count == 0:
            return True
        if self.mean == 0.0:
            return self.range_value == 0.0
        return stable_divide(self.range_value, self.mean) <= max_relative_drift
