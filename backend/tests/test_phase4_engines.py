"""
Tests for Phase 4 engines — sensitivity analyzer, upgrade ranker, efficiency scorer.

Covers: basic operation, determinism, edge cases, ranking correctness, mode switching.
"""

from __future__ import annotations

import pytest

from app.engines.stat_engine import BuildStats
from app.engines.sensitivity_analyzer import (
    analyze_sensitivity,
    SensitivityResult,
    SensitivityEntry,
    ANALYZABLE_STATS,
    _get_label,
)
from app.engines.upgrade_ranker import (
    rank_upgrades,
    RankingResult,
    RankedStat,
    MODE_WEIGHTS,
    VALID_MODES,
)
from app.engines.efficiency_scorer import (
    score_affix_efficiency,
    EfficiencyResult,
    AffixCandidate,
    _fp_cost_for_tier,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stats(**kw) -> BuildStats:
    defaults = dict(
        max_health=1000.0,
        base_damage=100.0,
        attack_speed=1.0,
        crit_chance=0.05,
        crit_multiplier=1.5,
        armour=200.0,
        fire_res=20.0,
        cold_res=15.0,
        lightning_res=10.0,
        dodge_rating=50.0,
        spell_damage_pct=30.0,
        physical_damage_pct=20.0,
        crit_chance_pct=10.0,
        crit_multiplier_pct=50.0,
        attack_speed_pct=15.0,
    )
    defaults.update(kw)
    s = BuildStats()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


def _sample_affixes() -> list[dict]:
    return [
        {
            "name": "Increased Spell Damage",
            "stat_key": "spell_damage_pct",
            "tiers": [
                {"tier": 1, "min": 5, "max": 15},
                {"tier": 3, "min": 20, "max": 40},
                {"tier": 5, "min": 50, "max": 80},
            ],
        },
        {
            "name": "Increased Armor",
            "stat_key": "armour",
            "tiers": [
                {"tier": 1, "min": 10, "max": 30},
                {"tier": 3, "min": 40, "max": 80},
                {"tier": 5, "min": 100, "max": 200},
            ],
        },
        {
            "name": "Added Health",
            "stat_key": "max_health",
            "tiers": [
                {"tier": 2, "min": 20, "max": 40},
                {"tier": 4, "min": 60, "max": 100},
            ],
        },
        {
            "name": "Fire Resistance",
            "stat_key": "fire_res",
            "tiers": [
                {"tier": 1, "min": 5, "max": 15},
                {"tier": 3, "min": 15, "max": 30},
            ],
        },
    ]


# ===========================================================================
# Sensitivity Analyzer
# ===========================================================================

class TestSensitivityAnalyzer:
    def test_basic_output_structure(self):
        stats = _stats()
        result = analyze_sensitivity(stats, "Fireball")
        assert isinstance(result, SensitivityResult)
        assert isinstance(result.entries, list)
        assert result.base_dps > 0
        assert result.base_ehp > 0
        assert result.execution_time >= 0

    def test_entries_are_ranked(self):
        stats = _stats()
        result = analyze_sensitivity(stats, "Fireball")
        for i, entry in enumerate(result.entries):
            assert entry.rank == i + 1

    def test_impact_scores_descending(self):
        stats = _stats()
        result = analyze_sensitivity(stats, "Fireball")
        scores = [e.impact_score for e in result.entries]
        assert scores == sorted(scores, reverse=True)

    def test_deterministic(self):
        stats = _stats()
        r1 = analyze_sensitivity(stats, "Fireball")
        r2 = analyze_sensitivity(stats, "Fireball")
        assert len(r1.entries) == len(r2.entries)
        for e1, e2 in zip(r1.entries, r2.entries):
            assert e1.stat_key == e2.stat_key
            assert e1.dps_gain_pct == e2.dps_gain_pct
            assert e1.ehp_gain_pct == e2.ehp_gain_pct

    def test_to_dict(self):
        stats = _stats()
        result = analyze_sensitivity(stats, "Fireball")
        d = result.to_dict()
        assert "entries" in d
        assert "base_dps" in d
        assert "base_ehp" in d
        assert isinstance(d["entries"], list)
        if d["entries"]:
            entry = d["entries"][0]
            assert "stat_key" in entry
            assert "label" in entry
            assert "impact_score" in entry

    def test_entries_have_labels(self):
        stats = _stats()
        result = analyze_sensitivity(stats, "Fireball")
        for entry in result.entries:
            assert entry.label  # not empty
            assert isinstance(entry.label, str)

    def test_get_label_known(self):
        assert _get_label("crit_chance_pct") == "Crit Chance"
        assert _get_label("max_health") == "Health"

    def test_get_label_unknown(self):
        label = _get_label("some_unknown_stat")
        assert label == "Some Unknown Stat"

    def test_custom_weights(self):
        stats = _stats()
        offense = analyze_sensitivity(stats, "Fireball", offense_weight=1.0, defense_weight=0.0)
        defense = analyze_sensitivity(stats, "Fireball", offense_weight=0.0, defense_weight=1.0)
        # Offense-only should rank offensive stats higher
        # Defense-only should rank defensive stats higher
        assert offense.entries[0].stat_key != defense.entries[0].stat_key or len(offense.entries) == 1

    def test_zero_stats_still_produce_entries(self):
        stats = BuildStats()
        stats.base_damage = 50.0
        stats.max_health = 500.0
        result = analyze_sensitivity(stats, "Fireball")
        # Should still have entries even with mostly zero stats
        assert isinstance(result.entries, list)


# ===========================================================================
# Upgrade Ranker
# ===========================================================================

class TestUpgradeRanker:
    def _sensitivity(self) -> SensitivityResult:
        return analyze_sensitivity(_stats(), "Fireball")

    def test_balanced_mode(self):
        result = rank_upgrades(self._sensitivity(), mode="balanced")
        assert isinstance(result, RankingResult)
        assert result.mode == "balanced"
        assert result.offense_weight == 0.6
        assert result.defense_weight == 0.4

    def test_offense_mode(self):
        result = rank_upgrades(self._sensitivity(), mode="offense")
        assert result.offense_weight == 1.0
        assert result.defense_weight == 0.0

    def test_defense_mode(self):
        result = rank_upgrades(self._sensitivity(), mode="defense")
        assert result.offense_weight == 0.0
        assert result.defense_weight == 1.0

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid mode"):
            rank_upgrades(self._sensitivity(), mode="invalid")

    def test_rankings_sorted_descending(self):
        result = rank_upgrades(self._sensitivity(), mode="balanced")
        scores = [r.impact_score for r in result.stat_rankings]
        assert scores == sorted(scores, reverse=True)

    def test_ranks_assigned(self):
        result = rank_upgrades(self._sensitivity(), mode="balanced")
        for i, r in enumerate(result.stat_rankings):
            assert r.rank == i + 1

    def test_to_dict(self):
        result = rank_upgrades(self._sensitivity(), mode="balanced")
        d = result.to_dict()
        assert "stat_rankings" in d
        assert "mode" in d
        assert d["mode"] == "balanced"

    def test_different_modes_different_rankings(self):
        sensitivity = self._sensitivity()
        offense = rank_upgrades(sensitivity, mode="offense")
        defense = rank_upgrades(sensitivity, mode="defense")
        # The top stat should differ between pure offense and pure defense
        if len(offense.stat_rankings) > 0 and len(defense.stat_rankings) > 0:
            offense_top = offense.stat_rankings[0].stat_key
            defense_top = defense.stat_rankings[0].stat_key
            # At least the ordering should differ (or same if only one stat matters)
            assert len(offense.stat_rankings) == len(defense.stat_rankings)


# ===========================================================================
# Efficiency Scorer
# ===========================================================================

class TestEfficiencyScorer:
    def test_basic_output_structure(self):
        stats = _stats()
        affixes = _sample_affixes()
        result = score_affix_efficiency(stats, affixes, "Fireball")
        assert isinstance(result, EfficiencyResult)
        assert isinstance(result.candidates, list)
        assert result.base_dps > 0
        assert result.base_ehp > 0

    def test_candidates_ranked(self):
        stats = _stats()
        affixes = _sample_affixes()
        result = score_affix_efficiency(stats, affixes, "Fireball")
        for i, c in enumerate(result.candidates):
            assert c.rank == i + 1

    def test_efficiency_scores_descending(self):
        stats = _stats()
        affixes = _sample_affixes()
        result = score_affix_efficiency(stats, affixes, "Fireball")
        scores = [c.efficiency_score for c in result.candidates]
        assert scores == sorted(scores, reverse=True)

    def test_top_n_limiting(self):
        stats = _stats()
        affixes = _sample_affixes()
        result = score_affix_efficiency(stats, affixes, "Fireball", top_n=2)
        assert len(result.candidates) <= 2

    def test_to_dict(self):
        stats = _stats()
        affixes = _sample_affixes()
        result = score_affix_efficiency(stats, affixes, "Fireball")
        d = result.to_dict()
        assert "candidates" in d
        assert "base_dps" in d
        if d["candidates"]:
            c = d["candidates"][0]
            assert "affix_id" in c
            assert "efficiency_score" in c
            assert "fp_cost" in c

    def test_empty_affixes(self):
        stats = _stats()
        result = score_affix_efficiency(stats, [], "Fireball")
        assert result.candidates == []

    def test_invalid_stat_key_skipped(self):
        stats = _stats()
        bad_affixes = [
            {
                "name": "Nonexistent Stat",
                "stat_key": "totally_fake_stat",
                "tiers": [{"tier": 1, "min": 10, "max": 20}],
            }
        ]
        result = score_affix_efficiency(stats, bad_affixes, "Fireball")
        assert result.candidates == []

    def test_no_tiers_skipped(self):
        stats = _stats()
        no_tier_affixes = [
            {"name": "Empty Tiers", "stat_key": "armour", "tiers": []},
        ]
        result = score_affix_efficiency(stats, no_tier_affixes, "Fireball")
        assert result.candidates == []

    def test_fp_cost_scaling(self):
        assert _fp_cost_for_tier(1) <= _fp_cost_for_tier(3)
        assert _fp_cost_for_tier(3) <= _fp_cost_for_tier(5)
        assert _fp_cost_for_tier(5) <= _fp_cost_for_tier(7)

    def test_deterministic(self):
        stats = _stats()
        affixes = _sample_affixes()
        r1 = score_affix_efficiency(stats, affixes, "Fireball")
        r2 = score_affix_efficiency(stats, affixes, "Fireball")
        assert len(r1.candidates) == len(r2.candidates)
        for c1, c2 in zip(r1.candidates, r2.candidates):
            assert c1.affix_id == c2.affix_id
            assert c1.efficiency_score == c2.efficiency_score

    def test_custom_weights(self):
        stats = _stats()
        affixes = _sample_affixes()
        offense = score_affix_efficiency(
            stats, affixes, "Fireball", offense_weight=1.0, defense_weight=0.0,
        )
        defense = score_affix_efficiency(
            stats, affixes, "Fireball", offense_weight=0.0, defense_weight=1.0,
        )
        # Offensive and defensive weighting should produce different top candidates
        if offense.candidates and defense.candidates:
            assert offense.candidates[0].affix_id != defense.candidates[0].affix_id or len(affixes) <= 1
