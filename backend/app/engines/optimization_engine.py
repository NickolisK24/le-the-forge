"""
Optimization Engine — identifies which stat upgrades provide the largest gains.

Mirrors the logic in frontend/src/lib/simulation.ts:getStatUpgrades().

Workflow:
  1. Compute baseline DPS and EHP from current stats.
  2. For each candidate stat increment, apply the delta and recompute.
  3. Rank by DPS gain %. Include EHP gain % for defensive context.

Pure module — no DB, no HTTP.
"""

import re
from dataclasses import dataclass, asdict

from app.constants.combat import CRIT_CHANCE_CAP
from app.domain.calculators.conversion_calculator import (
    DamageConversion,
    apply_conversions,
)
from app.domain.calculators.damage_type_router import (
    combined_increased_stats,
    tags_for_stats,
)
from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps, _get_skill_def
from app.engines.defense_engine import calculate_defense
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


def _normalize_skill_name(skill_name: str) -> str:
    """Convert a skill name from snake_case / lowercase / CamelCase to the
    title-case-with-spaces form used as keys in ``combat_engine.SKILL_STATS``.

    Build imports from Last Epoch Tools and Maxroll emit skill names in
    various casings (e.g. ``"shadow_cascade"`` or ``"ShadowCascade"``), but
    ``SKILL_STATS`` is keyed by the in-game display name (``"Shadow Cascade"``).
    Without normalization ``_get_skill_def`` returns ``None``, ``calculate_dps``
    zeroes out, and the optimizer's rankings become meaningless.

    Examples:
        ``"shadow_cascade"`` → ``"Shadow Cascade"``
        ``"shadow cascade"`` → ``"Shadow Cascade"``
        ``"ShadowCascade"``  → ``"Shadow Cascade"``
        ``"Shadow Cascade"`` → ``"Shadow Cascade"`` (no-op)
    """
    if not skill_name:
        return skill_name
    # Insert a space between a lowercase letter and a following uppercase
    # letter so that CamelCase splits on word boundaries.
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", skill_name)
    # Convert snake_case / kebab-case separators to spaces.
    spaced = spaced.replace("_", " ").replace("-", " ")
    # Collapse consecutive whitespace and title-case each word.
    return " ".join(spaced.split()).title()


def _applicable_damage_stat_keys(
    skill_name: str,
    conversions: list[DamageConversion] | None = None,
) -> frozenset[str] | None:
    """Return the set of ``*_damage_pct`` stat keys that can actually scale
    ``skill_name``'s damage, or ``None`` if the skill is unknown.

    Uses :func:`combined_increased_stats` over the skill's damage types
    plus any tag-modifier stats in its ``scaling_stats`` tuple, then adds
    the delivery-tag stats for ``is_melee`` / ``is_throwing`` / ``is_bow``
    flags (those tags are typically tracked as booleans rather than via
    ``scaling_stats`` entries).

    When ``conversions`` is provided, the damage-type set is derived from
    the *post-conversion* distribution rather than from
    ``skill_def.damage_types``. This matters for skills whose tree nodes
    convert one channel to another (e.g. phys→fire): once converted, the
    source channel's increased pool no longer applies, and the target
    channel's pool does. A synthetic per-type dict ``{dt: 1/n}`` (equal
    split over the static types) is run through
    :func:`conversion_calculator.apply_conversions`; types that remain
    non-zero in the output are the effective post-conversion channels.

    Example — Shadow Cascade (physical+void, is_melee=True):
        → {"physical_damage_pct", "void_damage_pct", "melee_damage_pct"}

    Example — same skill with a phys→fire 100% conversion node:
        → {"fire_damage_pct", "elemental_damage_pct",
           "void_damage_pct", "melee_damage_pct"}

    A ``None`` return signals "unknown skill — do not filter", so callers
    fall back to testing every candidate increment rather than silently
    dropping all of them.
    """
    skill_def = _get_skill_def(skill_name)
    if skill_def is None:
        return None

    if conversions:
        n = len(skill_def.damage_types) or 1
        share = 1.0 / n
        scaled = {dt: share for dt in skill_def.damage_types}
        post = apply_conversions(scaled, conversions)
        effective_types = list(post.keys())
    else:
        effective_types = skill_def.damage_types

    applicable = set(combined_increased_stats(
        effective_types,
        tags_for_stats(skill_def.scaling_stats),
    ))

    # Delivery tags are stored as booleans on SkillStatDef, so combine them
    # into the applicable set explicitly.
    if skill_def.is_melee:
        applicable.add("melee_damage_pct")
    if skill_def.is_throwing:
        applicable.add("throwing_damage_pct")
    if skill_def.is_bow:
        applicable.add("bow_damage_pct")

    return frozenset(applicable)


