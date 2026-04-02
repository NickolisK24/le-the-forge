"""
Final Combat Validation Suite (Step 80).

Integration validation layer that connects all Phase A systems into
a single damage pipeline and verifies correctness end-to-end:

  1. Accuracy roll      (Step 77) — did the hit land?
  2. Dodge roll         (Step 78) — did the enemy dodge?
  3. Block roll         (Step 79) — did the enemy block?
  4. Critical roll      (Step 63) — was it a crit?
  5. Damage conversion  (Step 58) — split physical → elemental
  6. Armor mitigation   (Step 62) — reduce physical post-conversion
  7. Resistance         (Step 61) — reduce by type resistances
  8. Penetration/shred  (Step 64) — subtract before resistance cap
  9. Shield absorption  (Step 72) — shield absorbs before health
 10. Health damage       (Step 65) — apply to enemy health
 11. Overkill           (Step 74) — compute excess
 12. Leech              (Step 73) — restore player resources
 13. Reflection         (Step 71) — reflect portion back
 14. On-kill            (Step 67) — fire on-kill effects if dead

Public API:
  HitInput      — all inputs for a single hit
  HitResult     — full breakdown of what happened
  resolve_hit(hit_input) -> HitResult
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.accuracy import calculate_hit_chance, roll_hit
from app.domain.armor import apply_armor
from app.domain.block import block_result
from app.domain.calculators.damage_type_router import DamageType
from app.domain.critical import apply_crit, roll_crit
from app.domain.damage_conversion import ConversionRule, apply_conversions
from app.domain.dodge import roll_dodge
from app.domain.enemy import EnemyInstance
from app.domain.leech import apply_leech_to_pool, calculate_leech
from app.domain.on_kill import OnKillContext, OnKillEffect, OnKillRegistry
from app.domain.overkill import overkill_amount
from app.domain.penetration import effective_resistance
from app.domain.reflection import apply_reflection
from app.domain.resistance import apply_resistance
from app.domain.shields import AbsorptionShield


@dataclass(frozen=True)
class HitInput:
    """All inputs needed to resolve one hit."""
    base_damage:          float
    damage_type:          DamageType         = DamageType.PHYSICAL
    attacker_accuracy:    float              = 10_000.0
    crit_chance:          float              = 0.05
    crit_multiplier:      float              = 2.0
    conversion_rules:     tuple[ConversionRule, ...] = field(default_factory=tuple)
    enemy:                EnemyInstance | None = None
    shield:               AbsorptionShield | None = None
    # Defensive rolls (deterministic when provided)
    rng_hit:              float | None = None
    rng_dodge:            float | None = None
    rng_block:            float | None = None
    rng_crit:             float | None = None
    # Block settings
    enemy_block_chance:   float = 0.0
    enemy_block_eff:      float = 0.5
    # Dodge rating
    enemy_dodge_chance:   float = 0.0
    # Attacker penetration per type
    penetration:          float = 0.0
    # Leech settings
    leech_pct:            float = 0.0
    current_mana:         float = 0.0
    max_mana:             float = 1.0
    # Reflect settings
    reflect_pct:          float = 0.0
    # On-kill registry
    on_kill_registry:     OnKillRegistry | None = None
    rng_on_kill:          float | None = None


@dataclass
class HitResult:
    """Full breakdown of what happened for one hit."""
    landed:            bool  = False
    dodged:            bool  = False
    blocked:           bool  = False
    is_crit:           bool  = False
    raw_damage:        float = 0.0
    crit_damage:       float = 0.0
    post_armor:        float = 0.0
    post_resistance:   float = 0.0
    shield_absorbed:   float = 0.0
    health_damage:     float = 0.0
    overkill:          float = 0.0
    mana_leeched:      float = 0.0
    reflected_damage:  float = 0.0
    on_kill_effects:   list[OnKillEffect] = field(default_factory=list)


def resolve_hit(inp: HitInput) -> HitResult:
    """
    Run a full damage pipeline for one hit and return a HitResult.

    Each stage is skipped gracefully if the relevant optional input
    (enemy, shield, registry) is not provided.
    """
    result = HitResult()

    # 1. Accuracy check
    acc_chance = calculate_hit_chance(
        inp.attacker_accuracy,
        0.0,   # evasion handled by dodge separately
    )
    result.landed = roll_hit(acc_chance, inp.rng_hit)
    if not result.landed:
        return result

    # 2. Dodge check
    result.dodged = roll_dodge(inp.enemy_dodge_chance, inp.rng_dodge)
    if result.dodged:
        return result

    # 3. Block check
    block_dmg, result.blocked = block_result(
        inp.base_damage,
        inp.enemy_block_chance,
        inp.enemy_block_eff,
        inp.rng_block,
    )
    working_damage = block_dmg

    # 4. Crit
    result.is_crit = roll_crit(inp.crit_chance, inp.rng_crit)
    if result.is_crit:
        working_damage = apply_crit(working_damage, True, inp.crit_multiplier)
    result.raw_damage  = inp.base_damage
    result.crit_damage = working_damage

    # 5. Damage type conversion
    damage_map: dict[DamageType, float] = {inp.damage_type: working_damage}
    if inp.conversion_rules:
        damage_map = apply_conversions(damage_map, list(inp.conversion_rules))

    # 6. Armor mitigation (physical only)
    armor = inp.enemy.armor if inp.enemy else 0
    post_armor_map: dict[DamageType, float] = {}
    for dt, amt in damage_map.items():
        if dt is DamageType.PHYSICAL:
            post_armor_map[dt] = apply_armor(amt, float(armor))
        else:
            post_armor_map[dt] = amt
    result.post_armor = sum(post_armor_map.values())

    # 7 & 8. Resistance + penetration/shred
    post_res_map: dict[DamageType, float] = {}
    for dt, amt in post_armor_map.items():
        if inp.enemy:
            base_res = inp.enemy.stats.capped_resistances.get(dt.value, 0.0)
            shred    = inp.enemy.current_shred(dt.value)
            eff_res  = effective_resistance(base_res, inp.penetration, shred)
        else:
            eff_res = 0.0
        post_res_map[dt] = apply_resistance(amt, eff_res)
    total_post_res = sum(post_res_map.values())
    result.post_resistance = total_post_res

    # 9. Shield absorption
    working = total_post_res
    if inp.shield is not None:
        overflow = inp.shield.take_damage(working)
        result.shield_absorbed = working - overflow
        working = overflow
    result.health_damage = working

    # 10. Apply to enemy health
    enemy_health_before = inp.enemy.current_health if inp.enemy else working
    if inp.enemy:
        inp.enemy.take_damage(working)
        enemy_health_after = inp.enemy.current_health
    else:
        enemy_health_after = max(0.0, enemy_health_before - working)

    # 11. Overkill
    result.overkill = overkill_amount(working, max(0.0, enemy_health_before))

    # 12. Leech
    leeched = calculate_leech(working, inp.leech_pct)
    result.mana_leeched = leeched
    # (caller handles actually restoring mana using apply_leech_to_pool)

    # 13. Reflection
    _, reflected = apply_reflection(working, inp.reflect_pct)
    result.reflected_damage = reflected

    # 14. On-kill
    if (
        inp.on_kill_registry is not None
        and inp.enemy is not None
        and not inp.enemy.is_alive
    ):
        ctx = OnKillContext(
            enemy_name=inp.enemy.stats.resistances and "" or "",
            enemy_max_health=inp.enemy.max_health,
            overkill_damage=result.overkill,
        )
        result.on_kill_effects = inp.on_kill_registry.process_kill(
            ctx, inp.rng_on_kill
        )

    return result
