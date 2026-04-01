"""
Stat Group Registry — canonical groupings of BuildStats field names.

Each constant is a frozenset of BuildStats field-name strings that share a
single semantic role. Consumers iterate or intersect against these sets
instead of defining their own inline field lists.

Rules:
- Pure data — no logic, no imports from engine or calculator modules
- All values are frozenset[str] of BuildStats attribute names
- One group per semantic concern
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Damage — increased (additive) pools
# ---------------------------------------------------------------------------

ELEMENTAL_DAMAGE_INCREASED: frozenset[str] = frozenset({
    "fire_damage_pct",
    "cold_damage_pct",
    "lightning_damage_pct",
})

DAMAGE_INCREASED_GROUP: frozenset[str] = frozenset({
    "spell_damage_pct",
    "physical_damage_pct",
    "fire_damage_pct",
    "cold_damage_pct",
    "lightning_damage_pct",
    "necrotic_damage_pct",
    "void_damage_pct",
    "poison_damage_pct",
    "minion_damage_pct",
    "melee_damage_pct",
    "throwing_damage_pct",
    "bow_damage_pct",
    "elemental_damage_pct",
    "dot_damage_pct",
})

# ---------------------------------------------------------------------------
# Damage — more (multiplicative)
# ---------------------------------------------------------------------------

DAMAGE_MORE_GROUP: frozenset[str] = frozenset({
    "more_damage_pct",
})

# ---------------------------------------------------------------------------
# Ailment damage pools (additive increased sources per ailment type)
# ---------------------------------------------------------------------------

BLEED_DAMAGE_INCREASED: frozenset[str] = frozenset({
    "physical_damage_pct",
    "dot_damage_pct",
    "bleed_damage_pct",
})

IGNITE_DAMAGE_INCREASED: frozenset[str] = frozenset({
    "fire_damage_pct",
    "dot_damage_pct",
    "ignite_damage_pct",
})

POISON_DAMAGE_INCREASED: frozenset[str] = frozenset({
    "poison_damage_pct",
    "dot_damage_pct",
    "poison_dot_damage_pct",
})
