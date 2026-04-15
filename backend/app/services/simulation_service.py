"""
Simulation Service — stateless orchestration of engine calls.

Unlike build_analysis_service (which requires a saved Build model),
this service accepts raw data dicts and delegates to engines directly.
This allows the frontend to call simulation endpoints without persisting
a build first.
"""

from app.domain.skill_modifiers import SkillModifiers
from app.engines import stat_engine, combat_engine, defense_engine, optimization_engine
from app.engines.stat_engine import BuildStats
from app.skills.skill_classifier import classify_skill, classify_skills, detect_primary_skill
from app.utils.exceptions import SimulationError, BuildValidationError
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


def _resolve_skill_modifiers(
    skill_name: str,
    spec_tree: list[dict] | None,
    stats: BuildStats,
) -> SkillModifiers | None:
    """Resolve skill tree nodes into SkillModifiers and merge build stat bonuses.

    Returns None if no spec_tree is provided (backward compatible).
    When spec_tree is provided, also merges build_stat_bonuses into the
    already-resolved BuildStats object.
    """
    if not spec_tree:
        return None
    try:
        from app.services.skill_tree_resolver import resolve_skill_tree_stats
        result = resolve_skill_tree_stats(skill_name, spec_tree)
        # Merge build stat bonuses into the existing BuildStats
        for stat_key, value in result.get("build_stat_bonuses", {}).items():
            if hasattr(stats, stat_key):
                current = getattr(stats, stat_key)
                setattr(stats, stat_key, current + value)
        return result.get("skill_modifiers")
    except Exception as exc:
        log.warning("resolve_skill_modifiers.failed", skill=skill_name, error=str(exc))
        return None


def _extract_conversions(
    skill_name: str,
    spec_tree: list[dict] | None,
) -> list:
    """Extract DamageConversion objects from the skill's allocated tree.

    Returns an empty list when ``spec_tree`` is missing/empty or when
    extraction fails for any reason — never raises. Callers can pass the
    result straight to ``calculate_dps`` / ``get_stat_upgrades`` as the
    ``conversions`` argument.
    """
    if not spec_tree:
        return []
    try:
        from app.services.skill_tree_resolver import extract_damage_conversions
        return extract_damage_conversions(skill_name, spec_tree)
    except Exception as exc:
        log.warning("extract_conversions.failed", skill=skill_name, error=str(exc))
        return []


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
    spec_tree: list[dict] | None = None,
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

    # Resolve skill tree modifiers if spec_tree is provided
    sm = _resolve_skill_modifiers(skill_name, spec_tree, stats)

    # Pull damage-type conversions allocated in the skill tree so the DPS
    # layer applies them. Without this, conversion nodes (e.g. phys → fire)
    # are silently dropped and the per-type damage breakdown is wrong.
    conversions = _extract_conversions(skill_name, spec_tree)

    dps_result = combat_engine.calculate_dps(
        stats, skill_name, skill_level,
        skill_modifiers=sm, conversions=conversions,
    )
    mc_result = combat_engine.monte_carlo_dps(
        stats, skill_name, skill_level,
        n=n_simulations, seed=seed,
        skill_modifiers=sm, conversions=conversions,
    )

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
    conversions: list | None = None,
    spec_tree: list[dict] | None = None,
) -> list[dict]:
    """Rank stat upgrades by DPS/EHP gain from a stats dict.

    ``conversions`` is an optional list of ``DamageConversion`` objects
    describing skill-tree conversion nodes. When present, it is forwarded
    to :func:`optimization_engine.get_stat_upgrades` so that %-damage
    filtering reflects the post-conversion damage profile.

    ``spec_tree`` is the per-skill allocation list consumed by
    :func:`skill_tree_resolver.extract_damage_conversions`. When
    provided, conversions are derived from it via ``_extract_conversions``
    and override the ``conversions`` kwarg — most callers should use this
    rather than constructing ``DamageConversion`` objects themselves.
    """
    log.info("simulate_optimize", skill=skill_name, top_n=top_n)
    stats = _build_stats_from_dict(stats_dict)

    if spec_tree:
        conversions = _extract_conversions(skill_name, spec_tree)

    upgrades = optimization_engine.get_stat_upgrades(
        stats, skill_name, skill_level, top_n=top_n, conversions=conversions,
    )
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
    spec_tree: list[dict] | None = None,
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

    # Resolve skill tree modifiers and merge build stat bonuses
    sm = _resolve_skill_modifiers(skill_name, spec_tree, stats)

    # Pull damage-type conversions allocated in the skill tree so the DPS
    # layer and the optimizer both see the correct post-conversion damage
    # profile (otherwise tree-level phys→fire / etc. is silently dropped).
    conversions = _extract_conversions(skill_name, spec_tree)

    dps_result = combat_engine.calculate_dps(
        stats, skill_name, skill_level,
        skill_modifiers=sm, conversions=conversions,
    )
    mc_result = combat_engine.monte_carlo_dps(
        stats, skill_name, skill_level,
        n=n_simulations, seed=seed,
        skill_modifiers=sm, conversions=conversions,
    )
    defense_result = defense_engine.calculate_defense(stats)
    upgrades = optimization_engine.get_stat_upgrades(
        stats, skill_name, skill_level, top_n=5, conversions=conversions,
    )

    # Auto-detect primary skill from skill loadout if available
    build_skills = kwargs.get("skills", []) if "kwargs" in dir() else []
    skill_classifications = classify_skills([skill_name]) if skill_name else {}
    detected_primary = skill_name  # fallback to the passed skill_name

    return {
        "primary_skill": detected_primary,
        "skill_level": skill_level,
        "skill_classifications": skill_classifications,
        "stats": stats.to_dict(),
        "dps": dps_result.to_dict(),
        "monte_carlo": mc_result.to_dict(),
        "defense": defense_result.to_dict(),
        "stat_upgrades": [u.to_dict() for u in upgrades],
        "seed": seed,
    }


