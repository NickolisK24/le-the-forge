"""
Stat Sensitivity Analyzer — Phase 4 Engine

For each stat present on a build, calculates:
  - Marginal DPS gain from a simulated +10% increase
  - Marginal EHP gain from a simulated +10% increase
  - Combined impact score (configurable offense/defense weighting)

Uses the existing stat pipeline, combat engine, and defense engine.
All results are deterministic: same input → same output.

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

import time
from copy import copy as _copy
from dataclasses import dataclass, field

from app.constants.combat import CRIT_CHANCE_CAP
from app.engines.stat_engine import BuildStats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class SensitivityEntry:
    """One stat's sensitivity result."""
    stat_key: str
    label: str
    current_value: float
    dps_gain_pct: float
    ehp_gain_pct: float
    impact_score: float
    rank: int = 0

    def to_dict(self) -> dict:
        return {
            "stat_key": self.stat_key,
            "label": self.label,
            "current_value": round(self.current_value, 2),
            "dps_gain_pct": round(self.dps_gain_pct, 2),
            "ehp_gain_pct": round(self.ehp_gain_pct, 2),
            "impact_score": round(self.impact_score, 4),
            "rank": self.rank,
        }


@dataclass
class SensitivityResult:
    """Full sensitivity analysis output."""
    entries: list[SensitivityEntry]
    base_dps: float
    base_ehp: float
    primary_skill: str
    offense_weight: float
    defense_weight: float
    execution_time: float

    def to_dict(self) -> dict:
        return {
            "entries": [e.to_dict() for e in self.entries],
            "base_dps": round(self.base_dps, 2),
            "base_ehp": round(self.base_ehp, 2),
            "primary_skill": self.primary_skill,
            "offense_weight": self.offense_weight,
            "defense_weight": self.defense_weight,
            "execution_time": round(self.execution_time, 4),
        }


# ---------------------------------------------------------------------------
# Stat catalog — human-readable labels for stat keys
# ---------------------------------------------------------------------------

STAT_LABELS: dict[str, str] = {
    "crit_multiplier_pct": "Crit Multiplier",
    "crit_chance_pct": "Crit Chance",
    "attack_speed_pct": "Attack Speed",
    "spell_damage_pct": "Spell Damage",
    "physical_damage_pct": "Physical Damage",
    "fire_damage_pct": "Fire Damage",
    "cold_damage_pct": "Cold Damage",
    "lightning_damage_pct": "Lightning Damage",
    "necrotic_damage_pct": "Necrotic Damage",
    "void_damage_pct": "Void Damage",
    "poison_damage_pct": "Poison Damage",
    "cast_speed": "Cast Speed",
    "melee_damage_pct": "Melee Damage",
    "throwing_damage_pct": "Throwing Damage",
    "bow_damage_pct": "Bow Damage",
    "elemental_damage_pct": "Elemental Damage",
    "dot_damage_pct": "DoT Damage",
    "minion_damage_pct": "Minion Damage",
    "added_spell_damage": "Flat Spell Damage",
    "added_melee_physical": "Flat Melee Physical",
    "bleed_chance_pct": "Bleed Chance",
    "ignite_chance_pct": "Ignite Chance",
    "poison_chance_pct": "Poison Chance",
    "bleed_damage_pct": "Bleed Damage",
    "ignite_damage_pct": "Ignite Damage",
    "max_health": "Health",
    "armour": "Armour",
    "dodge_rating": "Dodge Rating",
    "block_chance": "Block Chance",
    "block_effectiveness": "Block Effectiveness",
    "endurance": "Endurance",
    "crit_avoidance": "Crit Avoidance",
    "glancing_blow": "Glancing Blow",
    "fire_res": "Fire Resistance",
    "cold_res": "Cold Resistance",
    "lightning_res": "Lightning Resistance",
    "void_res": "Void Resistance",
    "necrotic_res": "Necrotic Resistance",
    "physical_res": "Physical Resistance",
    "leech": "Leech",
    "health_regen": "Health Regen",
    "more_damage_pct": "More Damage",
    "ward": "Ward",
    "ward_regen": "Ward Regen",
}


def _get_label(stat_key: str) -> str:
    return STAT_LABELS.get(stat_key, stat_key.replace("_", " ").title())


# ---------------------------------------------------------------------------
# Core: evaluate one stat bump
# ---------------------------------------------------------------------------

