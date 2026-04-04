"""
G8 — Rotation Execution Engine

Drives a RotationDefinition through time using the CooldownTracker,
GlobalCooldown, and PriorityResolver to produce an ordered sequence of
CastResult objects.

Unlike the timeline_engine (which follows step order strictly), the executor
uses priority-based selection: at each decision point it picks the highest-
priority ready skill from the entire rotation.

CastResult
----------
skill_id:    Which skill was cast
cast_at:     Simulation time when cast began
resolves_at: cast_at + cast_time
damage:      base_damage from the SkillDefinition
step_index:  Index of the matching RotationStep
"""

from __future__ import annotations
from dataclasses import dataclass

from rotation.models.rotation_definition import RotationDefinition
from rotation.cooldown_tracker            import CooldownTracker
from rotation.global_cooldown             import GlobalCooldown
from rotation.priority_resolver           import resolve_next, next_ready_time
from skills.models.skill_definition       import SkillDefinition


@dataclass
class CastResult:
    skill_id:    str
    cast_at:     float
    resolves_at: float
    damage:      float
    step_index:  int


def execute_rotation(
    rotation:       RotationDefinition,
    skill_registry: dict[str, SkillDefinition],
    duration:       float,
    gcd:            float = 0.0,
    max_iters:      int   = 100_000,
) -> list[CastResult]:
    """
    Simulate the rotation for `duration` seconds using priority selection.

    Parameters
    ----------
    rotation:
        The rotation to execute.
    skill_registry:
        Mapping skill_id → SkillDefinition.
    duration:
        Simulation length in seconds.
    gcd:
        Global cooldown duration (0 = no GCD).
    max_iters:
        Safety cap on iterations to prevent infinite loops.

    Returns
    -------
    Ordered list of CastResult.
    """
    if not rotation.steps:
        return []

    tracker  = CooldownTracker()
    global_cd = GlobalCooldown(base_gcd=gcd)

    # Filter steps to those whose skill exists in the registry
    valid_steps = [s for s in rotation.steps if s.skill_id in skill_registry]
    if not valid_steps:
        return []

    results: list[CastResult] = []
    current_time = 0.0
    iters = 0

    while current_time < duration and iters < max_iters:
        iters += 1

        chosen = resolve_next(valid_steps, tracker, global_cd, current_time)
        if chosen is None:
            # Nothing ready — advance clock to next ready moment
            nrt = next_ready_time(valid_steps, tracker, global_cd, current_time)
            if nrt <= current_time:
                # Safety: shouldn't happen, but avoid infinite loop
                current_time += 0.001
                continue
            current_time = nrt
            continue

        step_index, step = chosen
        skill = skill_registry[step.skill_id]

        resolves_at = current_time + skill.cast_time
        results.append(CastResult(
            skill_id    = step.skill_id,
            cast_at     = current_time,
            resolves_at = resolves_at,
            damage      = skill.base_damage,
            step_index  = step_index,
        ))

        # Advance clock past cast + intentional delay
        current_time = resolves_at + step.delay_after_cast

        # Apply cooldowns
        tracker.start(step.skill_id, results[-1].cast_at, skill.cooldown)
        if gcd > 0:
            global_cd.trigger(results[-1].cast_at)

    return results
