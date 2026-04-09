"""
Corruption Scaler — Phase 7 Engine

Models corruption-based scaling for enemy health and damage in Last Epoch's
Monolith of Fate endgame system.

Corruption scaling (community-documented curve):
  - Enemy damage scales linearly: +0.5% per corruption level
  - Enemy health scales with an accelerating curve:
    - 0-200: +1% per corruption level (linear)
    - 200+: quadratic acceleration: base + 0.005 * (corruption - 200)^1.5

Standard breakpoints: 0, 100, 200, 300, 400, 500.

Runs BossEncounterSimulator at each breakpoint and computes:
  - DPS efficiency (raw DPS vs scaled enemy HP)
  - Survivability score (build EHP vs scaled enemy damage)
  - Recommended max corruption (highest level where survival >= threshold)

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from app.engines.stat_engine import BuildStats
from app.engines.boss_encounter import simulate_boss_encounter
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Corruption scaling formulas
# ---------------------------------------------------------------------------

STANDARD_BREAKPOINTS = [0, 100, 200, 300, 400, 500]


def health_multiplier(corruption: int) -> float:
    """Enemy health multiplier at a given corruption level.

    0-200: linear 1% per level → at 200: 3.0x
    200+:  accelerating curve → at 300: ~4.6x, 400: ~7.5x, 500: ~11.5x
    """
    if corruption <= 0:
        return 1.0
    if corruption <= 200:
        return 1.0 + corruption * 0.01
    # Base at 200 plus accelerating curve
    base_at_200 = 3.0  # 1.0 + 200 * 0.01
    excess = corruption - 200
    return base_at_200 + 0.005 * (excess ** 1.5)


def damage_multiplier(corruption: int) -> float:
    """Enemy damage multiplier at a given corruption level.

    Linear: +0.5% per corruption level.
    """
    if corruption <= 0:
        return 1.0
    return 1.0 + corruption * 0.005


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class CorruptionDataPoint:
    corruption: int
    dps_efficiency: float     # 0.0 - 1.0+ (raw DPS / scaled enemy HP factor)
    survivability_score: int  # 0-100

    def to_dict(self) -> dict:
        return {
            "corruption": self.corruption,
            "dps_efficiency": round(self.dps_efficiency, 2),
            "survivability_score": self.survivability_score,
        }


@dataclass
class CorruptionScalingResult:
    boss_id: str
    recommended_max_corruption: int
    curve: list[CorruptionDataPoint]
    execution_time: float = 0.0

    def to_dict(self) -> dict:
        return {
            "boss_id": self.boss_id,
            "recommended_max_corruption": self.recommended_max_corruption,
            "curve": [dp.to_dict() for dp in self.curve],
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def scale_corruption(
    stats: BuildStats,
    boss: dict,
    primary_skill: str,
    skill_level: int = 20,
    breakpoints: list[int] | None = None,
    survival_threshold: int = 70,
) -> CorruptionScalingResult:
    """Run boss encounter at each corruption breakpoint and compute scaling curve.

    Args:
        stats: Fully resolved BuildStats.
        boss: Boss profile dict.
        primary_skill: Build's primary skill.
        skill_level: Skill level.
        breakpoints: Corruption levels to test (default: 0, 100, 200, 300, 400, 500).
        survival_threshold: Minimum survivability score to recommend (default 70).

    Returns:
        CorruptionScalingResult with curve data and recommended max corruption.
    """
    t_start = time.perf_counter()
    boss_id = boss.get("id", "unknown")
    bps = breakpoints or STANDARD_BREAKPOINTS

    curve: list[CorruptionDataPoint] = []
    recommended_max = 0

    # Get baseline DPS efficiency at corruption 0
    baseline_result = simulate_boss_encounter(
        stats, boss, primary_skill, skill_level,
        corruption=0,
        health_multiplier=1.0,
        damage_multiplier=1.0,
    )
    baseline_ttk = baseline_result.summary.total_ttk_seconds
    if baseline_ttk <= 0:
        baseline_ttk = 1.0  # prevent division by zero

    for corruption in bps:
        hp_mult = health_multiplier(corruption)
        dmg_mult = damage_multiplier(corruption)

        result = simulate_boss_encounter(
            stats, boss, primary_skill, skill_level,
            corruption=corruption,
            health_multiplier=hp_mult,
            damage_multiplier=dmg_mult,
        )

        # DPS efficiency: how well the build handles the scaled HP
        # 1.0 = same as corruption 0, lower = worse
        current_ttk = result.summary.total_ttk_seconds
        if current_ttk > 0 and current_ttk != float("inf"):
            dps_efficiency = baseline_ttk / current_ttk
        else:
            dps_efficiency = 0.0

        survival = result.summary.overall_survival_score

        curve.append(CorruptionDataPoint(
            corruption=corruption,
            dps_efficiency=dps_efficiency,
            survivability_score=survival,
        ))

        if survival >= survival_threshold:
            recommended_max = corruption

    elapsed = time.perf_counter() - t_start
    log.info(
        "corruption_scaler.done",
        boss_id=boss_id,
        recommended_max=recommended_max,
        breakpoints=len(bps),
        elapsed=round(elapsed, 4),
    )

    return CorruptionScalingResult(
        boss_id=boss_id,
        recommended_max_corruption=recommended_max,
        curve=curve,
        execution_time=elapsed,
    )
