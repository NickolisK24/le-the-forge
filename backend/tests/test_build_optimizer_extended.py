"""
Extended build optimizer tests — parametrized coverage.
"""

from __future__ import annotations

import pytest

from app.engines.build_optimizer import (
    optimize_build, pareto_front, OptimizationResult, UpgradeCandidate,
)
from app.engines.stat_engine import BuildStats


def _build(char_class="Mage", mastery="Sorcerer", primary_skill="Fireball") -> dict:
    return {"character_class": char_class, "mastery": mastery,
            "passive_tree": [], "gear": [], "primary_skill": primary_skill}


def _stats(**kw) -> BuildStats:
    defaults = dict(max_health=1000.0, base_damage=100.0, attack_speed=1.0,
                    crit_chance=0.05, crit_multiplier=1.5, armour=100.0)
    defaults.update(kw)
    s = BuildStats()
    for k, v in defaults.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# A. All class/mastery combinations
# ---------------------------------------------------------------------------

_CLASSES = [
    ("Mage", "Sorcerer"), ("Mage", "Runemaster"), ("Mage", "Spellblade"),
    ("Sentinel", "Forge Guard"), ("Sentinel", "Paladin"), ("Sentinel", "Void Knight"),
    ("Rogue", "Bladedancer"), ("Rogue", "Marksman"), ("Rogue", "Falconer"),
    ("Primalist", "Shaman"), ("Primalist", "Druid"), ("Primalist", "Beastmaster"),
    ("Acolyte", "Lich"), ("Acolyte", "Necromancer"), ("Acolyte", "Warlock"),
]


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_optimize(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    assert isinstance(r, OptimizationResult)


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_pareto(char_class, mastery):
    result = pareto_front(_build(char_class=char_class, mastery=mastery))
    assert isinstance(result, list)


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_classes_deterministic(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r1 = optimize_build(b, iterations=5)
    r2 = optimize_build(b, iterations=5)
    assert r1.best_upgrade["stat"] == r2.best_upgrade["stat"]


# ---------------------------------------------------------------------------
# B. Goal weight combinations
# ---------------------------------------------------------------------------

_WEIGHT_COMBOS = [
    (1.0, 0.0), (0.0, 1.0), (1.0, 1.0), (0.5, 0.5),
    (0.7, 0.3), (0.3, 0.7), (2.0, 1.0), (1.0, 2.0),
    (0.1, 0.9), (0.9, 0.1),
]


@pytest.mark.parametrize("dw,ew", _WEIGHT_COMBOS)
def test_weight_combos_return_result(dw, ew):
    r = optimize_build(_build(), goals={"dps_weight": dw, "ehp_weight": ew}, iterations=5)
    assert isinstance(r, OptimizationResult)


@pytest.mark.parametrize("dw,ew", _WEIGHT_COMBOS)
def test_weight_combos_goals_preserved(dw, ew):
    r = optimize_build(_build(), goals={"dps_weight": dw, "ehp_weight": ew}, iterations=5)
    assert r.goals["dps_weight"] == pytest.approx(dw)
    assert r.goals["ehp_weight"] == pytest.approx(ew)


@pytest.mark.parametrize("dw,ew", _WEIGHT_COMBOS)
def test_weight_combos_score_formula(dw, ew):
    r = optimize_build(_build(), goals={"dps_weight": dw, "ehp_weight": ew}, iterations=5)
    best = r.best_upgrade
    expected = best["dps_gain_pct"] * dw + best["ehp_gain_pct"] * ew
    assert best["composite_score"] == pytest.approx(expected, abs=0.01)


# ---------------------------------------------------------------------------
# C. Iteration counts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 2, 3, 5, 7, 10])
def test_small_iteration_counts(n):
    r = optimize_build(_build(), iterations=n)
    assert r.iterations == n
    assert len(r.all_upgrades) == n


@pytest.mark.parametrize("n", [1, 3, 5, 7, 10])
def test_ranks_sequential_for_n(n):
    r = optimize_build(_build(), iterations=n)
    ranks = [u["rank"] for u in r.all_upgrades]
    assert ranks == list(range(1, n + 1))


# ---------------------------------------------------------------------------
# D. Skill levels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("skill_level", [1, 5, 10, 15, 20, 25, 30])
def test_skill_levels_resolve(skill_level):
    r = optimize_build(_build(), skill_level=skill_level, iterations=5)
    assert isinstance(r, OptimizationResult)


@pytest.mark.parametrize("skill", [
    "Fireball", "Frostbolt", "Lightning Blast", "Hammer Throw",
    "Shuriken Throw", "Maelstrom",
])
def test_primary_skill_parameter(skill):
    r = optimize_build(_build(), primary_skill=skill, iterations=5)
    assert isinstance(r, OptimizationResult)


# ---------------------------------------------------------------------------
# E. BuildStats input
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("base_damage", [10.0, 50.0, 100.0, 500.0, 1000.0])
def test_stats_base_damage_levels(base_damage):
    s = _stats(base_damage=base_damage)
    r = optimize_build(s, iterations=5)
    assert isinstance(r, OptimizationResult)


@pytest.mark.parametrize("max_health", [100.0, 500.0, 1000.0, 5000.0])
def test_stats_max_health_levels(max_health):
    s = _stats(max_health=max_health)
    r = optimize_build(s, iterations=5)
    assert isinstance(r, OptimizationResult)


# ---------------------------------------------------------------------------
# F. Pareto front properties
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_pareto_nonempty_per_class(char_class, mastery):
    result = pareto_front(_build(char_class=char_class, mastery=mastery))
    assert len(result) > 0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_pareto_elements_have_stat(char_class, mastery):
    result = pareto_front(_build(char_class=char_class, mastery=mastery))
    for item in result:
        assert "stat" in item


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_pareto_elements_sorted_dps_desc(char_class, mastery):
    result = pareto_front(_build(char_class=char_class, mastery=mastery))
    dps_gains = [r["dps_gain_pct"] for r in result]
    assert dps_gains == sorted(dps_gains, reverse=True)


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_pareto_deterministic_per_class(char_class, mastery):
    b = _build(char_class=char_class, mastery=mastery)
    r1 = pareto_front(b)
    r2 = pareto_front(b)
    assert len(r1) == len(r2)


# ---------------------------------------------------------------------------
# G. Upgrade candidate fields
# ---------------------------------------------------------------------------

_REQUIRED_FIELDS = ["stat", "label", "delta", "dps_gain_pct", "ehp_gain_pct",
                     "composite_score", "rank"]


@pytest.mark.parametrize("char_class,mastery", _CLASSES[:5])
def test_best_upgrade_fields_present(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    for field in _REQUIRED_FIELDS:
        assert field in r.best_upgrade


@pytest.mark.parametrize("char_class,mastery", _CLASSES[:5])
def test_all_upgrades_have_all_fields(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    for upgrade in r.all_upgrades:
        for field in _REQUIRED_FIELDS:
            assert field in upgrade


# ---------------------------------------------------------------------------
# H. Score ordering
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_all_upgrades_sorted_descending(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    scores = [u["composite_score"] for u in r.all_upgrades]
    assert scores == sorted(scores, reverse=True)


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_best_upgrade_rank_1(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    assert r.best_upgrade["rank"] == 1


# ---------------------------------------------------------------------------
# I. Stat changes dict
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_stat_changes_nonempty(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    assert len(r.stat_changes) > 0


@pytest.mark.parametrize("char_class,mastery", _CLASSES)
def test_stat_changes_key_matches_best(char_class, mastery):
    r = optimize_build(_build(char_class=char_class, mastery=mastery), iterations=5)
    assert r.best_upgrade["stat"] in r.stat_changes


# ---------------------------------------------------------------------------
# J. Execution time
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 5, 10])
def test_execution_time_nonneg(n):
    r = optimize_build(_build(), iterations=n)
    assert r.execution_time >= 0.0
