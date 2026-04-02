"""
Cast Speed & Attack Speed Scaling (Step 53).

Converts raw speed stats into effective action timings.

Formula (same for both cast and attack speed):
    effective_interval = base_interval / (1 + speed_bonus)
    effective_rate     = base_rate     * (1 + speed_bonus)

Where speed_bonus is a decimal (e.g. 0.30 = +30% faster).

Public API:
  effective_cast_interval(base_interval, cast_speed_pct) -> float
  effective_attack_interval(base_interval, attack_speed_pct) -> float
  effective_cast_rate(base_rate, cast_speed_pct) -> float
  effective_attack_rate(base_rate, attack_speed_pct) -> float
  scale_hit_interval(base_interval, cast_speed_pct, hit_count) -> float
      Per-hit interval within a multi-hit cast, also scaled by cast speed.
"""

from __future__ import annotations

_MIN_INTERVAL: float = 0.05   # 50 ms — hard floor; prevents divide-by-zero and absurd speeds


def _speed_multiplier(speed_pct: float) -> float:
    """
    Convert a speed bonus percentage to a multiplier.

    speed_pct=0   → 1.00 (no change)
    speed_pct=50  → 1.50 (50% faster)
    speed_pct=100 → 2.00 (twice as fast)
    """
    return 1.0 + max(0.0, speed_pct) / 100.0


def effective_cast_interval(base_interval: float, cast_speed_pct: float) -> float:
    """
    Seconds between casts after applying cast speed bonus.

        effective = max(MIN, base / (1 + cast_speed_pct/100))

    Raises ValueError if base_interval <= 0.
    """
    if base_interval <= 0:
        raise ValueError(f"base_interval must be > 0, got {base_interval}")
    return max(_MIN_INTERVAL, base_interval / _speed_multiplier(cast_speed_pct))


def effective_attack_interval(base_interval: float, attack_speed_pct: float) -> float:
    """
    Seconds between attacks after applying attack speed bonus.

    Same formula as cast speed; kept separate so callers are explicit about
    which speed stat they are applying.
    """
    if base_interval <= 0:
        raise ValueError(f"base_interval must be > 0, got {base_interval}")
    return max(_MIN_INTERVAL, base_interval / _speed_multiplier(attack_speed_pct))


def effective_cast_rate(base_rate: float, cast_speed_pct: float) -> float:
    """
    Casts per second after applying cast speed bonus.

        effective = base_rate * (1 + cast_speed_pct/100)
    """
    if base_rate <= 0:
        raise ValueError(f"base_rate must be > 0, got {base_rate}")
    return base_rate * _speed_multiplier(cast_speed_pct)


def effective_attack_rate(base_rate: float, attack_speed_pct: float) -> float:
    """
    Attacks per second after applying attack speed bonus.
    """
    if base_rate <= 0:
        raise ValueError(f"base_rate must be > 0, got {base_rate}")
    return base_rate * _speed_multiplier(attack_speed_pct)


def scale_hit_interval(
    base_interval: float,
    cast_speed_pct: float,
    hit_count: int,
) -> float:
    """
    Per-hit interval within a multi-hit cast, scaled by cast speed.

    The total cast window is divided evenly across hit_count hits:
        per_hit = effective_cast_interval(base, speed) / hit_count

    Returns the floor-clamped per-hit interval.
    Raises ValueError if hit_count < 1.
    """
    if hit_count < 1:
        raise ValueError(f"hit_count must be >= 1, got {hit_count}")
    cast_window = effective_cast_interval(base_interval, cast_speed_pct)
    return max(_MIN_INTERVAL, cast_window / hit_count)
