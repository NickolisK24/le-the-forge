"""
On-Kill Event System (Step 67).

Fires registered effects when an enemy dies. On-kill effects are a
common ARPG mechanic used for: mana/health restoration, buff application,
ailment spreading, and chain reactions.

  OnKillEffect    — what fires when a kill is detected
  OnKillContext   — information about the kill event
  OnKillRegistry  — holds registered effects; call process_kill() each time
                    an enemy death is detected

Public API:
    OnKillEffectType  — enum of available effects
    OnKillEffect(effect_type, value, chance_pct, source)
    OnKillContext(enemy_archetype, enemy_health, overkill_damage, elapsed)
    OnKillRegistry.register(effect) -> None
    OnKillRegistry.process_kill(context, rng_roll=None) -> list[OnKillEffect]
        Returns the list of effects that fired.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class OnKillEffectType(enum.Enum):
    RESTORE_MANA    = "restore_mana"    # restore flat mana
    RESTORE_HEALTH  = "restore_health"  # restore flat health
    GAIN_BUFF       = "gain_buff"       # apply a damage/speed buff
    RESET_COOLDOWN  = "reset_cooldown"  # named skill's CD goes to 0
    APPLY_AILMENT   = "apply_ailment"   # spread an ailment to nearby enemies
    GRANT_CHARGE    = "grant_charge"    # add a resource charge


@dataclass(frozen=True)
class OnKillContext:
    """
    Information about a kill event.

    enemy_name       — name/id of the enemy that died
    enemy_max_health — max health of the killed enemy
    overkill_damage  — how much damage exceeded the enemy's health
    elapsed          — fight time at moment of kill
    """
    enemy_name:       str   = ""
    enemy_max_health: float = 0.0
    overkill_damage:  float = 0.0
    elapsed:          float = 0.0


@dataclass(frozen=True)
class OnKillEffect:
    """
    An effect that fires on enemy death.

    effect_type  — what happens
    value        — magnitude (mana/health restored, buff value, etc.)
    duration     — duration of applied buff/ailment (0 if not applicable)
    chance_pct   — probability this effect fires (100 = always)
    source       — identifier of the skill/node that granted this effect
    skill_name   — for RESET_COOLDOWN: which skill is reset
    """
    effect_type: OnKillEffectType
    value:       float = 0.0
    duration:    float = 0.0
    chance_pct:  float = 100.0
    source:      str   = ""
    skill_name:  str   = ""

    def __post_init__(self) -> None:
        if not (0.0 <= self.chance_pct <= 100.0):
            raise ValueError(f"chance_pct must be in [0, 100], got {self.chance_pct}")


class OnKillRegistry:
    """
    Holds registered on-kill effects and evaluates them on each kill.

    Usage::

        registry = OnKillRegistry()
        registry.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=30.0))
        fired = registry.process_kill(OnKillContext(enemy_name="slime"))
    """

    def __init__(self) -> None:
        self._effects: list[OnKillEffect] = []

    def register(self, effect: OnKillEffect) -> None:
        """Add an on-kill effect to the registry."""
        self._effects.append(effect)

    def clear(self) -> None:
        """Remove all registered effects."""
        self._effects = []

    @property
    def effects(self) -> list[OnKillEffect]:
        """Read-only snapshot of registered effects."""
        return list(self._effects)

    def process_kill(
        self,
        context: OnKillContext,
        rng_roll: float | None = None,
    ) -> list[OnKillEffect]:
        """
        Evaluate all registered effects against the kill context.

        Returns the list of effects that fired (passed chance roll).
        rng_roll in [0, 100): None → treated as 0 (always fires if chance > 0).
        """
        if rng_roll is None:
            rng_roll = 0.0

        fired: list[OnKillEffect] = []
        for effect in self._effects:
            if rng_roll < effect.chance_pct:
                fired.append(effect)
        return fired
