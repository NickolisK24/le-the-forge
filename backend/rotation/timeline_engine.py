"""
G6 — RotationTimeline Engine

Converts a RotationDefinition + a SkillDefinition registry into an ordered
list of cast events on a simulation timeline.

Each CastEvent records:
  skill_id     — which skill was cast
  cast_at      — absolute simulation time the cast begins
  resolves_at  — cast_at + cast_time (when damage is applied)
  step_index   — index in rotation.steps that generated this event

The engine advances time by:
  1. Waiting for the next ready window:
       max(current_time, GCD_unlock, skill_cooldown_unlock)
  2. Adding cast_time to reach resolves_at
  3. Adding step.delay_after_cast
  4. Repeating for repeat_count casts per step, then advancing to next step
"""

from __future__ import annotations
from dataclasses import dataclass, field

from rotation.models.rotation_definition import RotationDefinition
from rotation.models.rotation_step       import RotationStep
from rotation.cooldown_tracker            import CooldownTracker
from rotation.global_cooldown             import GlobalCooldown
from skills.models.skill_definition       import SkillDefinition


@dataclass
class CastEvent:
    skill_id:    str
    cast_at:     float
    resolves_at: float
    step_index:  int


def build_timeline(
    rotation:     RotationDefinition,
    skill_registry: dict[str, SkillDefinition],
    duration:     float,
    gcd:          float = 0.0,
) -> list[CastEvent]:
    """
    Generate all cast events that fit within `duration` seconds.

    Parameters
    ----------
    rotation:
        The rotation to execute.
    skill_registry:
        Mapping skill_id → SkillDefinition.  Skills not present are skipped.
    duration:
        Simulation wall-clock length in seconds.
    gcd:
        Global cooldown duration (seconds). 0 = no GCD.

    Returns
    -------
    Ordered list of CastEvent objects.
    """
    if not rotation.steps:
        return []

    tracker = CooldownTracker()
    global_cd = GlobalCooldown(base_gcd=gcd)

    events: list[CastEvent] = []
    current_time = 0.0
    step_index = 0
    n_steps = len(rotation.steps)

    while current_time < duration:
        step = rotation.steps[step_index % n_steps]
        skill = skill_registry.get(step.skill_id)

        if skill is None:
            # Unknown skill — advance step, don't hang
            step_index += 1
            if not rotation.loop and step_index >= n_steps:
                break
            continue

        for _ in range(step.repeat_count):
            # Advance time to when both GCD and skill cooldown are clear
            ready = max(
                current_time,
                global_cd.locked_until(),
                current_time + tracker.time_remaining(step.skill_id, current_time),
            )
            # Recalculate with the advanced ready time
            ready = max(
                ready,
                ready + tracker.time_remaining(step.skill_id, ready),
            )

            if ready >= duration:
                current_time = duration  # exhaust outer loop
                break

            resolves_at = ready + skill.cast_time
            events.append(CastEvent(
                skill_id    = step.skill_id,
                cast_at     = ready,
                resolves_at = resolves_at,
                step_index  = step_index % n_steps,
            ))

            # Advance clock
            current_time = resolves_at + step.delay_after_cast

            # Apply cooldowns
            tracker.start(step.skill_id, ready, skill.cooldown)
            if gcd > 0:
                global_cd.trigger(ready)

            if current_time >= duration:
                break

        step_index += 1
        if not rotation.loop and step_index >= n_steps:
            break

    return events
