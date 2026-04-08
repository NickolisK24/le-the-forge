"""
Upgrade Ranker — Phase 4 Engine

Takes sensitivity analysis results and produces ranked lists:
  - DPS impact descending
  - EHP impact descending
  - Combined (weighted) impact score

Supports three modes: "offense" (100/0), "defense" (0/100), "balanced" (60/40).

Labels each result with a human-readable stat name from game data.

Pure module — no DB, no HTTP.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.engines.sensitivity_analyzer import SensitivityEntry, SensitivityResult
from app.utils.logging import ForgeLogger

log = ForgeLogger(__name__)


# ---------------------------------------------------------------------------
# Mode weights
# ---------------------------------------------------------------------------

MODE_WEIGHTS: dict[str, tuple[float, float]] = {
    "balanced": (0.6, 0.4),
    "offense":  (1.0, 0.0),
    "defense":  (0.0, 1.0),
}

VALID_MODES = frozenset(MODE_WEIGHTS.keys())


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class RankedStat:
    """A stat entry ranked within a specific mode."""
    stat_key: str
    label: str
    dps_gain_pct: float
    ehp_gain_pct: float
    impact_score: float
    rank: int

    def to_dict(self) -> dict:
        return {
            "stat_key": self.stat_key,
            "label": self.label,
            "dps_gain_pct": round(self.dps_gain_pct, 2),
            "ehp_gain_pct": round(self.ehp_gain_pct, 2),
            "impact_score": round(self.impact_score, 4),
            "rank": self.rank,
        }


@dataclass
class RankingResult:
    """Output of the upgrade ranker."""
    stat_rankings: list[RankedStat]
    mode: str
    offense_weight: float
    defense_weight: float

    def to_dict(self) -> dict:
        return {
            "stat_rankings": [s.to_dict() for s in self.stat_rankings],
            "mode": self.mode,
            "offense_weight": self.offense_weight,
            "defense_weight": self.defense_weight,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def rank_upgrades(
    sensitivity: SensitivityResult,
    mode: str = "balanced",
) -> RankingResult:
    """Produce a ranked list of stat upgrades from sensitivity analysis.

    Args:
        sensitivity: Output from analyze_sensitivity().
        mode: One of "balanced", "offense", or "defense".
              - "balanced" uses 60% DPS / 40% EHP weighting.
              - "offense" uses 100% DPS / 0% EHP.
              - "defense" uses 0% DPS / 100% EHP.

    Returns:
        RankingResult with stats sorted by the mode's impact score.

    Raises:
        ValueError: If mode is not one of the valid options.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"Invalid mode '{mode}'. Must be one of: {', '.join(sorted(VALID_MODES))}")

    offense_w, defense_w = MODE_WEIGHTS[mode]

    log.info("rank_upgrades.start", mode=mode, n_entries=len(sensitivity.entries))

    ranked: list[RankedStat] = []
    for entry in sensitivity.entries:
        score = entry.dps_gain_pct * offense_w + entry.ehp_gain_pct * defense_w
        ranked.append(RankedStat(
            stat_key=entry.stat_key,
            label=entry.label,
            dps_gain_pct=entry.dps_gain_pct,
            ehp_gain_pct=entry.ehp_gain_pct,
            impact_score=round(score, 4),
            rank=0,
        ))

    # Sort by impact_score descending
    ranked.sort(key=lambda r: r.impact_score, reverse=True)
    for i, r in enumerate(ranked):
        r.rank = i + 1

    log.info("rank_upgrades.done", mode=mode, top_stat=ranked[0].stat_key if ranked else "none")

    return RankingResult(
        stat_rankings=ranked,
        mode=mode,
        offense_weight=offense_w,
        defense_weight=defense_w,
    )
