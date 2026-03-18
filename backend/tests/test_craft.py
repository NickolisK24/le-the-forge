"""
Tests for the craft service — pure math functions and session mutation.
These are the most critical tests since the crafting engine is the
most mathematically precise feature of The Forge.
"""

import pytest
from app.services.craft_service import (
    fracture_risk,
    fracture_risk_pct,
    instability_gain,
    fp_cost,
    optimal_path_search,
    simulate_sequence,
    compare_strategies,
    create_session,
    apply_action,
    get_session_summary,
)


# ---------------------------------------------------------------------------
# Pure math
# ---------------------------------------------------------------------------

class TestFractureRisk:

    def test_zero_instability_is_zero_risk(self):
        assert fracture_risk(0) == 0.0

    def test_max_instability_is_full_risk(self):
        assert fracture_risk(80) == 1.0

    def test_risk_is_quadratic(self):
        # At half instability (40), risk should be 25% (0.5^2)
        assert abs(fracture_risk(40) - 0.25) < 0.01

    def test_seals_reduce_effective_instability(self):
        # 1 seal reduces effective instability by 12
        risk_unsealed = fracture_risk(40)
        risk_sealed = fracture_risk(40, sealed_count=1)
        assert risk_sealed < risk_unsealed

    def test_three_seals_capped_at_zero(self):
        # 3 seals * 12 = 36 reduction, so inst=30 → effective=0
        assert fracture_risk(30, sealed_count=3) == 0.0

    def test_risk_never_exceeds_one(self):
        assert fracture_risk(80, sealed_count=0) <= 1.0
        assert fracture_risk(100, sealed_count=0) <= 1.0  # over-max input

    def test_risk_pct_rounds_to_one_decimal(self):
        pct = fracture_risk_pct(34)
        assert isinstance(pct, float)
        assert pct == round(pct, 1)

    def test_risk_pct_range(self):
        for inst in range(0, 81, 5):
            pct = fracture_risk_pct(inst)
            assert 0.0 <= pct <= 100.0


class TestFPCost:

    def test_known_actions(self):
        assert fp_cost("add_affix") == 4
        assert fp_cost("upgrade_affix") == 5
        assert fp_cost("seal_affix") == 8
        assert fp_cost("unseal_affix") == 2
        assert fp_cost("remove_affix") == 3

    def test_unknown_action_returns_default(self):
        assert fp_cost("unknown") == 4


class TestOptimalPath:

    def test_returns_list_of_steps(self):
        path = optimal_path_search(20, [{"name": "Cast Speed", "tier": 1, "sealed": False}], 28)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_steps_have_required_keys(self):
        path = optimal_path_search(20, [{"name": "Cast Speed", "tier": 1, "sealed": False}], 28)
        for step in path:
            assert "action" in step
            assert "risk_pct" in step
            assert "note" in step
            assert "cumulative_survival_pct" in step
            assert "sealed_count_at_step" in step

    def test_seal_step_has_zero_risk(self):
        # With two affixes, the algorithm may seal one before upgrading the other
        path = optimal_path_search(
            50,  # high instability → should trigger sealing
            [
                {"name": "Cast Speed", "tier": 1, "sealed": False},
                {"name": "Health", "tier": 2, "sealed": False},
            ],
            28,
        )
        seal_steps = [s for s in path if s["action"] == "seal_affix"]
        for s in seal_steps:
            assert s["risk_pct"] == 0.0

    def test_high_instability_final_step_has_higher_risk(self):
        path_low = optimal_path_search(10, [{"name": "X", "tier": 1, "sealed": False}], 28)
        path_high = optimal_path_search(60, [{"name": "X", "tier": 1, "sealed": False}], 28)
        # Both should return steps; high instability path should have higher step risks
        if path_low and path_high:
            max_low = max(s["risk_pct"] for s in path_low)
            max_high = max(s["risk_pct"] for s in path_high)
            assert max_high > max_low

    def test_cumulative_survival_decreases_monotonically(self):
        path = optimal_path_search(
            30, [{"name": "Spell Damage", "tier": 1, "sealed": False}], 28
        )
        upgrade_steps = [s for s in path if s["action"] == "upgrade_affix"]
        survivals = [s["cumulative_survival_pct"] for s in upgrade_steps]
        for i in range(1, len(survivals)):
            assert survivals[i] <= survivals[i - 1] + 0.01  # allow tiny float drift

    def test_already_at_t4_returns_empty(self):
        path = optimal_path_search(20, [{"name": "Health", "tier": 4, "sealed": False}], 28)
        assert path == []

    def test_simulation_brick_and_perfect_sum_to_one(self):
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0}] * 3
        result = simulate_sequence(20, 28, steps, n_simulations=1_000)
        total = result["brick_chance"] + result["perfect_item_chance"]
        assert abs(total - 1.0) < 0.02  # within 2% (Monte Carlo variance)

    def test_simulation_zero_risk_never_bricks(self):
        # With 7 seals, effective instability = max(0, inst - 84) = 0 for any inst ≤ 84.
        # 5 upgrade steps * max gain 10 = max 50 instability → always stays below 84.
        # Fracture risk is therefore 0 throughout, so brick_chance must be 0.
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 7}] * 5
        result = simulate_sequence(0, 40, steps, n_simulations=500)
        assert result["brick_chance"] == 0.0
        assert result["perfect_item_chance"] == 1.0

    def test_simulation_high_risk_bricks_frequently(self):
        # At 80 instability with no seals, fracture risk is 100%
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0}]
        result = simulate_sequence(80, 28, steps, n_simulations=200)
        assert result["brick_chance"] == 1.0

    def test_compare_strategies_returns_three(self):
        strategies = compare_strategies(
            30,
            [{"name": "Health", "tier": 1, "sealed": False}],
            28,
        )
        assert len(strategies) == 3
        names = {s["name"] for s in strategies}
        assert "Aggressive" in names
        assert "Balanced" in names
        assert "Conservative" in names

    def test_conservative_lower_brick_than_aggressive_at_high_instability(self):
        # At high instability, conservative (seal first) should brick less than aggressive
        strategies = compare_strategies(
            55,
            [
                {"name": "Health", "tier": 1, "sealed": False},
                {"name": "Spell Damage", "tier": 1, "sealed": False},
            ],
            40,  # enough FP for seals
        )
        aggressive = next(s for s in strategies if s["name"] == "Aggressive")
        conservative = next(s for s in strategies if s["name"] == "Conservative")
        assert conservative["brick_chance"] <= aggressive["brick_chance"]


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

