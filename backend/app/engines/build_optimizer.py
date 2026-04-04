"""
Multi-Objective Build Optimizer — Upgrade 4

Extends single-value upgrade ranking to a weighted multi-objective system.
Given a build and a goals dict, it evaluates every candidate stat increment
using a composite score:

    score = dps_gain_pct * dps_weight + ehp_gain_pct * ehp_weight

Returns ranked upgrade recommendations with full stat delta breakdown.

Rules enforced:
- Deterministic: no RNG, identical inputs → identical outputs
- No cross-engine coupling: communicates via BuildStats + typed result
- No magic numbers: weights and limits from constants.json / caller
- Telemetry: execution_time and iterations on every result
"""

from __future__ import annotations

import json
import math
import os
import time
from copy import copy as _copy
from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from app.engines.stat_engine import BuildStats, aggregate_stats
from app.engines.combat_engine import calculate_dps
from app.engines.defense_engine import calculate_ehp
from app.engines.optimization_engine import STAT_TEST_INCREMENTS
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_CONSTANTS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "game_data", "constants.json"
)


@lru_cache(maxsize=1)
def _load_constants() -> dict:
    with open(_CONSTANTS_PATH) as f:
        return json.load(f)


def _const(section: str, key: str, default: Any = None) -> Any:
    return _load_constants().get(section, {}).get(key, default)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class UpgradeCandidate:
    """A single stat upgrade option with multi-objective scoring."""
    stat:          str
    label:         str
    delta:         float
    dps_gain_pct:  float
    ehp_gain_pct:  float
    composite_score: float
    rank:          int

    def to_dict(self) -> dict:
        return {
            "stat":             self.stat,
            "label":            self.label,
            "delta":            self.delta,
            "dps_gain_pct":     round(self.dps_gain_pct, 2),
            "ehp_gain_pct":     round(self.ehp_gain_pct, 2),
            "composite_score":  round(self.composite_score, 4),
            "rank":             self.rank,
        }


@dataclass
class OptimizationResult:
    """Full multi-objective optimization output."""
    best_upgrade:  dict          # UpgradeCandidate.to_dict() of top result
    score:         float         # composite score of best upgrade
    stat_changes:  dict          # stat → delta mapping for best upgrade
    all_upgrades:  list[dict]    # all candidates ranked
    goals:         dict          # the goals dict used
    iterations:    int           # number of candidate evaluations
    execution_time: float

    def to_dict(self) -> dict:
        return {
            "best_upgrade":  self.best_upgrade,
            "score":         round(self.score, 4),
            "stat_changes":  self.stat_changes,
            "all_upgrades":  self.all_upgrades,
            "goals":         self.goals,
            "iterations":    self.iterations,
            "execution_time": round(self.execution_time, 4),
        }


# ---------------------------------------------------------------------------
# Core evaluation
# ---------------------------------------------------------------------------

