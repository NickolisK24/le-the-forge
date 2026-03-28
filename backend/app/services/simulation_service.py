"""
Simulation Service — stateless orchestration of engine calls.

Unlike build_analysis_service (which requires a saved Build model),
this service accepts raw data dicts and delegates to engines directly.
This allows the frontend to call simulation endpoints without persisting
a build first.
"""

from app.engines import stat_engine, combat_engine, defense_engine, optimization_engine
from app.engines.stat_engine import BuildStats
from app.utils.exceptions import SimulationError, BuildValidationError
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


def aggregate_stats(
    character_class: str,
    mastery: str,
    allocated_node_ids: list[int],
    nodes: list[dict],
    gear_affixes: list[dict],
    passive_stats: dict | None = None,
) -> BuildStats:
    """Aggregate stats from raw inputs — no saved build required."""
    return stat_engine.aggregate_stats(
        character_class=character_class,
        mastery=mastery,
        allocated_node_ids=allocated_node_ids,
        nodes=nodes,
        gear_affixes=gear_affixes,
        passive_stats=passive_stats,
    )


def simulate_combat(
    stats_dict: dict,
    skill_name: str,
    skill_level: int = 20,
    n_simulations: int = 10_000,
    seed: int | None = None,
) -> dict:
    """Calculate DPS + Monte Carlo from a stats dict and skill."""
    log.info(
        "simulate_combat",
        skill=skill_name,
        skill_level=skill_level,
        n=n_simulations,
        seed=seed,
    )
    stats = _build_stats_from_dict(stats_dict)

    dps_result = combat_engine.calculate_dps(stats, skill_name, skill_level)
    mc_result = combat_engine.monte_carlo_dps(stats, skill_name, skill_level, n=n_simulations, seed=seed)

    return {
        "dps": dps_result.to_dict(),
        "monte_carlo": mc_result.to_dict(),
        "seed": seed,
    }


def simulate_defense(stats_dict: dict) -> dict:
    """Calculate EHP and survivability from a stats dict."""
    log.info("simulate_defense")
    stats = _build_stats_from_dict(stats_dict)
    defense_result = defense_engine.calculate_defense(stats)
    return defense_result.to_dict()


def simulate_optimize(
    stats_dict: dict,
    skill_name: str,
    skill_level: int = 20,
    top_n: int = 5,
) -> list[dict]:
    """Rank stat upgrades by DPS/EHP gain from a stats dict."""
    log.info("simulate_optimize", skill=skill_name, top_n=top_n)
    stats = _build_stats_from_dict(stats_dict)
    upgrades = optimization_engine.get_stat_upgrades(stats, skill_name, skill_level, top_n=top_n)
    return [u.to_dict() for u in upgrades]


def simulate_full_build(
    character_class: str,
    mastery: str,
    allocated_node_ids: list[int],
    nodes: list[dict],
    gear_affixes: list[dict],
    skill_name: str,
    skill_level: int = 20,
    n_simulations: int = 5_000,
    seed: int | None = None,
    passive_stats: dict | None = None,
) -> dict:
    """
    Full pipeline: stats → combat → defense → optimize.
    Equivalent to build_analysis_service.analyze_build() but from raw data.
    """
    log.info(
        "simulate_full_build",
        character_class=character_class,
        mastery=mastery,
        skill=skill_name,
        n=n_simulations,
        seed=seed,
    )
    stats = aggregate_stats(
        character_class=character_class,
        mastery=mastery,
        allocated_node_ids=allocated_node_ids,
        nodes=nodes,
        gear_affixes=gear_affixes,
        passive_stats=passive_stats,
    )

    dps_result = combat_engine.calculate_dps(stats, skill_name, skill_level)
    mc_result = combat_engine.monte_carlo_dps(stats, skill_name, skill_level, n=n_simulations, seed=seed)
    defense_result = defense_engine.calculate_defense(stats)
    upgrades = optimization_engine.get_stat_upgrades(stats, skill_name, skill_level, top_n=5)

    return {
        "primary_skill": skill_name,
        "skill_level": skill_level,
        "stats": stats.to_dict(),
        "dps": dps_result.to_dict(),
        "monte_carlo": mc_result.to_dict(),
        "defense": defense_result.to_dict(),
        "stat_upgrades": [u.to_dict() for u in upgrades],
        "seed": seed,
    }


def _build_stats_from_dict(d: dict) -> BuildStats:
    """Construct a BuildStats dataclass from a flat dict, ignoring unknown keys."""
    stats = BuildStats()
    for key, value in d.items():
        if hasattr(stats, key):
            try:
                setattr(stats, key, float(value))
            except (TypeError, ValueError):
                pass
    return stats