@dataclass
class StatUpgrade:
    stat: str
    label: str
    dps_gain_pct: float
    ehp_gain_pct: float
    explanation: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


# Candidate increments — comprehensive stat testing
STAT_TEST_INCREMENTS: list = [
    # Offense — damage %
    {"key": "crit_multiplier_pct", "label": "+40% Crit Multiplier",       "delta": 40},
    {"key": "crit_chance_pct",     "label": "+7% Crit Chance",            "delta": 7},
    {"key": "attack_speed_pct",    "label": "+10% Attack Speed",          "delta": 10},
    {"key": "spell_damage_pct",    "label": "+40% Spell Damage",          "delta": 40},
    {"key": "physical_damage_pct", "label": "+40% Physical Damage",       "delta": 40},
    {"key": "fire_damage_pct",     "label": "+40% Fire Damage",           "delta": 40},
    {"key": "cold_damage_pct",     "label": "+40% Cold Damage",           "delta": 40},
    {"key": "lightning_damage_pct","label": "+40% Lightning Damage",      "delta": 40},
    {"key": "necrotic_damage_pct", "label": "+40% Necrotic Damage",       "delta": 40},
    {"key": "void_damage_pct",     "label": "+40% Void Damage",           "delta": 40},
    {"key": "poison_damage_pct",   "label": "+40% Poison Damage",         "delta": 40},
    {"key": "cast_speed",          "label": "+10% Cast Speed",            "delta": 10},
    {"key": "melee_damage_pct",    "label": "+40% Melee Damage",          "delta": 40},
    {"key": "throwing_damage_pct", "label": "+40% Throwing Damage",       "delta": 40},
    {"key": "bow_damage_pct",      "label": "+40% Bow Damage",            "delta": 40},
    {"key": "elemental_damage_pct","label": "+40% Elemental Damage",      "delta": 40},
    {"key": "dot_damage_pct",      "label": "+40% DoT Damage",            "delta": 40},
    {"key": "minion_damage_pct",   "label": "+40% Minion Damage",         "delta": 40},
    # Offense — flat added damage
    {"key": "added_spell_damage",  "label": "+15 Flat Spell Damage",      "delta": 15},
    {"key": "added_melee_physical","label": "+18 Flat Melee Physical",    "delta": 18},
    # Offense — ailments
    {"key": "bleed_chance_pct",    "label": "+30% Bleed Chance",          "delta": 30},
    {"key": "ignite_chance_pct",   "label": "+30% Ignite Chance",         "delta": 30},
    {"key": "poison_chance_pct",   "label": "+30% Poison Chance",         "delta": 30},
    {"key": "bleed_damage_pct",    "label": "+40% Bleed Damage",          "delta": 40},
    {"key": "ignite_damage_pct",   "label": "+40% Ignite Damage",         "delta": 40},
    # Defense — health / armour
    {"key": "max_health",          "label": "+300 Health",                "delta": 300},
    {"key": "armour",              "label": "+200 Armour",                "delta": 200},
    {"key": "dodge_rating",        "label": "+150 Dodge Rating",          "delta": 150},
    {"key": "block_chance",        "label": "+20% Block Chance",          "delta": 20},
    {"key": "block_effectiveness", "label": "+200 Block Effectiveness",   "delta": 200},
    {"key": "endurance",           "label": "+20% Endurance",             "delta": 20},
    {"key": "crit_avoidance",      "label": "+40% Crit Avoidance",        "delta": 40},
    {"key": "glancing_blow",       "label": "+20% Glancing Blow",         "delta": 20},
    # Defense — resistances
    {"key": "fire_res",            "label": "+20% Fire Resistance",       "delta": 20},
    {"key": "cold_res",            "label": "+20% Cold Resistance",       "delta": 20},
    {"key": "lightning_res",       "label": "+20% Lightning Resistance",  "delta": 20},
    {"key": "void_res",            "label": "+20% Void Resistance",       "delta": 20},
    {"key": "necrotic_res",        "label": "+20% Necrotic Resistance",   "delta": 20},
    {"key": "physical_res",        "label": "+10% Physical Resistance",   "delta": 10},
    # Sustain
    {"key": "leech",               "label": "+5% Leech",                  "delta": 5},
    {"key": "health_regen",        "label": "+15 Health Regen",           "delta": 15},
]


