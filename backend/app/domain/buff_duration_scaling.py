"""
Buff Duration Scaling (Step 56).

Applies the ``buff_duration_pct`` stat to extend buff durations.

Formula:
    effective_duration = base_duration * (1 + buff_duration_pct / 100)

Where buff_duration_pct is an additive percentage increase (e.g. 50 = +50%).
Negative values are clamped to 0 (no reduction below base duration).

Public API:
  scale_buff_duration(base_duration, buff_duration_pct) -> float
  apply_buff_duration(buff, stats) -> BuffInstance
      Returns a new BuffInstance with the scaled duration.
"""

from __future__ import annotations

from app.domain.timeline import BuffInstance


def scale_buff_duration(base_duration: float, buff_duration_pct: float) -> float:
    """
    Return the effective buff duration after applying the duration bonus.

        effective = base_duration * (1 + max(0, buff_duration_pct) / 100)

    Raises ValueError if base_duration < 0.
    """
    if base_duration < 0:
        raise ValueError(f"base_duration must be >= 0, got {base_duration}")
    multiplier = 1.0 + max(0.0, buff_duration_pct) / 100.0
    return base_duration * multiplier


def apply_buff_duration(buff: BuffInstance, buff_duration_pct: float) -> BuffInstance:
    """
    Return a new BuffInstance with duration scaled by *buff_duration_pct*.

    All other fields (buff_type, value, source) are preserved.
    """
    scaled = scale_buff_duration(buff.duration, buff_duration_pct)
    return BuffInstance(
        buff_type=buff.buff_type,
        value=buff.value,
        duration=scaled,
        source=buff.source,
    )
