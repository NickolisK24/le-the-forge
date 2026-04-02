"""
Multi-Skill Rotation Support (Step 57).

Models a priority-ordered list of skills and selects the next skill to
cast based on availability (cooldown ready + mana affordable).

  SkillEntry     — a skill slot in the rotation (name, cost, cooldown, priority)
  RotationEngine — manages the list, evaluates which skill fires next
  select_next(entries, mana, cooldowns) -> SkillEntry | None
      Pure function; returns the highest-priority ready skill.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillEntry:
    """
    A skill slot in the rotation.

    name          — unique identifier for this skill
    mana_cost     — mana required to cast
    cooldown      — base cooldown in seconds (0 = no cooldown)
    priority      — lower number = higher priority (1 is highest)
    """
    name:      str
    mana_cost: float
    cooldown:  float = 0.0
    priority:  int   = 1

    def __post_init__(self) -> None:
        if self.mana_cost < 0:
            raise ValueError(f"mana_cost must be >= 0, got {self.mana_cost}")
        if self.cooldown < 0:
            raise ValueError(f"cooldown must be >= 0, got {self.cooldown}")
        if self.priority < 1:
            raise ValueError(f"priority must be >= 1, got {self.priority}")


def select_next(
    entries: list[SkillEntry],
    current_mana: float,
    cooldown_remaining: dict[str, float] | None = None,
) -> SkillEntry | None:
    """
    Return the highest-priority skill that is ready to cast.

    A skill is *ready* when:
      1. Its cooldown has expired: cooldown_remaining.get(name, 0.0) <= 0.
      2. The caster can afford it: current_mana >= mana_cost.

    Among all ready skills, returns the one with the lowest ``priority``
    number. Ties broken by position in *entries* (first listed wins).

    Returns None if no skill is ready.
    """
    if cooldown_remaining is None:
        cooldown_remaining = {}

    ready = [
        e for e in entries
        if cooldown_remaining.get(e.name, 0.0) <= 0.0
        and current_mana >= e.mana_cost
    ]

    if not ready:
        return None

    return min(ready, key=lambda e: (e.priority, entries.index(e)))


class RotationEngine:
    """
    Stateful rotation manager.

    Tracks cooldown timers for each registered skill and advances them
    each tick. Delegates skill selection to ``select_next()``.

    Usage::

        engine = RotationEngine()
        engine.add(SkillEntry("fireball", mana_cost=30, cooldown=2.0, priority=1))
        engine.add(SkillEntry("frostbolt", mana_cost=20, cooldown=0.0, priority=2))

        skill = engine.next_skill(current_mana=50.0)
        if skill:
            engine.trigger(skill.name)   # starts cooldown
        engine.tick(0.5)                 # advance time
    """

    def __init__(self) -> None:
        self._entries: list[SkillEntry] = []
        self._cooldowns: dict[str, float] = {}

    def add(self, entry: SkillEntry) -> None:
        """Register a skill in the rotation."""
        if any(e.name == entry.name for e in self._entries):
            raise ValueError(f"Skill '{entry.name}' already registered")
        self._entries.append(entry)
        self._cooldowns[entry.name] = 0.0

    def trigger(self, name: str) -> None:
        """
        Mark skill *name* as just cast — starts its cooldown.

        Raises KeyError if the skill is not registered.
        """
        if name not in self._cooldowns:
            raise KeyError(f"Skill '{name}' not registered")
        entry = next(e for e in self._entries if e.name == name)
        self._cooldowns[name] = entry.cooldown

    def tick(self, delta: float) -> None:
        """Advance all cooldown timers by *delta* seconds."""
        if delta < 0:
            raise ValueError(f"delta must be >= 0, got {delta}")
        for name in self._cooldowns:
            self._cooldowns[name] = max(0.0, self._cooldowns[name] - delta)

    def next_skill(self, current_mana: float) -> SkillEntry | None:
        """Return the highest-priority ready skill, or None."""
        return select_next(self._entries, current_mana, self._cooldowns)

    @property
    def cooldowns(self) -> dict[str, float]:
        """Read-only snapshot of current cooldown timers."""
        return dict(self._cooldowns)

    @property
    def entries(self) -> list[SkillEntry]:
        """Read-only snapshot of registered skills."""
        return list(self._entries)
