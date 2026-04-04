"""
Multi-Target Combat Engine (Step 101).

Enables combat against multiple EncounterEnemy objects simultaneously.

  HitDistribution   — enum: SINGLE / CLEAVE / SPLIT / CHAIN
  distribute_damage — pure function that maps damage to a list of enemies
  MultiTargetEngine — stateful engine that applies distributed hits
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from encounter.enemy import EncounterEnemy
from encounter.enemy_damage_pipeline import (EncounterHitResult,
                                              resolve_hit_against_enemy)
from app.domain.calculators.damage_type_router import DamageType


class HitDistribution(enum.Enum):
    SINGLE = "single"   # one target only
    CLEAVE = "cleave"   # full damage to all targets
    SPLIT  = "split"    # damage divided equally among all targets
    CHAIN  = "chain"    # full damage to primary, then reduced to others


@dataclass(frozen=True)
class MultiHitConfig:
    """Configuration for a multi-target hit."""
    distribution:      HitDistribution = HitDistribution.SINGLE
    chain_falloff_pct: float           = 50.0   # CHAIN: % of damage per hop
    damage_type:       DamageType      = DamageType.PHYSICAL
    crit_chance:       float           = 0.05
    crit_multiplier:   float           = 2.0
    penetration:       float           = 0.0
    rng_hit:           float | None    = None
    rng_crit:          float | None    = None


class MultiTargetEngine:
    """
    Applies multi-target damage distributions to a list of enemies.

    apply_hit(primary_idx, enemies, base_damage, config) applies damage
    to enemies according to the HitDistribution and returns per-enemy results.
    """

    def apply_hit(
        self,
        enemies:      list[EncounterEnemy],
        base_damage:  float,
        config:       MultiHitConfig | None = None,
        primary_idx:  int = 0,
    ) -> list[EncounterHitResult | None]:
        """
        Apply *base_damage* to *enemies* per *config*.

        Returns a list of EncounterHitResult aligned with *enemies*
        (None for skipped targets).
        """
        if not enemies:
            return []

        cfg     = config or MultiHitConfig()
        alive   = [e for e in enemies if e.is_alive]
        results: list[EncounterHitResult | None] = [None] * len(enemies)

        if not alive:
            return results

        dist = cfg.distribution

        if dist is HitDistribution.SINGLE:
            idx = min(primary_idx, len(enemies) - 1)
            if enemies[idx].is_alive:
                results[idx] = self._hit(enemies[idx], base_damage, cfg)

        elif dist is HitDistribution.CLEAVE:
            for i, e in enumerate(enemies):
                if e.is_alive:
                    results[i] = self._hit(e, base_damage, cfg)

        elif dist is HitDistribution.SPLIT:
            n = len(alive)
            split_dmg = base_damage / n if n > 0 else 0.0
            for i, e in enumerate(enemies):
                if e.is_alive:
                    results[i] = self._hit(e, split_dmg, cfg)

        elif dist is HitDistribution.CHAIN:
            primary = enemies[min(primary_idx, len(enemies) - 1)]
            dmg = base_damage
            for i, e in enumerate(enemies):
                if not e.is_alive:
                    continue
                results[i] = self._hit(e, dmg, cfg)
                dmg = dmg * (cfg.chain_falloff_pct / 100.0)
                if dmg < 0.001:
                    break

        return results

    @staticmethod
    def _hit(enemy: EncounterEnemy, damage: float,
             cfg: MultiHitConfig) -> EncounterHitResult:
        return resolve_hit_against_enemy(
            enemy, damage,
            damage_type=cfg.damage_type,
            crit_chance=cfg.crit_chance,
            crit_multiplier=cfg.crit_multiplier,
            penetration=cfg.penetration,
            rng_hit=cfg.rng_hit,
            rng_crit=cfg.rng_crit,
        )

    @staticmethod
    def total_damage(results: list[EncounterHitResult | None]) -> float:
        return sum(r.health_dealt for r in results if r is not None)
