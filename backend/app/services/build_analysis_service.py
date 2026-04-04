"""
Build Analysis Service — orchestrates the engine pipeline for a full build analysis.

Pipeline: build → stat_engine → combat_engine → defense_engine → optimization_engine → output

Extracted from build_service.py so the orchestration layer is separate from CRUD.
"""

import re

from app.models import Build
from app.engines import stat_engine, combat_engine, defense_engine, optimization_engine
from app.services.passive_stat_resolver import resolve_passive_stats
from app.services.skill_tree_resolver import resolve_skill_tree_stats
from app.utils.exceptions import BuildValidationError

# ---------------------------------------------------------------------------
# Unique item stat extraction
# ---------------------------------------------------------------------------

# Maps human-readable stat fragments from unique affix/implicit strings → BuildStats field
_UNIQUE_STAT_PATTERNS: list[tuple[re.Pattern, str]] = [
    (re.compile(r"increased fire damage", re.I), "fire_damage_pct"),
    (re.compile(r"increased cold damage", re.I), "cold_damage_pct"),
    (re.compile(r"increased lightning damage", re.I), "lightning_damage_pct"),
    (re.compile(r"increased necrotic damage", re.I), "necrotic_damage_pct"),
    (re.compile(r"increased void damage", re.I), "void_damage_pct"),
    (re.compile(r"increased poison damage", re.I), "poison_damage_pct"),
    (re.compile(r"increased physical damage", re.I), "physical_damage_pct"),
    (re.compile(r"increased spell damage", re.I), "spell_damage_pct"),
    (re.compile(r"increased elemental damage", re.I), "elemental_damage_pct"),
    (re.compile(r"increased melee damage", re.I), "melee_damage_pct"),
    (re.compile(r"increased minion damage", re.I), "minion_damage_pct"),
    (re.compile(r"increased damage over time", re.I), "dot_damage_pct"),
    (re.compile(r"fire cast speed|fire.+cast speed", re.I), "cast_speed"),
    (re.compile(r"increased cast speed", re.I), "cast_speed"),
    (re.compile(r"increased attack speed", re.I), "attack_speed_pct"),
    (re.compile(r"spell critical multiplier|critical strike multiplier", re.I), "crit_multiplier_pct"),
    (re.compile(r"critical strike chance|critical chance", re.I), "crit_chance_pct"),
    (re.compile(r"fire resistance", re.I), "fire_res"),
    (re.compile(r"cold resistance", re.I), "cold_res"),
    (re.compile(r"lightning resistance", re.I), "lightning_res"),
    (re.compile(r"void resistance", re.I), "void_res"),
    (re.compile(r"necrotic resistance", re.I), "necrotic_res"),
    (re.compile(r"poison resistance", re.I), "poison_res"),
    (re.compile(r"physical resistance", re.I), "physical_res"),
    (re.compile(r"all resistances", re.I), "_all_res"),
    (re.compile(r"added health|max health|\+\d+.{0,10}health$", re.I), "max_health"),
    (re.compile(r"increased health$|increased maximum health", re.I), "health_pct"),
    (re.compile(r"armou?r", re.I), "armour"),
    (re.compile(r"dodge rating", re.I), "dodge_rating"),
    (re.compile(r"block chance", re.I), "block_chance"),
    (re.compile(r"endurance threshold", re.I), "endurance_threshold"),
    (re.compile(r"endurance$", re.I), "endurance"),
    (re.compile(r"ward retention", re.I), "ward_retention_pct"),
    (re.compile(r"ward per second|ward regen", re.I), "ward_regen"),
    (re.compile(r"added ward|maximum ward", re.I), "ward"),
    (re.compile(r"mana before health", re.I), "hybrid_health"),
    (re.compile(r"increased mana$|maximum mana|added mana", re.I), "max_mana"),
    (re.compile(r"mana regeneration|mana regen", re.I), "mana_regen"),
    (re.compile(r"health regeneration|health regen", re.I), "health_regen"),
    (re.compile(r"leech", re.I), "leech"),
    (re.compile(r"health on kill", re.I), "health_on_kill"),
    (re.compile(r"ward on kill", re.I), "ward_on_kill"),
    (re.compile(r"strength$", re.I), "strength"),
    (re.compile(r"intelligence$", re.I), "intelligence"),
    (re.compile(r"dexterity$", re.I), "dexterity"),
    (re.compile(r"vitality$", re.I), "vitality"),
    (re.compile(r"attunement$", re.I), "attunement"),
    (re.compile(r"all attributes", re.I), "_all_attributes"),
    (re.compile(r"movement speed", re.I), "movement_speed"),
    (re.compile(r"area.{0,10}skills|increased area", re.I), "area_pct"),
    (re.compile(r"void penetration", re.I), "void_penetration"),
    (re.compile(r"fire penetration", re.I), "fire_penetration"),
    (re.compile(r"cold penetration", re.I), "cold_penetration"),
    (re.compile(r"lightning penetration", re.I), "lightning_penetration"),
    (re.compile(r"necrotic penetration", re.I), "necrotic_penetration"),
    (re.compile(r"physical penetration", re.I), "physical_penetration"),
    (re.compile(r"poison chance|chance to poison", re.I), "poison_chance_pct"),
    (re.compile(r"ignite chance|chance to ignite", re.I), "ignite_chance_pct"),
    (re.compile(r"bleed chance|chance.+bleed", re.I), "bleed_chance_pct"),
    (re.compile(r"shock chance|chance to shock", re.I), "shock_chance_pct"),
]