# Every *_damage_pct candidate tested by this engine. Used together with
# :func:`_applicable_damage_stat_keys` to skip damage buckets a skill can't
# actually use (e.g. fire_damage_pct for a pure-physical build), which would
# otherwise produce 0% dps_gain rows and pollute the top-N ranking whenever
# the sort falls back to insertion order.
_ALL_DAMAGE_PCT_KEYS: frozenset[str] = frozenset(
    inc["key"] for inc in STAT_TEST_INCREMENTS if inc["key"].endswith("_damage_pct")
)


def get_stat_upgrades(
    stats: BuildStats,
    primary_skill: str,
    skill_level: int = 20,
    top_n: int = 5,
    conversions: list[DamageConversion] | None = None,
) -> list[StatUpgrade]:
    """
    Test each stat increment and rank by DPS gain.

    Args:
        stats: current aggregated BuildStats
        primary_skill: the skill to use as DPS reference (e.g. "Fireball")
        skill_level: the level of that skill
        top_n: how many top upgrades to return
        conversions: optional damage-type conversions allocated in the skill
                     tree. When provided, %-damage filtering uses the
                     post-conversion channel set so converted skills test
                     the right damage buckets (e.g. phys→fire converted
                     attacks test fire_damage_pct, not physical_damage_pct).

    Returns:
        List of StatUpgrade sorted by dps_gain_pct descending, length top_n.
    """
    # Normalize incoming skill names (snake_case / CamelCase / etc.) to the
    # title-case-with-spaces form SKILL_STATS is keyed by, so that imported
    # builds from LE Tools / Maxroll don't silently produce zero DPS rankings.
    primary_skill = _normalize_skill_name(primary_skill)

    log.info("get_stat_upgrades.start", skill=primary_skill, top_n=top_n)
    base_dps = calculate_dps(
        stats, primary_skill, skill_level, conversions=conversions,
    ).dps
    base_ehp = calculate_defense(stats).effective_hp

    if base_dps == 0:
        log.warning(
            "get_stat_upgrades.zero_baseline_dps",
            skill=primary_skill,
            message=(
                "Baseline DPS is 0 — skill definition not found in SKILL_STATS. "
                "Stat upgrade rankings will be meaningless (all dps_gain_pct=0)."
            ),
        )

    # Restrict %-damage testing to buckets the skill can actually use
    # (e.g. Shadow Cascade → physical/void/melee). Non-damage stats like
    # resistances, crit, speed, and flat added damage are always tested.
    # Conversions, if present, shift the effective channel set so the
    # filter reflects the post-conversion damage profile.
    applicable_damage_keys = _applicable_damage_stat_keys(
        primary_skill, conversions=conversions,
    )

    results = []

    for increment in STAT_TEST_INCREMENTS:
        key = increment["key"]
        delta = increment["delta"]
        label = increment["label"]

        # Skip %-damage stats the skill cannot scale with — they'd always
        # return 0% DPS gain and pollute the ranking.
        if (
            key in _ALL_DAMAGE_PCT_KEYS
            and applicable_damage_keys is not None
            and key not in applicable_damage_keys
        ):
            continue

        # Clone stats and apply delta
        from copy import copy as _copy
        modified = _copy(stats)
        current_val = getattr(modified, key, 0.0)
        setattr(modified, key, current_val + delta)

        # Re-derive dependent stats for crit
        if key == "crit_chance_pct":
            base_crit = stats.crit_chance - stats.crit_chance_pct / 100
            modified.crit_chance = min(CRIT_CHANCE_CAP,base_crit + modified.crit_chance_pct / 100)
        elif key == "crit_multiplier_pct":
            base_mult = stats.crit_multiplier - stats.crit_multiplier_pct / 100
            modified.crit_multiplier = base_mult + modified.crit_multiplier_pct / 100

        new_dps = calculate_dps(
            modified, primary_skill, skill_level, conversions=conversions,
        ).dps
        new_ehp = calculate_defense(modified).effective_hp

        dps_gain = ((new_dps - base_dps) / base_dps * 100) if base_dps > 0 else 0.0
        ehp_gain = ((new_ehp - base_ehp) / base_ehp * 100) if base_ehp > 0 else 0.0

        results.append(StatUpgrade(
            stat=key,
            label=label,
            dps_gain_pct=round(dps_gain * 10) / 10,
            ehp_gain_pct=round(ehp_gain * 10) / 10,
        ))

    # Sort by DPS gain descending, return top N
    results.sort(key=lambda r: r.dps_gain_pct, reverse=True)
    top = results[:top_n]

    # Generate explanations for the top results
    for rank, upgrade in enumerate(top, 1):
        upgrade.explanation = _explain_upgrade(upgrade, stats, rank)

    return top


