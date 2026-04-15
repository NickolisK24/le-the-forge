"""
Skill Calculator — pure skill computation functions.

Rules:
- Pure computation only
- No registry access
- No Flask dependencies
- Accept typed domain objects when possible
"""

from __future__ import annotations

from app.domain.skill import SkillStatDef
from app.domain.calculators.damage_type_router import DamageType
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Per-type flat-added-damage lookup tables
# ---------------------------------------------------------------------------
#
# Each weapon-style pool has a set of BuildStats fields, one per damage type.
# sum_flat_damage() used to sum *all* of them whenever the matching is_* flag
# was set, which inflated a skill's base damage with flat damage types it
# couldn't actually deal (e.g. Shadow Cascade — a physical/void melee skill —
# picked up added_melee_fire and added_melee_necrotic). Routing flat damage
# through these per-type tables restricts accumulation to the skill's
# declared damage_types tuple.
#
# Types without an entry for a given weapon style (e.g. VOID for bow) are
# intentionally absent — those flat fields simply don't exist in BuildStats.

_FLAT_MELEE_BY_TYPE: dict[DamageType, str] = {
    DamageType.PHYSICAL:  "added_melee_physical",
    DamageType.FIRE:      "added_melee_fire",
    DamageType.COLD:      "added_melee_cold",
    DamageType.LIGHTNING: "added_melee_lightning",
    DamageType.VOID:      "added_melee_void",
    DamageType.NECROTIC:  "added_melee_necrotic",
}

_FLAT_SPELL_BY_TYPE: dict[DamageType, str] = {
    DamageType.FIRE:      "added_spell_fire",
    DamageType.COLD:      "added_spell_cold",
    DamageType.LIGHTNING: "added_spell_lightning",
    DamageType.NECROTIC:  "added_spell_necrotic",
    DamageType.VOID:      "added_spell_void",
}
# Note: added_spell_damage is a generic physical-flavoured spell flat stat
# and isn't in _FLAT_SPELL_BY_TYPE — it's added separately below and only
# when the skill's damage_types is exactly {PHYSICAL}, so it doesn't
# double-count alongside a specific type like added_spell_fire.

_FLAT_THROW_BY_TYPE: dict[DamageType, str] = {
    DamageType.PHYSICAL:  "added_throw_physical",
    DamageType.FIRE:      "added_throw_fire",
    DamageType.COLD:      "added_throw_cold",
}

_FLAT_BOW_BY_TYPE: dict[DamageType, str] = {
    DamageType.PHYSICAL:  "added_bow_physical",
    DamageType.FIRE:      "added_bow_fire",
}


def scale_skill_damage(
    base: float,
    scaling: float,
    level: int,
    damage_types: tuple[DamageType, ...] = (),
) -> dict[DamageType, float]:
    """
    Apply level scaling and distribute the total evenly across damage types.

    Returns a dict mapping each DamageType to its portion of the scaled total.
    For a single-type skill the dict has one entry equal to the full scaled value.
    For multi-type skills each entry is total / n, so the sum is always preserved.

    Returns an empty dict when damage_types is empty — callers must fall back
    to the untyped total (e.g. for spell-only skills pending data migration).
    """
    total = base * (1 + scaling * (level - 1))
    if not damage_types:
        return {}
    per_type = total / len(damage_types)
    return {dt: per_type for dt in damage_types}


def hits_per_cast(added: int) -> int:
    """Total hits per cast: base 1 plus any spec-tree additions."""
    return max(1, 1 + added)


def sum_flat_damage(stats: BuildStats, skill_def: SkillStatDef) -> float:
    """Sum flat added damage applicable to a skill's attack type *and* its
    declared damage types.

    Previously this summed every flat-damage field for the matching weapon
    style (all six ``added_melee_*`` fields for any melee skill, etc.),
    which inflated base damage with types the skill couldn't deal — a
    Shadow Cascade (physical/void melee) would wrongly pick up
    ``added_melee_fire``, ``added_melee_necrotic``, and so on.

    Now each weapon-style block filters by ``skill_def.damage_types`` via
    the per-type lookup tables above. When ``damage_types`` is empty
    (unmigrated data or tag-only skills like ``"Rip Blood"``) we fall back
    to the original broad sum so behaviour is unchanged for those skills.
    """
    total = 0.0
    skill_types: set[DamageType] = set(skill_def.damage_types)

    if skill_def.is_spell:
        if skill_types:
            for dt in skill_types:
                field = _FLAT_SPELL_BY_TYPE.get(dt)
                if field is not None:
                    total += getattr(stats, field, 0.0)
            # added_spell_damage is the generic physical-flavoured spell flat
            # stat. Include it only when the skill deals pure physical damage
            # — if other specific types are present (e.g. PHYSICAL + FIRE),
            # including it would double-count the physical portion against
            # the type-specific added_spell_* fields.
            if skill_types == {DamageType.PHYSICAL}:
                total += stats.added_spell_damage
        else:
            # Fallback: no declared damage_types — preserve legacy broad sum.
            total += (stats.added_spell_damage + stats.added_spell_fire +
                      stats.added_spell_cold + stats.added_spell_lightning +
                      stats.added_spell_necrotic + stats.added_spell_void)

    if skill_def.is_melee:
        if skill_types:
            for dt in skill_types:
                field = _FLAT_MELEE_BY_TYPE.get(dt)
                if field is not None:
                    total += getattr(stats, field, 0.0)
        else:
            total += (stats.added_melee_physical + stats.added_melee_fire +
                      stats.added_melee_cold + stats.added_melee_lightning +
                      stats.added_melee_void + stats.added_melee_necrotic)

    if skill_def.is_throwing:
        if skill_types:
            for dt in skill_types:
                field = _FLAT_THROW_BY_TYPE.get(dt)
                if field is not None:
                    total += getattr(stats, field, 0.0)
        else:
            total += (stats.added_throw_physical + stats.added_throw_fire +
                      stats.added_throw_cold)

    if skill_def.is_bow:
        if skill_types:
            for dt in skill_types:
                field = _FLAT_BOW_BY_TYPE.get(dt)
                if field is not None:
                    total += getattr(stats, field, 0.0)
        else:
            total += stats.added_bow_physical + stats.added_bow_fire

    return total
