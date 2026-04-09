"""
Armor Shred Steady-State Calculator — models sustained armor shred in DPS scenarios.

In Last Epoch, armor shred works as follows:
  - Each hit has a chance (armour_shred_chance%) to apply one stack of armor shred
  - Each stack reduces enemy armor by ARMOR_PER_STACK (100)
  - Stacks last STACK_DURATION seconds (4s in LE)
  - Maximum STACK_CAP stacks (20 stacks = 2000 armor reduction)

For DPS calculations, we model the steady-state stack count:
  stacks = min(application_rate × stack_duration, STACK_CAP)

This is a pure calculation module — no DB, no HTTP.
"""

from __future__ import annotations


# Last Epoch armor shred constants
ARMOR_PER_STACK: float = 100.0     # armor reduced per shred stack
STACK_DURATION: float = 4.0        # seconds per stack before expiry
STACK_CAP: int = 20                # maximum concurrent stacks


def steady_state_stacks(
    shred_chance_pct: float,
    hits_per_second: float,
    hit_count: int = 1,
) -> float:
    """Calculate expected steady-state armor shred stacks.

    At steady state, stacks arrive at the application rate and expire
    after STACK_DURATION seconds:

        application_rate = shred_chance × hits_per_second × hit_count
        stacks = min(application_rate × STACK_DURATION, STACK_CAP)

    Args:
        shred_chance_pct: Armor shred chance as a percentage (e.g., 85 = 85%).
        hits_per_second: Effective attacks per second.
        hit_count: Hits per attack (multi-hit skills).

    Returns:
        Expected number of concurrent shred stacks (float, 0 to STACK_CAP).
    """
    if shred_chance_pct <= 0 or hits_per_second <= 0:
        return 0.0
    chance = min(shred_chance_pct / 100.0, 1.0)
    rate = chance * hits_per_second * max(1, hit_count)
    return min(rate * STACK_DURATION, float(STACK_CAP))


def armor_shred_amount(
    shred_chance_pct: float,
    hits_per_second: float,
    hit_count: int = 1,
) -> float:
    """Calculate total armor reduction from steady-state shred stacks.

    Returns:
        Total armor reduction (stacks × ARMOR_PER_STACK).
    """
    stacks = steady_state_stacks(shred_chance_pct, hits_per_second, hit_count)
    return stacks * ARMOR_PER_STACK
