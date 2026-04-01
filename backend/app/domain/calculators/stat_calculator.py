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
