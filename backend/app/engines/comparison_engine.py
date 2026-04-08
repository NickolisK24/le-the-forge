"""
Comparison Engine — side-by-side simulation comparison of two builds.

Accepts two Build objects, runs the full combat + defense simulation for each,
and returns a structured comparison result with per-category winners.
"""

from dataclasses import dataclass, field, asdict
from typing import Optional

from app.engines.stat_engine import BuildStats
from app.engines import combat_engine, defense_engine


@dataclass(frozen=True)
class DPSComparison:
    raw_dps_a: float
    raw_dps_b: float
    crit_contribution_a: float
    crit_contribution_b: float
    ailment_dps_a: float
    ailment_dps_b: float
    total_dps_a: float
    total_dps_b: float
    winner: str  # "a", "b", or "tie"

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class EHPComparison:
    max_health_a: float
    max_health_b: float
    effective_hp_a: float
    effective_hp_b: float
    armor_reduction_pct_a: float
    armor_reduction_pct_b: float
    avg_resistance_a: float
    avg_resistance_b: float
    survivability_score_a: float
    survivability_score_b: float
    winner: str  # "a", "b", or "tie"

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class StatDelta:
    stat_key: str
    value_a: float
    value_b: float
    delta: float

    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class SkillInfo:
    skill_name: str
    points_allocated: int
    slot: int


@dataclass(frozen=True)
class SkillComparison:
    skills_a: list
    skills_b: list
    shared: list
    unique_to_a: list
    unique_to_b: list

    def to_dict(self):
        return {
            "skills_a": self.skills_a,
            "skills_b": self.skills_b,
            "shared": self.shared,
            "unique_to_a": self.unique_to_a,
            "unique_to_b": self.unique_to_b,
        }


