"""
Multi-Enemy Simulation (Step 66).

Handles distributing damage across multiple enemy targets simultaneously.
Supports two hit distribution models:

  SINGLE  — only the primary (first) target is hit
  CLEAVE  — all targets take full damage (e.g. melee cleave)
  SPLIT   — damage is divided equally among all targets
  CHAIN   — targets are hit in order; each hit deals full damage

TargetGroup manages a list of EnemyInstance objects and applies the
appropriate distribution for a given hit.

Public API:
    HitMode           — enum of distribution strategies
    TargetGroup       — manages a group of EnemyInstance targets
    TargetGroup.apply_hit(damage, mode) -> list[float]
        Returns the per-enemy actual damage dealt list.
    TargetGroup.living  -> list[EnemyInstance]
    TargetGroup.all_dead -> bool
"""

from __future__ import annotations

import enum

from app.domain.enemy import EnemyInstance


class HitMode(enum.Enum):
    SINGLE = "single"   # primary target only
    CLEAVE = "cleave"   # all targets full damage
    SPLIT  = "split"    # damage divided equally
    CHAIN  = "chain"    # sequential full-damage hits


class TargetGroup:
    """
    A group of enemies that can be hit together.

    Enemies are ordered; index 0 is the primary target.
    Dead enemies are excluded from SPLIT divisor calculations but still
    receive 0 damage in the output list for accurate index mapping.
    """

    def __init__(self, enemies: list[EnemyInstance]) -> None:
        if not enemies:
            raise ValueError("TargetGroup requires at least one enemy")
        self._enemies = list(enemies)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def enemies(self) -> list[EnemyInstance]:
        """All enemies (including dead)."""
        return list(self._enemies)

    @property
    def living(self) -> list[EnemyInstance]:
        """Enemies still alive."""
        return [e for e in self._enemies if e.is_alive]

    @property
    def all_dead(self) -> bool:
        """True if every enemy in the group is dead."""
        return all(not e.is_alive for e in self._enemies)

    @property
    def count(self) -> int:
        """Total enemy count (including dead)."""
        return len(self._enemies)

    # ------------------------------------------------------------------
    # Hit distribution
    # ------------------------------------------------------------------

    def apply_hit(self, damage: float, mode: HitMode = HitMode.SINGLE) -> list[float]:
        """
        Apply *damage* to enemies according to *mode*.

        Returns a list of actual damage dealt per enemy (same length as
        self.enemies). Dead enemies always receive 0.

        Raises ValueError if damage < 0.
        """
        if damage < 0:
            raise ValueError(f"damage must be >= 0, got {damage}")

        if mode is HitMode.SINGLE:
            return self._hit_single(damage)
        if mode is HitMode.CLEAVE:
            return self._hit_cleave(damage)
        if mode is HitMode.SPLIT:
            return self._hit_split(damage)
        if mode is HitMode.CHAIN:
            return self._hit_chain(damage)
        raise ValueError(f"Unknown HitMode: {mode}")

    def _hit_single(self, damage: float) -> list[float]:
        results = [0.0] * len(self._enemies)
        for i, enemy in enumerate(self._enemies):
            if enemy.is_alive:
                results[i] = enemy.take_damage(damage)
                break
        return results

    def _hit_cleave(self, damage: float) -> list[float]:
        return [e.take_damage(damage) for e in self._enemies]

    def _hit_split(self, damage: float) -> list[float]:
        living_count = sum(1 for e in self._enemies if e.is_alive)
        if living_count == 0:
            return [0.0] * len(self._enemies)
        share = damage / living_count
        return [e.take_damage(share) if e.is_alive else 0.0 for e in self._enemies]

    def _hit_chain(self, damage: float) -> list[float]:
        """Hit each living enemy in order with full damage."""
        return [e.take_damage(damage) if e.is_alive else 0.0 for e in self._enemies]

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def total_damage_dealt(self, results: list[float]) -> float:
        """Sum a damage results list."""
        return sum(results)
