"""
Buff/Debuff Timeline Engine (Step 4).

Models time-limited stat modifiers (buffs and debuffs) applied during combat:
  - BuffType      — category of modifier (damage, speed, resistance, etc.)
  - BuffInstance  — a single active buff/debuff with a remaining duration
  - TimelineEngine — manages a collection of active buffs, advances time,
                     and provides aggregated modifier queries
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class BuffType(enum.Enum):
    DAMAGE_MULTIPLIER  = "damage_multiplier"   # additive % bonus to damage
    ATTACK_SPEED       = "attack_speed"        # additive % bonus to attack speed
    CAST_SPEED         = "cast_speed"          # additive % bonus to cast speed
    MOVEMENT_SPEED     = "movement_speed"      # additive % bonus to move speed
    RESISTANCE_SHRED   = "resistance_shred"    # flat reduction of enemy resistance
    DAMAGE_TAKEN       = "damage_taken"        # additive % more damage taken (debuff)
    CRIT_CHANCE_BONUS  = "crit_chance_bonus"   # flat additive crit chance bonus


@dataclass(frozen=True)
class BuffInstance:
    """
    One active buff or debuff modifier.

    buff_type  — category determining how `value` is interpreted
    value      — magnitude of the modifier (positive = beneficial by convention,
                 negative = detrimental; interpretation is caller's responsibility)
    duration   — remaining seconds before this buff expires
    source     — optional identifier of the skill/item that applied this buff
    """
    buff_type: BuffType
    value:     float
    duration:  float
    source:    str = ""


class TimelineEngine:
    """
    Manages the set of active buffs/debuffs over simulated time.

    Usage::

        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.tick(1.0)
        bonus = engine.total_modifier(BuffType.DAMAGE_MULTIPLIER)  # 20.0
    """

    def __init__(self) -> None:
        self._active: list[BuffInstance] = []

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_buff(self, buff: BuffInstance) -> None:
        """Append a new buff/debuff to the timeline."""
        self._active.append(buff)

    def tick(self, delta: float) -> list[BuffInstance]:
        """
        Advance time by *delta* seconds.

        Returns the list of buffs that expired this tick (for event hooks).
        """
        expired: list[BuffInstance] = []
        surviving: list[BuffInstance] = []

        for buff in self._active:
            new_duration = buff.duration - delta
            if new_duration > 0.0:
                surviving.append(BuffInstance(
                    buff_type=buff.buff_type,
                    value=buff.value,
                    duration=new_duration,
                    source=buff.source,
                ))
            else:
                expired.append(buff)

        self._active = surviving
        return expired

    def clear(self) -> None:
        """Remove all active buffs."""
        self._active = []

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def active_buffs(self) -> list[BuffInstance]:
        """Read-only snapshot of currently active buffs."""
        return list(self._active)

    def buffs_of_type(self, buff_type: BuffType) -> list[BuffInstance]:
        """Return all active buffs matching *buff_type*."""
        return [b for b in self._active if b.buff_type is buff_type]

    def total_modifier(self, buff_type: BuffType) -> float:
        """
        Sum of `value` across all active buffs of the given type.

        For additive modifiers (e.g. DAMAGE_MULTIPLIER) this is the total
        additive bonus percentage. Caller is responsible for interpreting
        the result in context.
        """
        return sum(b.value for b in self._active if b.buff_type is buff_type)

    def has_any(self, buff_type: BuffType) -> bool:
        """Return True if at least one buff of *buff_type* is active."""
        return any(b.buff_type is buff_type for b in self._active)
