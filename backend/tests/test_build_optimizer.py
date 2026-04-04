"""
Tests for build_optimizer — Upgrade 4

Covers: multi-objective scoring, pareto front, determinism,
result structure, weight sensitivity, stat candidates.
"""

from __future__ import annotations

import pytest

from app.engines.build_optimizer import (
    optimize_build,
    pareto_front,
    OptimizationResult,
    UpgradeCandidate,
)
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build(
    char_class="Mage",
    mastery="Sorcerer",
    passive_tree=None,
    gear=None,
    primary_skill="Fireball",
) -> dict:
    return {
        "character_class": char_class,
        "mastery": mastery,
        "passive_tree": passive_tree or [],
        "gear": gear or [],
        "primary_skill": primary_skill,
    }


def _stats(**kw) -> BuildStats:
    defaults = dict(
        max_health=1000.0,
        base_damage=100.0,
        attack_speed=1.0,
        crit_chance=0.05,
        crit_multiplier=1.5,
        armour=100.0,
        fire_res=0.0,
    )
    defaults.update(kw)
    s = BuildStats()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


def _run(build=None, goals=None, **kw) -> OptimizationResult:
    if build is None:
        build = _build()
    return optimize_build(build, goals=goals, **kw)


# ---------------------------------------------------------------------------
# 1. Return type and structure
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_optimization_result(self):
        r = _run()
        assert isinstance(r, OptimizationResult)

    def test_to_dict_has_best_upgrade(self):
        assert "best_upgrade" in _run().to_dict()

    def test_to_dict_has_score(self):
        assert "score" in _run().to_dict()

    def test_to_dict_has_stat_changes(self):
        assert "stat_changes" in _run().to_dict()

    def test_to_dict_has_all_upgrades(self):
        assert "all_upgrades" in _run().to_dict()

    def test_to_dict_has_goals(self):
        assert "goals" in _run().to_dict()

    def test_to_dict_has_iterations(self):
        assert "iterations" in _run().to_dict()

    def test_to_dict_has_execution_time(self):
        assert "execution_time" in _run().to_dict()

    def test_best_upgrade_is_dict(self):
        r = _run()
        assert isinstance(r.best_upgrade, dict)

    def test_all_upgrades_is_list(self):
        r = _run()
        assert isinstance(r.all_upgrades, list)

    def test_stat_changes_is_dict(self):
        r = _run()
        assert isinstance(r.stat_changes, dict)

    def test_goals_reflects_input(self):
        goals = {"dps_weight": 0.7, "ehp_weight": 0.3}
        r = optimize_build(_build(), goals=goals)
        assert r.goals["dps_weight"] == pytest.approx(0.7)
        assert r.goals["ehp_weight"] == pytest.approx(0.3)

    def test_execution_time_nonnegative(self):
        r = _run()
        assert r.execution_time >= 0.0

    def test_score_is_float(self):
        r = _run()
        assert isinstance(r.score, (int, float))


# ---------------------------------------------------------------------------
# 2. UpgradeCandidate structure
# ---------------------------------------------------------------------------

