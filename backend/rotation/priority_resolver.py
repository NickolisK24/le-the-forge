"""
G7 — Priority Resolver

Given a set of candidate rotation steps, selects the one to cast next.

Selection rules (applied in order):
  1. Only steps whose skill is ready (not on cooldown, not GCD-locked) are eligible.
  2. Among eligible steps, the one with the lowest priority value wins.
  3. Ties (same priority) are broken by the step's original index in the rotation
     (earlier step wins).
  4. If no step is eligible, return None (caller handles the wait).
"""

from __future__ import annotations

from rotation.models.rotation_step import RotationStep
from rotation.cooldown_tracker      import CooldownTracker
from rotation.global_cooldown       import GlobalCooldown


def resolve_next(
    steps:        list[RotationStep],
    tracker:      CooldownTracker,
    gcd:          GlobalCooldown,
    current_time: float,
) -> tuple[int, RotationStep] | None:
    """
    Return (index, step) for the highest-priority ready step, or None.

    Parameters
    ----------
    steps:
        All rotation steps in their defined order.
    tracker:
        Current cooldown state.
    gcd:
        Current global cooldown state.
    current_time:
        Simulation clock in seconds.

    Returns
    -------
    (original_index, step) or None if nothing is ready.
    """
    if gcd.is_locked(current_time):
        return None

    candidates: list[tuple[int, int, RotationStep]] = []  # (priority, index, step)
    for i, step in enumerate(steps):
        if tracker.is_ready(step.skill_id, current_time):
            candidates.append((step.priority, i, step))

    if not candidates:
        return None

    # Sort: lowest priority value first, then earliest original index
    candidates.sort(key=lambda x: (x[0], x[1]))
    _, original_index, chosen_step = candidates[0]
    return original_index, chosen_step


def next_ready_time(
    steps:        list[RotationStep],
    tracker:      CooldownTracker,
    gcd:          GlobalCooldown,
    current_time: float,
) -> float:
    """
    Return the earliest future time at which at least one step becomes ready.

    Returns `current_time` if something is already ready.
    """
    best = float("inf")
    gcd_wait = gcd.time_remaining(current_time) if gcd.is_locked(current_time) else 0.0

    for step in steps:
        cd_wait = tracker.time_remaining(step.skill_id, current_time)
        ready_in = max(cd_wait, gcd_wait)
        best = min(best, ready_in)

    return current_time + (best if best != float("inf") else 0.0)
