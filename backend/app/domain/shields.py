"""
Damage Absorption Shields (Step 72).

A shield absorbs incoming damage before it reaches the health pool.
Damage hits the shield first; any overflow spills into health.

  AbsorptionShield — tracks current shield value and absorbs damage
  absorb(shield_hp, incoming) -> (shield_remaining, overflow)
"""

from __future__ import annotations

from dataclasses import dataclass


def absorb(shield_hp: float, incoming: float) -> tuple[float, float]:
    """
    Apply *incoming* damage to a shield of *shield_hp*.

    Returns (shield_remaining, overflow_to_health).
    Raises ValueError if shield_hp < 0 or incoming < 0.
    """
    if shield_hp < 0:
        raise ValueError(f"shield_hp must be >= 0, got {shield_hp}")
    if incoming < 0:
        raise ValueError(f"incoming must be >= 0, got {incoming}")
    absorbed   = min(shield_hp, incoming)
    overflow   = max(0.0, incoming - shield_hp)
    remaining  = max(0.0, shield_hp - absorbed)
    return remaining, overflow


@dataclass
class AbsorptionShield:
    """Mutable shield that absorbs damage before health is affected."""
    max_shield:     float
    current_shield: float

    def __post_init__(self) -> None:
        if self.max_shield < 0:
            raise ValueError(f"max_shield must be >= 0, got {self.max_shield}")
        if self.current_shield < 0:
            raise ValueError(f"current_shield must be >= 0, got {self.current_shield}")

    @classmethod
    def at_full(cls, max_shield: float) -> "AbsorptionShield":
        return cls(max_shield=max_shield, current_shield=max_shield)

    def take_damage(self, incoming: float) -> float:
        """Absorb damage; return overflow that hits health."""
        self.current_shield, overflow = absorb(self.current_shield, incoming)
        return overflow

    def restore(self, amount: float) -> None:
        """Restore shield up to max_shield."""
        self.current_shield = min(self.max_shield, self.current_shield + max(0.0, amount))

    @property
    def is_depleted(self) -> bool:
        return self.current_shield <= 0.0
