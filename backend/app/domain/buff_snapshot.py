"""
Snapshot vs Dynamic Buff Handling (Step 69).

Controls whether a buff's value is locked at the moment it is applied
(snapshot) or re-evaluated each tick from the current stat pool (dynamic).

  SNAPSHOT — value captured once when the buff is created; stat changes
             afterwards have no effect on this buff instance. Used for
             ailment damage (DoT damage is locked to the hit that applied it).

  DYNAMIC  — value re-read from the stat pool each tick; benefits from
             stats added/removed during the fight. Used for speed buffs,
             resistance auras, etc.

  SnapshotBuff  — a buff whose value was locked at application time
  DynamicBuff   — a buff resolved against a live stat accessor each tick
  resolve_buff_value(buff, stat_accessor) -> float
      Returns the current effective value for any buff type.

Public API:
    BuffResolutionMode  — enum: SNAPSHOT | DYNAMIC
    SnapshotBuff(buff_type, value, duration, source, mode=SNAPSHOT)
    DynamicBuff(buff_type, stat_field, duration, source, mode=DYNAMIC)
    resolve_buff_value(buff, stat_accessor=None) -> float
"""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable

from app.domain.timeline import BuffType


class BuffResolutionMode(enum.Enum):
    SNAPSHOT = "snapshot"
    DYNAMIC  = "dynamic"


@dataclass(frozen=True)
class SnapshotBuff:
    """
    A buff whose value is locked at application time.

    Used for DoT damage: the damage-per-tick is determined when the
    ailment is applied and does not change if stats change later.
    """
    buff_type: BuffType
    value:     float
    duration:  float
    source:    str = ""
    mode:      BuffResolutionMode = BuffResolutionMode.SNAPSHOT

    def __post_init__(self) -> None:
        if self.duration < 0:
            raise ValueError(f"duration must be >= 0, got {self.duration}")


@dataclass(frozen=True)
class DynamicBuff:
    """
    A buff whose value is re-read from the stat pool each tick.

    stat_field — name of the stat field on BuildStats to read (e.g. "cast_speed")
    Used for auras, persistent speed bonuses, resistance buffs, etc.
    """
    buff_type:  BuffType
    stat_field: str
    duration:   float
    source:     str = ""
    mode:       BuffResolutionMode = BuffResolutionMode.DYNAMIC

    def __post_init__(self) -> None:
        if self.duration < 0:
            raise ValueError(f"duration must be >= 0, got {self.duration}")
        if not self.stat_field:
            raise ValueError("stat_field must not be empty")


# Type alias for stat accessors
StatAccessor = Callable[[str], float]


def resolve_buff_value(
    buff: SnapshotBuff | DynamicBuff,
    stat_accessor: StatAccessor | None = None,
) -> float:
    """
    Return the current effective value of *buff*.

    - SnapshotBuff: returns buff.value directly (locked at application time)
    - DynamicBuff:  calls stat_accessor(buff.stat_field); returns 0.0 if
                    stat_accessor is None or field is absent

    Raises TypeError for unknown buff types.
    """
    if isinstance(buff, SnapshotBuff):
        return buff.value
    if isinstance(buff, DynamicBuff):
        if stat_accessor is None:
            return 0.0
        try:
            return float(stat_accessor(buff.stat_field))
        except (AttributeError, KeyError, TypeError):
            return 0.0
    raise TypeError(f"Unknown buff type: {type(buff)}")


def snapshot_from_stats(
    buff_type: BuffType,
    stat_accessor: StatAccessor,
    stat_field: str,
    duration: float,
    source: str = "",
) -> SnapshotBuff:
    """
    Capture the current stat value and return a SnapshotBuff locked to it.

    Convenience factory: reads the stat now and freezes it into the buff.
    """
    value = float(stat_accessor(stat_field))
    return SnapshotBuff(buff_type=buff_type, value=value, duration=duration, source=source)
