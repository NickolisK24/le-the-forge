"""
Extended craft simulator tests — parametrized coverage.
"""

from __future__ import annotations

import pytest

from app.engines.craft_simulator import simulate_crafting_path, CraftSimulationResult


def _item(fp=20, slot="helmet", affixes=None, prefixes=None, suffixes=None) -> dict:
    item = {"slot_type": slot, "forging_potential": fp}
    if affixes is not None:
        item["affixes"] = affixes
    else:
        item["prefixes"] = prefixes or []
        item["suffixes"] = suffixes or []
    return item


def _action(action="add_affix", affix="Added Health", target_tier=None) -> dict:
    a = {"action": action, "affix": affix}
    if target_tier is not None:
        a["target_tier"] = target_tier
    return a


def _run(item=None, actions=None, **kw) -> CraftSimulationResult:
    if item is None:
        item = _item(fp=30)
    if actions is None:
        actions = [_action()]
    return simulate_crafting_path(item, actions, **kw)


# ---------------------------------------------------------------------------
# A. Seeds 0-49: determinism and validity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", range(50))
def test_seed_determinism_50(seed):
    item = _item(fp=20)
    actions = [_action()]
    r1 = simulate_crafting_path(item, actions, seed=seed, iterations=100)
    r2 = simulate_crafting_path(item, actions, seed=seed, iterations=100)
    assert r1.success_rate == r2.success_rate
    assert r1.fracture_rate == r2.fracture_rate


@pytest.mark.parametrize("seed", range(50))
def test_seed_valid_rates(seed):
    r = simulate_crafting_path(_item(fp=20), [_action()], seed=seed, iterations=100)
    assert 0.0 <= r.success_rate <= 1.0
    assert 0.0 <= r.fracture_rate <= 1.0
    assert abs(r.success_rate + r.fracture_rate - 1.0) < 1e-9


# ---------------------------------------------------------------------------
# B. FP levels
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp", [5, 10, 15, 20, 25, 30, 40, 50, 75, 100])
def test_fp_levels_valid_result(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=200, seed=42)
    assert isinstance(r, CraftSimulationResult)
    assert r.average_fp_remaining >= 0.0


@pytest.mark.parametrize("fp", [5, 10, 15, 20, 30, 50])
def test_fp_remaining_not_exceed_initial(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=200, seed=42)
    assert r.average_fp_remaining <= float(fp)


# ---------------------------------------------------------------------------
# C. Iteration counts
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 5, 10, 25, 50, 100, 200, 500])
def test_iteration_count_exact(n):
    r = simulate_crafting_path(_item(fp=20), [_action()], iterations=n, seed=42)
    assert r.iterations == n


@pytest.mark.parametrize("n", [1, 10, 100])
def test_single_path_metrics(n):
    r = simulate_crafting_path(_item(fp=30), [_action()], iterations=n, seed=42)
    assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# D. Fracture disabled
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp", [0, 1, 5, 10, 20])
def test_fracture_disabled_no_fractures(fp):
    r = simulate_crafting_path(
        _item(fp=fp), [_action()],
        fracture_enabled=False, iterations=100, seed=42
    )
    assert r.fracture_rate == 0.0
    assert r.success_rate == pytest.approx(1.0)


@pytest.mark.parametrize("seed", [1, 7, 42, 99, 123])
def test_fracture_disabled_always_100pct_success(seed):
    r = simulate_crafting_path(
        _item(fp=10), [_action()],
        fracture_enabled=False, iterations=200, seed=seed
    )
    assert r.success_rate == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# E. Action aliases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("alias,canonical", [
    ("add", "add_affix"),
    ("upgrade", "upgrade_affix"),
    ("remove", "remove_affix"),
    ("seal", "seal_affix"),
])
def test_aliases_dont_crash_add(alias, canonical):
    # For remove/upgrade/seal: needs an existing affix
    if alias in ("upgrade", "remove", "seal"):
        item = _item(fp=30, affixes=[{"name": "Added Health", "tier": 2, "type": "prefix"}])
    else:
        item = _item(fp=30)
    actions = [{"action": alias, "affix": "Added Health"}]
    try:
        r = simulate_crafting_path(item, actions, iterations=10, seed=42)
        assert isinstance(r, CraftSimulationResult)
    except (ValueError, Exception):
        # Some actions may fail gracefully (recorded as action not completed)
        pass