# ---------------------------------------------------------------------------
# Explanation generation
# ---------------------------------------------------------------------------

_OFFENSE_STATS = {
    "crit_multiplier_pct", "crit_chance_pct", "attack_speed_pct", "cast_speed",
    "spell_damage_pct", "physical_damage_pct", "fire_damage_pct", "cold_damage_pct",
    "lightning_damage_pct", "necrotic_damage_pct", "void_damage_pct", "poison_damage_pct",
    "melee_damage_pct", "throwing_damage_pct", "bow_damage_pct", "elemental_damage_pct",
    "dot_damage_pct", "minion_damage_pct", "added_spell_damage", "added_melee_physical",
    "bleed_chance_pct", "ignite_chance_pct", "poison_chance_pct",
    "bleed_damage_pct", "ignite_damage_pct",
}

_DEFENSE_STATS = {
    "max_health", "armour", "dodge_rating", "block_chance", "block_effectiveness",
    "endurance", "crit_avoidance", "glancing_blow",
    "fire_res", "cold_res", "lightning_res", "void_res", "necrotic_res", "physical_res",
    "leech", "health_regen",
}

# Rough thresholds where % damage scaling starts to see diminishing returns
_DIMINISHING_THRESHOLD = 300.0


def _explain_upgrade(upgrade: "StatUpgrade", stats: BuildStats, rank: int) -> str:
    """Generate a short contextual explanation for why a stat upgrade is valuable."""
    stat = upgrade.stat
    current = getattr(stats, stat, 0.0)
    parts = []

    if upgrade.dps_gain_pct > 0 and upgrade.ehp_gain_pct > 0:
        parts.append(f"Improves both offense (+{upgrade.dps_gain_pct}% DPS) and defense (+{upgrade.ehp_gain_pct}% EHP).")
    elif upgrade.dps_gain_pct > 0:
        parts.append(f"Pure offense boost at +{upgrade.dps_gain_pct}% DPS.")
    elif upgrade.ehp_gain_pct > 0:
        parts.append(f"Defensive upgrade at +{upgrade.ehp_gain_pct}% EHP.")

    # Diminishing return warning for % damage stats
    if stat.endswith("_damage_pct") and current >= _DIMINISHING_THRESHOLD:
        parts.append(f"Current {stat} is {current:.0f}% — approaching diminishing returns.")
    elif stat.endswith("_damage_pct") and current < _DIMINISHING_THRESHOLD:
        parts.append(f"Current {stat} is only {current:.0f}% — well below the diminishing return threshold, making this highly efficient.")

    # Resistance context
    if stat.endswith("_res"):
        if current >= 75:
            parts.append("Already at resistance cap (75%). No further benefit.")
        elif current < 30:
            parts.append(f"Currently at {current:.0f}% — very low. Priority defensive gap.")
        elif current < 60:
            parts.append(f"Currently at {current:.0f}% — below comfortable levels.")

    # Crit context
    if stat == "crit_chance_pct":
        effective_crit = min(CRIT_CHANCE_CAP,stats.crit_chance)
        parts.append(f"Effective crit is {effective_crit*100:.1f}%.")
    elif stat == "crit_multiplier_pct":
        parts.append(f"Current crit multiplier is {stats.crit_multiplier:.2f}x.")

    # Health context
    if stat == "max_health" and stats.max_health < 1500:
        parts.append(f"Base health is low ({stats.max_health:.0f}). This is a high-priority survivability upgrade.")

    return " ".join(parts) if parts else f"Ranked #{rank} by marginal DPS gain."