def _evaluate_stat(
    stats: BuildStats,
    stat_key: str,
    base_dps: float,
    base_ehp: float,
    primary_skill: str,
    skill_level: int,
    offense_weight: float,
    defense_weight: float,
) -> SensitivityEntry:
    """Apply a +10% bump (or flat equivalent) to stat_key and measure gains."""
    current_value = getattr(stats, stat_key, 0.0)

    # Calculate the delta: 10% of current value, with a floor so zero-value
    # stats still get tested (use a meaningful baseline bump).
    if current_value > 0:
        delta = current_value * 0.10
    else:
        # For zero-value stats, use a small representative increment
        delta = 10.0

    modified = _copy(stats)
    setattr(modified, stat_key, current_value + delta)

    # Re-derive crit from pct fields (same pattern as optimization_engine.py)
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
    impact = dps_gain * offense_weight + ehp_gain * defense_weight

    return SensitivityEntry(
        stat_key=stat_key,
        label=_get_label(stat_key),
        current_value=current_value,
        dps_gain_pct=round(dps_gain, 2),
        ehp_gain_pct=round(ehp_gain, 2),
        impact_score=round(impact, 4),
    )


# ---------------------------------------------------------------------------
# Stats to analyze — all stats on BuildStats that matter for DPS or EHP
# ---------------------------------------------------------------------------

ANALYZABLE_STATS: list[str] = [
    # Offense %
    "spell_damage_pct", "physical_damage_pct", "fire_damage_pct",
    "cold_damage_pct", "lightning_damage_pct", "necrotic_damage_pct",
    "void_damage_pct", "poison_damage_pct", "melee_damage_pct",
    "throwing_damage_pct", "bow_damage_pct", "elemental_damage_pct",
    "dot_damage_pct", "minion_damage_pct",
    # Offense speed/crit
    "crit_chance_pct", "crit_multiplier_pct", "attack_speed_pct", "cast_speed",
    # Offense flat
    "added_spell_damage", "added_melee_physical",
    # Ailment
    "bleed_chance_pct", "ignite_chance_pct", "poison_chance_pct",
    "bleed_damage_pct", "ignite_damage_pct",
    # Defense
    "max_health", "armour", "dodge_rating", "block_chance",
    "block_effectiveness", "endurance", "crit_avoidance", "glancing_blow",
    # Resistances
    "fire_res", "cold_res", "lightning_res", "void_res",
    "necrotic_res", "physical_res",
    # Sustain
    "leech", "health_regen",
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_sensitivity(
    stats: BuildStats,
    primary_skill: str,
    skill_level: int = 20,
    offense_weight: float = 0.6,
    defense_weight: float = 0.4,
) -> SensitivityResult:
    """Run stat sensitivity analysis on a resolved BuildStats.

    For each stat in ANALYZABLE_STATS, applies a +10% bump and measures
    the marginal DPS and EHP gains. Results are ranked by combined
    impact score (offense_weight * dps_gain + defense_weight * ehp_gain).

    Args:
        stats: Fully resolved BuildStats.
        primary_skill: Skill used as DPS reference.
        skill_level: Level of the primary skill.
        offense_weight: Weight for DPS gain in impact score (default 0.6).
        defense_weight: Weight for EHP gain in impact score (default 0.4).

    Returns:
        SensitivityResult with ranked entries.
    """
    log.info(
        "analyze_sensitivity.start",
        skill=primary_skill,
        offense_weight=offense_weight,
        defense_weight=defense_weight,
    )

    t_start = time.perf_counter()

    base_dps = calculate_dps(stats, primary_skill, skill_level).dps
    base_ehp = calculate_ehp(stats)

    entries: list[SensitivityEntry] = []
    for stat_key in ANALYZABLE_STATS:
        entry = _evaluate_stat(
            stats, stat_key, base_dps, base_ehp,
            primary_skill, skill_level,
            offense_weight, defense_weight,
        )
        # Only include stats that have nonzero impact
        if entry.dps_gain_pct != 0.0 or entry.ehp_gain_pct != 0.0:
            entries.append(entry)

    # Sort by impact_score descending
    entries.sort(key=lambda e: e.impact_score, reverse=True)
    for i, e in enumerate(entries):
        e.rank = i + 1

    elapsed = time.perf_counter() - t_start

    log.info(
        "analyze_sensitivity.done",
        n_entries=len(entries),
        elapsed=round(elapsed, 4),
    )

    return SensitivityResult(
        entries=entries,
        base_dps=base_dps,
        base_ehp=base_ehp,
        primary_skill=primary_skill,
        offense_weight=offense_weight,
        defense_weight=defense_weight,
        execution_time=elapsed,
    )
