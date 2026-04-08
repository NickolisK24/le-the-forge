"""
stack_resolver — Strict StackBehavior resolution for BuffInstance re-application.

Single responsibility: given an existing BuffInstance and its BuffDefinition,
return a new BuffInstance with the correct stacks and duration applied.

Invariants enforced on every path:
  - stack_count is always clamped to [1, definition.max_stacks]
  - remaining_duration is never set above definition.duration_seconds
  - remaining_duration is never negative (guaranteed by BuffInstance.tick)
  - Input instances are never mutated; always returns a new BuffInstance

Supported behaviors (StackBehavior enum):
  ADD_STACK        — +1 stack, hard-clamped to max_stacks; duration unchanged
  REFRESH_DURATION — duration reset to definition.duration_seconds; stacks unchanged
  IGNORE           — existing instance returned as-is (no copy needed)
  REPLACE          — fresh instance at stack_count=1 with new timestamp/source

Public API:
    resolve_stack(existing, definition, timestamp, source) -> BuffInstance
"""

from __future__ import annotations

from buffs.buff_definition import BuffDefinition, StackBehavior
from buffs.buff_instance import BuffInstance


def resolve_stack(
    existing: BuffInstance,
    definition: BuffDefinition,
    timestamp: float,
    source: str | None = None,
) -> BuffInstance:
    """Apply *definition*'s stack_behavior to *existing* and return the result.

    Args:
        existing:   the currently active BuffInstance for this buff_id.
        definition: the buff template being re-applied (must match existing.definition.buff_id).
        timestamp:  monotonic timestamp of the re-application event.
        source:     optional source identifier for REPLACE (ignored by other modes).

    Returns:
        A new (or the same, for IGNORE) BuffInstance reflecting the resolved state.

    Raises:
        ValueError: if definition.buff_id does not match existing.definition.buff_id.
    """
    if existing.definition.buff_id != definition.buff_id:
        raise ValueError(
            f"buff_id mismatch: existing={existing.definition.buff_id!r}, "
            f"definition={definition.buff_id!r}"
        )

    behavior = definition.stack_behavior

    if behavior is StackBehavior.ADD_STACK:
        return _resolve_add_stack(existing, definition)

    if behavior is StackBehavior.REFRESH_DURATION:
        return _resolve_refresh_duration(existing, definition)

    if behavior is StackBehavior.IGNORE:
        return existing  # Explicitly documented: no change.

    if behavior is StackBehavior.REPLACE:
        return _resolve_replace(definition, timestamp, source)

    # Exhaustive guard — unreachable if StackBehavior enum is extended without
    # updating this module. Raises rather than silently falling through.
    raise NotImplementedError(f"Unhandled StackBehavior: {behavior!r}")


# ---------------------------------------------------------------------------
# Per-behavior helpers
# ---------------------------------------------------------------------------

def _resolve_add_stack(existing: BuffInstance, definition: BuffDefinition) -> BuffInstance:
    """Increment stack count by 1, hard-clamped to definition.max_stacks.

    Duration is intentionally preserved — the existing timer keeps running.
    """
    # Clamp existing stacks first in case the instance was created before
    # max_stacks was tightened (defensive against stale state).
    current = min(existing.stack_count, definition.max_stacks)
    new_stacks = min(current + 1, definition.max_stacks)

    updated = BuffInstance(
        definition=existing.definition,
        stack_count=new_stacks,
        applied_timestamp=existing.applied_timestamp,
        source=existing.source,
    )
    # Bypass __post_init__ default; carry the live remaining_duration forward.
    updated.remaining_duration = existing.remaining_duration
    return updated


def _resolve_refresh_duration(
    existing: BuffInstance, definition: BuffDefinition
) -> BuffInstance:
    """Reset duration to definition.duration_seconds; preserve stack count.

    Stack count is re-clamped to max_stacks so a tightened definition cannot
    leave the instance in an over-stacked state after a refresh.
    """
    clamped_stacks = min(existing.stack_count, definition.max_stacks)

    updated = BuffInstance(
        definition=existing.definition,
        stack_count=clamped_stacks,
        applied_timestamp=existing.applied_timestamp,
        source=existing.source,
    )
    # __post_init__ sets remaining_duration = definition.duration_seconds, which
    # is exactly what we want — no manual override needed.
    return updated


def _resolve_replace(
    definition: BuffDefinition,
    timestamp: float,
    source: str | None,
) -> BuffInstance:
    """Overwrite with a completely fresh instance at stack_count=1."""
    return BuffInstance(
        definition=definition,
        stack_count=1,
        applied_timestamp=timestamp,
        source=source,
    )
