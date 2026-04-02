"""
Skill Cooldown System (Step 52).

Tracks per-skill cooldown state and integrates with the fight timeline.

  SkillCooldown   — mutable state for one skill's cooldown
  CooldownManager — manages a set of skill cooldowns, advances time,
                    and gates cast attempts
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SkillCooldown:
    """
    Mutable cooldown state for a single skill.

    cooldown_duration  — full cooldown length in seconds (0 = no cooldown)
    cooldown_remaining — seconds until the skill can be used again
    """
    skill_name:         str
    cooldown_duration:  float
    cooldown_remaining: float = 0.0

    def __post_init__(self) -> None:
        if self.cooldown_duration < 0:
            raise ValueError(
                f"cooldown_duration must be >= 0, got {self.cooldown_duration}"
            )
        if self.cooldown_remaining < 0:
            raise ValueError(
                f"cooldown_remaining must be >= 0, got {self.cooldown_remaining}"
            )

    @property
    def is_ready(self) -> bool:
        """True if the skill can currently be cast."""
        return self.cooldown_remaining <= 0.0

    def trigger(self) -> None:
        """
        Record that the skill was just cast.

        Starts the cooldown timer (sets cooldown_remaining = cooldown_duration).
        Skills with cooldown_duration=0 are always ready.
        """
        self.cooldown_remaining = self.cooldown_duration

    def tick(self, delta: float) -> None:
        """
        Advance the cooldown timer by ``delta`` seconds.

        Clamps at 0 — remaining never goes negative.
        """
        if delta < 0:
            raise ValueError(f"delta must be >= 0, got {delta}")
        self.cooldown_remaining = max(0.0, self.cooldown_remaining - delta)


class CooldownManager:
    """
    Manages cooldown state for a collection of skills.

    Usage::

        manager = CooldownManager()
        manager.register("fireball", cooldown_duration=3.0)
        if manager.can_cast("fireball"):
            manager.trigger("fireball")
        manager.tick(1.0)
    """

    def __init__(self) -> None:
        self._cooldowns: dict[str, SkillCooldown] = {}

    def register(self, skill_name: str, cooldown_duration: float) -> None:
        """Register a skill with a given cooldown duration."""
        self._cooldowns[skill_name] = SkillCooldown(
            skill_name=skill_name,
            cooldown_duration=cooldown_duration,
        )

    def can_cast(self, skill_name: str) -> bool:
        """
        Return True if the skill is ready to cast.

        Raises KeyError if the skill has not been registered.
        """
        return self._cooldowns[skill_name].is_ready

    def trigger(self, skill_name: str) -> None:
        """
        Mark a skill as cast, starting its cooldown.

        Raises KeyError if the skill has not been registered.
        Raises RuntimeError if the skill is still on cooldown.
        """
        cd = self._cooldowns[skill_name]
        if not cd.is_ready:
            raise RuntimeError(
                f"Cannot cast '{skill_name}': {cd.cooldown_remaining:.3f}s remaining"
            )
        cd.trigger()

    def tick(self, delta: float) -> None:
        """Advance all cooldown timers by ``delta`` seconds."""
        for cd in self._cooldowns.values():
            cd.tick(delta)

    def remaining(self, skill_name: str) -> float:
        """Return seconds until the skill is ready. 0.0 if already ready."""
        return self._cooldowns[skill_name].cooldown_remaining

    @property
    def all_cooldowns(self) -> dict[str, float]:
        """Snapshot of remaining cooldown per skill name."""
        return {name: cd.cooldown_remaining for name, cd in self._cooldowns.items()}
