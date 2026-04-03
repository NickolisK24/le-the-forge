"""
G10 — Rotation Metrics Engine

Computes summary statistics from a list of CastResult objects produced by
the rotation executor.

Metrics
-------
total_damage:        Sum of all cast damages.
total_casts:         Number of cast events.
duration_used:       Last resolves_at time (effective fight window used).
dps:                 total_damage / duration_used  (0 if duration_used == 0).
uptime_fraction:     Fraction of duration_used that had an active cast.
idle_time:           Total seconds with no cast in-flight.
efficiency:          1 - idle_time / duration_used  (same as uptime_fraction).
cast_counts:         {skill_id: count} per-skill breakdown.
damage_by_skill:     {skill_id: total_damage} per-skill breakdown.
avg_cast_interval:   Average time between consecutive cast starts (0 if < 2 casts).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from collections import defaultdict

from rotation.rotation_executor import CastResult


@dataclass
class RotationMetrics:
    total_damage:       float
    total_casts:        int
    duration_used:      float
    dps:                float
    uptime_fraction:    float
    idle_time:          float
    efficiency:         float
    cast_counts:        dict[str, int]
    damage_by_skill:    dict[str, float]
    avg_cast_interval:  float


def compute_metrics(results: list[CastResult], duration: float) -> RotationMetrics:
    """
    Compute rotation metrics from an ordered CastResult list.

    Parameters
    ----------
    results:
        Ordered list from execute_rotation / build_timeline.
    duration:
        Total simulation window (seconds) — used to compute idle time
        relative to the full window even if the last cast ended early.
    """
    if not results:
        return RotationMetrics(
            total_damage      = 0.0,
            total_casts       = 0,
            duration_used     = 0.0,
            dps               = 0.0,
            uptime_fraction   = 0.0,
            idle_time         = duration,
            efficiency        = 0.0,
            cast_counts       = {},
            damage_by_skill   = {},
            avg_cast_interval = 0.0,
        )

    total_damage  = sum(r.damage for r in results)
    total_casts   = len(results)
    duration_used = results[-1].resolves_at if results else 0.0

    # Per-skill stats
    cast_counts:     dict[str, int]   = defaultdict(int)
    damage_by_skill: dict[str, float] = defaultdict(float)
    for r in results:
        cast_counts[r.skill_id]     += 1
        damage_by_skill[r.skill_id] += r.damage

    # Idle time = gaps between resolves_at and next cast_at
    active_time = 0.0
    for r in results:
        active_time += r.resolves_at - r.cast_at  # cast duration

    # Gaps between casts (using full duration as window)
    idle_time = max(0.0, duration - active_time)
    uptime_fraction = max(0.0, min(1.0, active_time / duration)) if duration > 0 else 0.0
    efficiency = uptime_fraction

    dps = total_damage / duration_used if duration_used > 0 else 0.0

    # Average interval between consecutive casts
    if total_casts >= 2:
        intervals = [
            results[i].cast_at - results[i - 1].cast_at
            for i in range(1, total_casts)
        ]
        avg_cast_interval = sum(intervals) / len(intervals)
    else:
        avg_cast_interval = 0.0

    return RotationMetrics(
        total_damage      = total_damage,
        total_casts       = total_casts,
        duration_used     = duration_used,
        dps               = dps,
        uptime_fraction   = uptime_fraction,
        idle_time         = idle_time,
        efficiency        = efficiency,
        cast_counts       = dict(cast_counts),
        damage_by_skill   = dict(damage_by_skill),
        avg_cast_interval = avg_cast_interval,
    )