def simulate_sensitivity(
    stats_dict: dict,
    skill_name: str,
    skill_level: int = 20,
    stat_keys: list[str] | None = None,
    delta: float = 10.0,
) -> list[dict]:
    """Stat sensitivity analysis — which stats give the most marginal value."""
    log.info("simulate_sensitivity", skill=skill_name, delta=delta)
    stats = _build_stats_from_dict(stats_dict)
    return optimization_engine.stat_sensitivity(
        stats, skill_name, skill_level, stat_keys=stat_keys, delta=delta
    )


def run_encounter_from_build(
    build_dict: dict,
    encounter_dict: dict | None = None,
) -> dict:
    """
    Compile a BuildDefinition dict → stats → encounter simulation.

    build_dict:     validated BuildDefinitionSchema payload
    encounter_dict: validated SimulateEncounterSchema payload (optional overrides)
    """
    from builds.build_definition  import BuildDefinition
    from builds.build_stats_engine import BuildStatsEngine

    build   = BuildDefinition.from_dict(build_dict)
    engine  = BuildStatsEngine()
    params  = engine.to_encounter_params(build)

    # Merge encounter overrides (template, duration, distribution, etc.)
    enc = encounter_dict or {}
    return run_encounter_simulation(
        base_damage     = params["base_damage"],
        crit_chance     = params["crit_chance"],
        crit_multiplier = params["crit_multiplier"],
        enemy_template  = enc.get("enemy_template",  "STANDARD_BOSS"),
        fight_duration  = enc.get("fight_duration",  60.0),
        tick_size       = enc.get("tick_size",        0.1),
        distribution    = enc.get("distribution",    "SINGLE"),
    )


def run_encounter_simulation(
    base_damage: float,
    enemy_template: str = "TRAINING_DUMMY",
    fight_duration: float = 60.0,
    tick_size: float = 0.1,
    distribution: str = "SINGLE",
    crit_chance: float = 0.05,
    crit_multiplier: float = 2.0,
) -> dict:
    """Run a Phase C encounter simulation and return serialised results."""
    from encounter.boss_templates import (
        TRAINING_DUMMY, STANDARD_BOSS, SHIELDED_BOSS, ADD_FIGHT, MOVEMENT_BOSS,
        load_template,
    )
    from encounter.multi_target import HitDistribution, MultiHitConfig
    from encounter.state_machine import EncounterMachine

    _template_map = {
        "TRAINING_DUMMY": TRAINING_DUMMY,
        "STANDARD_BOSS":  STANDARD_BOSS,
        "SHIELDED_BOSS":  SHIELDED_BOSS,
        "ADD_FIGHT":      ADD_FIGHT,
        "MOVEMENT_BOSS":  MOVEMENT_BOSS,
    }
    template = _template_map[enemy_template]

    _dist_map = {
        "SINGLE": HitDistribution.SINGLE,
        "CLEAVE": HitDistribution.CLEAVE,
        "SPLIT":  HitDistribution.SPLIT,
        "CHAIN":  HitDistribution.CHAIN,
    }
    hit_config = MultiHitConfig(
        distribution=_dist_map[distribution],
        crit_chance=crit_chance,
        crit_multiplier=crit_multiplier,
        # rng_hit/rng_crit left at None so the engine uses real random rolls
    )

    cfg = load_template(template, base_damage=base_damage, hit_config=hit_config)
    # Override fight_duration/tick_size when caller provides explicit values
    from dataclasses import replace
    cfg = replace(cfg, fight_duration=fight_duration, tick_size=tick_size)

    result = EncounterMachine(cfg).run()

    elapsed_ticks = result.ticks_simulated
    dps = result.total_damage / result.elapsed_time if result.elapsed_time > 0 else 0.0

    log.info(
        "run_encounter_simulation",
        template=enemy_template,
        base_damage=base_damage,
        total_damage=result.total_damage,
        dps=round(dps, 2),
    )

    return {
        "total_damage":    result.total_damage,
        "dps":             dps,
        "elapsed_time":    result.elapsed_time,
        "ticks_simulated": elapsed_ticks,
        "all_enemies_dead": result.all_enemies_dead,
        "enemies_killed":  result.enemies_killed,
        "total_casts":     result.total_casts,
        "downtime_ticks":  result.downtime_ticks,
        "active_phase_id": result.active_phase_id,
        "damage_per_tick": result.damage_per_tick,
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
