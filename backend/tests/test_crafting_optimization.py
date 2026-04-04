"""
Tests for Monte Carlo crafting, PathGenerator, CraftScorer, CraftOptimizer,
compute_craft_metrics, CraftResult, CraftDataIntegration, and CraftLogger.
Phase P — crafting optimization.

Run from backend/:
    python -m pytest tests/test_crafting_optimization.py -v --tb=short
"""

from __future__ import annotations
import random
import pytest

from crafting.simulation.monte_carlo_crafting import (
    MonteCarloCraftSimulator, MCCraftConfig, MCCraftResult,
)
from crafting.optimization.path_generator import PathGenerator, PathCandidate
from crafting.optimization.scoring import CraftScorer, CraftScore
from crafting.optimization.craft_optimizer import CraftOptimizer, OptimizationResult
from crafting.metrics.craft_metrics import compute_craft_metrics, CraftMetrics
from crafting.models.craft_state import CraftState, AffixState
from crafting.models.craft_action import CraftAction, ActionType
from crafting.models.craft_result import CraftResult
from services.craft_data_integration import CraftDataIntegration, AffixDefinition
from crafting.models.bis_target import BisTarget, AffixRequirement
from debug.craft_logger import CraftLogger, CraftLogEntry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state(
    item_id: str = "helm_001",
    item_class: str = "helm",
    fp: int = 100,
    instability: int = 0,
    affixes: list[AffixState] | None = None,
    fractured: bool = False,
    metadata: dict | None = None,
) -> CraftState:
    return CraftState(
        item_id=item_id,
        item_name="Test Helm",
        item_class=item_class,
        forging_potential=fp,
        instability=instability,
        affixes=affixes or [],
        is_fractured=fractured,
        metadata=metadata or {},
    )


def make_affix(affix_id: str, current_tier: int = 3, max_tier: int = 7) -> AffixState:
    return AffixState(affix_id=affix_id, current_tier=current_tier, max_tier=max_tier)


def simple_add_actions(*affix_ids: str) -> list[CraftAction]:
    return [CraftAction(ActionType.ADD_AFFIX, new_affix_id=aid) for aid in affix_ids]


# ===========================================================================
# MonteCarloCraftSimulator.run
# ===========================================================================

class TestMonteCarloCraftSimulator:

    def _make_sim(self, n_runs: int = 100, seed: int = 42) -> MonteCarloCraftSimulator:
        cfg = MCCraftConfig(n_runs=n_runs, base_seed=seed, stop_on_fracture=True)
        return MonteCarloCraftSimulator(cfg)

    def test_run_returns_mc_craft_result(self):
        sim = self._make_sim(n_runs=10)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert isinstance(result, MCCraftResult)

    def test_run_n_runs_matches_config(self):
        sim = self._make_sim(n_runs=50)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert result.n_runs == 50

    def test_success_rate_in_range(self):
        sim = self._make_sim(n_runs=100)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert 0.0 <= result.success_rate <= 1.0

    def test_fracture_rate_in_range(self):
        sim = self._make_sim(n_runs=100)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert 0.0 <= result.fracture_rate <= 1.0

    def test_fracture_rate_plus_success_rate_equals_one(self):
        sim = self._make_sim(n_runs=100)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert abs(result.fracture_rate + result.success_rate - 1.0) < 1e-9

    def test_mean_fp_spent_positive_when_actions_present(self):
        sim = self._make_sim(n_runs=20)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert result.mean_fp_spent > 0

    def test_mean_fp_zero_when_no_actions(self):
        sim = self._make_sim(n_runs=20)
        state = make_state(fp=100)
        result = sim.run(state, [])
        assert result.mean_fp_spent == 0.0

    def test_deterministic_with_same_seed(self):
        state = make_state(fp=100)
        actions = simple_add_actions("life_flat", "cast_speed")
        r1 = MonteCarloCraftSimulator(MCCraftConfig(n_runs=50, base_seed=99)).run(state, actions)
        r2 = MonteCarloCraftSimulator(MCCraftConfig(n_runs=50, base_seed=99)).run(state, actions)
        assert r1.success_rate == r2.success_rate
        assert r1.mean_fp_spent == r2.mean_fp_spent

    def test_different_seed_different_results(self):
        state = make_state(fp=100, instability=50)
        actions = simple_add_actions("life_flat")
        r1 = MonteCarloCraftSimulator(MCCraftConfig(n_runs=200, base_seed=1)).run(state, actions)
        r2 = MonteCarloCraftSimulator(MCCraftConfig(n_runs=200, base_seed=2)).run(state, actions)
        # With different seeds, at least one metric should differ
        differs = (r1.success_rate != r2.success_rate or r1.mean_fp_spent != r2.mean_fp_spent)
        assert differs

    def test_percentile_5_le_mean_le_percentile_95(self):
        sim = self._make_sim(n_runs=100)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert result.percentile_5_fp <= result.mean_fp_spent
        assert result.mean_fp_spent <= result.percentile_95_fp

    def test_std_fp_spent_nonnegative(self):
        sim = self._make_sim(n_runs=50)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert result.std_fp_spent >= 0.0

    def test_mean_crafts_positive_when_actions_present(self):
        sim = self._make_sim(n_runs=20)
        state = make_state(fp=100)
        result = sim.run(state, simple_add_actions("life_flat"))
        assert result.mean_crafts > 0


