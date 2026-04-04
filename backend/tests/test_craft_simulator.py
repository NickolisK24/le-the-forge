"""
Tests for craft_simulator — Upgrade 3

Covers: Monte Carlo determinism, result structure, success/fracture rates,
FP tracking, affix tier outcomes, action aliases, edge cases.
"""

from __future__ import annotations

import pytest

from app.engines.craft_simulator import simulate_crafting_path, CraftSimulationResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _item(fp=20, prefixes=None, suffixes=None, affixes=None) -> dict:
    item = {"forging_potential": fp}
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
# 1. Return type and structure
# ---------------------------------------------------------------------------

class TestReturnType:
    def test_returns_craft_simulation_result(self):
        r = _run()
        assert isinstance(r, CraftSimulationResult)

    def test_to_dict_has_success_rate(self):
        assert "success_rate" in _run().to_dict()

    def test_to_dict_has_fracture_rate(self):
        assert "fracture_rate" in _run().to_dict()

    def test_to_dict_has_average_fp_remaining(self):
        assert "average_fp_remaining" in _run().to_dict()

    def test_to_dict_has_median_fp_remaining(self):
        assert "median_fp_remaining" in _run().to_dict()

    def test_to_dict_has_expected_affix_tiers(self):
        assert "expected_affix_tiers" in _run().to_dict()

    def test_to_dict_has_actions_completed_avg(self):
        assert "actions_completed_avg" in _run().to_dict()

    def test_to_dict_has_fp_spent_avg(self):
        assert "fp_spent_avg" in _run().to_dict()

    def test_to_dict_has_iterations(self):
        r = _run(iterations=77)
        assert r.to_dict()["iterations"] == 77

    def test_to_dict_has_execution_time(self):
        assert "execution_time" in _run().to_dict()

    def test_success_rate_is_float(self):
        r = _run()
        assert isinstance(r.success_rate, float)

    def test_fracture_rate_is_float(self):
        r = _run()
        assert isinstance(r.fracture_rate, float)

    def test_expected_affix_tiers_is_dict(self):
        r = _run()
        assert isinstance(r.expected_affix_tiers, dict)

    def test_execution_time_positive(self):
        r = _run(iterations=10)
        assert r.execution_time >= 0.0


# ---------------------------------------------------------------------------
# 2. Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    @pytest.mark.parametrize("seed", [0, 1, 7, 42, 100, 999])
    def test_same_seed_same_success_rate(self, seed):
        item = _item(fp=20)
        actions = [_action()]
        r1 = simulate_crafting_path(item, actions, seed=seed, iterations=200)
        r2 = simulate_crafting_path(item, actions, seed=seed, iterations=200)
        assert r1.success_rate == r2.success_rate

    @pytest.mark.parametrize("seed", [42, 1234])
    def test_same_seed_same_fracture_rate(self, seed):
        item = _item(fp=20)
        actions = [_action()]
        r1 = simulate_crafting_path(item, actions, seed=seed, iterations=200)
        r2 = simulate_crafting_path(item, actions, seed=seed, iterations=200)
        assert r1.fracture_rate == r2.fracture_rate

    def test_same_seed_same_fp_remaining(self):
        item = _item(fp=20)
        actions = [_action()]
        r1 = simulate_crafting_path(item, actions, seed=42, iterations=200)
        r2 = simulate_crafting_path(item, actions, seed=42, iterations=200)
        # Same seed + same success rate → fp remaining should be equal or very close
        assert r1.success_rate == r2.success_rate
        assert abs(r1.average_fp_remaining - r2.average_fp_remaining) < 1.0

    def test_input_item_not_mutated(self):
        item = _item(fp=25)
        original_fp = item["forging_potential"]
        _run(item=item, iterations=50)
        assert item["forging_potential"] == original_fp

    def test_input_actions_not_mutated(self):
        actions = [_action()]
        original_action = actions[0]["action"]
        _run(actions=actions, iterations=20)
        assert actions[0]["action"] == original_action

    def test_no_global_rng_contamination(self):
        import random
        random.seed(0)
        r1 = _run(seed=42, iterations=100)
        random.seed(999)
        r2 = _run(seed=42, iterations=100)
        assert r1.success_rate == r2.success_rate


