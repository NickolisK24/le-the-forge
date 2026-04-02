"""
Enemy Damage Resolution Bridge (Step 97).

Bridges Phase A hit resolution (combat_validation.HitInput/resolve_hit)
into EncounterEnemy objects. Applies the full combat math pipeline to
compute post-mitigation damage, then applies it to the encounter enemy.

  resolve_hit_against_enemy(inp, enemy) -> EncounterHitResult
      Runs the Phase A pipeline using enemy stats as inputs, then
      applies the resulting damage to the EncounterEnemy.

The bridge extracts the enemy's armor, resistances, and shield into the
HitInput, runs resolve_hit(), and feeds the output back to the enemy.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, HitResult, resolve_hit
from app.domain.damage_conversion import ConversionRule
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.on_kill import OnKillRegistry
from app.domain.shields import AbsorptionShield
from encounter.enemy import EncounterEnemy


@dataclass
class EncounterHitResult:
    """
    Result of a hit resolved against an EncounterEnemy.

    hit_result      — full Phase A HitResult breakdown
    health_dealt    — actual health damage applied to the enemy
    enemy_alive     — whether the enemy is still alive after the hit
    overkill        — cumulative overkill on the enemy (from EncounterEnemy)
    """
    hit_result:   HitResult
    health_dealt: float
    enemy_alive:  bool
    overkill:     float


def resolve_hit_against_enemy(
    enemy:            EncounterEnemy,
    base_damage:      float,
    *,
    damage_type:      DamageType = DamageType.PHYSICAL,
    penetration:      float = 0.0,
    crit_chance:      float = 0.05,
    crit_multiplier:  float = 2.0,
    conversion_rules: tuple[ConversionRule, ...] = (),
    leech_pct:        float = 0.0,
    reflect_pct:      float = 0.0,
    on_kill_registry: OnKillRegistry | None = None,
    rng_hit:          float | None = None,
    rng_crit:         float | None = None,
    rng_dodge:        float | None = None,
    rng_block:        float | None = None,
    rng_on_kill:      float | None = None,
) -> EncounterHitResult:
    """
    Run the full Phase A damage pipeline against *enemy*.

    Extracts armor, resistances, and shield from the EncounterEnemy,
    builds a HitInput, resolves the hit, then applies the resulting
    health_damage to the enemy.

    Returns an EncounterHitResult with the pipeline breakdown and
    post-application enemy state.
    """
    # Build the domain EnemyInstance from EncounterEnemy's current state
    domain_enemy = EnemyInstance.from_stats(
        EnemyStats(
            health=max(1, int(enemy.current_health)),
            armor=int(enemy.armor),
            resistances=dict(enemy.resistances),
        )
    )

    # Build a transient AbsorptionShield matching the enemy's current shield
    shield: AbsorptionShield | None = None
    if enemy.shield > 0.0:
        shield = AbsorptionShield(
            current_shield=enemy.shield,
            max_shield=enemy.max_shield,
        )

    inp = HitInput(
        base_damage=base_damage,
        damage_type=damage_type,
        crit_chance=crit_chance,
        crit_multiplier=crit_multiplier,
        conversion_rules=conversion_rules,
        enemy=domain_enemy,
        shield=shield,
        penetration=penetration,
        leech_pct=leech_pct,
        reflect_pct=reflect_pct,
        on_kill_registry=on_kill_registry,
        rng_hit=rng_hit,
        rng_crit=rng_crit,
        rng_dodge=rng_dodge,
        rng_block=rng_block,
        rng_on_kill=rng_on_kill,
    )

    hit = resolve_hit(inp)

    # Sync shield back to EncounterEnemy
    if shield is not None:
        enemy.shield = shield.current_shield

    # Apply health damage directly to the encounter enemy
    health_dealt = 0.0
    if hit.health_damage > 0.0:
        health_dealt = enemy.apply_damage(hit.health_damage)

    return EncounterHitResult(
        hit_result=hit,
        health_dealt=health_dealt,
        enemy_alive=enemy.is_alive,
        overkill=enemy.overkill,
    )
