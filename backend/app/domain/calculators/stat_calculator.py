"""
Global stat math utilities.

Rules:
- Pure math only
- No registry access
- No Flask usage
- No domain object mutation
- Designed for reuse across affix, skill, and combat logic
"""


def apply_percent_bonus(base: float, percent: float) -> float:
    """
    Apply an additive percentage bonus to a base value.

    Standard Last Epoch formula: base * (1 + percent / 100)

    Args:
        base:    the value before the bonus
        percent: the bonus in percent points (e.g. 20 for +20%)

    Returns:
        The scaled value.
    """
    return base * (1 + percent / 100)


def apply_more_multiplier(base: float, more_pct: float) -> float:
    """
    Apply a multiplicative 'more' modifier.

    Unlike apply_percent_bonus, more_pct is already a decimal fraction
    (0.25 = 25% more), not a percent point value. Kept separate from
    apply_percent_bonus because increased% and more% stack differently:
    increased% bonuses are summed first (additive pool), more% bonuses
    are multiplied in afterward (multiplicative chain).

    Example:
        base     = 100
        more_pct = 0.25
        result   = 125.0
    """
    return base * (1 + more_pct)
