"""
Encounter Result Aggregator (Step 105).

Collects and summarizes outcome metrics from one or more EncounterRunResult
objects, producing aggregated statistics useful for build comparison.

  AggregatedResult   — summary across multiple runs
  aggregate_results  — compute average/min/max/std across runs
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from encounter.state_machine import EncounterRunResult


@dataclass
class AggregatedResult:
    """Summary statistics across one or more EncounterRunResult objects."""
    run_count:          int
    total_damage_avg:   float
    total_damage_min:   float
    total_damage_max:   float
    total_damage_std:   float
    elapsed_time_avg:   float
    average_dps_avg:    float
    kills_avg:          float
    total_casts_avg:    float
    downtime_ticks_avg: float
    all_killed_rate:    float   # fraction of runs where all enemies died


def aggregate_results(results: list[EncounterRunResult]) -> AggregatedResult:
    """
    Compute summary statistics across *results*.

    Raises ValueError if results is empty.
    """
    if not results:
        raise ValueError("results must not be empty")

    n = len(results)

    damages     = [r.total_damage for r in results]
    times       = [r.elapsed_time for r in results]
    kills       = [r.enemies_killed for r in results]
    casts       = [r.total_casts for r in results]
    dt_ticks    = [r.downtime_ticks for r in results]
    all_killed  = [r.all_enemies_dead for r in results]
    dps_values  = [r.total_damage / r.elapsed_time if r.elapsed_time > 0 else 0.0
                   for r in results]

    def _mean(xs):    return sum(xs) / len(xs)
    def _std(xs, mu): return math.sqrt(sum((x - mu) ** 2 for x in xs) / len(xs))

    dmg_mu = _mean(damages)

    return AggregatedResult(
        run_count=n,
        total_damage_avg=dmg_mu,
        total_damage_min=min(damages),
        total_damage_max=max(damages),
        total_damage_std=_std(damages, dmg_mu),
        elapsed_time_avg=_mean(times),
        average_dps_avg=_mean(dps_values),
        kills_avg=_mean(kills),
        total_casts_avg=_mean(casts),
        downtime_ticks_avg=_mean(dt_ticks),
        all_killed_rate=sum(1 for x in all_killed if x) / n,
    )