# Matches: "+20–80%" or "+20-80%" or "+5" or "6%" etc. — captures the numeric range/value
_RANGE_RE = re.compile(r"\+?(\d+(?:\.\d+)?)\s*[–\-]\s*(\d+(?:\.\d+)?)|(?:\+|(?<=\s))(\d+(?:\.\d+)?)\s*%?")


def _midpoint(raw: str) -> float | None:
    """Parse a range like '20–80' or single value '20' from a stat string, return midpoint."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*[–\-]\s*(\d+(?:\.\d+)?)", raw)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    m = re.search(r"\+?(\d+(?:\.\d+)?)", raw)
    if m:
        return float(m.group(1))
    return None


def _extract_unique_affixes(unique: dict) -> list[dict]:
    """
    Parse a unique item's implicit + affix strings into synthetic gear affix dicts
    that the stat engine can consume directly via stat_key.

    Returns a list of {"stat_key": str, "value": float} dicts.
    These are injected into gear_affixes and handled as a special path in aggregate_stats.
    """
    results: list[dict] = []
    sources = []

    # Parse implicit (single string, may contain semicolons for multiple stats)
    implicit = unique.get("implicit", "")
    if implicit:
        sources.extend(s.strip() for s in implicit.split(";") if s.strip())

    # Parse affix strings
    for affix_str in (unique.get("affixes") or []):
        sources.append(affix_str.strip())

    for raw in sources:
        value = _midpoint(raw)
        if value is None:
            continue
        for pattern, stat_key in _UNIQUE_STAT_PATTERNS:
            if pattern.search(raw):
                results.append({"stat_key": stat_key, "value": value})
                break  # one stat per line

    return results


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

    # Build a map from raw_node_id (int, stored in build.passive_tree) → namespaced string id
    # so we can pass real DB stats to both the resolver and aggregate_stats.
    raw_id_to_str = {n.raw_node_id: n.id for n in db_nodes}
    nodes = [
        {"id": n.raw_node_id, "str_id": n.id, "type": n.node_type, "name": n.name}
        for n in db_nodes
    ]

    # Flatten all gear affixes across slots; also extract stats from equipped unique items
    gear_affixes = []
    for slot in (build.gear or []):
        slot_affixes = slot.get("affixes") or []
        item_name = slot.get("item_name")

        if slot_affixes:
            gear_affixes.extend(slot_affixes)
        elif item_name:
            # Gear slot has a unique item but no structured affixes — parse stats from
            # uniques.json so they contribute to the simulation.
            from app.game_data.game_data_loader import get_all_uniques
            uniques = get_all_uniques()
            unique = next((u for u in uniques if u.get("name") == item_name), None)
            if unique:
                gear_affixes.extend(_extract_unique_affixes(unique))

    # Primary skill: first slot with a skill name, fallback to empty
    primary_skill = None
    skill_level = 20
    primary_spec_tree: list[int] = []
    sorted_skills = sorted(build.skills, key=lambda s: s.slot)
    if sorted_skills:
        primary_skill = sorted_skills[0].skill_name or None
        skill_level = max(1, sorted_skills[0].points_allocated or 20)
        primary_spec_tree = sorted_skills[0].spec_tree or []

    # Map build.passive_tree (list of ints) to DB namespaced string IDs, then resolve
    # real stat values from the PassiveNode.stats column.
    allocated_int_ids = [nid for nid in (build.passive_tree or []) if isinstance(nid, int)]
    allocated_str_ids = [raw_id_to_str[nid] for nid in allocated_int_ids if nid in raw_id_to_str]
    passive_stats = resolve_passive_stats(allocated_str_ids) if allocated_str_ids else None

    # Resolve skill spec tree stats.
    # spec_tree is stored as a flat list of node IDs (same node repeated per point):
    # [2, 2, 2, 6, 6, 7] means node 2 × 3pts, node 6 × 2pts, node 7 × 1pt.
    from collections import Counter
    spec_tree_allocations = []
    if primary_skill and primary_spec_tree:
        counts = Counter(primary_spec_tree)
        spec_tree_allocations = [{"node_id": nid, "points": pts} for nid, pts in counts.items()]

    skill_tree_result = resolve_skill_tree_stats(primary_skill or "", spec_tree_allocations)

    # 1. Aggregate stats (base stats + passives + gear)
    stats = stat_engine.aggregate_stats(
        character_class=build.character_class,
        mastery=build.mastery,
        allocated_node_ids=allocated_int_ids,
        nodes=nodes,
        gear_affixes=gear_affixes,
        passive_stats=passive_stats,
    )

    # Apply spec tree build-stat bonuses (e.g. node adds +10% fire res, +5% crit chance)
    if skill_tree_result["build_stat_bonuses"]:
        stat_engine._add_partial(stats, skill_tree_result["build_stat_bonuses"])

    # 2. DPS — pass skill_modifiers from spec tree
    dps_result = combat_engine.calculate_dps(
        stats, primary_skill or "", skill_level,
        skill_modifiers=skill_tree_result["skill_modifiers"],
    )

    # 3. Monte Carlo DPS variance (5k sims — lighter than backend 10k)
    mc_result = combat_engine.monte_carlo_dps(
        stats, primary_skill or "", skill_level, n=5_000,
        skill_modifiers=skill_tree_result["skill_modifiers"],
    )

    # 3b. Per-skill DPS for all occupied skill slots (rotation breakdown).
    # Each skill uses its own spec_tree modifiers; build-wide stats are shared.
    # combined_dps is a naive sum (rotation ceiling — assumes all skills active simultaneously).
    dps_per_skill = []
    combined_dps = 0.0
    for skill in sorted_skills:
        s_name = skill.skill_name or None
        if not s_name:
            continue
        s_level = max(1, skill.points_allocated or 20)
        s_spec_tree = skill.spec_tree or []
        s_counts = Counter(s_spec_tree)
        s_allocations = [{"node_id": nid, "points": pts} for nid, pts in s_counts.items()]
        s_tree_result = resolve_skill_tree_stats(s_name, s_allocations)
        s_dps = combat_engine.calculate_dps(
            stats, s_name, s_level,
            skill_modifiers=s_tree_result["skill_modifiers"],
        )
        dps_per_skill.append({
            "skill_name": s_name,
            "skill_level": s_level,
            "slot": skill.slot,
            "dps": round(s_dps.dps),
            "total_dps": round(s_dps.total_dps),
            "is_primary": skill.slot == sorted_skills[0].slot,
        })
        combined_dps += s_dps.total_dps

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
        "skill_tree_modifiers": skill_tree_result["skill_modifiers"],
        "skill_tree_special_effects": skill_tree_result["special_effects"][:10],
        "dps_per_skill": dps_per_skill,
        "combined_dps": round(combined_dps),
    }
