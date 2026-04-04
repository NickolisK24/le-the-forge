"""
More Multiplier Calculator — multiplicative 'more' damage stacking.

In Last Epoch, 'more' modifiers each multiply independently rather than
adding together. This calculator applies them sequentially so each source
compounds correctly.

Rules:
- Pure computation only
- No registry access
- No Flask dependencies
"""

from __future__ import annotations


def apply_more_multiplier(base: float, more_values: list[float]) -> float:
    """
    Apply a sequence of multiplicative 'more' modifiers to a base value.

    Each value in more_values is a percent-point (50.0 = 50% more) and is
    applied as a separate multiplier — they compound, not add.

    Example:
        apply_more_multiplier(100.0, [50.0, 20.0])
        = 100.0 * (1 + 0.50) * (1 + 0.20)
        = 100.0 * 1.5 * 1.2
        = 180.0

    Args:
        base:        starting value before multipliers
        more_values: list of percent-point more modifiers
    """
    result = base
    for v in more_values:
        result *= (1 + v / 100)
    return result
