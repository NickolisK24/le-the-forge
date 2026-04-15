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
from app.domain.calculators.conversion_calculator import DamageConversion
from app.domain.calculators.damage_type_router import DamageType
from app.domain.passive import SkillTreeStats
from app.domain.skill_modifiers import SkillModifiers
from functools import lru_cache

from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

_DATA_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "data")
)
_SKILL_TREE_NODES_PATH = os.path.join(_DATA_DIR, "classes", "skill_tree_nodes.json")


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
    skill_mods = SkillModifiers()
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


def _accumulate(field: str, value: float, build_stats: dict, skill_mods: SkillModifiers) -> None:
    """Route a field to either build_stats or skill_mods bucket."""
    if field == "_more_damage":
        skill_mods.more_damage_pct += value
    elif field == "_skill_attack_speed_pct":
        skill_mods.attack_speed_pct += value
    elif field == "_skill_cast_speed_pct":
        skill_mods.cast_speed_pct += value
    elif field == "_added_hits_per_cast":
        skill_mods.added_hits_per_cast += int(value)
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
) -> SkillTreeStats:
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
    skill_modifiers = SkillModifiers()
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

        sm = result["skill_mods"]  # SkillModifiers from _parse_description
        skill_modifiers.more_damage_pct += sm.more_damage_pct
        skill_modifiers.added_hits_per_cast += sm.added_hits_per_cast
        skill_modifiers.attack_speed_pct += sm.attack_speed_pct
        skill_modifiers.cast_speed_pct += sm.cast_speed_pct
        skill_modifiers.crit_chance_pct += sm.crit_chance_pct
        skill_modifiers.crit_multiplier_pct += sm.crit_multiplier_pct

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
        "skill_modifiers": SkillModifiers(),
        "special_effects": [],
    }


# ---------------------------------------------------------------------------
# Damage type conversion extraction
# ---------------------------------------------------------------------------
#
# The skill tree node data file (skill_tree_nodes.json) is only partially
# machine-readable for conversions:
#
#   * Most conversion nodes describe the effect *only* in narrative text on
#     the left-hand side of the description's pipe separator
#     (e.g. "Base physical damage is converted to fire."). These cannot be
#     parsed reliably and are tracked as a data gap.
#   * A small number of nodes encode the conversion in the structured
#     stat-line side after the pipe, e.g.
#       "Base Physical Damage -> Cold Damage 100%"
#       "Physical -> Cold +100%"
#     These are extractable: source and target are both DamageType names,
#     separated by an arrow, with a trailing percentage.
#
# This parser handles the structured form. Lines whose source or target
# isn't a known DamageType, or whose suffix indicates a defensive /
# resistance / chance conversion (e.g. "Physical -> Cold Damage Taken 100%",
# "Physical -> Cold Res Shred 100%") are intentionally skipped.
# ---------------------------------------------------------------------------

_DAMAGE_NAMES = "physical|fire|cold|lightning|necrotic|void|poison"

# Match a single source-type → target-type damage-conversion fragment with
# an explicit percentage. Both sides must mention exactly one damage word,
# and the line must end with a percent value.
_CONVERSION_LINE_RE = re.compile(
    rf"\b({_DAMAGE_NAMES})\b[^->]*?\s*(?:->|→|=>)\s*"
    rf"\b({_DAMAGE_NAMES})\b[^%]*?([+\-]?\s*\d+(?:\.\d+)?)\s*%",
    re.I,
)

# Sub-strings that disqualify a fragment even if the regex matches —
# defensive ("damage taken"), resistance shred, or chance conversions all
# share the same arrow syntax but are not hit-damage conversions.
_NON_DAMAGE_KEYWORDS = (
    "damage taken",
    "res ",
    "resistance",
    "shred",
    "chance",
    "penetration",
)


