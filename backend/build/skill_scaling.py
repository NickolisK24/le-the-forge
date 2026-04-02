"""
Skill Scaling Hooks (Step 90).

Applies stat-based scaling to skills based on their tags. Tags declare
what stat categories a skill benefits from (e.g. "fire", "spell", "melee").

  ScalingTag       — known tag categories
  scale_skill      — multiplies base_damage by matching stat bonuses
  effective_damage — convenience: returns the fully-scaled damage value

Scaling formula:
    scaled = base_damage * (1 + sum(matching_stat_values) / 100)

This is the standard additive increased damage formula: all matching
stats are summed first, then the total bonus is applied as a multiplier.

Rules:
- Tags are case-insensitive for matching
- Stats not matching any tag are ignored
- Multiple matching tags stack additively (all bonuses summed together)
- base_damage < 0 is accepted but unusual
- Empty stat_pool or empty tags produce no scaling (returns base_damage)
"""

from __future__ import annotations

from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Tag definitions
# ---------------------------------------------------------------------------

class ScalingTag:
    """
    Known tag categories and the stat_key suffix each maps to.

    Each tag matches any stat_key that equals <tag>_damage_pct.
    Additional stat_keys may be passed via extra_stat_keys.
    """
    FIRE        = "fire"
    COLD        = "cold"
    LIGHTNING   = "lightning"
    PHYSICAL    = "physical"
    VOID        = "void"
    NECROTIC    = "necrotic"
    POISON      = "poison"
    SPELL       = "spell"
    MELEE       = "melee"
    BOW         = "bow"
    THROWING    = "throwing"
    ELEMENTAL   = "elemental"
    DOT         = "dot"

    @staticmethod
    def stat_key(tag: str) -> str:
        """Return the primary stat_key for a given tag: '<tag>_damage_pct'."""
        return f"{tag.lower()}_damage_pct"


# ---------------------------------------------------------------------------
# Core scaling function
# ---------------------------------------------------------------------------

def scale_skill(
    base_damage: float,
    tags: list[str],
    stat_pool: dict[str, float],
) -> float:
    """
    Scale *base_damage* using bonuses from *stat_pool* that match *tags*.

    For each tag, the corresponding stat_key ('<tag>_damage_pct') is looked up
    in stat_pool. All matching values are summed additively, then applied once:

        scaled = base_damage * (1 + total_bonus / 100)

    Tags without a matching entry in stat_pool contribute 0.

    Args:
        base_damage  — raw damage before scaling
        tags         — list of tag strings (e.g. ["fire", "spell"])
        stat_pool    — flat stat dict (from passive + gear aggregation)

    Returns:
        Scaled damage value.
    """
    if not tags or not stat_pool:
        return base_damage

    total_bonus = 0.0
    for tag in tags:
        key = ScalingTag.stat_key(tag)
        total_bonus += stat_pool.get(key, 0.0)

    return base_damage * (1.0 + total_bonus / 100.0)


def effective_damage(
    base_damage: float,
    tags: list[str],
    stat_pool: dict[str, float],
    extra_flat: float = 0.0,
) -> float:
    """
    Return final damage after tag-based scaling plus any flat addition.

        result = scale_skill(base_damage + extra_flat, tags, stat_pool)

    extra_flat is added to base_damage before scaling (flat added damage).
    """
    return scale_skill(base_damage + extra_flat, tags, stat_pool)
