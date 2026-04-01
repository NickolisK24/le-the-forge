"""
Damage Type Router — centralized routing from damage type to applicable stat groups.

Answers two questions:
  1. For a hit damage type, which BuildStats _pct fields form its increased pool?
  2. For an ailment type, which BuildStats _pct fields form its increased pool?

Rules:
- Pure data — no logic beyond dict lookup
- No engine imports, no registry access, no Flask context
- Single source of truth: replace ad-hoc frozenset literals scattered across calculators
"""

from __future__ import annotations

import enum


# ---------------------------------------------------------------------------
# DamageType enum
# ---------------------------------------------------------------------------

class DamageType(enum.Enum):
    """All distinct damage types in Last Epoch, including ailments and source types."""

    # Hit damage types
    PHYSICAL  = "physical"
    FIRE      = "fire"
    COLD      = "cold"
    LIGHTNING = "lightning"
    NECROTIC  = "necrotic"
    VOID      = "void"
    POISON    = "poison"

    # Source / delivery types (appear in scaling_stats but are not elemental types)
    SPELL  = "spell"
    MINION = "minion"

    # Ailment types (apply DoT; distinct increased pools from their hit counterparts)
    BLEED  = "bleed"
    IGNITE = "ignite"


# ---------------------------------------------------------------------------
# Elemental meta-set (fire, cold, lightning share elemental_damage_pct)
# ---------------------------------------------------------------------------

ELEMENTAL_TYPES: frozenset[DamageType] = frozenset({
    DamageType.FIRE,
    DamageType.COLD,
    DamageType.LIGHTNING,
})


# ---------------------------------------------------------------------------
# Stat name → DamageType lookup
# ---------------------------------------------------------------------------

# Maps a BuildStats _pct field name to its primary DamageType.
# Meta-stats (elemental_damage_pct, dot_damage_pct, melee_damage_pct, etc.)
# are not primary type indicators and are intentionally omitted.
STAT_TO_TYPE: dict[str, DamageType] = {
    "physical_damage_pct":  DamageType.PHYSICAL,
    "fire_damage_pct":      DamageType.FIRE,
    "cold_damage_pct":      DamageType.COLD,
    "lightning_damage_pct": DamageType.LIGHTNING,
    "necrotic_damage_pct":  DamageType.NECROTIC,
    "void_damage_pct":      DamageType.VOID,
    "poison_damage_pct":    DamageType.POISON,
    "spell_damage_pct":     DamageType.SPELL,
    "minion_damage_pct":    DamageType.MINION,
    "bleed_damage_pct":     DamageType.BLEED,
    "ignite_damage_pct":    DamageType.IGNITE,
}


# ---------------------------------------------------------------------------
# Routing tables
# ---------------------------------------------------------------------------

# Hit damage: for each type, the BuildStats fields that form its increased pool.
# Elemental types include elemental_damage_pct because that bonus applies to all three.
_HIT_INCREASED_STATS: dict[DamageType, frozenset[str]] = {
    DamageType.PHYSICAL:  frozenset({"physical_damage_pct"}),
    DamageType.FIRE:      frozenset({"fire_damage_pct", "elemental_damage_pct"}),
    DamageType.COLD:      frozenset({"cold_damage_pct", "elemental_damage_pct"}),
    DamageType.LIGHTNING: frozenset({"lightning_damage_pct", "elemental_damage_pct"}),
    DamageType.NECROTIC:  frozenset({"necrotic_damage_pct"}),
    DamageType.VOID:      frozenset({"void_damage_pct"}),
    DamageType.POISON:    frozenset({"poison_damage_pct"}),
    DamageType.SPELL:     frozenset({"spell_damage_pct"}),
    DamageType.MINION:    frozenset({"minion_damage_pct"}),
}

# Ailment damage: DoT-specific increased pools.
# POISON as an ailment includes dot_damage_pct and poison_dot_damage_pct
# in addition to the shared poison_damage_pct.
_AILMENT_INCREASED_STATS: dict[DamageType, frozenset[str]] = {
    DamageType.BLEED:  frozenset({"physical_damage_pct", "dot_damage_pct", "bleed_damage_pct"}),
    DamageType.IGNITE: frozenset({"fire_damage_pct", "dot_damage_pct", "ignite_damage_pct"}),
    DamageType.POISON: frozenset({"poison_damage_pct", "dot_damage_pct", "poison_dot_damage_pct"}),
}


# ---------------------------------------------------------------------------
# Routing functions
# ---------------------------------------------------------------------------

def increased_stats_for(damage_type: DamageType) -> frozenset[str]:
    """
    Return the BuildStats field names that form the increased damage pool
    for a hit damage type.

    Raises KeyError for ailment-only types (BLEED, IGNITE); use
    ailment_increased_stats() for those.
    """
    return _HIT_INCREASED_STATS[damage_type]


def ailment_increased_stats(damage_type: DamageType) -> frozenset[str]:
    """
    Return the BuildStats field names for an ailment's increased damage pool.

    Valid for: BLEED, IGNITE, POISON (as DoT).
    Raises KeyError for non-ailment types.
    """
    return _AILMENT_INCREASED_STATS[damage_type]


def damage_types_for_stats(stat_names: tuple[str, ...]) -> set[DamageType]:
    """
    Convert a skill's scaling_stats tuple into the set of DamageTypes it deals.

    Unknown stat names (meta-stats like elemental_damage_pct) are silently
    skipped — they are bonuses, not primary type indicators.
    """
    return {STAT_TO_TYPE[s] for s in stat_names if s in STAT_TO_TYPE}