# ---------------------------------------------------------------------------
# 3. Rate invariants
# ---------------------------------------------------------------------------

class TestRateInvariants:
    def test_success_rate_in_range(self):
        r = _run(iterations=200)
        assert 0.0 <= r.success_rate <= 1.0

    def test_fracture_rate_in_range(self):
        r = _run(iterations=200)
        assert 0.0 <= r.fracture_rate <= 1.0

    def test_success_plus_fracture_equals_one(self):
        r = _run(iterations=500, seed=42)
        assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)

    def test_no_fracture_when_disabled(self):
        r = simulate_crafting_path(
            _item(fp=5),  # low FP to trigger fracture normally
            [_action()],
            fracture_enabled=False,
            iterations=200,
            seed=42,
        )
        assert r.fracture_rate == 0.0

    def test_success_rate_one_when_fracture_disabled(self):
        r = simulate_crafting_path(
            _item(fp=5),
            [_action()],
            fracture_enabled=False,
            iterations=200,
            seed=42,
        )
        assert r.success_rate == pytest.approx(1.0)

    def test_low_fp_lower_actions_completed(self):
        # With fp=3 and cost≈4 per action, actions stop immediately (no FP)
        r_low = simulate_crafting_path(_item(fp=3), [_action()], iterations=500, seed=42,
                                       fracture_enabled=False)
        r_high = simulate_crafting_path(_item(fp=50), [_action()], iterations=500, seed=42,
                                        fracture_enabled=False)
        # High FP → can complete more actions
        assert r_high.actions_completed_avg >= r_low.actions_completed_avg

    def test_high_fp_more_actions_with_fracture_disabled(self):
        r_low = simulate_crafting_path(_item(fp=2), [_action()], iterations=500, seed=42,
                                       fracture_enabled=False)
        r_high = simulate_crafting_path(_item(fp=80), [_action()], iterations=500, seed=42,
                                        fracture_enabled=False)
        # High FP → 100% success both (fracture disabled), but high FP has more FP remaining
        assert r_high.average_fp_remaining >= r_low.average_fp_remaining


# ---------------------------------------------------------------------------
# 4. FP tracking
# ---------------------------------------------------------------------------

class TestFPTracking:
    def test_fp_remaining_nonnegative(self):
        r = _run(iterations=200)
        assert r.average_fp_remaining >= 0.0

    def test_median_fp_nonnegative(self):
        r = _run(iterations=200)
        assert r.median_fp_remaining >= 0.0

    def test_fp_spent_nonnegative(self):
        r = _run(iterations=200)
        assert r.fp_spent_avg >= 0.0

    def test_fp_remaining_not_exceed_initial(self):
        item = _item(fp=30)
        r = simulate_crafting_path(item, [_action()], iterations=200)
        assert r.average_fp_remaining <= 30.0

    def test_fp_spent_plus_remaining_approx_initial(self):
        item = _item(fp=30)
        r = simulate_crafting_path(item, [_action()], iterations=500, seed=42)
        assert r.fp_spent_avg + r.average_fp_remaining == pytest.approx(30.0, abs=5.0)

    def test_more_actions_more_fp_spent(self):
        item = _item(fp=50)
        r1 = simulate_crafting_path(item, [_action()], iterations=200, seed=42,
                                    fracture_enabled=False)
        r2 = simulate_crafting_path(
            item,
            [_action(), _action()],
            iterations=200, seed=42, fracture_enabled=False,
        )
        assert r2.fp_spent_avg >= r1.fp_spent_avg

    def test_out_of_fp_stops_actions(self):
        item = _item(fp=0)
        r = simulate_crafting_path(item, [_action()], iterations=100, seed=42,
                                   fracture_enabled=False)
        # No FP → 0 actions done on average
        assert r.actions_completed_avg == pytest.approx(0.0, abs=0.1)


# ---------------------------------------------------------------------------
# 5. Action aliases
# ---------------------------------------------------------------------------

