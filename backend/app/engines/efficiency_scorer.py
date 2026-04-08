"""
Efficiency Scorer — Phase 4 Engine

Takes a build and a list of candidate gear affixes. For each candidate:
  - Calculates expected DPS gain and EHP gain
  - Pulls forge potential cost from crafting_rules.json
  - Computes efficiency_score = weighted_impact / fp_cost
  - Sorts by efficiency_score descending

Returns top N candidates (default 10).

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

import time
from copy import copy as _copy
from dataclasses import dataclass

from app.constants.combat import CRIT_CHANCE_CAP
from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp
from app.engines.sensitivity_analyzer import _get_label
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class AffixCandidate:
    """A single affix upgrade candidate with efficiency scoring."""
    affix_id: str
    label: str
    stat_key: str
    tier: int
    stat_value: float
    dps_gain_pct: float
    ehp_gain_pct: float
    fp_cost: int
    efficiency_score: float
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "affix_id": self.affix_id,
            "label": self.label,
            "dps_gain_pct": round(self.dps_gain_pct, 2),
            "ehp_gain_pct": round(self.ehp_gain_pct, 2),
            "fp_cost": self.fp_cost,
            "efficiency_score": round(self.efficiency_score, 4),
            "rank": self.rank,
        }


@dataclass
class EfficiencyResult:
    """Output of the efficiency scorer."""
    candidates: list[AffixCandidate]
    base_dps: float
    base_ehp: float
    execution_time: float

    def to_dict(self) -> dict:
        return {
            "candidates": [c.to_dict() for c in self.candidates],
            "base_dps": round(self.base_dps, 2),
            "base_ehp": round(self.base_ehp, 2),
            "execution_time": round(self.execution_time, 4),
        }


# ---------------------------------------------------------------------------
# FP cost lookup
# ---------------------------------------------------------------------------

def _get_avg_fp_cost() -> int:
    """Average FP cost for adding/upgrading an affix from crafting_rules.json."""
    try:
        from flask import current_app
        pipeline = current_app.extensions.get("game_data")
        if pipeline and hasattr(pipeline, "crafting_rules"):
            rules = pipeline.crafting_rules
            add_cost = rules.get("fp_costs", {}).get("add_affix", {})
            upgrade_cost = rules.get("fp_costs", {}).get("upgrade_affix", {})
            avg_add = (add_cost.get("min", 2) + add_cost.get("max", 6)) / 2
            avg_upgrade = (upgrade_cost.get("min", 1) + upgrade_cost.get("max", 5)) / 2
            return round((avg_add + avg_upgrade) / 2)
    except RuntimeError:
        pass
    # Fallback: average of add (2-6) and upgrade (1-5) costs
    return 4


def _fp_cost_for_tier(tier: int) -> int:
    """Estimate FP cost scaling by tier.

    Higher tiers are more expensive. The base average is ~4 FP,
    scaling roughly with tier number.
    """
    base = _get_avg_fp_cost()
    # Tiers 1-2 cost less, tiers 5+ cost more
    if tier <= 2:
        return max(1, base - 1)
    elif tier <= 4:
        return base
    elif tier <= 6:
        return base + 1
    else:
        return base + 2


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def _evaluate_affix(
    stats: BuildStats,
    affix: dict,
    base_dps: float,
    base_ehp: float,
    primary_skill: str,
    skill_level: int,
    offense_weight: float,
    defense_weight: float,
) -> AffixCandidate | None:
    """Evaluate a single affix candidate for its DPS/EHP impact and efficiency."""
    stat_key = affix.get("stat_key")
    if not stat_key or not hasattr(stats, stat_key):
        return None

    affix_id = affix.get("id", affix.get("name", "unknown"))
    name = affix.get("name", affix_id)
    tiers = affix.get("tiers", [])

    # Use the highest available tier's midpoint value
    if not tiers:
        return None

    best_tier = tiers[-1]  # highest tier
    tier_num = best_tier.get("tier", len(tiers))
    stat_value = (best_tier.get("min", 0) + best_tier.get("max", 0)) / 2
    if stat_value == 0:
        return None

    fp_cost = _fp_cost_for_tier(tier_num)

    # Apply the stat bump
    modified = _copy(stats)
    current_val = getattr(modified, stat_key, 0.0)
    setattr(modified, stat_key, current_val + stat_value)

    # Re-derive crit
    if stat_key == "crit_chance_pct":
        base_crit = stats.crit_chance - stats.crit_chance_pct / 100
        modified.crit_chance = min(CRIT_CHANCE_CAP, base_crit + modified.crit_chance_pct / 100)
    elif stat_key == "crit_multiplier_pct":
        base_mult = stats.crit_multiplier - stats.crit_multiplier_pct / 100
        modified.crit_multiplier = base_mult + modified.crit_multiplier_pct / 100

    new_dps = calculate_dps(modified, primary_skill, skill_level).dps
    new_ehp = calculate_ehp(modified)

    dps_gain = ((new_dps - base_dps) / base_dps * 100) if base_dps > 0 else 0.0
    ehp_gain = ((new_ehp - base_ehp) / base_ehp * 100) if base_ehp > 0 else 0.0
    weighted_impact = dps_gain * offense_weight + ehp_gain * defense_weight

    # Efficiency = impact / cost, handling zero FP cost gracefully
    if fp_cost > 0:
        efficiency = weighted_impact / fp_cost
    else:
        # Zero cost = infinite efficiency; cap at impact itself
        efficiency = weighted_impact

    tier_label = f"T{tier_num}"
    label = f"{name} ({tier_label})"

    return AffixCandidate(
        affix_id=f"{affix_id}_t{tier_num}",
        label=label,
        stat_key=stat_key,
        tier=tier_num,
        stat_value=stat_value,
        dps_gain_pct=round(dps_gain, 2),
        ehp_gain_pct=round(ehp_gain, 2),
        fp_cost=fp_cost,
        efficiency_score=round(efficiency, 4),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_affix_efficiency(
    stats: BuildStats,
    candidate_affixes: list[dict],
    primary_skill: str,
    skill_level: int = 20,
    top_n: int = 10,
    offense_weight: float = 0.6,
    defense_weight: float = 0.4,
) -> EfficiencyResult:
    """Score candidate affixes by efficiency (impact per FP cost).

    Args:
        stats: Fully resolved BuildStats.
        candidate_affixes: List of affix dicts from game data. Each must have
            at minimum: id/name, stat_key, tiers (list of {tier, min, max}).
        primary_skill: Skill used as DPS reference.
        skill_level: Level of the primary skill.
        top_n: Number of top candidates to return (default 10).
        offense_weight: Weight for DPS gain (default 0.6).
        defense_weight: Weight for EHP gain (default 0.4).

    Returns:
        EfficiencyResult with candidates sorted by efficiency_score descending.
    """
    log.info(
        "score_affix_efficiency.start",
        n_candidates=len(candidate_affixes),
        skill=primary_skill,
        top_n=top_n,
    )

    t_start = time.perf_counter()

    base_dps = calculate_dps(stats, primary_skill, skill_level).dps
    base_ehp = calculate_ehp(stats)

    results: list[AffixCandidate] = []
    for affix in candidate_affixes:
        candidate = _evaluate_affix(
            stats, affix, base_dps, base_ehp,
            primary_skill, skill_level,
            offense_weight, defense_weight,
        )
        if candidate is not None:
            results.append(candidate)

    # Sort by efficiency_score descending
    results.sort(key=lambda c: c.efficiency_score, reverse=True)
    top = results[:top_n]
    for i, c in enumerate(top):
        c.rank = i + 1

    elapsed = time.perf_counter() - t_start

    log.info(
        "score_affix_efficiency.done",
        n_results=len(top),
        elapsed=round(elapsed, 4),
    )

    return EfficiencyResult(
        candidates=top,
        base_dps=base_dps,
        base_ehp=base_ehp,
        execution_time=elapsed,
    )
