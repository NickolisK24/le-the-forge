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

    more_pct is a percent point value (50.0 = 50% more), consistent with
    apply_percent_bonus and all other pct fields in the codebase.
    Kept separate from apply_percent_bonus because increased% and more%
    stack differently: increased% bonuses are summed first (additive pool),
    more% bonuses are multiplied in afterward (multiplicative chain).

    Example:
        base     = 100
        more_pct = 50.0
        result   = 150.0
    """
    return base * (1 + more_pct / 100)


def combine_additive_percents(*values: float) -> float:
    """
    Combine additive percent-point values into a single total.

    All inputs must be percent-points (25.0 means 25%).
    Additive bonuses are summed before any multiplicative modifiers
    are applied — this function enforces that grouping.

    Example:
        combine_additive_percents(25.0, 10.0, 15.0) → 50.0
    """
    return sum(values)
