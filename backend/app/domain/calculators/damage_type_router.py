"""
Damage Type Router — centralized routing from damage type to applicable stat groups.

Two distinct concepts:

  DamageType — the elemental/damage channel: what type of damage is dealt.
               (PHYSICAL, FIRE, COLD, …, BLEED, IGNITE)

  SkillTag   — the delivery/source modifier: how the damage is dealt.
               (SPELL, MELEE, THROWING, BOW, MINION)

Tags are modifiers, not channels. A fire spell has DamageType.FIRE *and*
SkillTag.SPELL — the stat pools from both must be combined. Using SkillTag.SPELL
alone is always wrong for an elemental skill.

Routing functions:
  increased_stats_for(damage_type)       → frozenset of hit-damage stat fields
  tag_stats_for(skill_tag)               → frozenset of tag-modifier stat fields
  combined_increased_stats(types, tags)  → union of both pools
  ailment_increased_stats(damage_type)   → frozenset for ailment DoT pools

Rules:
- Pure data — no logic beyond dict lookup
- No engine imports, no registry access, no Flask context
- Single source of truth for all damage stat routing
"""

from __future__ import annotations

import enum
from typing import Iterable


# ---------------------------------------------------------------------------
# DamageType — elemental / damage channels
# ---------------------------------------------------------------------------

class DamageType(enum.Enum):
    """
    The damage channel: what elemental or physical type is dealt.

    Ailment types (BLEED, IGNITE) have their own DoT-specific increased pools
    accessed via ailment_increased_stats().
    """

    PHYSICAL  = "physical"
    FIRE      = "fire"
    COLD      = "cold"
    LIGHTNING = "lightning"
    NECROTIC  = "necrotic"
    VOID      = "void"
    POISON    = "poison"

    # Ailment types — DoT channels with distinct increased pools
    BLEED  = "bleed"
    IGNITE = "ignite"


# ---------------------------------------------------------------------------
# SkillTag — delivery / source modifiers
# ---------------------------------------------------------------------------

class SkillTag(enum.Enum):
    """
    How the damage is delivered. Tags are modifiers, not channels.

    A fire spell carries DamageType.FIRE + SkillTag.SPELL.
    SkillTag.SPELL alone is never a complete description of an elemental skill.
    """

    SPELL    = "spell"
    MELEE    = "melee"
    THROWING = "throwing"
    BOW      = "bow"
    MINION   = "minion"


# ---------------------------------------------------------------------------
# Elemental meta-set (FIRE, COLD, LIGHTNING share elemental_damage_pct)
# ---------------------------------------------------------------------------

ELEMENTAL_TYPES: frozenset[DamageType] = frozenset({
    DamageType.FIRE,
    DamageType.COLD,
    DamageType.LIGHTNING,
})


# ---------------------------------------------------------------------------
# Reverse lookups — stat field name → DamageType or SkillTag
# ---------------------------------------------------------------------------

STAT_TO_TYPE: dict[str, DamageType] = {
    "physical_damage_pct":  DamageType.PHYSICAL,
    "fire_damage_pct":      DamageType.FIRE,
    "cold_damage_pct":      DamageType.COLD,
    "lightning_damage_pct": DamageType.LIGHTNING,
    "necrotic_damage_pct":  DamageType.NECROTIC,
    "void_damage_pct":      DamageType.VOID,
    "poison_damage_pct":    DamageType.POISON,
    "bleed_damage_pct":     DamageType.BLEED,
    "ignite_damage_pct":    DamageType.IGNITE,
}

STAT_TO_TAG: dict[str, SkillTag] = {
    "spell_damage_pct":    SkillTag.SPELL,
    "minion_damage_pct":   SkillTag.MINION,
    "melee_damage_pct":    SkillTag.MELEE,
    "throwing_damage_pct": SkillTag.THROWING,
    "bow_damage_pct":      SkillTag.BOW,
}


