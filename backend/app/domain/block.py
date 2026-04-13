"""
Block Mechanics (Step 79).

Blocking reduces damage from hits by a flat percentage. Unlike dodge
(full avoidance), a successful block still allows some damage through
based on block effectiveness.

  block_result(incoming, block_chance, block_effectiveness, rng_roll=None)
      -> (damage_taken, blocked)
      damage_taken = incoming * (1 - block_effectiveness) if blocked else incoming
      blocked      = True if the roll succeeded

  BLOCK_CHANCE_CAP = 0.85
"""

from __future__ import annotations

# VERIFIED: 1.4.3 spec §3.5 — block chance effectiveness is capped at 85%
BLOCK_CHANCE_CAP: float = 0.85


def roll_block(block_chance: float, rng_roll: float | None = None) -> bool:
    """Return True if the block succeeds."""
    if rng_roll is None:
        rng_roll = 0.0
    clamped = max(0.0, min(BLOCK_CHANCE_CAP, block_chance))
    return rng_roll < clamped


def block_result(
    incoming: float,
    block_chance: float,
    block_effectiveness: float,
    rng_roll: float | None = None,
) -> tuple[float, bool]:
    """
    Resolve a block attempt against *incoming* damage.

    block_effectiveness is a fraction in [0, 1]:
      0.0 → block absorbs nothing (damage unchanged)
      1.0 → block absorbs all damage (0 taken)
      0.5 → block absorbs 50% (glancing blow)

    Returns (damage_taken, was_blocked).
    Raises ValueError if incoming < 0 or block_effectiveness not in [0, 1].
    """
    if incoming < 0:
        raise ValueError(f"incoming must be >= 0, got {incoming}")
    if not (0.0 <= block_effectiveness <= 1.0):
        raise ValueError(f"block_effectiveness must be in [0, 1], got {block_effectiveness}")

    was_blocked = roll_block(block_chance, rng_roll)
    if was_blocked:
        damage_taken = incoming * (1.0 - block_effectiveness)
    else:
        damage_taken = incoming
    return damage_taken, was_blocked