class TestActionAliases:
    @pytest.mark.parametrize("alias,canonical", [
        ("upgrade", "upgrade_affix"),
        ("add", "add_affix"),
        ("remove", "remove_affix"),
        ("seal", "seal_affix"),
    ])
    def test_alias_resolves_without_error(self, alias, canonical):
        item = _item(fp=30, affixes=[{"name": "Added Health", "tier": 2, "type": "prefix"}])
        actions = [{"action": alias, "affix": "Added Health"}]
        r = simulate_crafting_path(item, actions, iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)

    def test_canonical_action_works(self):
        item = _item(fp=30)
        actions = [{"action": "add_affix", "affix": "Added Health"}]
        r = simulate_crafting_path(item, actions, iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)


# ---------------------------------------------------------------------------
# 6. Iteration count
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 10, 50, 100, 500, 1000])
def test_iteration_count_respected(n):
    r = _run(iterations=n)
    assert r.iterations == n


def test_single_iteration_valid():
    r = _run(iterations=1)
    assert r.iterations == 1
    assert 0.0 <= r.success_rate <= 1.0


# ---------------------------------------------------------------------------
# 7. Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    def test_zero_iterations_raises(self):
        with pytest.raises(ValueError):
            simulate_crafting_path(_item(), [_action()], iterations=0)

    def test_empty_actions_raises(self):
        with pytest.raises(ValueError):
            simulate_crafting_path(_item(), [], iterations=10)

    def test_negative_iterations_raises(self):
        with pytest.raises(ValueError):
            simulate_crafting_path(_item(), [_action()], iterations=-1)


# ---------------------------------------------------------------------------
# 8. Affix tier tracking
# ---------------------------------------------------------------------------

class TestAffixTierTracking:
    def test_expected_tiers_is_dict(self):
        r = _run(iterations=50)
        assert isinstance(r.expected_affix_tiers, dict)

    def test_to_dict_rounds_tiers(self):
        r = _run(iterations=50)
        d = r.to_dict()
        for v in d["expected_affix_tiers"].values():
            # Values should be rounded floats
            assert isinstance(v, float)

    def test_affix_tiers_nonnegative(self):
        r = _run(iterations=100)
        for v in r.expected_affix_tiers.values():
            assert v >= 0.0


# ---------------------------------------------------------------------------
# 9. Actions completed
# ---------------------------------------------------------------------------

class TestActionsCompleted:
    def test_actions_completed_nonnegative(self):
        r = _run(iterations=100)
        assert r.actions_completed_avg >= 0.0

    def test_actions_completed_at_most_n_actions(self):
        n = 3
        actions = [_action() for _ in range(n)]
        r = simulate_crafting_path(_item(fp=50), actions, iterations=200, seed=42,
                                   fracture_enabled=False)
        assert r.actions_completed_avg <= n

    def test_actions_completed_at_least_0(self):
        r = _run(iterations=50)
        assert r.actions_completed_avg >= 0.0


# ---------------------------------------------------------------------------
# 10. Multiple sequential actions
# ---------------------------------------------------------------------------

class TestMultipleActions:
    def test_two_actions_run_without_error(self):
        item = _item(fp=50)
        actions = [
            {"action": "add_affix", "affix": "Added Health"},
            {"action": "upgrade_affix", "affix": "Added Health", "target_tier": 3},
        ]
        r = simulate_crafting_path(item, actions, iterations=100, seed=42)
        assert isinstance(r, CraftSimulationResult)

    def test_three_actions_run_without_error(self):
        item = _item(fp=100)
        actions = [
            {"action": "add_affix", "affix": "Added Health"},
            {"action": "add_affix", "affix": "Increased Spell Damage"},
            {"action": "upgrade_affix", "affix": "Added Health"},
        ]
        r = simulate_crafting_path(item, actions, iterations=100, seed=42)
        assert isinstance(r, CraftSimulationResult)


# ---------------------------------------------------------------------------
# 11. Both item schemas supported
# ---------------------------------------------------------------------------