# ===========================================================================
# PathGenerator.greedy
# ===========================================================================

class TestPathGeneratorGreedy:

    def _gen(self, seed: int = 0) -> PathGenerator:
        return PathGenerator(rng=random.Random(seed))

    def test_missing_affixes_get_add_affix_actions(self):
        gen = self._gen()
        state = make_state()
        target = ["life_flat", "cast_speed"]
        tiers = {"life_flat": 5, "cast_speed": 3}
        candidate = gen.greedy(state, target, tiers)
        action_types = [a.action_type for a in candidate.actions]
        assert ActionType.ADD_AFFIX in action_types

    def test_greedy_adds_both_missing_affixes(self):
        gen = self._gen()
        state = make_state()
        target = ["life_flat", "cast_speed"]
        tiers = {"life_flat": 3, "cast_speed": 3}
        candidate = gen.greedy(state, target, tiers)
        new_ids = [a.new_affix_id for a in candidate.actions if a.action_type == ActionType.ADD_AFFIX]
        assert "life_flat" in new_ids
        assert "cast_speed" in new_ids

    def test_upgrade_actions_generated_for_below_target_tier(self):
        gen = self._gen()
        affix = make_affix("life_flat", current_tier=2, max_tier=7)
        state = make_state(affixes=[affix])
        target = ["life_flat"]
        tiers = {"life_flat": 5}
        candidate = gen.greedy(state, target, tiers)
        upgrade_actions = [a for a in candidate.actions if a.action_type == ActionType.UPGRADE_AFFIX]
        # Needs 3 upgrades (2 -> 5)
        assert len(upgrade_actions) == 3

    def test_upgrade_correct_affix(self):
        gen = self._gen()
        affix = make_affix("life_flat", current_tier=1, max_tier=7)
        state = make_state(affixes=[affix])
        candidate = gen.greedy(state, ["life_flat"], {"life_flat": 4})
        for a in candidate.actions:
            if a.action_type == ActionType.UPGRADE_AFFIX:
                assert a.target_affix_id == "life_flat"

    def test_empty_targets_returns_empty_action_list(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.greedy(state, [], {})
        assert candidate.actions == []

    def test_returns_path_candidate(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.greedy(state, ["life_flat"], {"life_flat": 3})
        assert isinstance(candidate, PathCandidate)

    def test_strategy_is_greedy(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.greedy(state, ["life_flat"], {"life_flat": 3})
        assert candidate.strategy == "greedy"

    def test_estimated_fp_positive(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.greedy(state, ["life_flat"], {"life_flat": 3})
        assert candidate.estimated_fp > 0

    def test_no_upgrades_when_already_at_target_tier(self):
        gen = self._gen()
        affix = make_affix("life_flat", current_tier=5, max_tier=7)
        state = make_state(affixes=[affix])
        candidate = gen.greedy(state, ["life_flat"], {"life_flat": 5})
        upgrades = [a for a in candidate.actions if a.action_type == ActionType.UPGRADE_AFFIX]
        assert len(upgrades) == 0


# ===========================================================================
# PathGenerator.randomized
# ===========================================================================

class TestPathGeneratorRandomized:

    def _gen(self, seed: int = 0) -> PathGenerator:
        return PathGenerator(rng=random.Random(seed))

    def test_randomized_returns_n_variants(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat", "cast_speed"], {"life_flat": 3, "cast_speed": 3}, n_variants=5)
        assert len(results) == 5

    def test_randomized_first_is_greedy(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat"], {"life_flat": 3}, n_variants=3)
        assert results[0].strategy == "greedy"

    def test_randomized_subsequent_are_randomized_strategy(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat", "cast_speed"], {"life_flat": 3, "cast_speed": 3}, n_variants=5)
        strategies = [r.strategy for r in results[1:]]
        assert all(s == "randomized" for s in strategies)

    def test_randomized_all_are_path_candidates(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat"], {"life_flat": 3}, n_variants=4)
        for r in results:
            assert isinstance(r, PathCandidate)

    def test_randomized_action_lengths_match_base(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat", "cast_speed"],
                                  {"life_flat": 3, "cast_speed": 3}, n_variants=4)
        base_len = len(results[0].actions)
        for r in results[1:]:
            assert len(r.actions) == base_len

    def test_randomized_single_variant_returns_one(self):
        gen = self._gen()
        state = make_state()
        results = gen.randomized(state, ["life_flat"], {"life_flat": 3}, n_variants=1)
        assert len(results) == 1


# ===========================================================================
# PathGenerator.heuristic
# ===========================================================================

class TestPathGeneratorHeuristic:

    def _gen(self, seed: int = 0) -> PathGenerator:
        return PathGenerator(rng=random.Random(seed))

    def test_heuristic_returns_path_candidate(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.heuristic(state, ["life_flat"], {"life_flat": 3})
        assert isinstance(candidate, PathCandidate)

    def test_heuristic_strategy_is_heuristic(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.heuristic(state, ["life_flat"], {"life_flat": 3})
        assert candidate.strategy == "heuristic"

    def test_heuristic_missing_affixes_first(self):
        """Missing affixes should be added before upgrades."""
        gen = self._gen()
        affix = make_affix("cast_speed", current_tier=1, max_tier=7)
        state = make_state(affixes=[affix])  # cast_speed present, life_flat missing
        candidate = gen.heuristic(state, ["life_flat", "cast_speed"],
                                   {"life_flat": 3, "cast_speed": 4})
        # First action should be ADD_AFFIX for life_flat
        first_add = next((a for a in candidate.actions if a.action_type == ActionType.ADD_AFFIX), None)
        first_upgrade = next((a for a in candidate.actions if a.action_type == ActionType.UPGRADE_AFFIX), None)
        if first_add and first_upgrade:
            add_idx = candidate.actions.index(first_add)
            upgrade_idx = candidate.actions.index(first_upgrade)
            assert add_idx < upgrade_idx

    def test_heuristic_then_upgrades(self):
        gen = self._gen()
        affix = make_affix("life_flat", current_tier=2, max_tier=7)
        state = make_state(affixes=[affix])
        candidate = gen.heuristic(state, ["life_flat"], {"life_flat": 5})
        upgrades = [a for a in candidate.actions if a.action_type == ActionType.UPGRADE_AFFIX]
        assert len(upgrades) == 3

    def test_heuristic_empty_targets_empty_actions(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.heuristic(state, [], {})
        assert candidate.actions == []

    def test_heuristic_estimated_fp_positive_when_actions(self):
        gen = self._gen()
        state = make_state()
        candidate = gen.heuristic(state, ["life_flat"], {"life_flat": 3})
        assert candidate.estimated_fp > 0


# ===========================================================================
# CraftScorer.score
# ===========================================================================

class TestCraftScorer:

    def _scorer(self) -> CraftScorer:
        return CraftScorer()

    def test_all_target_affixes_at_target_tier_score_near_one(self):
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=5, max_tier=7)
        state = make_state(fp=100, affixes=[affix])
        score = scorer.score(state, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        assert score.total > 0.5

    def test_no_affixes_completion_is_zero(self):
        scorer = self._scorer()
        state = make_state(fp=100)
        score = scorer.score(state, ["life_flat", "cast_speed"], {"life_flat": 5, "cast_speed": 3}, initial_fp=100)
        assert score.completion_score == 0.0

    def test_no_affixes_tier_score_is_zero(self):
        scorer = self._scorer()
        state = make_state(fp=100)
        score = scorer.score(state, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        assert score.tier_score == 0.0

    def test_fractured_item_applies_penalty(self):
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=5, max_tier=7)
        state_ok = make_state(fp=100, affixes=[affix])
        state_frac = make_state(fp=100, affixes=[affix], fractured=True)
        score_ok = scorer.score(state_ok, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        score_frac = scorer.score(state_frac, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        assert score_frac.total < score_ok.total
        assert score_frac.penalty == 0.5

    def test_no_fracture_no_penalty(self):
        scorer = self._scorer()
        state = make_state(fp=100)
        score = scorer.score(state, ["life_flat"], {"life_flat": 3}, initial_fp=100)
        assert score.penalty == 0.0

    def test_fp_efficiency_equals_remaining_over_initial(self):
        scorer = self._scorer()
        state = make_state(fp=60)
        score = scorer.score(state, ["life_flat"], {"life_flat": 3}, initial_fp=100)
        assert abs(score.fp_efficiency - 0.6) < 1e-4

    def test_total_in_zero_to_one_range(self):
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=3)
        state = make_state(fp=80, affixes=[affix])
        score = scorer.score(state, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        assert 0.0 <= score.total <= 1.0

    def test_score_sequence_delegates_to_score(self):
        from crafting.simulation.sequence_simulator import SequenceResult
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=3)
        state = make_state(fp=80, affixes=[affix])

        class FakeSeqResult:
            final_state = state

        score = scorer.score_sequence(FakeSeqResult(), ["life_flat"], {"life_flat": 3}, 100)
        assert isinstance(score, CraftScore)

    def test_completion_score_partial(self):
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=3)
        state = make_state(fp=100, affixes=[affix])
        score = scorer.score(state, ["life_flat", "cast_speed"], {"life_flat": 3, "cast_speed": 3}, initial_fp=100)
        assert score.completion_score == pytest.approx(0.5)

    def test_tier_score_below_target(self):
        scorer = self._scorer()
        affix = make_affix("life_flat", current_tier=1, max_tier=7)
        state = make_state(fp=100, affixes=[affix])
        score = scorer.score(state, ["life_flat"], {"life_flat": 5}, initial_fp=100)
        # tier_score = (1/5) / 1 = 0.2
        assert score.tier_score == pytest.approx(0.2)

    def test_returns_craft_score_dataclass(self):
        scorer = self._scorer()
        state = make_state(fp=100)
        score = scorer.score(state, [], {}, initial_fp=100)
        assert isinstance(score, CraftScore)


# ===========================================================================
# CraftOptimizer.optimize
# ===========================================================================

class TestCraftOptimizer:

    def test_optimize_returns_optimization_result(self):
        opt = CraftOptimizer(rng=random.Random(42))
        state = make_state(fp=100)
        result = opt.optimize(state, ["life_flat"], {"life_flat": 3})
        assert isinstance(result, OptimizationResult)

    def test_optimize_best_score_in_range(self):
        opt = CraftOptimizer(rng=random.Random(42))
        state = make_state(fp=100)
        result = opt.optimize(state, ["life_flat"], {"life_flat": 3})
        assert 0.0 <= result.best_score.total <= 1.0

    def test_optimize_best_path_is_list(self):
        opt = CraftOptimizer(rng=random.Random(42))
        state = make_state(fp=100)
        result = opt.optimize(state, ["life_flat"], {"life_flat": 3})
        assert isinstance(result.best_path, list)

    def test_optimize_seeded_deterministic(self):
        state = make_state(fp=100)
        actions_target = ["life_flat"]
        tiers = {"life_flat": 3}
        r1 = CraftOptimizer(rng=random.Random(7)).optimize(state, actions_target, tiers)
        r2 = CraftOptimizer(rng=random.Random(7)).optimize(state, actions_target, tiers)
        assert r1.best_score.total == r2.best_score.total

    def test_optimize_candidates_evaluated_positive(self):
        opt = CraftOptimizer(rng=random.Random(42))
        state = make_state(fp=100)
        result = opt.optimize(state, ["life_flat"], {"life_flat": 3})
        assert result.candidates_evaluated > 0

    def test_optimize_iterations_recorded(self):
        opt = CraftOptimizer(rng=random.Random(42))
        state = make_state(fp=100)
        result = opt.optimize(state, ["life_flat"], {"life_flat": 3}, iterations=2)
        assert result.iterations == 2

    def test_optimize_empty_targets_returns_result(self):
        opt = CraftOptimizer(rng=random.Random(0))
        state = make_state(fp=100)
        result = opt.optimize(state, [], {})
        assert isinstance(result, OptimizationResult)


# ===========================================================================
# compute_craft_metrics
# ===========================================================================

class TestComputeCraftMetrics:

    def _mc_result(self, success_rate: float = 0.8, n_runs: int = 100,
                   mean_fp: float = 30.0) -> MCCraftResult:
        fracture_rate = 1.0 - success_rate
        return MCCraftResult(
            n_runs=n_runs,
            success_rate=success_rate,
            mean_fp_spent=mean_fp,
            std_fp_spent=5.0,
            mean_crafts=3.0,
            fracture_rate=fracture_rate,
            percentile_5_fp=20.0,
            percentile_95_fp=40.0,
        )

    def test_returns_craft_metrics(self):
        mc = self._mc_result()
        result = compute_craft_metrics(mc)
        assert isinstance(result, CraftMetrics)

    def test_success_probability_matches_input(self):
        mc = self._mc_result(success_rate=0.75)
        result = compute_craft_metrics(mc)
        assert result.success_probability == 0.75

    def test_confidence_low_le_success_probability(self):
        mc = self._mc_result()
        result = compute_craft_metrics(mc)
        assert result.confidence_low <= result.success_probability

    def test_success_probability_le_confidence_high(self):
        mc = self._mc_result()
        result = compute_craft_metrics(mc)
        assert result.success_probability <= result.confidence_high

    def test_confidence_low_ge_zero(self):
        mc = self._mc_result(success_rate=0.02)
        result = compute_craft_metrics(mc, max_fp_budget=200)
        assert result.confidence_low >= 0.0

    def test_confidence_high_le_one(self):
        mc = self._mc_result(success_rate=0.99)
        result = compute_craft_metrics(mc)
        assert result.confidence_high <= 1.0

    def test_expected_failures_equals_fracture_rate_times_100(self):
        mc = self._mc_result(success_rate=0.6)
        result = compute_craft_metrics(mc)
        assert abs(result.expected_failures - 40.0) < 1e-9

    def test_mean_fp_cost_matches_input(self):
        mc = self._mc_result(mean_fp=42.0)
        result = compute_craft_metrics(mc)
        assert result.mean_fp_cost == 42.0

    def test_fp_efficiency_computed(self):
        mc = self._mc_result(mean_fp=50.0)
        result = compute_craft_metrics(mc, max_fp_budget=200)
        assert abs(result.fp_efficiency - 0.25) < 1e-9

    def test_std_fp_cost_matches_input(self):
        mc = self._mc_result()
        result = compute_craft_metrics(mc)
        assert result.std_fp_cost == 5.0


# ===========================================================================
# CraftResult
# ===========================================================================

class TestCraftResult:

    def _score(self, total: float = 0.7) -> CraftScore:
        return CraftScore(total=total, tier_score=0.5, completion_score=0.5,
                          fp_efficiency=0.5, penalty=0.0)

    def _result(self, success_prob: float = 0.5, score_total: float = 0.7) -> CraftResult:
        return CraftResult(
            build_id="build_1",
            item_id="helm_001",
            best_sequence=[],
            score=self._score(score_total),
            success_probability=success_prob,
            mean_fp_cost=30.0,
            expected_fracture_rate=0.3,
            total_steps=3,
        )

    def test_is_viable_true_when_conditions_met(self):
        result = self._result(success_prob=0.4, score_total=0.6)
        assert result.is_viable is True

    def test_is_viable_false_low_success_probability(self):
        result = self._result(success_prob=0.2, score_total=0.7)
        assert result.is_viable is False

    def test_is_viable_false_low_score(self):
        result = self._result(success_prob=0.5, score_total=0.3)
        assert result.is_viable is False

    def test_is_viable_boundary_success_prob_exactly_03(self):
        result = self._result(success_prob=0.3, score_total=0.5)
        assert result.is_viable is True

    def test_is_viable_boundary_score_exactly_05(self):
        result = self._result(success_prob=0.3, score_total=0.5)
        assert result.is_viable is True

    def test_summary_returns_dict(self):
        result = self._result()
        assert isinstance(result.summary(), dict)

    def test_summary_has_build_id(self):
        result = self._result()
        assert "build_id" in result.summary()

    def test_summary_has_item_id(self):
        result = self._result()
        assert "item_id" in result.summary()

    def test_summary_has_score(self):
        result = self._result()
        assert "score" in result.summary()

    def test_summary_has_success_probability(self):
        result = self._result()
        assert "success_probability" in result.summary()

    def test_summary_has_mean_fp_cost(self):
        result = self._result()
        assert "mean_fp_cost" in result.summary()

    def test_summary_has_steps(self):
        result = self._result()
        assert "steps" in result.summary()

    def test_summary_has_viable(self):
        result = self._result()
        assert "viable" in result.summary()

    def test_summary_viable_matches_is_viable(self):
        result = self._result(success_prob=0.4, score_total=0.6)
        assert result.summary()["viable"] == result.is_viable


# ===========================================================================
# CraftDataIntegration
# ===========================================================================

class TestCraftDataIntegration:

    def _integration(self) -> CraftDataIntegration:
        return CraftDataIntegration()

    def _helm_affix(self, affix_id: str = "life_flat", max_tier: int = 7) -> AffixDefinition:
        return AffixDefinition(
            affix_id=affix_id, affix_name="Life Flat", category="prefix",
            max_tier=max_tier, valid_item_classes=["helm"],
        )

    def test_unknown_affix_produces_warning(self):
        integration = self._integration()
        state = make_state(affixes=[make_affix("unknown_affix")])
        report = integration.validate_state(state)
        assert any("unknown affix" in w for w in report.warnings)

    def test_registered_affix_no_warning(self):
        integration = self._integration()
        integration.register_affix(self._helm_affix("life_flat"))
        state = make_state(affixes=[make_affix("life_flat")])
        report = integration.validate_state(state)
        assert not any("life_flat" in w for w in report.warnings)

    def test_registered_affix_tier_exceeds_max_produces_error(self):
        integration = self._integration()
        integration.register_affix(self._helm_affix("life_flat", max_tier=5))
        state = make_state(affixes=[AffixState("life_flat", current_tier=7, max_tier=7)])
        report = integration.validate_state(state)
        assert not report.valid
        assert any("exceeds max" in e for e in report.errors)

    def test_invalid_item_class_produces_error(self):
        integration = self._integration()
        defn = AffixDefinition(
            affix_id="life_flat", affix_name="Life Flat", category="prefix",
            max_tier=7, valid_item_classes=["helm"],
        )
        integration.register_affix(defn)
        # Use chest instead of helm
        state = CraftState(
            item_id="chest_001", item_name="Test Chest", item_class="chest",
            forging_potential=100, instability=0,
            affixes=[make_affix("life_flat")],
        )
        report = integration.validate_state(state)
        assert not report.valid
        assert any("not valid" in e for e in report.errors)

    def test_valid_item_class_no_error(self):
        integration = self._integration()
        integration.register_affix(self._helm_affix("life_flat"))
        state = make_state(item_class="helm", affixes=[make_affix("life_flat")])
        report = integration.validate_state(state)
        assert report.valid

    def test_validate_bis_target_exceeds_max_tier_error(self):
        integration = self._integration()
        integration.register_affix(self._helm_affix("life_flat", max_tier=5))
        target = BisTarget(
            item_class="helm",
            requirements=[AffixRequirement(affix_id="life_flat", target_tier=8)],
        )
        report = integration.validate_bis_target(target)
        assert not report.valid
        assert any("exceeds max" in e for e in report.errors)

    def test_validate_bis_target_valid(self):
        integration = self._integration()
        integration.register_affix(self._helm_affix("life_flat", max_tier=7))
        target = BisTarget(
            item_class="helm",
            requirements=[AffixRequirement(affix_id="life_flat", target_tier=5)],
        )
        report = integration.validate_bis_target(target)
        assert report.valid

    def test_validate_bis_target_unknown_affix_warning(self):
        integration = self._integration()
        target = BisTarget(
            item_class="helm",
            requirements=[AffixRequirement(affix_id="unknown_affix", target_tier=3)],
        )
        report = integration.validate_bis_target(target)
        assert any("unknown" in w for w in report.warnings)

    def test_get_available_affixes_filters_by_item_class(self):
        integration = self._integration()
        helm_affix = AffixDefinition("life_flat", "Life Flat", "prefix", 7, ["helm"])
        chest_affix = AffixDefinition("armor_flat", "Armor Flat", "prefix", 7, ["chest"])
        integration.register_bulk([helm_affix, chest_affix])
        helm_affixes = integration.get_available_affixes("helm")
        assert "life_flat" in helm_affixes
        assert "armor_flat" not in helm_affixes

    def test_get_available_affixes_universal_affix(self):
        """Affix with empty valid_item_classes is available for all."""
        integration = self._integration()
        universal = AffixDefinition("any_flat", "Any Flat", "prefix", 7, [])
        integration.register_affix(universal)
        assert "any_flat" in integration.get_available_affixes("helm")
        assert "any_flat" in integration.get_available_affixes("chest")

    def test_enrich_state_sets_max_tier_from_registry(self):
        integration = self._integration()
        integration.register_affix(AffixDefinition("life_flat", "Life Flat", "prefix", 5, []))
        affix = AffixState("life_flat", current_tier=1, max_tier=7)
        state = make_state(affixes=[affix])
        integration.enrich_state(state)
        assert state.affixes[0].max_tier == 5

    def test_enrich_state_unregistered_affix_unchanged(self):
        integration = self._integration()
        affix = AffixState("unknown", current_tier=1, max_tier=7)
        state = make_state(affixes=[affix])
        integration.enrich_state(state)
        assert state.affixes[0].max_tier == 7

    def test_register_bulk_registers_all(self):
        integration = self._integration()
        defns = [
            AffixDefinition(f"affix_{i}", f"Affix {i}", "prefix", 7, [])
            for i in range(5)
        ]
        integration.register_bulk(defns)
        for defn in defns:
            assert defn.affix_id in integration.get_available_affixes("helm")


# ===========================================================================
# CraftLogger
# ===========================================================================

class TestCraftLogger:

    def _logger(self, capacity: int = 2000) -> CraftLogger:
        return CraftLogger(capacity=capacity)

    def test_log_craft_creates_entry(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "craft"

    def test_log_fracture_creates_entry(self):
        logger = self._logger()
        logger.log_fracture("helm_001", "minor", 80, 50)
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "fracture"

    def test_log_success_creates_entry(self):
        logger = self._logger()
        logger.log_success("helm_001", 0.85, 30, 5)
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "success"

    def test_log_failure_creates_entry(self):
        logger = self._logger()
        logger.log_failure("helm_001", "fractured", 20)
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "failure"

    def test_log_glyph_creates_entry(self):
        logger = self._logger()
        logger.log_glyph("helm_001", "stability", 100, 97)
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "glyph"

    def test_log_rune_creates_entry(self):
        logger = self._logger()
        logger.log_rune("helm_001", "removal", "life_flat")
        entries = logger.get_entries()
        assert len(entries) == 1
        assert entries[0].event_type == "rune"

    def test_get_entries_returns_all(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_fracture("helm_001", "minor", 80, 50)
        logger.log_success("helm_001", 0.8, 20, 4)
        assert len(logger.get_entries()) == 3

    def test_get_entries_filtered_by_event_type(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_fracture("helm_001", "minor", 80, 50)
        logger.log_fracture("helm_002", "damaging", 60, 70)
        fractures = logger.get_entries(event_type="fracture")
        assert len(fractures) == 2
        assert all(e.event_type == "fracture" for e in fractures)

    def test_get_entries_filtered_by_item_id(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_craft("chest_001", "upgrade_affix", 100, 97, 20)
        helm_entries = logger.get_entries(item_id="helm_001")
        assert len(helm_entries) == 1
        assert helm_entries[0].item_id == "helm_001"

    def test_get_entries_filtered_by_both_event_type_and_item_id(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_fracture("helm_001", "minor", 80, 50)
        logger.log_fracture("chest_001", "minor", 80, 50)
        result = logger.get_entries(event_type="fracture", item_id="helm_001")
        assert len(result) == 1
        assert result[0].item_id == "helm_001"
        assert result[0].event_type == "fracture"

    def test_summary_by_type_counts(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_craft("helm_001", "upgrade_affix", 95, 91, 20)
        logger.log_fracture("helm_001", "minor", 80, 50)
        s = logger.summary()
        assert s["by_type"]["craft"] == 2
        assert s["by_type"]["fracture"] == 1

    def test_summary_fracture_rate(self):
        logger = self._logger()
        for _ in range(10):
            logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        for _ in range(2):
            logger.log_fracture("helm_001", "minor", 80, 50)
        s = logger.summary()
        assert abs(s["fracture_rate"] - 0.2) < 1e-9

    def test_summary_total_entries(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_success("helm_001", 0.9, 5, 1)
        s = logger.summary()
        assert s["total_entries"] == 2

    def test_clear_empties_entries(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.log_fracture("helm_001", "minor", 80, 50)
        logger.clear()
        assert len(logger.get_entries()) == 0

    def test_len_after_clear_is_zero(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        logger.clear()
        assert len(logger) == 0

    def test_capacity_enforced_deque_maxlen(self):
        logger = self._logger(capacity=5)
        for i in range(10):
            logger.log_craft(f"item_{i}", "add_affix", 100, 95, 10)
        assert len(logger) == 5

    def test_capacity_keeps_most_recent(self):
        logger = self._logger(capacity=3)
        for i in range(6):
            logger.log_craft(f"item_{i}", "add_affix", 100, 95, 10)
        entries = logger.get_entries()
        ids = [e.item_id for e in entries]
        assert "item_5" in ids
        assert "item_0" not in ids

    def test_log_entry_is_craft_log_entry(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        entries = logger.get_entries()
        assert isinstance(entries[0], CraftLogEntry)

    def test_log_craft_metadata_stored(self):
        logger = self._logger()
        logger.log_craft("helm_001", "add_affix", 100, 95, 10, metadata={"extra": "data"})
        entries = logger.get_entries()
        assert entries[0].metadata.get("extra") == "data"

    def test_log_fracture_metadata_has_fracture_type(self):
        logger = self._logger()
        logger.log_fracture("helm_001", "damaging", 80, 50)
        entry = logger.get_entries()[0]
        assert entry.metadata.get("fracture_type") == "damaging"

    def test_log_success_metadata_has_score(self):
        logger = self._logger()
        logger.log_success("helm_001", 0.77, 25, 4)
        entry = logger.get_entries()[0]
        assert entry.metadata.get("score") == 0.77

    def test_log_rune_metadata_has_affix_affected(self):
        logger = self._logger()
        logger.log_rune("helm_001", "removal", "life_flat")
        entry = logger.get_entries()[0]
        assert entry.metadata.get("affix_affected") == "life_flat"

    def test_summary_success_count(self):
        logger = self._logger()
        logger.log_success("helm_001", 0.8, 30, 5)
        logger.log_success("helm_001", 0.9, 25, 4)
        s = logger.summary()
        assert s["success_count"] == 2

    def test_get_entries_empty_returns_empty_list(self):
        logger = self._logger()
        assert logger.get_entries() == []

    def test_fracture_rate_zero_when_no_fractures(self):
        logger = self._logger()
        for _ in range(5):
            logger.log_craft("helm_001", "add_affix", 100, 95, 10)
        s = logger.summary()
        assert s["fracture_rate"] == 0.0
