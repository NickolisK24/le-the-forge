"""
apply_buff — Pure function for applying a BuffDefinition to an active buff dict.

Delegates all stacking logic to stack_resolver.resolve_stack, which enforces
strict stack/duration invariants for all four StackBehavior modes.

No side effects; always returns a new dict (shallow copy with the affected
entry replaced). The input dict is never mutated.

Public API:
    apply_buff(active_buffs, definition, timestamp, source) -> dict[str, BuffInstance]
"""

from __future__ import annotations

from buffs.buff_definition import BuffDefinition
from buffs.buff_instance import BuffInstance
from buffs.stack_resolver import resolve_stack


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
        result[buff_id] = resolve_stack(result[buff_id], definition, timestamp, source)
    else:
        result[buff_id] = BuffInstance(
            definition=definition,
            stack_count=1,
            applied_timestamp=timestamp,
            source=source,
        )

    return result
