"""
F6 — Ranking Engine

Sorts simulation results by score and returns the top N as
OptimizationResult objects.

Ties are broken by total_damage descending, then by the stringified
build fingerprint for full determinism.
"""

from __future__ import annotations

from builds.build_definition import BuildDefinition
from optimization.scoring    import score_result
from optimization.models.optimization_result import OptimizationResult


def rank_results(
    batch: list[tuple[BuildDefinition, dict | None, list[str]]],
    metric: str,
    top_n: int | None = None,
) -> list[OptimizationResult]:
    """
    Rank a batch of simulation results.

    Parameters
    ----------
    batch:
        List of (build_variant, simulation_output_or_None, mutations_applied).
    metric:
        Scoring metric name passed to score_result().
    top_n:
        Maximum number of results to return.  None = return all.

    Returns
    -------
    List of OptimizationResult ordered best → worst.
    """
    scored: list[tuple[float, float, str, BuildDefinition, dict, list[str]]] = []

    for build, result, mutations in batch:
        if result is None:
            continue
        s = score_result(result, metric)
        td = float(result.get("total_damage", 0.0))
        # Use build repr as deterministic tiebreaker
        fingerprint = str(sorted(build.to_dict().items()))
        scored.append((s, td, fingerprint, build, result, mutations))

    # Sort: primary = score desc, secondary = total_damage desc, tertiary = fingerprint asc
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))

    if top_n is not None:
        scored = scored[:top_n]

    return [
        OptimizationResult(
            rank              = i + 1,
            build_variant     = entry[3],
            score             = entry[0],
            simulation_output = entry[4],
            mutations_applied = entry[5],
        )
        for i, entry in enumerate(scored)
    ]
