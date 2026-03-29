"""
Skill Tree Resolver — reads allocated spec_tree node IDs for a skill and
accumulates their stat bonuses into dicts that the stat and combat engines
can apply.

Two kinds of output:
  build_stat_bonuses   dict[str, float]  — flat additions to BuildStats fields
                                           (e.g. attack_speed_pct += 10)
  skill_modifiers      dict[str, float]  — per-skill multipliers/additions used
                                           directly by calculate_dps:
    "more_damage_pct"       — multiplicative damage bonus (stacks as product)
    "added_hits_per_cast"   — extra hits per attack/cast (projectiles, etc.)
    "cast_speed_pct"        — additional cast speed specific to this skill
    "attack_speed_pct"      — additional attack speed specific to this skill
    "crit_chance_pct"       — additional crit chance specific to this skill
    "crit_multiplier_pct"   — additional crit multiplier specific to this skill
    "mana_cost_pct"         — mana cost modifier (not yet used in DPS calc)
    "area_pct"              — area modifier (not yet used in DPS calc)

Nodes whose descriptions contain mechanical transformations (e.g. "converts to
channelled", "Fireball pierces") are recorded in "special_effects" — they cannot
be summed numerically.

Description format used:
  "Flavor text. | Stat Label +value; Another Stat +value (downside)"
Everything after the pipe  |  is machine-parsed.
Values with "(downside)" are included as negative modifiers.
"""

import re
import os
import json
from functools import lru_cache

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
)
_SKILL_TREE_NODES_PATH = os.path.join(_DATA_DIR, "skill_tree_nodes.json")


# ---------------------------------------------------------------------------
# Stat label → BuildStats field  (single field)
# Composite labels handled in _apply_stat separately.
# ---------------------------------------------------------------------------

_STAT_LABEL_MAP: dict[str, str] = {
    # Damage (generic) — mapped to skill_modifiers "more_damage_pct"
    "damage":                        "_more_damage",
    "hit damage":                    "_more_damage",
    "hit damage against bleeding":   "_more_damage",
    "explosion damage":              "_more_damage",
    "final explosion damage":        "_more_damage",
    "middle explosion damage":       "_more_damage",
    "initial slam damage":           "_more_damage",
    "third strike damage":           "_more_damage",
    "damage per second":             "_more_damage",
    # Element-specific damage → add to per-skill scaling stats
    "fire damage":                   "fire_damage_pct",
    "cold damage":                   "cold_damage_pct",
    "lightning damage":              "lightning_damage_pct",
    "void damage":                   "void_damage_pct",
    "necrotic damage":               "necrotic_damage_pct",
    "poison damage":                 "poison_damage_pct",
    "physical damage":               "physical_damage_pct",
    "spell damage":                  "spell_damage_pct",
    "melee damage":                  "melee_damage_pct",
    "melee physical damage":         "physical_damage_pct",
    "melee fire damage":             "fire_damage_pct",
    "melee cold damage":             "cold_damage_pct",
    "melee lightning damage":        "lightning_damage_pct",
    "spell cold damage":             "cold_damage_pct",
    "damage over time":              "dot_damage_pct",
    # Speed
    "attack speed":                  "_skill_attack_speed_pct",
    "melee attack speed":            "_skill_attack_speed_pct",
    "cast speed":                    "_skill_cast_speed_pct",
    "speed and range":               "_skill_attack_speed_pct",
    # Crit
    "base crit chance":              "crit_chance_pct",
    "critical chance":               "crit_chance_pct",
    "crit chance":                   "crit_chance_pct",
    "critical strike chance":        "crit_chance_pct",
    "base critical strike chance":   "crit_chance_pct",
    "critical multiplier":           "crit_multiplier_pct",
    "critical strike multiplier":    "crit_multiplier_pct",
    # Defense
    "armor":                         "armour",
    "armour":                        "armour",
    "health":                        "max_health",
    "health leech":                  "leech",
    "health regen":                  "health_regen",
    "dodge rating":                  "dodge_rating",
    "block chance":                  "block_chance",
    "block effectiveness":           "block_effectiveness",
    "ward retention":                "ward_retention_pct",
    "physical resistance":           "physical_res",
    "cold resistance":               "cold_res",
    "fire resistance":               "fire_res",
    "elemental resistance":          "_elemental_res",
    # Ailment
    "bleed chance":                  "bleed_chance_pct",
    "ignite chance":                 "ignite_chance_pct",
    "ignite chance per second":      "ignite_chance_pct",
    "poison chance":                 "poison_chance_pct",
    "shock chance":                  "shock_chance_pct",
    "chill chance":                  "chill_chance_pct",
    "slow chance":                   "slow_chance_pct",
    # Shred
    "armor shred chance":            "armour_shred_chance",
    "armour shred chance":           "armour_shred_chance",
    "physical res shred chance":     "armour_shred_chance",
    "fire resistance shred chance":  "fire_shred_chance",
    "cold resistance shred chance":  "cold_shred_chance",
    # Penetration
    "fire penetration":              "fire_penetration",
    "cold penetration":              "cold_penetration",
    "lightning penetration":         "lightning_penetration",
    "void penetration":              "void_penetration",
    "physical penetration":          "physical_penetration",
    # Area / utility
    "area":                          "area_pct",
    "melee area":                    "area_pct",
    "cooldown recovery speed":       "cooldown_recovery_speed",
    "movespeed":                     "movement_speed",
    "mana efficiency":               "mana_efficiency_pct",
    # Projectiles → hits per cast
    "extra projectiles":             "_added_hits_per_cast",
    "additional projectiles":        "_added_hits_per_cast",
    "additional chains":             "_added_hits_per_cast",
}