def extract_damage_conversions(
    skill_name: str,
    spec_tree: list,
) -> list[DamageConversion]:
    """Extract :class:`DamageConversion` objects from a skill's allocated tree.

    Walks ``spec_tree`` (the same per-skill allocation list consumed by
    :func:`resolve_skill_tree_stats`), pulls each allocated node from the
    skill-tree data, and parses the structured side of its description for
    ``<source-type> -> <target-type> N%`` fragments.

    Returns an empty list — never raises — when:
      * ``spec_tree`` is empty;
      * the tree data isn't loaded or no tree matches ``skill_name``;
      * no allocated node carries a parseable conversion line.

    Per-point scaling matches :func:`_parse_description`: the fragment's
    percent value is multiplied by ``min(points, maxPoints)`` and the
    result is clamped to 100% (a single conversion can never exceed full).

    Caveat: the bulk of in-game conversion nodes describe their effect
    only in narrative text (left of the description's pipe). Those nodes
    are not machine-readable in the current data file and are therefore
    skipped. This is a known data gap, not a code error.
    """
    if not spec_tree:
        return []

    tree_data = get_tree_for_skill(skill_name)
    if not tree_data:
        log.debug(
            "extract_damage_conversions.no_tree_data",
            skill=skill_name,
        )
        return []

    nodes_by_id: dict[int, dict] = {
        n["id"]: n for n in tree_data.get("nodes", []) if "id" in n
    }

    conversions: list[DamageConversion] = []
    # Track allocated nodes whose description hints at a conversion (contains
    # "->" somewhere) so we can distinguish two outcomes:
    #   * no arrow nodes at all → expected silence (debug)
    #   * arrow nodes present but nothing parsed → data gap worth surfacing
    arrow_node_ids: list[int] = []

    for allocation in spec_tree:
        if not isinstance(allocation, dict):
            continue
        node_id = allocation.get("node_id")
        if node_id is None:
            continue
        try:
            points = int(allocation.get("points", 1))
        except (TypeError, ValueError):
            continue
        if points <= 0:
            continue

        node = nodes_by_id.get(node_id)
        if not node:
            continue

        description = node.get("description") or ""
        if "->" in description:
            arrow_node_ids.append(int(node_id))
        if "|" not in description:
            continue

        max_points = int(node.get("maxPoints", 1) or 1)
        clamped_points = min(points, max_points)

        structured = description.split("|", 1)[1]
        for fragment in structured.split(";"):
            frag = fragment.strip()
            if not frag:
                continue

            lower = frag.lower()
            if any(kw in lower for kw in _NON_DAMAGE_KEYWORDS):
                continue

            m = _CONVERSION_LINE_RE.search(frag)
            if not m:
                continue

            src_name = m.group(1).lower()
            tgt_name = m.group(2).lower()
            try:
                source = DamageType(src_name)
                target = DamageType(tgt_name)
            except ValueError:
                continue
            if source == target:
                continue

            try:
                pct_value = float(m.group(3).replace(" ", ""))
            except ValueError:
                continue

            scaled_pct = pct_value * clamped_points
            if scaled_pct <= 0:
                continue
            if scaled_pct > 100.0:
                scaled_pct = 100.0

            conversions.append(DamageConversion(source, target, scaled_pct))

    if not conversions:
        # Promote to warning when an allocated node's description mentions
        # "->" — those are conversion nodes whose narrative text couldn't be
        # parsed, so optimization will fall back to the static damage-type
        # list. Silent debug is only appropriate when no conversion-looking
        # nodes were allocated at all.
        if arrow_node_ids:
            log.warning(
                "extract_damage_conversions.no_machine_readable_conversions",
                skill=skill_name,
                narrative_conversion_node_count=len(arrow_node_ids),
                narrative_conversion_node_ids=arrow_node_ids,
                note=(
                    "allocated node(s) mention '->' in their description but "
                    "no structured conversion could be parsed; optimization "
                    "recommendations will not reflect post-conversion damage "
                    "types — tracked as a data gap, not a code error"
                ),
            )
        else:
            log.debug(
                "extract_damage_conversions.no_machine_readable_conversions",
                skill=skill_name,
                note=(
                    "no allocated node encodes a structured conversion; this "
                    "is expected for builds that don't use conversion nodes"
                ),
            )

    return conversions


def find_narrative_conversion_nodes(
    skill_name: str,
    spec_tree: list,
) -> list[int]:
    """Return allocated node IDs whose description contains ``"->"``.

    Used by callers that need to detect the "conversion node allocated but
    unparseable" data gap — i.e. when :func:`extract_damage_conversions`
    returned an empty list yet the user has clearly picked a conversion
    node whose effect lives only in prose. Never raises; returns ``[]``
    for missing/invalid inputs.
    """
    if not spec_tree:
        return []

    try:
        tree_data = get_tree_for_skill(skill_name)
    except Exception:
        return []
    if not tree_data:
        return []

    nodes_by_id: dict[int, dict] = {
        n["id"]: n for n in tree_data.get("nodes", []) if "id" in n
    }

    arrow_node_ids: list[int] = []
    for allocation in spec_tree:
        if not isinstance(allocation, dict):
            continue
        node_id = allocation.get("node_id")
        if node_id is None:
            continue
        try:
            points = int(allocation.get("points", 1))
        except (TypeError, ValueError):
            continue
        if points <= 0:
            continue
        node = nodes_by_id.get(node_id)
        if not node:
            continue
        description = node.get("description") or ""
        if "->" in description:
            arrow_node_ids.append(int(node_id))
    return arrow_node_ids
