"""
F4 — Scoring Engine

Assigns a numeric score to a simulation result dictionary.

All metrics are normalized so that HIGHER score = BETTER build,
regardless of the underlying direction of the raw metric.

Metrics
-------
dps            → score = dps
total_damage   → score = total_damage
ttk            → score = 1 / elapsed_time  (faster TTK = higher score; 0 if enemy not dead)
uptime         → score = uptime_fraction   (1 - downtime_ticks/ticks_simulated)
composite      → DPS scaled by uptime and TTK factors:
                 0.50·dps + 0.30·uptime_fraction·dps + 0.20·ttk_norm·dps
"""

from __future__ import annotations

VALID_METRICS = ("dps", "total_damage", "ttk", "uptime", "composite")


def score_result(simulation_output: dict, metric: str) -> float:
    """
    Compute a scalar score from a simulation result dict.

    Parameters
    ----------
    simulation_output:
        Dict returned by run_encounter_simulation / run_encounter_from_build.
    metric:
        One of VALID_METRICS.

    Returns
    -------
    float — higher is always better.
    """
    if metric not in VALID_METRICS:
        raise ValueError(
            f"Unknown metric '{metric}'. Must be one of {VALID_METRICS}"
        )

    dps          = float(simulation_output.get("dps", 0.0))
    total_damage = float(simulation_output.get("total_damage", 0.0))
    elapsed      = float(simulation_output.get("elapsed_time", 0.0))
    ticks        = int(simulation_output.get("ticks_simulated", 1))
    downtime     = int(simulation_output.get("downtime_ticks", 0))
    dead         = bool(simulation_output.get("all_enemies_dead", False))

    uptime_fraction = (1.0 - downtime / ticks) if ticks > 0 else 1.0

    if metric == "dps":
        return dps

    if metric == "total_damage":
        return total_damage

    if metric == "ttk":
        # Only reward builds that actually kill the enemy
        if not dead or elapsed <= 0:
            return 0.0
        return 1.0 / elapsed

    if metric == "uptime":
        return uptime_fraction

    if metric == "composite":
        # DPS scaled by uptime and TTK factors (all terms proportional to DPS
        # so the result stays in the same unit as dps, not a dimensionless [0,1]).
        # TTK factor: normalised to [0,1] assuming worst-case = 60 s fight.
        ttk_component = (1.0 / elapsed if dead and elapsed > 0 else 0.0)
        ttk_norm = min(ttk_component * 60.0, 1.0)
        return 0.50 * dps + 0.30 * uptime_fraction * dps + 0.20 * ttk_norm * dps

    return 0.0  # unreachable