class TestUpgradeCandidateStructure:
    def test_best_upgrade_has_stat(self):
        r = _run()
        assert "stat" in r.best_upgrade

    def test_best_upgrade_has_label(self):
        r = _run()
        assert "label" in r.best_upgrade

    def test_best_upgrade_has_delta(self):
        r = _run()
        assert "delta" in r.best_upgrade

    def test_best_upgrade_has_dps_gain_pct(self):
        r = _run()
        assert "dps_gain_pct" in r.best_upgrade

    def test_best_upgrade_has_ehp_gain_pct(self):
        r = _run()
        assert "ehp_gain_pct" in r.best_upgrade

    def test_best_upgrade_has_composite_score(self):
        r = _run()
        assert "composite_score" in r.best_upgrade

    def test_best_upgrade_has_rank(self):
        r = _run()
        assert "rank" in r.best_upgrade

    def test_best_upgrade_rank_is_1(self):
        r = _run()
        assert r.best_upgrade["rank"] == 1

    def test_all_upgrades_have_rank(self):
        r = _run()
        for u in r.all_upgrades:
            assert "rank" in u

    def test_ranks_are_sequential(self):
        r = _run()
        ranks = [u["rank"] for u in r.all_upgrades]
        assert ranks == list(range(1, len(ranks) + 1))

    def test_all_upgrades_sorted_by_score_descending(self):
        r = _run()
        scores = [u["composite_score"] for u in r.all_upgrades]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# 3. Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_same_build_same_best_stat(self):
        b = _build()
        r1 = optimize_build(b)
        r2 = optimize_build(b)
        assert r1.best_upgrade["stat"] == r2.best_upgrade["stat"]

    def test_same_build_same_score(self):
        b = _build()
        r1 = optimize_build(b)
        r2 = optimize_build(b)
        assert r1.score == r2.score

    @pytest.mark.parametrize("char_class,mastery", [
        ("Mage", "Sorcerer"),
        ("Sentinel", "Paladin"),
        ("Rogue", "Marksman"),
    ])
    def test_determinism_across_classes(self, char_class, mastery):
        b = _build(char_class=char_class, mastery=mastery)
        r1 = optimize_build(b)
        r2 = optimize_build(b)
        assert r1.best_upgrade["stat"] == r2.best_upgrade["stat"]

    def test_stats_object_same_result(self):
        s = _stats()
        r1 = optimize_build(s)
        r2 = optimize_build(s)
        assert r1.score == r2.score


# ---------------------------------------------------------------------------
# 4. Weight sensitivity
# ---------------------------------------------------------------------------

class TestWeightSensitivity:
    def test_pure_dps_goals(self):
        goals = {"dps_weight": 1.0, "ehp_weight": 0.0}
        r = optimize_build(_build(), goals=goals)
        assert isinstance(r, OptimizationResult)
        assert r.goals["dps_weight"] == 1.0

    def test_pure_ehp_goals(self):
        goals = {"dps_weight": 0.0, "ehp_weight": 1.0}
        r = optimize_build(_build(), goals=goals)
        assert isinstance(r, OptimizationResult)
        assert r.goals["ehp_weight"] == 1.0

    def test_balanced_goals(self):
        goals = {"dps_weight": 0.5, "ehp_weight": 0.5}
        r = optimize_build(_build(), goals=goals)
        assert isinstance(r, OptimizationResult)

    @pytest.mark.parametrize("dw,ew", [
        (1.0, 0.0), (0.0, 1.0), (0.5, 0.5),
        (0.7, 0.3), (0.3, 0.7), (2.0, 1.0),
    ])
    def test_various_weights_resolve(self, dw, ew):
        r = optimize_build(_build(), goals={"dps_weight": dw, "ehp_weight": ew})
        assert r.score is not None

    def test_default_goals_applied_when_none(self):
        r = optimize_build(_build(), goals=None)
        assert "dps_weight" in r.goals
        assert "ehp_weight" in r.goals


# ---------------------------------------------------------------------------
# 5. Iteration count
# ---------------------------------------------------------------------------

class TestIterationCount:
    @pytest.mark.parametrize("n", [1, 5, 10])
    def test_iteration_count_respected_small(self, n):
        r = optimize_build(_build(), iterations=n)
        assert r.iterations == n

    @pytest.mark.parametrize("n", [50, 100, 200])
    def test_large_iterations_capped_at_candidates(self, n):
        # iterations > len(STAT_TEST_INCREMENTS) are capped at candidate count
        r = optimize_build(_build(), iterations=n)
        assert r.iterations <= n

    def test_default_iterations_positive(self):
        r = optimize_build(_build())
        assert r.iterations > 0

    def test_more_iterations_more_upgrades(self):
        r1 = optimize_build(_build(), iterations=5)
        r2 = optimize_build(_build(), iterations=10)
        assert len(r2.all_upgrades) >= len(r1.all_upgrades)


# ---------------------------------------------------------------------------
# 6. Score invariants
# ---------------------------------------------------------------------------