def _evaluate_candidate(
    stats:        BuildStats,
    stat_key:     str,
    delta:        float,
    label:        str,
    primary_skill: str,
    skill_level:  int,
    dps_weight:   float,
    ehp_weight:   float,
    base_dps:     float,
    base_ehp:     float,
) -> UpgradeCandidate:
    """Evaluate one stat increment and return its UpgradeCandidate."""
    from app.constants.combat import CRIT_CHANCE_CAP

    modified = _copy(stats)
    current  = getattr(modified, stat_key, 0.0)
    setattr(modified, stat_key, current + delta)

    # Re-derive crit from pct fields
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

    score = dps_gain * dps_weight + ehp_gain * ehp_weight

    return UpgradeCandidate(
        stat=stat_key,
        label=label,
        delta=delta,
        dps_gain_pct=round(dps_gain, 2),
        ehp_gain_pct=round(ehp_gain, 2),
        composite_score=round(score, 4),
        rank=0,  # set after sorting
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def optimize_build(
    build: dict | BuildStats,
    goals: dict | None = None,
    iterations: int = 200,
    primary_skill: str | None = None,
    skill_level: int = 20,
) -> OptimizationResult:
    """Find the best stat upgrade using multi-objective scoring.

    This is the architecture-plan canonical function for multi-objective
    optimization.

    Args:
        build: Either a build dict (resolved via stat pipeline) or a
               resolved :class:`BuildStats`.
        goals: Objective weights dict, e.g.::

                   {"dps_weight": 0.6, "ehp_weight": 0.4}

               Defaults to ``{"dps_weight": 1.0, "ehp_weight": 0.5}``.
        iterations: Number of stat candidates to evaluate.  Capped at the
                    number of entries in STAT_TEST_INCREMENTS (default 200
                    means all candidates are tested).
        primary_skill: Skill used as DPS reference.  Falls back to
                       ``build.get("primary_skill")`` then ``"Fireball"``.
        skill_level: Skill level for DPS calculation (default 20).

    Returns:
        :class:`OptimizationResult` with best_upgrade, score, stat_changes,
        all ranked candidates, and telemetry.
    """
    if goals is None:
        goals = {
            "dps_weight": _const("optimization", "dps_weight", 1.0),
            "ehp_weight": _const("optimization", "ehp_weight", 0.5),
        }

    dps_weight = float(goals.get("dps_weight", 1.0))
    ehp_weight = float(goals.get("ehp_weight", 0.5))

    # Resolve stats
    if isinstance(build, BuildStats):
        stats = build
        skill = primary_skill or "Fireball"
    else:
        from app.engines.stat_resolution_pipeline import quick_resolve
        stats  = quick_resolve(build)
        skill  = primary_skill or build.get("primary_skill") or "Fireball"

    log.info(
        "optimize_build.start",
        dps_weight=dps_weight,
        ehp_weight=ehp_weight,
        skill=skill,
    )

    t_start = time.perf_counter()

    base_dps = calculate_dps(stats, skill, skill_level).dps
    base_ehp = calculate_ehp(stats)

    candidates = STAT_TEST_INCREMENTS[:iterations]
    results: list[UpgradeCandidate] = []

    for inc in candidates:
        candidate = _evaluate_candidate(
            stats=stats,
            stat_key=inc["key"],
            delta=inc["delta"],
            label=inc["label"],
            primary_skill=skill,
            skill_level=skill_level,
            dps_weight=dps_weight,
            ehp_weight=ehp_weight,
            base_dps=base_dps,
            base_ehp=base_ehp,
        )
        results.append(candidate)

    # Sort by composite score descending
    results.sort(key=lambda c: c.composite_score, reverse=True)
    for i, c in enumerate(results):
        c.rank = i + 1

    elapsed = time.perf_counter() - t_start

    if not results:
        return OptimizationResult(
            best_upgrade  = {},
            score         = 0.0,
            stat_changes  = {},
            all_upgrades  = [],
            goals         = dict(goals),
            iterations    = 0,
            execution_time = round(elapsed, 4),
        )

    best = results[0]
    stat_changes = {best.stat: best.delta}

    opt_result = OptimizationResult(
        best_upgrade  = best.to_dict(),
        score         = best.composite_score,
        stat_changes  = stat_changes,
        all_upgrades  = [c.to_dict() for c in results],
        goals         = dict(goals),
        iterations    = len(candidates),
        execution_time = round(elapsed, 4),
    )

    log.info(
        "optimize_build.done",
        best_stat=best.stat,
        score=best.composite_score,
        elapsed=elapsed,
    )
    return opt_result


def pareto_front(
    build: dict | BuildStats,
    primary_skill: str = "Fireball",
    skill_level: int = 20,
) -> list[dict]:
    """Return Pareto-optimal upgrades (no other upgrade is better in both DPS and EHP).

    A candidate is Pareto-optimal when no other candidate both increases DPS
    more AND increases EHP more simultaneously.

    Returns:
        List of UpgradeCandidate dicts on the Pareto front, sorted by
        dps_gain_pct descending.
    """
    if isinstance(build, BuildStats):
        stats = build
    else:
        from app.engines.stat_resolution_pipeline import quick_resolve
        stats = quick_resolve(build)

    base_dps = calculate_dps(stats, primary_skill, skill_level).dps
    base_ehp = calculate_ehp(stats)

    candidates = []
    for inc in STAT_TEST_INCREMENTS:
        c = _evaluate_candidate(
            stats=stats, stat_key=inc["key"], delta=inc["delta"],
            label=inc["label"], primary_skill=primary_skill,
            skill_level=skill_level, dps_weight=1.0, ehp_weight=1.0,
            base_dps=base_dps, base_ehp=base_ehp,
        )
        candidates.append(c)

    # Pareto filter: keep c if no other c2 dominates it
    pareto: list[UpgradeCandidate] = []
    for c in candidates:
        dominated = any(
            c2.dps_gain_pct >= c.dps_gain_pct and
            c2.ehp_gain_pct >= c.ehp_gain_pct and
            (c2.dps_gain_pct > c.dps_gain_pct or c2.ehp_gain_pct > c.ehp_gain_pct)
            for c2 in candidates
            if c2 is not c
        )
        if not dominated:
            pareto.append(c)

    pareto.sort(key=lambda c: c.dps_gain_pct, reverse=True)
    for i, c in enumerate(pareto):
        c.rank = i + 1
    return [c.to_dict() for c in pareto]
