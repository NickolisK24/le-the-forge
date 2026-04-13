"""
Armor Shred Steady-State Calculator — models sustained armor shred in DPS scenarios.

In Last Epoch, armor shred works as follows:
  - Each hit has a chance (armour_shred_chance%) to apply one stack of armor shred
  - Each stack reduces enemy armor by ARMOR_PER_STACK (100)
  - Stacks last STACK_DURATION seconds (4s in LE)
  - No stack cap — stacks are limited only by application rate × duration

For DPS calculations, we model the steady-state stack count:
  stacks = application_rate × stack_duration

This is a pure calculation module — no DB, no HTTP.
"""

from __future__ import annotations


# Last Epoch armor shred constants
# VERIFIED: 1.4.3 spec §4.3 — armor shred has no stack cap; stacks persist for 4s
ARMOR_PER_STACK: float = 100.0     # armor reduced per shred stack
STACK_DURATION: float = 4.0        # seconds per stack before expiry


def steady_state_stacks(
    shred_chance_pct: float,
    hits_per_second: float,
    hit_count: int = 1,
) -> float:
    """Calculate expected steady-state armor shred stacks.

    At steady state, stacks arrive at the application rate and expire
    after STACK_DURATION seconds:

        application_rate = shred_chance × hits_per_second × hit_count
        stacks = application_rate × STACK_DURATION

    Args:
        shred_chance_pct: Armor shred chance as a percentage (e.g., 85 = 85%).
        hits_per_second: Effective attacks per second.
        hit_count: Hits per attack (multi-hit skills).

    Returns:
        Expected number of concurrent shred stacks (float, unlimited).
    """
    if shred_chance_pct <= 0 or hits_per_second <= 0:
        return 0.0
    chance = min(shred_chance_pct / 100.0, 1.0)
    rate = chance * hits_per_second * max(1, hit_count)
    return rate * STACK_DURATION


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