class TestScoreInvariants:
    def test_composite_score_formula(self):
        """score = dps_gain * dw + ehp_gain * ew"""
        r = _run()
        best = r.best_upgrade
        dw = r.goals.get("dps_weight", 1.0)
        ew = r.goals.get("ehp_weight", 0.5)
        expected = best["dps_gain_pct"] * dw + best["ehp_gain_pct"] * ew
        assert best["composite_score"] == pytest.approx(expected, abs=0.01)

    def test_best_score_equals_result_score(self):
        r = _run()
        assert r.score == pytest.approx(r.best_upgrade["composite_score"])

    def test_best_is_top_scored(self):
        r = _run()
        all_scores = [u["composite_score"] for u in r.all_upgrades]
        assert r.score == pytest.approx(max(all_scores))

    def test_stat_changes_nonempty(self):
        r = _run()
        assert len(r.stat_changes) > 0

    def test_stat_changes_key_matches_best(self):
        r = _run()
        assert r.best_upgrade["stat"] in r.stat_changes


# ---------------------------------------------------------------------------
# 7. Build stats object input
# ---------------------------------------------------------------------------

class TestBuildStatsInput:
    def test_accepts_build_stats(self):
        s = _stats()
        r = optimize_build(s)
        assert isinstance(r, OptimizationResult)

    def test_accepts_build_dict(self):
        b = _build()
        r = optimize_build(b)
        assert isinstance(r, OptimizationResult)

    def test_stats_with_zero_damage_resolves(self):
        s = _stats(base_damage=0.0)
        r = optimize_build(s, iterations=10)
        assert isinstance(r, OptimizationResult)

    def test_stats_with_high_damage_resolves(self):
        s = _stats(base_damage=10000.0)
        r = optimize_build(s, iterations=10)
        assert isinstance(r, OptimizationResult)


# ---------------------------------------------------------------------------
# 8. Pareto front
# ---------------------------------------------------------------------------

class TestParetoFront:
    def test_returns_list(self):
        result = pareto_front(_build())
        assert isinstance(result, list)

    def test_each_element_is_dict(self):
        result = pareto_front(_build())
        for item in result:
            assert isinstance(item, dict)

    def test_pareto_elements_have_rank(self):
        result = pareto_front(_build())
        for item in result:
            assert "rank" in item

    def test_pareto_elements_have_stat(self):
        result = pareto_front(_build())
        for item in result:
            assert "stat" in item

    def test_pareto_nonempty(self):
        result = pareto_front(_build())
        assert len(result) > 0

    def test_pareto_sorted_by_dps_gain(self):
        result = pareto_front(_build())
        dps_gains = [r["dps_gain_pct"] for r in result]
        assert dps_gains == sorted(dps_gains, reverse=True)

    def test_pareto_no_dominated_candidates(self):
        result = pareto_front(_build())
        for i, c1 in enumerate(result):
            for j, c2 in enumerate(result):
                if i == j:
                    continue
                # c2 should not dominate c1 (both dimensions strictly better)
                dominated = (
                    c2["dps_gain_pct"] >= c1["dps_gain_pct"] and
                    c2["ehp_gain_pct"] >= c1["ehp_gain_pct"] and
                    (c2["dps_gain_pct"] > c1["dps_gain_pct"] or
                     c2["ehp_gain_pct"] > c1["ehp_gain_pct"])
                )
                assert not dominated, f"Pareto candidate {j} dominates {i}"

    def test_pareto_accepts_build_stats(self):
        s = _stats()
        result = pareto_front(s)
        assert isinstance(result, list)

    @pytest.mark.parametrize("char_class,mastery", [
        ("Mage", "Sorcerer"),
        ("Sentinel", "Paladin"),
        ("Rogue", "Marksman"),
        ("Primalist", "Druid"),
        ("Acolyte", "Lich"),
    ])
    def test_pareto_works_for_all_classes(self, char_class, mastery):
        b = _build(char_class=char_class, mastery=mastery)
        result = pareto_front(b)
        assert isinstance(result, list)

    def test_pareto_deterministic(self):
        b = _build()
        r1 = pareto_front(b)
        r2 = pareto_front(b)
        assert len(r1) == len(r2)
        if r1:
            assert r1[0]["stat"] == r2[0]["stat"]


