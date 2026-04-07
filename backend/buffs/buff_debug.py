"""
buff_debug — Debug export helper for active buff state.

Produces a fully serializable snapshot of all active BuffInstances, keyed by
buff_id.  Designed to be embedded directly inside ResolutionResult.layer_snapshots
alongside the stat pipeline's per-layer dicts.

Each entry contains:
    stacks             — current stack_count
    remaining_duration — seconds left (float) or None for permanent buffs
    source_id          — source identifier, or None if unset
    is_active          — True if the buff's conditions passed this evaluation;
                         always True when no BuffConditionResult is supplied

Usage inside resolution snapshots:
    result.layer_snapshots["buffs"] = export_active_buffs(active_buffs, condition_result)

Public API:
    BuffDebugEntry     — typed dict (TypedDict) for a single buff's debug data
    export_active_buffs(active_buffs, condition_result=None) -> dict[str, BuffDebugEntry]
"""

from __future__ import annotations

from typing import TypedDict

from buffs.buff_instance import BuffInstance
from buffs.buff_condition_evaluator import BuffConditionResult


class BuffDebugEntry(TypedDict):
    """Serializable debug record for one active BuffInstance."""
    stacks: int
    remaining_duration: float | None   # None = permanent
    source_id: str | None
    is_active: bool                    # False when activation_condition failed


def export_active_buffs(
    active_buffs: dict[str, BuffInstance],
    condition_result: BuffConditionResult | None = None,
) -> dict[str, BuffDebugEntry]:
    """Produce a serializable debug snapshot of all active buffs.

    Args:
        active_buffs:     current runtime buff state, keyed by buff_id.
        condition_result: output of evaluate_buff_conditions(); used to set
                          is_active per buff.  If None, all buffs are marked
                          is_active=True (unconditional snapshot mode).

    Returns:
        Dict of buff_id → BuffDebugEntry, ordered by buff_id for stable output.
        All values are JSON-serializable primitives (int, float, str, None, bool).
    """
    eligible_ids: frozenset[str] = (
        frozenset(condition_result.eligible.keys())
        if condition_result is not None
        else frozenset(active_buffs.keys())
    )

    return {
        buff_id: _build_entry(instance, buff_id in eligible_ids)
        for buff_id, instance in sorted(active_buffs.items())
    }


def _build_entry(instance: BuffInstance, is_active: bool) -> BuffDebugEntry:
    return BuffDebugEntry(
        stacks=instance.stack_count,
        remaining_duration=instance.remaining_duration,
        source_id=instance.source,
        is_active=is_active,
    )