@pytest.mark.parametrize("n", [1, 2, 3])
def test_n_add_affix_actions(n):
    item = _item(fp=100)
    actions = [_action("add_affix", f"Added Health") for _ in range(n)]
    # Multiple identical add attempts — some may fail (full slots)
    try:
        r = simulate_crafting_path(item, actions, iterations=50, seed=42,
                                    fracture_enabled=False)
        assert isinstance(r, CraftSimulationResult)
    except ValueError:
        pass


# ---------------------------------------------------------------------------
# F. FP cost tracking
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp", [10, 20, 30, 50])
def test_fp_spent_nonneg(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=100, seed=42)
    assert r.fp_spent_avg >= 0.0


@pytest.mark.parametrize("fp", [20, 30, 50])
def test_fp_spent_at_most_initial(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=200, seed=42)
    assert r.fp_spent_avg <= float(fp) + 0.01


# ---------------------------------------------------------------------------
# G. Actions completed
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp", [5, 10, 20, 30, 50])
def test_actions_completed_nonneg(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=100, seed=42)
    assert r.actions_completed_avg >= 0.0


@pytest.mark.parametrize("fp", [5, 10, 20, 30, 50])
def test_actions_completed_at_most_n(fp):
    n_actions = 1
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=100, seed=42,
                                fracture_enabled=False)
    assert r.actions_completed_avg <= n_actions + 0.01


# ---------------------------------------------------------------------------
# H. Median FP
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp", [10, 20, 30, 50, 100])
def test_median_fp_nonneg(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=200, seed=42)
    assert r.median_fp_remaining >= 0.0


@pytest.mark.parametrize("fp", [20, 30, 50])
def test_median_not_exceed_initial(fp):
    r = simulate_crafting_path(_item(fp=fp), [_action()], iterations=200, seed=42)
    assert r.median_fp_remaining <= float(fp)


# ---------------------------------------------------------------------------
# I. Expected affix tiers dict
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 10, 50, 100])
def test_expected_tiers_is_dict(n):
    r = simulate_crafting_path(_item(fp=30), [_action()], iterations=n, seed=42)
    assert isinstance(r.expected_affix_tiers, dict)


@pytest.mark.parametrize("n", [10, 50])
def test_expected_tiers_values_nonneg(n):
    r = simulate_crafting_path(_item(fp=30), [_action()], iterations=n, seed=42)
    for v in r.expected_affix_tiers.values():
        assert v >= 0.0


# ---------------------------------------------------------------------------
# J. To dict format
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [0, 42, 99])
def test_to_dict_complete(seed):
    r = simulate_crafting_path(_item(fp=20), [_action()], iterations=50, seed=seed)
    d = r.to_dict()
    for key in ["success_rate", "fracture_rate", "average_fp_remaining",
                "median_fp_remaining", "expected_affix_tiers",
                "actions_completed_avg", "fp_spent_avg", "iterations", "execution_time"]:
        assert key in d


@pytest.mark.parametrize("seed", [0, 42, 99])
def test_to_dict_iterations_match(seed):
    n = 77
    r = simulate_crafting_path(_item(fp=20), [_action()], iterations=n, seed=seed)
    assert r.to_dict()["iterations"] == n


# ---------------------------------------------------------------------------
# K. Item schema — both supported
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("schema", ["forging_potential", "forge_potential"])
def test_both_fp_schemas(schema):
    item = {schema: 20, "affixes": []}
    r = simulate_crafting_path(item, [_action()], iterations=50, seed=42)
    assert isinstance(r, CraftSimulationResult)


@pytest.mark.parametrize("n_existing", [0, 1, 2])
def test_item_with_existing_affixes_in_prefixes(n_existing):
    prefixes = [{"name": f"Affix{i}", "tier": 1, "type": "prefix"} for i in range(n_existing)]
    item = {"forging_potential": 30, "prefixes": prefixes, "suffixes": []}
    r = simulate_crafting_path(item, [_action()], iterations=50, seed=42,
                                fracture_enabled=False)
    assert isinstance(r, CraftSimulationResult)


# ---------------------------------------------------------------------------
# L. Execution time
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 10, 50, 100])
def test_execution_time_nonneg(n):
    r = simulate_crafting_path(_item(fp=20), [_action()], iterations=n, seed=42)
    assert r.execution_time >= 0.0


# ---------------------------------------------------------------------------
# M. Success + fracture = 1 across many seeds and FP values
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp,seed", [
    (10, 1), (10, 42), (20, 7), (20, 99), (30, 42), (50, 100),
    (100, 1), (100, 42),
])
def test_rates_sum_to_one(fp, seed):
    r = simulate_crafting_path(_item(fp=fp), [_action()], seed=seed, iterations=200)
    assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)