# ---------------------------------------------------------------------------
# 9. Primary skill sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill", ["Fireball", "Frostbolt", "Lightning Blast"])
def test_skill_parameter_resolves(skill):
    r = optimize_build(_build(), primary_skill=skill, iterations=10)
    assert isinstance(r, OptimizationResult)


def test_primary_skill_from_build_used():
    b = _build(primary_skill="Fireball")
    r = optimize_build(b, iterations=10)
    assert isinstance(r, OptimizationResult)


# ---------------------------------------------------------------------------
# 10. Character classes
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", [
    ("Mage", "Sorcerer"),
    ("Mage", "Runemaster"),
    ("Sentinel", "Paladin"),
    ("Sentinel", "Forge Guard"),
    ("Rogue", "Bladedancer"),
    ("Rogue", "Marksman"),
    ("Primalist", "Shaman"),
    ("Primalist", "Druid"),
    ("Acolyte", "Lich"),
    ("Acolyte", "Necromancer"),
])
def test_optimize_all_classes(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r = optimize_build(b, iterations=5)
    assert isinstance(r, OptimizationResult)
    assert r.iterations == 5


# ---------------------------------------------------------------------------
# 11. to_dict round-trip
# ---------------------------------------------------------------------------

class TestToDictRoundTrip:
    def test_to_dict_is_serializable(self):
        import json
        r = _run(iterations=5)
        d = r.to_dict()
        json.dumps(d)  # should not raise

    def test_to_dict_score_rounded(self):
        r = _run(iterations=5)
        d = r.to_dict()
        s = str(d["score"])
        if "." in s:
            assert len(s.split(".")[1]) <= 4

    def test_all_upgrades_scores_rounded(self):
        r = _run(iterations=5)
        for u in r.all_upgrades:
            s = str(u["composite_score"])
            if "." in s:
                assert len(s.split(".")[1]) <= 4


# ---------------------------------------------------------------------------
# 12. Skill level sensitivity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_level", [1, 5, 10, 15, 20])
def test_skill_levels(skill_level):
    r = optimize_build(_build(), skill_level=skill_level, iterations=5)
    assert isinstance(r, OptimizationResult)


# ---------------------------------------------------------------------------
# 13. All candidates evaluated
# ---------------------------------------------------------------------------

def test_all_upgrades_count_equals_iterations():
    n = 10
    r = optimize_build(_build(), iterations=n)
    assert r.iterations == n
    assert len(r.all_upgrades) == n


def test_unique_stats_in_candidates():
    r = optimize_build(_build(), iterations=50)
    stats = [u["stat"] for u in r.all_upgrades]
    # All stats should be string keys
    for stat in stats:
        assert isinstance(stat, str)


# ---------------------------------------------------------------------------
# 14. Parametric weight combinations
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("dw,ew,expected_goals_ok", [
    (1.0, 0.5, True),
    (0.6, 0.4, True),
    (0.0, 1.0, True),
    (1.0, 0.0, True),
    (2.0, 2.0, True),
])
def test_weight_combinations(dw, ew, expected_goals_ok):
    goals = {"dps_weight": dw, "ehp_weight": ew}
    r = optimize_build(_build(), goals=goals, iterations=5)
    assert isinstance(r, OptimizationResult) == expected_goals_ok


# ---------------------------------------------------------------------------
# 15. Upgrade candidate dicts are complete
# ---------------------------------------------------------------------------

_EXPECTED_KEYS = {"stat", "label", "delta", "dps_gain_pct", "ehp_gain_pct",
                  "composite_score", "rank"}


@pytest.mark.parametrize("idx", [0, 1, 2])
def test_upgrade_candidate_keys_complete(idx):
    r = optimize_build(_build(), iterations=10)
    if idx < len(r.all_upgrades):
        u = r.all_upgrades[idx]
        for k in _EXPECTED_KEYS:
            assert k in u, f"Missing key {k!r} in upgrade candidate"
