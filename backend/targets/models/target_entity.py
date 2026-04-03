"""
I1 — Target Entity Model

A TargetEntity represents one combat target in a multi-target encounter.
Each target carries its own health pool, alive flag, position index,
and an independent list of status effect names (stack counts stored
separately in MultiTargetStatusManager).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TargetEntity:
    """
    Single combat target.

    target_id      — unique identifier within the encounter
    max_health     — maximum hit points (> 0)
    current_health — current hit points (0 ≤ x ≤ max_health)
    position_index — ordering hint for nearest/chain/splash targeting
    status_list    — active status_ids on this target (names only;
                     stacks tracked by MultiTargetStatusManager)
    """
    target_id:      str
    max_health:     float
    current_health: float        = field(default=0.0)
    position_index: int          = 0
    status_list:    list[str]    = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id must not be empty")
        if self.max_health <= 0:
            raise ValueError("max_health must be > 0")
        if self.current_health == 0.0:
            # Default to full health when not explicitly set
            object.__setattr__(self, "current_health", self.max_health) \
                if hasattr(self, "__dataclass_fields__") else None
            self.current_health = self.max_health
        if self.current_health < 0:
            raise ValueError("current_health must be >= 0")
        if self.current_health > self.max_health:
            raise ValueError("current_health must be <= max_health")

    # ------------------------------------------------------------------
    # Derived
    # ------------------------------------------------------------------

    @property
    def is_alive(self) -> bool:
        return self.current_health > 0

    @property
    def health_pct(self) -> float:
        return self.current_health / self.max_health

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def apply_damage(self, amount: float) -> float:
        """
        Reduce current_health by *amount* (floored at 0).
        Returns actual damage dealt (may be < amount due to death cap).
        """
        if amount < 0:
            raise ValueError("damage amount must be >= 0")
        actual = min(amount, self.current_health)
        self.current_health = max(0.0, self.current_health - amount)
        return actual

    def heal(self, amount: float) -> None:
        if amount < 0:
            raise ValueError("heal amount must be >= 0")
        self.current_health = min(self.max_health, self.current_health + amount)

    def add_status(self, status_id: str) -> None:
        if status_id not in self.status_list:
            self.status_list.append(status_id)

    def remove_status(self, status_id: str) -> None:
        try:
            self.status_list.remove(status_id)
        except ValueError:
            pass

    def has_status(self, status_id: str) -> bool:
        return status_id in self.status_list

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "target_id":      self.target_id,
            "max_health":     self.max_health,
            "current_health": self.current_health,
            "health_pct":     round(self.health_pct, 4),
            "is_alive":       self.is_alive,
            "position_index": self.position_index,
            "status_list":    list(self.status_list),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TargetEntity":
        return cls(
            target_id=d["target_id"],
            max_health=d["max_health"],
            current_health=d.get("current_health", d["max_health"]),
            position_index=d.get("position_index", 0),
            status_list=list(d.get("status_list", [])),
        )