# Composite → multiple fields (handled in _apply_stat_to_result)
_COMPOSITE_STAT_LABELS: dict[str, list[str]] = {
    "attack and cast speed": ["_skill_attack_speed_pct", "_skill_cast_speed_pct"],
}


# ---------------------------------------------------------------------------
# Data loader
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _load_skill_tree_nodes() -> dict:
    if not os.path.exists(_SKILL_TREE_NODES_PATH):
        log.warning("skill_tree_resolver: skill_tree_nodes.json not found")
        return {}
    with open(_SKILL_TREE_NODES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_tree_for_skill(skill_name: str) -> dict | None:
    """Return the tree dict for a skill name (case-insensitive), or None."""
    trees = _load_skill_tree_nodes()
    lower = skill_name.lower()
    for tree_code, tree in trees.items():
        if tree.get("skill_name", "").lower() == lower:
            return {"code": tree_code, **tree}
    return None


# ---------------------------------------------------------------------------
# Value parser
# ---------------------------------------------------------------------------

_VALUE_RE = re.compile(
    r"([+\-])?\s*(\d+(?:\.\d+)?)\s*(%|x)?$"
)


def _parse_value(raw: str) -> float | None:
    """Parse a stat value string like '+10%', '-5', '20x' → float."""
    raw = raw.strip().rstrip("(downside)")
    m = _VALUE_RE.match(raw.strip())
    if not m:
        return None
    sign, digits, _ = m.groups()
    value = float(digits)
    if sign == "-":
        value = -value
    return value


# ---------------------------------------------------------------------------
# Stat line parser
# ---------------------------------------------------------------------------

_STAT_SPLIT_RE = re.compile(r";\s*")
_DOWNSIDE_RE = re.compile(r"\(downside\)", re.I)
_LABEL_VALUE_RE = re.compile(
    r"^(.*?)\s*([+\-]?\s*\d+(?:\.\d+)?(?:\s*%|x)?)\s*(\(downside\))?$",
    re.I,
)


def _parse_stat_line(raw_line: str) -> tuple[str, float, bool] | None:
    """
    Parse a single stat fragment like 'Fire Penetration +10%' or 'Mana Cost +33% (downside)'.
    Returns (label_lower, value, is_downside) or None.
    """
    raw = raw_line.strip()
    m = _LABEL_VALUE_RE.match(raw)
    if not m:
        return None
    label = m.group(1).strip().lower()
    val_str = m.group(2).strip()
    is_downside = bool(m.group(3))

    value = _parse_value(val_str)
    if value is None:
        return None
    # Downside means the stat is a penalty even if value is positive-looking
    if is_downside:
        value = -abs(value)
    return label, value, is_downside


def _parse_description(description: str, points_allocated: int, max_points: int) -> dict:
    """
    Parse a node description and return stat deltas scaled by points_allocated.

    Returns:
      {
        "build_stats": {field: value, ...},   # goes to BuildStats
        "skill_mods":  {key: value, ...},     # goes to skill_modifiers
        "special_effects": [str, ...],         # unmodelable mechanics
      }
    """
    build_stats: dict[str, float] = {}
    skill_mods: dict[str, float] = {}
    special_effects: list[str] = []

    if not description or "|" not in description:
        if description:
            special_effects.append(description.strip())
        return {"build_stats": build_stats, "skill_mods": skill_mods, "special_effects": special_effects}

    # Scale per-point: value in description is for 1 point invested, × points_allocated.
    # BUT max_points == 1 → value is the full node value already.
    # max_points > 1 → each point gives value/max_points? No — in LE, each point IS the step.
    # The description shows the per-point stat increase. Scale by actual points.
    scale = points_allocated  # one application per point

    stat_text = description.split("|", 1)[1].strip()

    for fragment in _STAT_SPLIT_RE.split(stat_text):
        fragment = fragment.strip()
        if not fragment:
            continue

        parsed = _parse_stat_line(fragment)
        if not parsed:
            special_effects.append(fragment)
            continue

        label, value, is_downside = parsed
        scaled_value = value * scale

        # Check composite labels first
        composite_fields = _COMPOSITE_STAT_LABELS.get(label)
        if composite_fields:
            for field in composite_fields:
                _accumulate(field, scaled_value, build_stats, skill_mods)
            continue

        # Single-field mapping
        field = _STAT_LABEL_MAP.get(label)
        if field:
            _accumulate(field, scaled_value, build_stats, skill_mods)
        else:
            special_effects.append(fragment)

    return {"build_stats": build_stats, "skill_mods": skill_mods, "special_effects": special_effects}


def _accumulate(field: str, value: float, build_stats: dict, skill_mods: dict) -> None:
    """Route a field to either build_stats or skill_mods bucket."""
    if field == "_more_damage":
        skill_mods["more_damage_pct"] = skill_mods.get("more_damage_pct", 0.0) + value
    elif field == "_skill_attack_speed_pct":
        skill_mods["attack_speed_pct"] = skill_mods.get("attack_speed_pct", 0.0) + value
    elif field == "_skill_cast_speed_pct":
        skill_mods["cast_speed_pct"] = skill_mods.get("cast_speed_pct", 0.0) + value
    elif field == "_added_hits_per_cast":
        skill_mods["added_hits_per_cast"] = skill_mods.get("added_hits_per_cast", 0.0) + value
    elif field == "_elemental_res":
        for res in ("fire_res", "cold_res", "lightning_res"):
            build_stats[res] = build_stats.get(res, 0.0) + value
    else:
        build_stats[field] = build_stats.get(field, 0.0) + value


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def resolve_skill_tree_stats(
    skill_name: str,
    spec_tree: list[dict],
) -> dict:
    """
    Accumulate all stat bonuses from a skill's allocated spec tree nodes.

    Args:
        skill_name:  e.g. "Fireball"
        spec_tree:   list of {"node_id": int, "points": int} dicts
                     (the BuildSkill.spec_tree JSON field)

    Returns:
        {
            "skill_name": str,
            "build_stat_bonuses": {field: total_value, ...},
            "skill_modifiers":    {
                "more_damage_pct":    float,   # sum of all "Damage +X%" nodes
                "added_hits_per_cast": float,  # extra projectiles / chains
                "attack_speed_pct":  float,
                "cast_speed_pct":    float,
                "crit_chance_pct":   float,
                "crit_multiplier_pct": float,
            },
            "special_effects":    [str, ...],
        }
    """
    if not spec_tree:
        return _empty_result(skill_name)

    tree_data = get_tree_for_skill(skill_name)
    if not tree_data:
        log.warning("resolve_skill_tree_stats: no tree found for skill", skill=skill_name)
        return _empty_result(skill_name)

    node_by_id: dict[int, dict] = {n["id"]: n for n in tree_data["nodes"]}

    build_stat_bonuses: dict[str, float] = {}
    skill_modifiers: dict[str, float] = {}
    special_effects: list[str] = []

    for allocation in spec_tree:
        node_id = allocation.get("node_id")
        points = int(allocation.get("points", 1))
        if points <= 0 or node_id is None:
            continue

        node = node_by_id.get(node_id)
        if not node:
            log.debug("resolve_skill_tree_stats: unknown node_id", skill=skill_name, node_id=node_id)
            continue

        max_pts = node.get("maxPoints", 1) or 1
        clamped_points = min(points, max_pts)

        result = _parse_description(
            node.get("description") or "",
            clamped_points,
            max_pts,
        )

        for field, val in result["build_stats"].items():
            build_stat_bonuses[field] = build_stat_bonuses.get(field, 0.0) + val

        for key, val in result["skill_mods"].items():
            skill_modifiers[key] = skill_modifiers.get(key, 0.0) + val

        special_effects.extend(result["special_effects"])

    return {
        "skill_name": skill_name,
        "build_stat_bonuses": build_stat_bonuses,
        "skill_modifiers": skill_modifiers,
        "special_effects": special_effects,
    }


def _empty_result(skill_name: str) -> dict:
    return {
        "skill_name": skill_name,
        "build_stat_bonuses": {},
        "skill_modifiers": {},
        "special_effects": [],
    }