class TestItemSchemas:
    def test_forging_potential_schema(self):
        item = {"forging_potential": 20, "prefixes": [], "suffixes": []}
        r = simulate_crafting_path(item, [_action()], iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)

    def test_forge_potential_schema(self):
        item = {"forge_potential": 20, "affixes": []}
        r = simulate_crafting_path(item, [_action()], iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)

    def test_item_with_existing_affixes(self):
        item = _item(fp=30, affixes=[{"name": "Added Health", "tier": 2, "type": "prefix"}])
        r = simulate_crafting_path(item, [_action("upgrade_affix", "Added Health")],
                                   iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)

    def test_item_with_sealed_affix(self):
        item = {
            "forging_potential": 30,
            "prefixes": [],
            "suffixes": [],
            "sealed_affix": {"name": "Added Health", "tier": 3, "type": "prefix"},
        }
        r = simulate_crafting_path(item, [_action()], iterations=50, seed=42)
        assert isinstance(r, CraftSimulationResult)


# ---------------------------------------------------------------------------
# 12. Fracture probability edge cases
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("fp,fracture_enabled,expected_fracture_ge", [
    (100, True, 0.0),
    (20, True, 0.0),
    (5, True, 0.0),
    (100, False, None),  # disabled
])
def test_fracture_rates_by_fp(fp, fracture_enabled, expected_fracture_ge):
    item = _item(fp=fp)
    r = simulate_crafting_path(item, [_action()], iterations=300, seed=42,
                               fracture_enabled=fracture_enabled)
    if not fracture_enabled:
        assert r.fracture_rate == 0.0
    else:
        assert r.fracture_rate >= expected_fracture_ge


# ---------------------------------------------------------------------------
# 13. Seed variety
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("seed", [0, 1, 2, 10, 42, 100, 200, 500, 1000, 9999])
def test_multiple_seeds_produce_valid_results(seed):
    r = simulate_crafting_path(_item(fp=20), [_action()], seed=seed, iterations=100)
    assert 0.0 <= r.success_rate <= 1.0
    assert 0.0 <= r.fracture_rate <= 1.0
    assert r.success_rate + r.fracture_rate == pytest.approx(1.0, abs=1e-9)


# ---------------------------------------------------------------------------
# 14. To dict numeric types
# ---------------------------------------------------------------------------

class TestToDictTypes:
    def test_success_rate_rounded(self):
        r = _run(iterations=100)
        d = r.to_dict()
        # 4 decimal places max
        s = str(d["success_rate"])
        if "." in s:
            assert len(s.split(".")[1]) <= 4

    def test_fracture_rate_rounded(self):
        r = _run(iterations=100)
        d = r.to_dict()
        s = str(d["fracture_rate"])
        if "." in s:
            assert len(s.split(".")[1]) <= 4

    def test_all_float_fields_are_numeric(self):
        r = _run(iterations=50)
        d = r.to_dict()
        for k in ["success_rate", "fracture_rate", "average_fp_remaining",
                  "median_fp_remaining", "actions_completed_avg", "fp_spent_avg",
                  "execution_time"]:
            assert isinstance(d[k], (int, float)), f"{k} should be numeric"

    def test_iterations_is_int(self):
        r = _run(iterations=50)
        d = r.to_dict()
        assert isinstance(d["iterations"], int)


# ---------------------------------------------------------------------------
# 15. Parametric action sequences
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n_actions", [1, 2, 3])
def test_n_sequential_add_actions(n_actions):
    item = _item(fp=100)
    actions = [_action() for _ in range(n_actions)]
    r = simulate_crafting_path(item, actions, iterations=100, seed=42,
                               fracture_enabled=False)
    assert isinstance(r, CraftSimulationResult)
    assert r.success_rate == pytest.approx(1.0)


@pytest.mark.parametrize("fp_val", [0, 1, 5, 10, 20, 30, 50, 100])
def test_various_initial_fp(fp_val):
    item = _item(fp=fp_val)
    r = simulate_crafting_path(item, [_action()], iterations=100, seed=42)
    assert 0.0 <= r.success_rate <= 1.0
    assert r.average_fp_remaining >= 0.0