# ---------------------------------------------------------------------------
# Routing tables
# ---------------------------------------------------------------------------

# Hit damage channels: stat fields that form each type's increased pool.
# Elemental types include elemental_damage_pct (applies to all three).
_HIT_INCREASED_STATS: dict[DamageType, frozenset[str]] = {
    DamageType.PHYSICAL:  frozenset({"physical_damage_pct"}),
    DamageType.FIRE:      frozenset({"fire_damage_pct", "elemental_damage_pct"}),
    DamageType.COLD:      frozenset({"cold_damage_pct", "elemental_damage_pct"}),
    DamageType.LIGHTNING: frozenset({"lightning_damage_pct", "elemental_damage_pct"}),
    DamageType.NECROTIC:  frozenset({"necrotic_damage_pct"}),
    DamageType.VOID:      frozenset({"void_damage_pct"}),
    DamageType.POISON:    frozenset({"poison_damage_pct"}),
}

# Skill tag modifiers: stat fields added when a skill carries a given tag.
_SKILL_TAG_STATS: dict[SkillTag, frozenset[str]] = {
    SkillTag.SPELL:    frozenset({"spell_damage_pct"}),
    SkillTag.MELEE:    frozenset({"melee_damage_pct"}),
    SkillTag.THROWING: frozenset({"throwing_damage_pct"}),
    SkillTag.BOW:      frozenset({"bow_damage_pct"}),
    SkillTag.MINION:   frozenset({"minion_damage_pct"}),
}

# Ailment DoT channels: broader stat pools that scale each ailment's damage.
# POISON as DoT includes dot_damage_pct and poison_dot_damage_pct in addition
# to the shared poison_damage_pct.
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
    Stat fields that form the increased damage pool for a hit damage channel.

    Raises KeyError for ailment-only types (BLEED, IGNITE); use
    ailment_increased_stats() for those.
    """
    return _HIT_INCREASED_STATS[damage_type]


def tag_stats_for(skill_tag: SkillTag) -> frozenset[str]:
    """
    Stat fields added by a skill delivery tag (SPELL, MELEE, MINION, etc.).
    """
    return _SKILL_TAG_STATS[skill_tag]


def combined_increased_stats(
    damage_types: Iterable[DamageType] = (),
    tags: Iterable[SkillTag] = (),
) -> frozenset[str]:
    """
    Union of all stat fields applicable to a skill's full damage profile.

    A fire spell requires both pools:
        combined_increased_stats(
            damage_types=[DamageType.FIRE],
            tags=[SkillTag.SPELL],
        )
        # → {"fire_damage_pct", "elemental_damage_pct", "spell_damage_pct"}
    """
    result: set[str] = set()
    for dt in damage_types:
        result |= _HIT_INCREASED_STATS[dt]
    for tag in tags:
        result |= _SKILL_TAG_STATS[tag]
    return frozenset(result)


def ailment_increased_stats(damage_type: DamageType) -> frozenset[str]:
    """
    Stat fields for an ailment's DoT increased damage pool.

    Valid for: BLEED, IGNITE, POISON (as DoT).
    Raises KeyError for non-ailment types.
    """
    return _AILMENT_INCREASED_STATS[damage_type]


def damage_types_for_stats(stat_names: tuple[str, ...]) -> set[DamageType]:
    """
    Extract the DamageType channels from a skill's scaling_stats tuple.

    Tag-modifier stats (spell_damage_pct, minion_damage_pct, etc.) are
    intentionally excluded — use tags_for_stats() for those.
    Meta-stats (elemental_damage_pct, dot_damage_pct) are also excluded.
    """
    return {STAT_TO_TYPE[s] for s in stat_names if s in STAT_TO_TYPE}


def tags_for_stats(stat_names: tuple[str, ...]) -> set[SkillTag]:
    """
    Extract the SkillTag modifiers from a skill's scaling_stats tuple.
    """
    return {STAT_TO_TAG[s] for s in stat_names if s in STAT_TO_TAG}
