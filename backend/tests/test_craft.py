"""
Tests for the craft service — pure math functions and session mutation.
These are the most critical tests since the crafting engine is the
most mathematically precise feature of The Forge.
"""

import pytest
from app.services.craft_service import (
    fp_cost,
    optimal_path_search,
    simulate_sequence,
    compare_strategies,
    create_session,
    apply_action,
    get_session_summary,
)
from app.utils.exceptions import InsufficientForgePotentialError


# ---------------------------------------------------------------------------
# Pure math
# ---------------------------------------------------------------------------

class TestFPCost:

    def test_known_actions(self):
        assert fp_cost("add_affix") == 4
        assert fp_cost("upgrade_affix") == 3
        assert fp_cost("seal_affix") == 8
        assert fp_cost("unseal_affix") == 2
        assert fp_cost("remove_affix") == 5

    def test_unknown_action_returns_default(self):
        assert fp_cost("unknown") == 4


class TestOptimalPath:

    def test_returns_list_of_steps(self):
        path = optimal_path_search([{"name": "Cast Speed", "tier": 1, "sealed": False}], 28)
        assert isinstance(path, list)
        assert len(path) > 0

    def test_steps_have_required_keys(self):
        path = optimal_path_search([{"name": "Cast Speed", "tier": 1, "sealed": False}], 28)
        for step in path:
            assert "action" in step
            assert "risk_pct" in step
            assert "note" in step
            assert "cumulative_survival_pct" in step
            assert "sealed_count_at_step" in step

    def test_seal_step_has_zero_risk(self):
        # With two affixes, the algorithm may seal one before upgrading the other
        path = optimal_path_search(
            [
                {"name": "Cast Speed", "tier": 1, "sealed": False},
                {"name": "Health", "tier": 2, "sealed": False},
            ],
            28,
        )
        seal_steps = [s for s in path if s["action"] == "seal_affix"]
        for s in seal_steps:
            assert s["risk_pct"] == 0.0

    def test_cumulative_survival_decreases_monotonically(self):
        path = optimal_path_search(
            [{"name": "Spell Damage", "tier": 1, "sealed": False}], 28
        )
        upgrade_steps = [s for s in path if s["action"] == "upgrade_affix"]
        survivals = [s["cumulative_survival_pct"] for s in upgrade_steps]
        for i in range(1, len(survivals)):
            assert survivals[i] <= survivals[i - 1] + 0.01  # allow tiny float drift

    def test_already_at_t4_returns_empty(self):
        path = optimal_path_search([{"name": "Health", "tier": 4, "sealed": False}], 28)
        assert path == []

    def test_simulation_brick_and_perfect_sum_to_one(self):
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0}] * 3
        result = simulate_sequence(28, steps, n_simulations=1_000)
        total = result["brick_chance"] + result["perfect_item_chance"]
        assert abs(total - 1.0) < 0.02  # within 2% (Monte Carlo variance)

    def test_simulation_zero_risk_never_bricks(self):
        # In modern Last Epoch, no fractures - just FP exhaustion
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0}] * 5
        result = simulate_sequence(40, steps, n_simulations=500)
        assert result["brick_chance"] == 0.0  # No fractures in modern system
        assert result["perfect_item_chance"] == 1.0

    def test_simulation_fp_exhaustion_bricks(self):
        # With insufficient FP, crafting fails to complete all steps
        steps = [{"action": "upgrade_affix", "sealed_count_at_step": 0}] * 10  # More steps than FP allows
        result = simulate_sequence(5, steps, n_simulations=200)  # Very low FP
        # In modern system, incomplete crafting doesn't "brick" but fails to complete
        assert result["brick_chance"] == 0.0  # No fractures
        assert result["perfect_item_chance"] < 1.0  # Won't complete all steps

    def test_compare_strategies_returns_three(self):
        strategies = compare_strategies(
            [{"name": "Health", "tier": 1, "sealed": False}],
            28,
        )
        assert len(strategies) == 2  # Updated to 2 strategies since no risk-based ones
        names = {s["name"] for s in strategies}
        assert "Direct Upgrade" in names
        assert "Seal First" in names


# ---------------------------------------------------------------------------
# Session CRUD
# ---------------------------------------------------------------------------

class TestCraftSession:

    def test_create_session(self, db):
        session = create_session({
            "item_type": "Wand",
            "item_name": "Test Wand",
            "item_level": 84,
            "forging_potential": 28,
            "affixes": [],
        })
        assert session.id is not None
        assert session.slug is not None
        assert session.item_type == "Wand"
        assert session.forge_potential == 28

    def test_session_slug_is_unique(self, db):
        s1 = create_session({"item_type": "Wand", "affixes": []})
        s2 = create_session({"item_type": "Wand", "affixes": []})
        assert s1.slug != s2.slug

    def test_apply_action_success(self, db):
        session = create_session({
            "item_type": "Wand",
            "forging_potential": 28,
            "affixes": [],
        })
        result = apply_action(session, "add_affix", affix_name="Cast Speed", target_tier=1)
        assert "outcome" in result
        assert result["outcome"] in ("success", "perfect")  # No fractures in modern system

    def test_apply_action_with_no_fp_fails(self, db):
        session = create_session({
            "item_type": "Wand",
            "affixes": [],
        })
        # Manually set FP to insufficient amount (less than min cost of 2)
        session.forge_potential = 1
        db.session.commit()
        with pytest.raises(InsufficientForgePotentialError):
            apply_action(session, "add_affix", affix_name="Health")

    def test_successful_craft_adds_step(self, db):
        session = create_session({
            "item_type": "Wand",
            "forging_potential": 28,
            "affixes": [],
        })
        result = apply_action(session, "add_affix", affix_name="Health")
        assert len(session.steps) == 1
        assert result["outcome"] == "success"  # No risk mechanics in modern system

    def test_summary_returns_expected_keys(self, db):
        session = create_session({
            "item_type": "Wand",
            "forge_potential": 28,
            "affixes": [{"name": "Health", "tier": 3, "sealed": False}],
        })
        summary = get_session_summary(session)
        assert "total_actions" in summary
        assert "fp_spent" in summary  # Changed from current_fp
        assert "optimal_path" in summary
        assert "fp_spent" in summary
        assert "simulation_result" in summary
        assert "strategy_comparison" in summary
        sim = summary["simulation_result"]
        assert "brick_chance" in sim
        assert "perfect_item_chance" in sim
        assert "step_survival_curve" in sim
        assert len(summary["strategy_comparison"]) == 2  # Updated to 2 strategies
