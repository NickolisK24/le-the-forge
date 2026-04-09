"""
tick_buffs — Time decay pass over all active buffs.

Execution flow per call:
  1. Tick every BuffInstance (reduces remaining_duration, clamped to 0).
  2. Collect buff_ids whose remaining_duration reached 0 (expired).
  3. Return a new dict with expired instances removed.

Permanent buffs (remaining_duration is None) are never ticked or expired.
The input dict is never mutated; iteration is over a snapshot to prevent
modification-during-iteration errors.

Public API:
    tick_buffs(active_buffs, delta_time) -> TickResult
    TickResult.active   — surviving buff dict
    TickResult.expired  — sorted list of expired buff_ids
"""

from __future__ import annotations

from dataclasses import dataclass

from buffs.buff_instance import BuffInstance


@dataclass(slots=True, frozen=True)
class TickResult:
    """Return value of tick_buffs.

    active  — dict of buff_id → BuffInstance for all buffs still running.
    expired — sorted list of buff_ids that reached zero duration this tick.
    """
    active: dict[str, BuffInstance]
    expired: tuple[str, ...]


def tick_buffs(
    active_buffs: dict[str, BuffInstance],
    delta_time: float,
) -> TickResult:
    """Advance all active buffs by *delta_time* seconds.

    Args:
        active_buffs: current buff state, keyed by buff_id.
        delta_time:   elapsed seconds since the last tick (must be >= 0).

    Returns:
        TickResult with the surviving active dict and a sorted tuple of
        expired buff_ids removed this tick.

    Raises:
        ValueError: if delta_time is negative.
    """
    if delta_time < 0:
        raise ValueError(f"delta_time must be >= 0, got {delta_time}")

    active: dict[str, BuffInstance] = {}
    expired: list[str] = []

    # Iterate over a snapshot of items — safe against any external mutation
    # and makes the two-pass semantics (tick then filter) explicit.
    for buff_id, instance in list(active_buffs.items()):
        instance.tick(delta_time)

        if instance.is_expired:
            expired.append(buff_id)
        else:
            active[buff_id] = instance

    return TickResult(active=active, expired=tuple(sorted(expired)))