# ---------------------------------------------------------------------------
# Stat sensitivity analysis
# ---------------------------------------------------------------------------

def stat_sensitivity(
    stats: BuildStats,
    primary_skill: str,
    skill_level: int = 20,
    stat_keys: list[str] | None = None,
    delta: float = 10.0,
    conversions: list[DamageConversion] | None = None,
) -> list[dict]:
    """
    Sensitivity analysis: for each stat, compute the DPS and EHP change per
    unit of that stat (normalized to a fixed delta).

    This answers "which stats give the most marginal value right now?"

    Args:
        stats: current aggregated BuildStats
        primary_skill: skill for DPS calculation
        skill_level: skill level
        stat_keys: specific stats to test (default: all from STAT_TEST_INCREMENTS)
        delta: the amount to bump each stat by (default 10)
        conversions: optional damage-type conversions; when provided, the
                     default %-damage filter uses the post-conversion
                     channel set (see :func:`_applicable_damage_stat_keys`).

    Returns:
        List of dicts sorted by dps_per_unit descending:
        [{"stat", "current_value", "delta", "dps_gain_pct", "ehp_gain_pct",
          "dps_per_unit", "ehp_per_unit", "category"}]
    """
    base_dps = calculate_dps(
        stats, primary_skill, skill_level, conversions=conversions,
    ).dps
    base_ehp = calculate_defense(stats).effective_hp

    # Build the stat list to test
    if stat_keys:
        # Caller specified an explicit list — respect it verbatim.
        increments = [{"key": k, "delta": delta} for k in stat_keys if hasattr(stats, k)]
    else:
        # No explicit list — test every candidate, but restrict %-damage
        # buckets to those the skill can actually scale with (same filter as
        # get_stat_upgrades) so unusable damage types don't produce noise.
        applicable_damage_keys = _applicable_damage_stat_keys(
            primary_skill, conversions=conversions,
        )
        increments = [
            {"key": inc["key"], "delta": delta}
            for inc in STAT_TEST_INCREMENTS
            if not (
                inc["key"] in _ALL_DAMAGE_PCT_KEYS
                and applicable_damage_keys is not None
                and inc["key"] not in applicable_damage_keys
            )
        ]

    results = []
    for inc in increments:
        key = inc["key"]
        d = inc["delta"]

        from copy import copy as _copy
        modified = _copy(stats)
        current_val = getattr(modified, key, 0.0)
        setattr(modified, key, current_val + d)

        # Re-derive crit
        if key == "crit_chance_pct":
            base_crit = stats.crit_chance - stats.crit_chance_pct / 100
            modified.crit_chance = min(CRIT_CHANCE_CAP,base_crit + modified.crit_chance_pct / 100)
        elif key == "crit_multiplier_pct":
            base_mult = stats.crit_multiplier - stats.crit_multiplier_pct / 100
            modified.crit_multiplier = base_mult + modified.crit_multiplier_pct / 100

        new_dps = calculate_dps(
            modified, primary_skill, skill_level, conversions=conversions,
        ).dps
        new_ehp = calculate_defense(modified).effective_hp

        dps_gain = ((new_dps - base_dps) / base_dps * 100) if base_dps > 0 else 0.0
        ehp_gain = ((new_ehp - base_ehp) / base_ehp * 100) if base_ehp > 0 else 0.0

        category = "offense" if key in _OFFENSE_STATS else "defense" if key in _DEFENSE_STATS else "utility"

        results.append({
            "stat": key,
            "current_value": round(current_val, 2),
            "delta": d,
            "dps_gain_pct": round(dps_gain, 2),
            "ehp_gain_pct": round(ehp_gain, 2),
            "dps_per_unit": round(dps_gain / d, 4) if d else 0,
            "ehp_per_unit": round(ehp_gain / d, 4) if d else 0,
            "category": category,
        })

    results.sort(key=lambda r: r["dps_per_unit"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Architecture-plan required function
# ---------------------------------------------------------------------------

def find_best_affix_upgrade(
    build: dict,
    primary_skill: str | None = None,
    skill_level: int = 20,
    top_n: int = 5,
) -> list[StatUpgrade]:
    """Find the single best affix upgrade for each slot in the build.

    This is the canonical interface from architecture_implementation_plan.md.
    It wraps :func:`get_stat_upgrades` with a build-dict–oriented API so
    callers don't need to construct a :class:`BuildStats` themselves.

    Algorithm:
    1. Aggregate build stats via the stat engine.
    2. Delegate to :func:`get_stat_upgrades` to test every candidate increment.
    3. Return the top *top_n* upgrades ranked by DPS gain.

    Args:
        build: Build dict with keys ``character_class``, ``mastery``,
               ``passive_tree``, ``gear`` (list of item dicts with affixes),
               and optionally ``primary_skill``.
        primary_skill: Skill to use as DPS reference; falls back to
                       ``build.get("primary_skill")`` then ``"Fireball"``.
        skill_level: Level of the primary skill (default 20).
        top_n: Number of upgrade recommendations to return (default 5).

    Returns:
        List of :class:`StatUpgrade` sorted by ``dps_gain_pct`` descending.
    """
    from app.engines.stat_engine import aggregate_stats

    # Resolve skill and normalize casing (imports may use snake_case / CamelCase).
    skill = primary_skill or build.get("primary_skill") or "Fireball"
    skill = _normalize_skill_name(skill)

    # Build the keyword dict aggregate_stats expects
    gear = build.get("gear", [])
    passive_tree = build.get("passive_tree", [])
    character_class = build.get("character_class", "")
    mastery = build.get("mastery", "")

    # aggregate_stats positional signature:
    #   (character_class, mastery, allocated_node_ids, nodes, gear_affixes, passive_stats=None)
    # passive_tree may be a list of ints (node IDs) or a list of dicts; normalise to int IDs.
    if passive_tree and isinstance(passive_tree[0], dict):
        allocated_ids = [int(n.get("id", n.get("node_id", 0))) for n in passive_tree]
        nodes_dicts   = passive_tree  # already in {id, type, name} format
    else:
        allocated_ids = [int(n) for n in passive_tree]
        nodes_dicts   = []

    # gear_affixes: flat list of {name, tier} dicts extracted from all gear slots
    gear_affixes: list[dict] = []
    for slot_item in gear:
        for affix in slot_item.get("affixes", []):
            gear_affixes.append(affix)
        for affix in slot_item.get("prefixes", []):
            gear_affixes.append(affix)
        for affix in slot_item.get("suffixes", []):
            gear_affixes.append(affix)

    stats = aggregate_stats(
        character_class,
        mastery,
        allocated_ids,
        nodes_dicts,
        gear_affixes,
    )

    return get_stat_upgrades(stats, skill, skill_level, top_n=top_n)