class TestCraftSession:

    def test_create_session(self, db):
        session = create_session({
            "item_type": "Wand",
            "item_name": "Test Wand",
            "item_level": 84,
            "instability": 0,
            "forge_potential": 28,
            "affixes": [],
        })
        assert session.id is not None
        assert session.slug is not None
        assert session.item_type == "Wand"
        assert session.instability == 0

    def test_session_slug_is_unique(self, db):
        s1 = create_session({"item_type": "Wand", "affixes": []})
        s2 = create_session({"item_type": "Wand", "affixes": []})
        assert s1.slug != s2.slug

    def test_apply_action_success(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 0,
            "forge_potential": 28,
            "affixes": [],
        })
        result = apply_action(session, "add_affix", affix_name="Cast Speed", target_tier=1)
        assert "outcome" in result
        assert result["outcome"] in ("success", "perfect", "fracture")

    def test_apply_action_with_no_fp_fails(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 0,
            "forge_potential": 0,
            "affixes": [],
        })
        result = apply_action(session, "add_affix", affix_name="Health")
        assert result["success"] is False
        assert "Forge Potential" in result["error"]

    def test_fractured_session_rejects_actions(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 0,
            "forge_potential": 28,
            "affixes": [],
        })
        session.is_fractured = True
        db.session.commit()
        result = apply_action(session, "add_affix", affix_name="Health")
        assert result["success"] is False
        assert "fractured" in result["error"].lower()

    def test_successful_craft_adds_step(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 0,
            "forge_potential": 28,
            "affixes": [],
        })
        initial_steps = len(list(session.steps))
        apply_action(session, "add_affix", affix_name="Cast Speed", target_tier=1)
        assert len(list(session.steps)) == initial_steps + 1

    def test_instability_increases_after_craft(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 0,
            "forge_potential": 28,
            "affixes": [],
        })
        initial_inst = session.instability
        result = apply_action(session, "add_affix", affix_name="Health")
        if result["outcome"] != "fracture":
            assert session.instability >= initial_inst

    def test_summary_returns_expected_keys(self, db):
        session = create_session({
            "item_type": "Wand",
            "instability": 20,
            "forge_potential": 28,
            "affixes": [{"name": "Health", "tier": 3, "sealed": False}],
        })
        summary = get_session_summary(session)
        assert "total_actions" in summary
        assert "current_risk_pct" in summary
        assert "optimal_path" in summary
        assert "fp_spent" in summary
        assert "simulation_result" in summary
        assert "strategy_comparison" in summary
        sim = summary["simulation_result"]
        assert "brick_chance" in sim
        assert "perfect_item_chance" in sim
        assert "step_survival_curve" in sim
        assert len(summary["strategy_comparison"]) == 3
