"""
Status Duration Scaling (Step 59).

Applies the ``ailment_duration_pct`` stat to extend the duration of
applied ailments (bleed, ignite, poison, shock, etc.).

Formula:
    effective_duration = base_duration * (1 + ailment_duration_pct / 100)

Where ailment_duration_pct is an additive percentage increase (e.g. 50 = +50%).
Negative values are clamped to 0 (no reduction below base duration).

Public API:
  scale_ailment_duration(base_duration, ailment_duration_pct) -> float
      Pure function; returns scaled duration for any ailment type.
"""

from __future__ import annotations


def scale_ailment_duration(base_duration: float, ailment_duration_pct: float) -> float:
    """
    Return the effective ailment duration after applying the duration bonus.

        effective = base_duration * (1 + max(0, ailment_duration_pct) / 100)

    Raises ValueError if base_duration < 0.
    """
    if base_duration < 0:
        raise ValueError(f"base_duration must be >= 0, got {base_duration}")
    multiplier = 1.0 + max(0.0, ailment_duration_pct) / 100.0
    return base_duration * multiplier
