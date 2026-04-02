"""
Status Effect Interaction System (Step 7).

Models how concurrent ailments modify each other's effectiveness.
Last Epoch interaction rules implemented here:

  Shock        — increases all damage taken by the enemy (additive % per stack).
                 All other ailment types benefit from shock automatically.
  Frostbite    — increases cold damage taken and amplifies chill effectiveness.
  Ignite + Shock — shock stacks amplify ignite damage further (multiplicative bonus).

Public API:
  InteractionResult  — describes a single interaction event
  evaluate_status_interactions(active) -> list[InteractionResult]
      Inspect active ailment list, return all applicable interaction bonuses.

  apply_interaction_multiplier(base_damage, active, ailment_type) -> float
      Compute the damage after all interactions are applied for one ailment type.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.ailments import AilmentInstance, AilmentType


# ---------------------------------------------------------------------------
# Interaction constants (Last Epoch tuning values)
# ---------------------------------------------------------------------------

# Each shock stack increases damage taken by this flat additive percentage
SHOCK_DAMAGE_BONUS_PER_STACK: float = 20.0  # %

# Frostbite increases cold damage taken by this flat additive percentage
FROSTBITE_COLD_DAMAGE_BONUS: float = 25.0  # %

# Additional multiplicative bonus applied to ignite when the target is also shocked
IGNITE_SHOCK_MULTIPLIER_BONUS: float = 0.10  # 10% more ignite damage per shock stack


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InteractionResult:
    """
    A single evaluated interaction between co-active status effects.

    source        — the ailment type that triggers the interaction
    target        — the ailment type (or None = all types) that benefits
    bonus_percent — additive percentage bonus to target damage (can be 0)
    multiplier    — multiplicative factor applied on top (1.0 = no bonus)
    description   — human-readable explanation
    """
    source:        AilmentType
    target:        AilmentType | None   # None = affects all damage types
    bonus_percent: float
    multiplier:    float
    description:   str


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def evaluate_status_interactions(
    active: list[AilmentInstance],
) -> list[InteractionResult]:
    """
    Inspect the active ailment list and return all applicable interactions.

    Each interaction is independent; callers sum or multiply as appropriate.
    An empty active list returns an empty result.
    """
    results: list[InteractionResult] = []

    # Count stacks per type
    counts: dict[AilmentType, int] = {}
    for inst in active:
        counts[inst.ailment_type] = counts.get(inst.ailment_type, 0) + inst.stack_count

    shock_stacks   = counts.get(AilmentType.SHOCK, 0)
    frost_stacks   = counts.get(AilmentType.FROSTBITE, 0)
    ignite_present = AilmentType.IGNITE in counts

    # Shock: increases all damage taken
    if shock_stacks > 0:
        bonus = shock_stacks * SHOCK_DAMAGE_BONUS_PER_STACK
        results.append(InteractionResult(
            source=AilmentType.SHOCK,
            target=None,
            bonus_percent=bonus,
            multiplier=1.0,
            description=(
                f"Shock ({shock_stacks} stack{'s' if shock_stacks != 1 else ''}) "
                f"+{bonus:.0f}% damage taken"
            ),
        ))

    # Frostbite: amplifies cold damage taken
    if frost_stacks > 0:
        bonus = frost_stacks * FROSTBITE_COLD_DAMAGE_BONUS
        results.append(InteractionResult(
            source=AilmentType.FROSTBITE,
            target=AilmentType.FROSTBITE,   # frostbite amplifies its own cold damage
            bonus_percent=bonus,
            multiplier=1.0,
            description=(
                f"Frostbite ({frost_stacks} stack{'s' if frost_stacks != 1 else ''}) "
                f"+{bonus:.0f}% cold damage taken"
            ),
        ))

    # Ignite + Shock synergy: additional multiplicative ignite bonus
    if ignite_present and shock_stacks > 0:
        mult = 1.0 + shock_stacks * IGNITE_SHOCK_MULTIPLIER_BONUS
        results.append(InteractionResult(
            source=AilmentType.SHOCK,
            target=AilmentType.IGNITE,
            bonus_percent=0.0,
            multiplier=mult,
            description=(
                f"Shock × Ignite synergy ({shock_stacks} shock stack{'s' if shock_stacks != 1 else ''}) "
                f"×{mult:.2f} ignite damage"
            ),
        ))

    return results


# ---------------------------------------------------------------------------
# Application helper
# ---------------------------------------------------------------------------

def apply_interaction_multiplier(
    base_damage: float,
    active: list[AilmentInstance],
    ailment_type: AilmentType,
) -> float:
    """
    Return ``base_damage`` after all applicable interaction bonuses are applied
    for the given ``ailment_type``.

    Additive percent bonuses (e.g. shock) are summed first, then multiplied:
        damage = base_damage × (1 + sum(bonus_percent)/100) × product(multipliers)

    Only interactions with target == ailment_type OR target == None are applied.
    """
    interactions = evaluate_status_interactions(active)

    additive_bonus = 0.0
    multiplicative = 1.0

    for result in interactions:
        if result.target is None or result.target is ailment_type:
            additive_bonus += result.bonus_percent
            multiplicative *= result.multiplier

    return base_damage * (1.0 + additive_bonus / 100.0) * multiplicative
