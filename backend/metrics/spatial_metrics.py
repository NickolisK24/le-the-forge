"""
K13 — Spatial Metrics Collector

Tracks aggregate spatial combat statistics across a simulation run:
  - Projectile spawns and deactivations
  - Hit and miss counts
  - Critical hit rate
  - Pierce and chain bounce totals
  - Travel distance distribution
  - AoE coverage area
"""

from __future__ import annotations

from dataclasses import dataclass, field


class SpatialMetrics:
    """
    Mutable metrics collector for spatial simulation runs.

    All record_* methods are called by the simulation engine or sync loop.
    summary() returns a snapshot dict suitable for serialisation.
    """

    def __init__(self) -> None:
        self._projectiles_spawned:   int   = 0
        self._projectiles_expired:   int   = 0
        self._hits:                  int   = 0
        self._misses:                int   = 0
        self._crits:                 int   = 0
        self._pierce_count:          int   = 0
        self._chain_bounces:         int   = 0
        self._total_damage:          float = 0.0
        self._total_overkill:        float = 0.0
        self._travel_distances:      list[float] = []
        self._aoe_areas:             list[float] = []

    # ------------------------------------------------------------------
    # Recording
    # ------------------------------------------------------------------

    def record_projectile_spawn(self) -> None:
        self._projectiles_spawned += 1

    def record_projectile_expired(self, distance_traveled: float) -> None:
        self._projectiles_expired += 1
        if distance_traveled >= 0:
            self._travel_distances.append(distance_traveled)

    def record_hit(
        self,
        damage: float,
        overkill: float = 0.0,
        is_critical: bool = False,
        pierced: bool = False,
    ) -> None:
        self._hits += 1
        self._total_damage += damage
        self._total_overkill += overkill
        if is_critical:
            self._crits += 1
        if pierced:
            self._pierce_count += 1

    def record_miss(self) -> None:
        self._misses += 1

    def record_chain_bounce(self) -> None:
        self._chain_bounces += 1

    def record_aoe(self, area: float) -> None:
        if area > 0:
            self._aoe_areas.append(area)

    # ------------------------------------------------------------------
    # Computed properties
    # ------------------------------------------------------------------

    @property
    def total_projectiles_spawned(self) -> int:
        return self._projectiles_spawned

    @property
    def total_hits(self) -> int:
        return self._hits

    @property
    def total_misses(self) -> int:
        return self._misses

    @property
    def total_damage(self) -> float:
        return self._total_damage

    @property
    def total_overkill(self) -> float:
        return self._total_overkill

    @property
    def crit_rate(self) -> float:
        """Fraction of hits that were critical. 0.0 if no hits."""
        return self._crits / self._hits if self._hits > 0 else 0.0

    @property
    def hit_rate(self) -> float:
        """Fraction of shots that hit (hits / (hits + misses)). 0.0 if no shots."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    @property
    def max_travel_distance(self) -> float:
        return max(self._travel_distances) if self._travel_distances else 0.0

    @property
    def avg_travel_distance(self) -> float:
        if not self._travel_distances:
            return 0.0
        return sum(self._travel_distances) / len(self._travel_distances)

    @property
    def total_aoe_area(self) -> float:
        return sum(self._aoe_areas)

    @property
    def total_chain_bounces(self) -> int:
        return self._chain_bounces

    @property
    def total_pierce_count(self) -> int:
        return self._pierce_count

    # ------------------------------------------------------------------
    # Snapshot
    # ------------------------------------------------------------------

    def summary(self) -> dict:
        return {
            "projectiles_spawned":  self._projectiles_spawned,
            "projectiles_expired":  self._projectiles_expired,
            "hits":                 self._hits,
            "misses":               self._misses,
            "hit_rate":             round(self.hit_rate, 4),
            "crits":                self._crits,
            "crit_rate":            round(self.crit_rate, 4),
            "pierce_count":         self._pierce_count,
            "chain_bounces":        self._chain_bounces,
            "total_damage":         round(self._total_damage, 4),
            "total_overkill":       round(self._total_overkill, 4),
            "max_travel_distance":  round(self.max_travel_distance, 4),
            "avg_travel_distance":  round(self.avg_travel_distance, 4),
            "total_aoe_area":       round(self.total_aoe_area, 4),
        }

    def reset(self) -> None:
        """Clear all recorded data."""
        self.__init__()  # type: ignore[misc]
