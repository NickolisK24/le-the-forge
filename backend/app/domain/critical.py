"""
Critical Strike System (Step 63).

Determines whether a hit is a critical strike and applies the crit
multiplier to the damage. Mirrors Last Epoch's crit model:

    effective_crit_chance = clamp(base_chance + bonus_pct / 100, 0, CRIT_CAP)
    crit_multiplier       = base_multiplier + increased_multiplier / 100
    crit_damage           = raw_damage * crit_multiplier

Constants:
    CRIT_CAP = 1.0   — maximum crit chance (100%)
    BASE_CRIT_MULTIPLIER = 2.0 — default 200% (i.e. double damage)

Public API:
    effective_crit_chance(base_chance, crit_chance_bonus_pct) -> float
        Returns clamped crit chance in [0, CRIT_CAP].

    effective_crit_multiplier(base_multiplier, increased_multiplier_pct) -> float
        Returns total crit multiplier.

    apply_crit(raw_damage, is_crit, crit_multiplier) -> float
        Returns damage after applying crit multiplier (if crit).

    roll_crit(crit_chance, rng_roll=None) -> bool
        Returns True if this hit is a critical strike.
"""

from __future__ import annotations

CRIT_CAP: float = 1.0
BASE_CRIT_MULTIPLIER: float = 2.0


def effective_crit_chance(base_chance: float, crit_chance_bonus_pct: float) -> float:
    """
    Return effective crit chance clamped to [0, CRIT_CAP].

        effective = clamp(base_chance + crit_chance_bonus_pct / 100, 0, 1)

    base_chance is a fraction (0.0–1.0); crit_chance_bonus_pct is additive
    percentage points (e.g. 10 = +10% crit chance).

    Raises ValueError if base_chance < 0.
    """
    if base_chance < 0:
        raise ValueError(f"base_chance must be >= 0, got {base_chance}")
    raw = base_chance + crit_chance_bonus_pct / 100.0
    return max(0.0, min(CRIT_CAP, raw))


def effective_crit_multiplier(
    base_multiplier: float, increased_multiplier_pct: float
) -> float:
    """
    Return total crit multiplier after applying increased crit multiplier.

        effective = base_multiplier + increased_multiplier_pct / 100

    base_multiplier is a total multiplier (e.g. 2.0 = 200% damage).
    increased_multiplier_pct is additive bonus (e.g. 50 → +50% → adds 0.5).

    Raises ValueError if base_multiplier < 1.
    """
    if base_multiplier < 1.0:
        raise ValueError(f"base_multiplier must be >= 1, got {base_multiplier}")
    return base_multiplier + max(0.0, increased_multiplier_pct) / 100.0


def apply_crit(raw_damage: float, is_crit: bool, crit_multiplier: float) -> float:
    """
    Return damage after applying the crit multiplier if this is a crit.

    Non-crit hits are returned unchanged.
    Raises ValueError if raw_damage < 0 or crit_multiplier < 1.
    """
    if raw_damage < 0:
        raise ValueError(f"raw_damage must be >= 0, got {raw_damage}")
    if crit_multiplier < 1.0:
        raise ValueError(f"crit_multiplier must be >= 1, got {crit_multiplier}")
    if not is_crit:
        return raw_damage
    return raw_damage * crit_multiplier


def roll_crit(crit_chance: float, rng_roll: float | None = None) -> bool:
    """
    Return True if this hit is a critical strike.

    rng_roll should be in [0, 100). None → treated as 0 (always crits if
    crit_chance > 0). Fires when rng_roll < crit_chance * 100.
    """
    if rng_roll is None:
        rng_roll = 0.0
    return rng_roll < crit_chance * 100.0
