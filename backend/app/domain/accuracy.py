"""
Hit Accuracy & Avoidance (Step 77).

Determines whether a hit lands based on attacker accuracy vs enemy evasion.
Uses Last Epoch's accuracy formula:

    hit_chance = attacker_accuracy / (attacker_accuracy + enemy_evasion)

Hit chance is clamped to [MIN_HIT_CHANCE, MAX_HIT_CHANCE].

  HIT_CHANCE_MIN = 0.05  — always at least 5% chance to hit
  HIT_CHANCE_MAX = 0.95  — always at least 5% chance to miss

  calculate_hit_chance(accuracy, evasion) -> float
  roll_hit(hit_chance, rng_roll=None) -> bool
"""

from __future__ import annotations

HIT_CHANCE_MIN: float = 0.05
HIT_CHANCE_MAX: float = 0.95


def calculate_hit_chance(accuracy: float, evasion: float) -> float:
    """
    Return clamped hit chance in [HIT_CHANCE_MIN, HIT_CHANCE_MAX].

        raw = accuracy / (accuracy + evasion)

    If both are 0, returns HIT_CHANCE_MAX (no evasion = always hit).
    Raises ValueError if accuracy < 0 or evasion < 0.
    """
    if accuracy < 0:
        raise ValueError(f"accuracy must be >= 0, got {accuracy}")
    if evasion < 0:
        raise ValueError(f"evasion must be >= 0, got {evasion}")
    if accuracy == 0.0 and evasion == 0.0:
        return HIT_CHANCE_MAX
    denom = accuracy + evasion
    raw   = accuracy / denom if denom > 0 else HIT_CHANCE_MAX
    return max(HIT_CHANCE_MIN, min(HIT_CHANCE_MAX, raw))


def roll_hit(hit_chance: float, rng_roll: float | None = None) -> bool:
    """
    Return True if the hit lands.

    rng_roll in [0, 1): None → 0 (always hits if hit_chance > 0).
    Fires when rng_roll < hit_chance.
    """
    if rng_roll is None:
        rng_roll = 0.0
    return rng_roll < hit_chance
