"""
Ailment stacking logic — stack limits and total damage calculation.

Builds on ailments.py (individual instances) to add:
  - STACK_LIMITS         — per-type maximum concurrent stacks
  - enforce_stack_limit()— trim oldest stacks when cap is exceeded
  - calculate_total_ailment_damage() — expected DPS across all active stacks
"""

from __future__ import annotations

from app.domain.ailments import AilmentInstance, AilmentType


# ---------------------------------------------------------------------------
# Stack limits (Last Epoch conventions)
# ---------------------------------------------------------------------------

STACK_LIMITS: dict[AilmentType, int] = {
    AilmentType.BLEED:     8,
    AilmentType.POISON:    8,
    AilmentType.IGNITE:    1,   # only the strongest/most-recent ignite counts
    AilmentType.SHOCK:     1,
    AilmentType.FROSTBITE: 1,
}


# ---------------------------------------------------------------------------
# Stacking helpers
# ---------------------------------------------------------------------------

def enforce_stack_limit(
    active: list[AilmentInstance],
    ailment_type: AilmentType,
) -> list[AilmentInstance]:
    """
    Remove oldest stacks of *ailment_type* until the count is within
    STACK_LIMITS[ailment_type].

    Stacks of other types are untouched.
    Oldest stacks are those earliest in the list (index 0 = first applied).
    """
    limit = STACK_LIMITS[ailment_type]
    same_type = [inst for inst in active if inst.ailment_type is ailment_type]
    other     = [inst for inst in active if inst.ailment_type is not ailment_type]

    # Keep only the most-recent `limit` stacks (trim front)
    trimmed = same_type[max(0, len(same_type) - limit):]
    return other + trimmed


def apply_ailment_with_limit(
    active: list[AilmentInstance],
    ailment_type: AilmentType,
    damage_per_tick: float,
    duration: float,
) -> list[AilmentInstance]:
    """
    Apply a new ailment stack and enforce the stack limit in one call.

    Equivalent to:
        apply_ailment(active, ...) → enforce_stack_limit(...)
    but avoids the caller needing to import both functions.
    """
    from app.domain.ailments import apply_ailment  # local import avoids circularity
    updated = apply_ailment(active, ailment_type, damage_per_tick, duration)
    return enforce_stack_limit(updated, ailment_type)


# ---------------------------------------------------------------------------
# Damage summary
# ---------------------------------------------------------------------------

def calculate_total_ailment_damage(active: list[AilmentInstance]) -> float:
    """
    Return the total expected damage-per-second across all active stacks.

    Each stack contributes damage_per_tick independently; this is the
    instantaneous DPS snapshot (not integrated over remaining duration).
    """
    return sum(inst.damage_per_tick for inst in active)
