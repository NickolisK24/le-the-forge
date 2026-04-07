"""
apply_buff — Pure function for applying a BuffDefinition to an active buff dict.

Handles all four StackBehavior modes deterministically:

    ADD_STACK       — increment stack_count up to definition.max_stacks
    REFRESH_DURATION — reset remaining_duration to definition.duration_seconds
    IGNORE          — leave the existing instance unchanged
    REPLACE         — overwrite with a fresh BuffInstance

No side effects; always returns a new dict (shallow copy with the affected
entry replaced). The input dict is never mutated.

Public API:
    apply_buff(active_buffs, definition, timestamp) -> dict[str, BuffInstance]
"""

from __future__ import annotations

from buffs.buff_definition import BuffDefinition, StackBehavior
from buffs.buff_instance import BuffInstance


def apply_buff(
    active_buffs: dict[str, BuffInstance],
    definition: BuffDefinition,
    timestamp: float,
    source: str | None = None,
) -> dict[str, BuffInstance]:
    """Apply *definition* to *active_buffs* and return the updated dict.

    Args:
        active_buffs: current active buff state, keyed by buff_id.
        definition:   the buff template to apply.
        timestamp:    monotonic timestamp of the application event.
        source:       optional identifier for what triggered the buff.

    Returns:
        A new dict with the buff entry created or updated according to
        definition.stack_behavior. All other entries are carried over
        unchanged.
    """
    result = dict(active_buffs)
    buff_id = definition.buff_id

    if buff_id in result:
        existing = result[buff_id]
        behavior = definition.stack_behavior

        if behavior is StackBehavior.ADD_STACK:
            new_stacks = min(existing.stack_count + 1, definition.max_stacks)
            updated = BuffInstance(
                definition=existing.definition,
                stack_count=new_stacks,
                applied_timestamp=existing.applied_timestamp,
                source=existing.source,
            )
            # Preserve remaining duration; only stack count changes.
            updated.remaining_duration = existing.remaining_duration
            result[buff_id] = updated

        elif behavior is StackBehavior.REFRESH_DURATION:
            updated = BuffInstance(
                definition=existing.definition,
                stack_count=existing.stack_count,
                applied_timestamp=existing.applied_timestamp,
                source=existing.source,
            )
            # Re-initialize duration from definition (same as a fresh instance).
            updated.remaining_duration = definition.duration_seconds
            result[buff_id] = updated

        elif behavior is StackBehavior.IGNORE:
            pass  # Return active_buffs unchanged.

        elif behavior is StackBehavior.REPLACE:
            result[buff_id] = BuffInstance(
                definition=definition,
                stack_count=1,
                applied_timestamp=timestamp,
                source=source,
            )

    else:
        result[buff_id] = BuffInstance(
            definition=definition,
            stack_count=1,
            applied_timestamp=timestamp,
            source=source,
        )

    return result