@dataclass(frozen=True)
class GearSlotComparison:
    slot: str
    item_a: Optional[str]
    rarity_a: Optional[str]
    item_b: Optional[str]
    rarity_b: Optional[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class ComparisonResult:
    slug_a: str
    slug_b: str
    name_a: str
    name_b: str
    dps: DPSComparison
    ehp: EHPComparison
    stat_deltas: list  # list of StatDelta
    overall_winner: str  # "a", "b", or "tie"
    overall_score_a: float
    overall_score_b: float
    skill_comparison: SkillComparison
    gear_comparison: list  # list of GearSlotComparison

    def to_dict(self):
        return {
            "slug_a": self.slug_a,
            "slug_b": self.slug_b,
            "name_a": self.name_a,
            "name_b": self.name_b,
            "dps": self.dps.to_dict(),
            "ehp": self.ehp.to_dict(),
            "stat_deltas": [d.to_dict() for d in self.stat_deltas],
            "overall_winner": self.overall_winner,
            "overall_score_a": self.overall_score_a,
            "overall_score_b": self.overall_score_b,
            "skill_comparison": self.skill_comparison.to_dict(),
            "gear_comparison": [g.to_dict() for g in self.gear_comparison],
        }


def _determine_winner(val_a: float, val_b: float) -> str:
    if abs(val_a - val_b) < 0.01:
        return "tie"
    return "a" if val_a > val_b else "b"


GEAR_SLOTS = [
    "head", "chest", "hands", "feet", "belt",
    "ring1", "ring2", "amulet", "weapon", "offhand",
]


def compare_builds(
    build_a,
    build_b,
    stats_a: BuildStats,
    stats_b: BuildStats,
    primary_skill_a: str,
    primary_skill_b: str,
    skill_level_a: int = 20,
    skill_level_b: int = 20,
) -> ComparisonResult:
    """
    Run full combat + defense simulation for two builds and produce a comparison.

    Parameters
    ----------
    build_a, build_b : Build models
    stats_a, stats_b : Aggregated BuildStats for each build
    primary_skill_a, primary_skill_b : Primary skill names
    skill_level_a, skill_level_b : Skill levels
    """
    # DPS
    dps_a = combat_engine.calculate_dps(stats_a, primary_skill_a, skill_level_a)
    dps_b = combat_engine.calculate_dps(stats_b, primary_skill_b, skill_level_b)

    dps_winner = _determine_winner(dps_a.total_dps, dps_b.total_dps)
    dps_cmp = DPSComparison(
        raw_dps_a=round(dps_a.dps, 2),
        raw_dps_b=round(dps_b.dps, 2),
        crit_contribution_a=round(dps_a.crit_contribution_pct, 2),
        crit_contribution_b=round(dps_b.crit_contribution_pct, 2),
        ailment_dps_a=round(dps_a.ailment_dps, 2),
        ailment_dps_b=round(dps_b.ailment_dps, 2),
        total_dps_a=round(dps_a.total_dps, 2),
        total_dps_b=round(dps_b.total_dps, 2),
        winner=dps_winner,
    )

    # EHP
    def_a = defense_engine.calculate_defense(stats_a)
    def_b = defense_engine.calculate_defense(stats_b)

    ehp_winner = _determine_winner(def_a.effective_hp, def_b.effective_hp)
    ehp_cmp = EHPComparison(
        max_health_a=round(def_a.max_health, 2),
        max_health_b=round(def_b.max_health, 2),
        effective_hp_a=round(def_a.effective_hp, 2),
        effective_hp_b=round(def_b.effective_hp, 2),
        armor_reduction_pct_a=round(def_a.armor_reduction_pct, 2),
        armor_reduction_pct_b=round(def_b.armor_reduction_pct, 2),
        avg_resistance_a=round(def_a.avg_resistance, 2),
        avg_resistance_b=round(def_b.avg_resistance, 2),
        survivability_score_a=round(def_a.survivability_score, 2),
        survivability_score_b=round(def_b.survivability_score, 2),
        winner=ehp_winner,
    )

    # Stat deltas — every stat that differs
    stat_deltas = []
    dict_a = stats_a.to_dict()
    dict_b = stats_b.to_dict()
    all_keys = sorted(set(dict_a.keys()) | set(dict_b.keys()))
    for key in all_keys:
        va = dict_a.get(key, 0.0)
        vb = dict_b.get(key, 0.0)
        if not isinstance(va, (int, float)) or not isinstance(vb, (int, float)):
            continue
        delta = round(vb - va, 4)
        if abs(delta) > 0.001:
            stat_deltas.append(StatDelta(
                stat_key=key,
                value_a=round(va, 4),
                value_b=round(vb, 4),
                delta=delta,
            ))

    # Overall winner: weighted 60% DPS, 40% EHP
    # Normalize to a 0-100 scale based on the pair
    dps_max = max(dps_a.total_dps, dps_b.total_dps, 1.0)
    ehp_max = max(def_a.effective_hp, def_b.effective_hp, 1.0)

    score_a = 0.6 * (dps_a.total_dps / dps_max * 100) + 0.4 * (def_a.effective_hp / ehp_max * 100)
    score_b = 0.6 * (dps_b.total_dps / dps_max * 100) + 0.4 * (def_b.effective_hp / ehp_max * 100)

    overall_winner = _determine_winner(score_a, score_b)

    # Skill comparison
    skills_a_list = [
        {"skill_name": s.skill_name, "points_allocated": s.points_allocated, "slot": s.slot}
        for s in sorted(build_a.skills, key=lambda s: s.slot)
    ]
    skills_b_list = [
        {"skill_name": s.skill_name, "points_allocated": s.points_allocated, "slot": s.slot}
        for s in sorted(build_b.skills, key=lambda s: s.slot)
    ]
    names_a = {s["skill_name"] for s in skills_a_list if s["skill_name"]}
    names_b = {s["skill_name"] for s in skills_b_list if s["skill_name"]}
    shared = sorted(names_a & names_b)
    unique_a = sorted(names_a - names_b)
    unique_b = sorted(names_b - names_a)

    skill_cmp = SkillComparison(
        skills_a=skills_a_list,
        skills_b=skills_b_list,
        shared=shared,
        unique_to_a=unique_a,
        unique_to_b=unique_b,
    )

    # Gear comparison
    gear_a_map = {g.get("slot"): g for g in (build_a.gear or [])} if build_a.gear else {}
    gear_b_map = {g.get("slot"): g for g in (build_b.gear or [])} if build_b.gear else {}

    gear_cmp = []
    all_slots = sorted(set(list(gear_a_map.keys()) + list(gear_b_map.keys()) + GEAR_SLOTS))
    seen = set()
    for slot in all_slots:
        if slot in seen or slot is None:
            continue
        seen.add(slot)
        ga = gear_a_map.get(slot, {})
        gb = gear_b_map.get(slot, {})
        if ga or gb:
            gear_cmp.append(GearSlotComparison(
                slot=slot,
                item_a=ga.get("item_name"),
                rarity_a=ga.get("rarity"),
                item_b=gb.get("item_name"),
                rarity_b=gb.get("rarity"),
            ))

    return ComparisonResult(
        slug_a=build_a.slug,
        slug_b=build_b.slug,
        name_a=build_a.name,
        name_b=build_b.name,
        dps=dps_cmp,
        ehp=ehp_cmp,
        stat_deltas=stat_deltas,
        overall_winner=overall_winner,
        overall_score_a=round(score_a, 2),
        overall_score_b=round(score_b, 2),
        skill_comparison=skill_cmp,
        gear_comparison=gear_cmp,
    )
