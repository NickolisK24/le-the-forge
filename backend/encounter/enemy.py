"""
Enemy Entity Core (Step 96).

Defines the encounter-layer enemy entity with health, armor, resistances,
and an absorb shield. Distinct from app.domain.enemy.EnemyInstance (used
in the combat math pipeline). EncounterEnemy is the stateful object that
lives inside an encounter simulation and can be reset between runs.

  EncounterEnemy   — mutable enemy entity for encounter simulation
  from_archetype() — convenience constructor from EnemyArchetype presets
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.enemy import EnemyArchetype, EnemyStats


@dataclass
class EncounterEnemy:
    """
    Mutable enemy entity used inside encounter simulations.

    max_health     — starting / maximum health
    current_health — current health (decremented by damage)
    armor          — flat armor value (used by pipeline for mitigation)
    resistances    — dict[damage_type_str, float] raw resistance percentages
    shield         — current absorb shield (absorbs damage before health)
    max_shield     — maximum shield capacity (for reset)
    name           — optional display name
    overkill       — accumulated overkill damage dealt to this enemy
    """

    max_health:     float
    current_health: float
    armor:          float
    resistances:    dict[str, float] = field(default_factory=dict)
    shield:         float = 0.0
    max_shield:     float = 0.0
    name:           str   = "enemy"
    overkill:       float = 0.0

    def __post_init__(self) -> None:
        if self.max_health <= 0:
            raise ValueError(f"max_health must be > 0, got {self.max_health}")
        if self.armor < 0:
            raise ValueError(f"armor must be >= 0, got {self.armor}")
        if self.shield < 0:
            raise ValueError(f"shield must be >= 0, got {self.shield}")

    # ------------------------------------------------------------------
    # Damage application
    # ------------------------------------------------------------------

    def apply_damage(self, amount: float) -> float:
        """
        Apply *amount* of post-mitigation damage.

        Shield absorbs first; overflow continues to health.
        Returns actual health damage dealt (0 if already dead).
        Tracks overkill (damage beyond current health).
        """
        if amount < 0:
            raise ValueError(f"damage amount must be >= 0, got {amount}")
        if not self.is_alive:
            return 0.0

        # Shield absorbs first
        if self.shield > 0.0:
            absorbed    = min(self.shield, amount)
            self.shield = max(0.0, self.shield - absorbed)
            amount     -= absorbed

        if amount <= 0.0:
            return 0.0

        # Apply to health
        health_damage       = min(amount, self.current_health)
        self.overkill      += max(0.0, amount - self.current_health)
        self.current_health = max(0.0, self.current_health - amount)
        return health_damage

    def apply_shield_damage(self, amount: float) -> tuple[float, float]:
        """
        Apply *amount* directly to the shield only.

        Returns (shield_absorbed, overflow).
        Overflow is the amount that exceeded the shield (not applied to health).
        """
        if amount < 0:
            raise ValueError(f"amount must be >= 0, got {amount}")
        absorbed    = min(self.shield, amount)
        overflow    = amount - absorbed
        self.shield = max(0.0, self.shield - absorbed)
        return absorbed, overflow

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0.0

    @property
    def health_pct(self) -> float:
        """Current health as a percentage of max_health (0–100)."""
        return (self.current_health / self.max_health) * 100.0

    @property
    def shield_pct(self) -> float:
        """Current shield as a percentage of max_shield, or 0 if no shield."""
        if self.max_shield <= 0.0:
            return 0.0
        return (self.shield / self.max_shield) * 100.0

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self) -> None:
        """Restore enemy to full health and shield; clear overkill."""
        self.current_health = self.max_health
        self.shield         = self.max_shield
        self.overkill       = 0.0

    # ------------------------------------------------------------------
    # Constructors
    # ------------------------------------------------------------------

    @classmethod
    def from_stats(
        cls,
        stats: EnemyStats,
        *,
        name: str = "enemy",
        shield: float = 0.0,
    ) -> "EncounterEnemy":
        """Create an EncounterEnemy from an EnemyStats domain object."""
        return cls(
            max_health=float(stats.health),
            current_health=float(stats.health),
            armor=float(stats.armor),
            resistances=dict(stats.resistances),
            shield=shield,
            max_shield=shield,
            name=name,
        )

    @classmethod
    def from_archetype(
        cls,
        archetype: EnemyArchetype,
        *,
        name: str | None = None,
        shield: float = 0.0,
    ) -> "EncounterEnemy":
        """Create an EncounterEnemy from an EnemyArchetype preset."""
        stats = archetype.base_stats()
        return cls.from_stats(stats, name=name or archetype.value, shield=shield)
