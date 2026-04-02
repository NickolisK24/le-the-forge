"""
F8 — Optimization Service

Coordinates the full optimization pipeline:

    OptimizationConfig
    → VariantGenerator  → list of (BuildDefinition, mutations)
    → ConstraintEngine  → filter invalid variants
    → BatchRunner       → simulate each variant
    → ScoringEngine     → inside ranking
    → RankingEngine     → top N OptimizationResult

This module is pure Python — no Flask imports.
"""

from __future__ import annotations

from builds.build_definition                  import BuildDefinition
from builds.build_stats_engine                import BuildStatsEngine
from optimization.models.optimization_config  import OptimizationConfig
from optimization.models.optimization_result  import OptimizationResult
from optimization.variant_generator           import VariantGenerator
from optimization.constraints                 import ConstraintEngine
from optimization.batch_runner                import BatchRunner, BatchProgress
from optimization.ranking                     import rank_results


_DEFAULT_ENCOUNTER = {
    "enemy_template": "STANDARD_BOSS",
    "fight_duration": 60.0,
    "tick_size":      0.1,
    "distribution":   "SINGLE",
}

_DEFAULT_TOP_N = 10


def optimize(
    base_build:         BuildDefinition,
    config:             OptimizationConfig,
    encounter_kwargs:   dict | None   = None,
    top_n:              int           = _DEFAULT_TOP_N,
    max_workers:        int           = 1,
    progress:           BatchProgress | None = None,
) -> dict:
    """
    Run the full optimization pipeline.

    Parameters
    ----------
    base_build:
        Starting build; all variants are mutations of this.
    config:
        OptimizationConfig controlling variant count, mutation depth,
        metric, constraints, and RNG seed.
    encounter_kwargs:
        Encounter parameters forwarded to the encounter engine.
        Defaults to STANDARD_BOSS / 60s / 0.1s tick.
    top_n:
        Maximum number of results to include in the response.
    max_workers:
        Thread pool size for the BatchRunner.
    progress:
        Optional BatchProgress tracker updated during simulation.

    Returns
    -------
    {
        "results":                     list[dict],   # top_n OptimizationResult dicts
        "total_variants_generated":    int,
        "variants_passed_constraints": int,
        "variants_simulated":          int,
        "variants_failed_simulation":  int,
    }
    """
    enc = encounter_kwargs or dict(_DEFAULT_ENCOUNTER)
    stats_engine      = BuildStatsEngine()
    constraint_engine = ConstraintEngine(config.constraints)
    generator         = VariantGenerator(config)
    runner            = BatchRunner(enc, max_workers=max_workers)

    # 1. Generate variants
    raw_variants = generator.generate(base_build)
    total_generated = len(raw_variants)

    # 2. Apply constraints (compile stats once per variant for constraint checks)
    passing: list[tuple[BuildDefinition, list[str]]] = []
    for variant, mutations in raw_variants:
        try:
            stats  = stats_engine.compile(variant)
            params = stats_engine.to_encounter_params(variant)
            ok, _  = constraint_engine.check(variant, stats, params)
            if ok:
                passing.append((variant, mutations))
        except Exception:
            pass  # compile error → treat as constraint failure

    passed_constraints = len(passing)

    # 3. Run simulations in batch
    builds   = [v for v, _ in passing]
    mutations_map = {id(v): m for v, m in passing}

    if progress is not None:
        progress.total = len(builds)

    batch_results = runner.run_batch(builds, progress=progress)

    # 4. Build the full batch list with mutations attached
    full_batch: list[tuple[BuildDefinition, dict | None, list[str]]] = [
        (b, r, mutations_map.get(id(b), []))
        for b, r in batch_results
    ]

    failed_sims = sum(1 for _, r, _ in full_batch if r is None)
    simulated   = len(full_batch) - failed_sims

    # 5. Rank
    ranked = rank_results(full_batch, config.target_metric, top_n=top_n)

    return {
        "results":                     [r.to_dict() for r in ranked],
        "total_variants_generated":    total_generated,
        "variants_passed_constraints": passed_constraints,
        "variants_simulated":          simulated,
        "variants_failed_simulation":  failed_sims,
    }
