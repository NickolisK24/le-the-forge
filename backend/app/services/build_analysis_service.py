"""
Build Analysis Service — orchestrates the engine pipeline for a full build analysis.

Pipeline: build → stat_engine → combat_engine → defense_engine → optimization_engine → output

Extracted from build_service.py so the orchestration layer is separate from CRUD.
"""

from app.models import Build
from app.engines import stat_engine, combat_engine, defense_engine, optimization_engine
from app.utils.exceptions import BuildValidationError


def analyze_build(build: Build) -> dict:
    """
    Run the full simulation pipeline for a build.

    Returns:
        {
            primary_skill, skill_level,
            stats,          # all aggregated BuildStats fields
            dps,            # DPSResult
            monte_carlo,    # MonteCarloDPS (5k simulations)
            defense,        # DefenseResult incl. EHP, dodge, ward sustainability
            stat_upgrades,  # top 5 StatUpgrade ranked by DPS gain
        }

    Raises:
        BuildValidationError: if the build is missing required data.
    """
    from app.models import PassiveNode

    if not build.character_class or not build.mastery:
        raise BuildValidationError("Build is missing character class or mastery.")

    if not build.skills or len(build.skills) == 0:
        raise BuildValidationError(
            "Build has no skills assigned. Add at least one skill to simulate."
        )

    # Load passive nodes for the build's class
    db_nodes = PassiveNode.query.filter_by(character_class=build.character_class).all()
    nodes = [{"id": n.id, "type": n.node_type, "name": n.name} for n in db_nodes]

    # Flatten all gear affixes across slots
    gear_affixes = []
    for slot in (build.gear or []):
        for affix in slot.get("affixes", []):
            gear_affixes.append(affix)

    # Primary skill: first slot with a skill name, fallback to empty
    primary_skill = None
    skill_level = 20
    sorted_skills = sorted(build.skills, key=lambda s: s.slot)
    if sorted_skills:
        primary_skill = sorted_skills[0].skill_name or None
        skill_level = max(1, sorted_skills[0].points_allocated or 20)

    # 1. Aggregate stats
    stats = stat_engine.aggregate_stats(
        character_class=build.character_class,
        mastery=build.mastery,
        allocated_node_ids=build.passive_tree or [],
        nodes=nodes,
        gear_affixes=gear_affixes,
    )

    # 2. DPS
    dps_result = combat_engine.calculate_dps(stats, primary_skill or "", skill_level)

    # 3. Monte Carlo DPS variance (5k sims — lighter than backend 10k)
    mc_result = combat_engine.monte_carlo_dps(stats, primary_skill or "", skill_level, n=5_000)

    # 4. Defense
    defense_result = defense_engine.calculate_defense(stats)

    # 5. Upgrade advisor
    upgrades = optimization_engine.get_stat_upgrades(
        stats, primary_skill or "", skill_level, top_n=5
    )

    return {
        "primary_skill": primary_skill,
        "skill_level": skill_level,
        "stats": stats.to_dict(),
        "dps": dps_result.to_dict(),
        "monte_carlo": mc_result.to_dict(),
        "defense": defense_result.to_dict(),
        "stat_upgrades": [u.to_dict() for u in upgrades],
    }
