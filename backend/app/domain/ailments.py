"""
Ailment domain model — simulation types for status effects.

Distinct from ailment_calculator.py (which does steady-state DPS math).
This module models individual ailment instances for tick-based simulation:
  - AilmentType  — enumeration of supported ailment kinds
  - AilmentInstance — a single active stack with its own damage and timer
  - apply_ailment() — add a new stack to an active list
  - tick_ailments() — advance simulation time, collect damage, expire stacks
"""

from __future__ import annotations
import enum
from dataclasses import dataclass


class AilmentType(enum.Enum):
    BLEED     = "bleed"
    IGNITE    = "ignite"
    POISON    = "poison"
    SHOCK     = "shock"
    FROSTBITE = "frostbite"


@dataclass(frozen=True)
class AilmentInstance:
    """
    One active ailment stack on an enemy.

    damage_per_tick — damage dealt per second of simulation time
    duration        — remaining seconds before this stack expires
    stack_count     — number of identical applications collapsed into this
                      instance (used when stacks are merged; default 1)
    """
    ailment_type:    AilmentType
    damage_per_tick: float
    duration:        float
    stack_count:     int = 1


# ---------------------------------------------------------------------------
# Simulation functions
# ---------------------------------------------------------------------------

def apply_ailment(
    active: list[AilmentInstance],
    ailment_type: AilmentType,
    damage_per_tick: float,
    duration: float,
) -> list[AilmentInstance]:
    """
    Add a new ailment stack and return the updated list.

    Each application creates an independent instance with its own timer.
    Stack-limit enforcement is handled separately in the stacking layer.
    """
    return [*active, AilmentInstance(
        ailment_type=ailment_type,
        damage_per_tick=damage_per_tick,
        duration=duration,
    )]


def tick_ailments(
    active: list[AilmentInstance],
    tick_delta: float,
) -> tuple[list[AilmentInstance], float]:
    """
    Advance simulation time by tick_delta seconds.

    Returns:
        (remaining, total_damage)
        remaining    — instances still alive after tick
        total_damage — sum of damage dealt this tick across all stacks
    """
    remaining: list[AilmentInstance] = []
    total_damage = 0.0

    for inst in active:
        total_damage += inst.damage_per_tick * tick_delta
        new_duration = inst.duration - tick_delta
        if new_duration > 0.0:
            remaining.append(AilmentInstance(
                ailment_type=inst.ailment_type,
                damage_per_tick=inst.damage_per_tick,
                duration=new_duration,
                stack_count=inst.stack_count,
            ))

    return remaining, total_damage
