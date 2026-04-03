"""
I6 — Damage Distribution Engine

Distributes a damage value across one or more targets according to
a named distribution type.

Distribution types:
    single_target  — full damage to one target
    full_aoe       — full damage to every target
    split_damage   — total damage divided equally across targets
    splash         — full damage to primary, splash_pct to others
    chain          — handled by ChainEngine (I7); not implemented here
"""

from __future__ import annotations

from dataclasses import dataclass

from targets.models.target_entity import TargetEntity

VALID_DISTRIBUTIONS = frozenset(
    {"single_target", "full_aoe", "split_damage", "splash", "chain"}
)


@dataclass(frozen=True)
class DamageEvent:
    """Result of applying damage to one target."""
    target_id:      str
    damage_dealt:   float
    overkill:       float        # damage in excess of remaining HP (>= 0)
    killed:         bool


class MultiTargetDistribution:
    """
    distribute(damage, distribution, primary, all_targets, splash_pct)
        → list[DamageEvent]

    primary      — the primary/selected target (required for
                   single_target and splash)
    all_targets  — full alive pool (required for full_aoe, split_damage,
                   splash secondary hits)
    splash_pct   — fraction of damage applied to non-primary targets
                   in splash mode (0.0–1.0, default 0.3)
    """

    def distribute(
        self,
        damage: float,
        distribution: str,
        primary: TargetEntity | None = None,
        all_targets: list[TargetEntity] | None = None,
        splash_pct: float = 0.3,
    ) -> list[DamageEvent]:
        if distribution not in VALID_DISTRIBUTIONS:
            raise ValueError(
                f"Unknown distribution {distribution!r}. "
                f"Must be one of: {sorted(VALID_DISTRIBUTIONS)}"
            )
        if damage < 0:
            raise ValueError("damage must be >= 0")

        targets = all_targets or []
        alive = [t for t in targets if t.is_alive]

        if distribution == "single_target":
            if primary is None:
                raise ValueError("single_target requires a primary target")
            return [self._hit(primary, damage)]

        if distribution == "full_aoe":
            if not alive:
                return []
            return [self._hit(t, damage) for t in alive]

        if distribution == "split_damage":
            if not alive:
                return []
            per_target = damage / len(alive)
            return [self._hit(t, per_target) for t in alive]

        if distribution == "splash":
            if primary is None:
                raise ValueError("splash requires a primary target")
            events = [self._hit(primary, damage)]
            secondaries = [t for t in alive if t.target_id != primary.target_id]
            splash_dmg = damage * splash_pct
            for t in secondaries:
                events.append(self._hit(t, splash_dmg))
            return events

        # "chain" is handled by ChainEngine — return empty here
        return []

    @staticmethod
    def _hit(target: TargetEntity, damage: float) -> DamageEvent:
        pre_hp = target.current_health
        actual = target.apply_damage(damage)
        overkill = max(0.0, damage - pre_hp)
        return DamageEvent(
            target_id=target.target_id,
            damage_dealt=actual,
            overkill=overkill,
            killed=not target.is_alive,
        )
