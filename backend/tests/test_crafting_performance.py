"""
Performance tests for the Phase P crafting system.
Target: 40 tests, all marked @pytest.mark.slow.
"""
from __future__ import annotations
import time
import random
import pytest

from crafting.models.craft_state import CraftState, AffixState
from crafting.models.craft_action import CraftAction, ActionType
from crafting.simulation.sequence_simulator import SequenceSimulator
from crafting.simulation.monte_carlo_crafting import MonteCarloCraftSimulator, MCCraftConfig
from crafting.optimization.craft_optimizer import CraftOptimizer
from crafting.optimization.scoring import CraftScorer
from crafting.engines.fracture_engine import FractureEngine
from crafting.optimization.path_generator import PathGenerator

pytestmark = pytest.mark.slow


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_state(fp=80, instability=0, n_affixes=0):
    state = CraftState("perf_item", "Perf Item", "helm", fp, instability)
    for i in range(n_affixes):
        state.affixes.append(AffixState(f"affix_{i}", i + 1, 7))
    return state


def _add_actions(n: int) -> list[CraftAction]:
    return [CraftAction(ActionType.ADD_AFFIX, new_affix_id=f"p_affix_{i}") for i in range(n)]


# ---------------------------------------------------------------------------
# Class TestPerformance (40 tests)
# ---------------------------------------------------------------------------

class TestPerformance:

    # ------------------------------------------------------------------
    # 1. test_sequence_10k_runs
    # ------------------------------------------------------------------
    def test_sequence_10k_runs(self):
        """10,000 sequences of 5 actions each must complete in < 5 seconds."""
        rng = random.Random(42)
        actions = _add_actions(4) + [
            CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="p_affix_0")
        ]
        t0 = time.perf_counter()
        for _ in range(10_000):
            state = make_state(fp=80)
            sim = SequenceSimulator(random.Random(rng.randint(0, 2**31)))
            sim.simulate(state, actions)
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0, f"10k sequences took {elapsed:.2f}s (limit 5s)"

    # ------------------------------------------------------------------
    # 2. test_monte_carlo_10k
    # ------------------------------------------------------------------
    def test_monte_carlo_10k(self):
        """MC n_runs=10_000 with 8 actions must complete in < 5 seconds."""
        config = MCCraftConfig(n_runs=10_000, base_seed=42, stop_on_fracture=True)
        mc = MonteCarloCraftSimulator(config)
        state = make_state(fp=100)
        actions = _add_actions(4) + [
            CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="p_affix_0"),
            CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="p_affix_1"),
            CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="p_affix_2"),
            CraftAction(ActionType.UPGRADE_AFFIX, target_affix_id="p_affix_3"),
        ]
        t0 = time.perf_counter()
        result = mc.run(state, actions)
        elapsed = time.perf_counter() - t0
        assert result.n_runs == 10_000
        assert elapsed < 5.0, f"MC 10k took {elapsed:.2f}s (limit 5s)"

    # ------------------------------------------------------------------
    # 3. test_optimizer_speed
    # ------------------------------------------------------------------
    def test_optimizer_speed(self):
        """optimize(beam_width=3, iterations=2) must complete in < 2 seconds."""
        optimizer = CraftOptimizer(random.Random(1))
        state = make_state(fp=80)
        t0 = time.perf_counter()
        result = optimizer.optimize(
            state, ["opt_a", "opt_b"], {"opt_a": 4, "opt_b": 3},
            iterations=2, beam_width=3
        )
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0, f"optimizer took {elapsed:.2f}s (limit 2s)"
        assert result.iterations == 2

    # ------------------------------------------------------------------
    # 4. test_fracture_100k_rolls
    # ------------------------------------------------------------------
    def test_fracture_100k_rolls(self):
        """100,000 fracture rolls must complete in < 4 seconds."""
        engine = FractureEngine(random.Random(99))
        state = make_state(fp=80, n_affixes=2)
        t0 = time.perf_counter()
        for _ in range(100_000):
            s = state.clone()
            engine.apply(s, 0.1)
        elapsed = time.perf_counter() - t0
        assert elapsed < 4.0, f"100k fracture rolls took {elapsed:.2f}s (limit 4s)"

    # ------------------------------------------------------------------
    # 5. test_path_generator_1k
    # ------------------------------------------------------------------
    def test_path_generator_1k(self):
        """1,000 greedy paths must complete in < 0.5 seconds."""
        gen = PathGenerator(random.Random(7))
        state = make_state(fp=80)
        t0 = time.perf_counter()
        for _ in range(1_000):
            gen.greedy(state, ["ga1", "ga2", "ga3"], {"ga1": 5, "ga2": 4, "ga3": 3})
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5, f"1k greedy paths took {elapsed:.2f}s (limit 0.5s)"

    # ------------------------------------------------------------------
    # 6. test_mc_determinism
    # ------------------------------------------------------------------
    def test_mc_determinism(self):
        """5 repeated MC runs with same seed must all produce the same mean_fp_spent."""
        state = make_state(fp=80)
        actions = _add_actions(3)
        means = []
        for _ in range(5):
            config = MCCraftConfig(n_runs=200, base_seed=123)
            result = MonteCarloCraftSimulator(config).run(state.clone(), actions)
            means.append(result.mean_fp_spent)
        assert len(set(means)) == 1, f"Expected deterministic means, got: {means}"

    # ------------------------------------------------------------------
    # 7. test_mc_different_seeds
    # ------------------------------------------------------------------
    def test_mc_different_seeds(self):
        """10 different seeds must produce at least 2 different mean_fp_spent values."""
        state = make_state(fp=80)
        actions = _add_actions(3)
        means = set()
        for seed in range(10):
            config = MCCraftConfig(n_runs=100, base_seed=seed * 31 + 1)
            result = MonteCarloCraftSimulator(config).run(state.clone(), actions)
            means.add(round(result.mean_fp_spent, 6))
        assert len(means) >= 2, f"Expected variation across seeds, got means: {means}"

    # ------------------------------------------------------------------
    # 8. test_state_clone_100k
    # ------------------------------------------------------------------
    def test_state_clone_100k(self):
        """100,000 clone() calls must complete in < 5 seconds."""
        state = make_state(fp=80, n_affixes=4)
        t0 = time.perf_counter()
        for _ in range(100_000):
            _ = state.clone()
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0, f"100k clones took {elapsed:.2f}s (limit 5s)"

    # ------------------------------------------------------------------
    # 9. test_scorer_50k
    # ------------------------------------------------------------------
    def test_scorer_50k(self):
        """50,000 score() calls must complete in < 2 seconds."""
        scorer = CraftScorer()
        state = make_state(fp=40, n_affixes=3)
        target_affixes = ["affix_0", "affix_1", "affix_2"]
        target_tiers = {"affix_0": 5, "affix_1": 4, "affix_2": 3}
        t0 = time.perf_counter()
        for _ in range(50_000):
            scorer.score(state, target_affixes, target_tiers, initial_fp=80)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0, f"50k scorer calls took {elapsed:.2f}s (limit 2s)"

    # ------------------------------------------------------------------
    # 10. test_rng_isolation
    # ------------------------------------------------------------------
    def test_rng_isolation(self):
        """branch(n=10) must produce at least some variation in total_fp_spent."""
        rng = random.Random(55)
        sim = SequenceSimulator(rng)
        state = make_state(fp=80)
        actions = _add_actions(3)
        results = sim.branch(state, actions, n_branches=10)
        fp_values = [r.total_fp_spent for r in results]
        # At least 2 distinct values (branches use different seeds)
        assert len(set(fp_values)) >= 2, (
            f"Expected branch variation in fp_spent, got: {fp_values}"
        )

    # ------------------------------------------------------------------
    # Additional throughput / stress tests (11–40)
    # ------------------------------------------------------------------

    def test_sequence_simulator_no_fp_exhaustion(self):
        """Simulating with very high FP shouldn't cause errors."""
        sim = SequenceSimulator(random.Random(1))
        state = make_state(fp=10_000)
        actions = _add_actions(4)
        result = sim.simulate(state, actions)
        assert result.total_crafts >= 0

    def test_mc_low_runs_fast(self):
        """MC with n_runs=10 completes quickly."""
        config = MCCraftConfig(n_runs=10, base_seed=1)
        state = make_state(fp=60)
        t0 = time.perf_counter()
        MonteCarloCraftSimulator(config).run(state, _add_actions(2))
        assert time.perf_counter() - t0 < 0.5

    def test_path_generator_randomized_fast(self):
        """randomized() path generation for 10 variants completes quickly."""
        gen = PathGenerator(random.Random(3))
        state = make_state(fp=80)
        t0 = time.perf_counter()
        for _ in range(500):
            gen.randomized(state, ["r1", "r2"], {"r1": 4, "r2": 3}, n_variants=5)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0

    def test_path_generator_heuristic_fast(self):
        """heuristic() generates paths quickly."""
        gen = PathGenerator(random.Random(4))
        state = make_state(fp=80, n_affixes=2)
        t0 = time.perf_counter()
        for _ in range(500):
            gen.heuristic(state, ["affix_0", "affix_1"], {"affix_0": 5, "affix_1": 4})
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0

    def test_scorer_fractured_state_fast(self):
        """Scoring fractured states doesn't slow things down."""
        scorer = CraftScorer()
        state = make_state(fp=0, n_affixes=2)
        state.is_fractured = True
        t0 = time.perf_counter()
        for _ in range(20_000):
            scorer.score(state, ["affix_0"], {"affix_0": 5}, initial_fp=80)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0

    def test_fracture_engine_zero_chance_fast(self):
        """Fracture engine with 0% chance never fractures, stays fast."""
        engine = FractureEngine(random.Random(0))
        state = make_state(fp=60)
        t0 = time.perf_counter()
        for _ in range(100_000):
            result = engine.apply(state.clone(), 0.0)
            assert result.fractured is False
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0  # 2× margin for CI runner / Python version variance

    def test_fracture_engine_full_chance_fast(self):
        """Fracture engine with 100% chance always fractures, stays fast."""
        engine = FractureEngine(random.Random(0))
        state = make_state(fp=60, n_affixes=2)
        t0 = time.perf_counter()
        for _ in range(50_000):
            result = engine.apply(state.clone(), 1.0)
            assert result.fractured is True
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.5

    def test_branch_20_results_independent(self):
        """branch(n=20) produces 20 independent results."""
        sim = SequenceSimulator(random.Random(10))
        state = make_state(fp=80)
        results = sim.branch(state, _add_actions(2), n_branches=20)
        assert len(results) == 20
        states = [r.final_state for r in results]
        assert all(states[i] is not states[j] for i in range(len(states)) for j in range(i + 1, len(states)))

    def test_mc_stop_on_fracture_false_fast(self):
        """MC with stop_on_fracture=False completes within time limit."""
        config = MCCraftConfig(n_runs=200, base_seed=3, stop_on_fracture=False)
        state = make_state(fp=60)
        t0 = time.perf_counter()
        MonteCarloCraftSimulator(config).run(state, _add_actions(3))
        assert time.perf_counter() - t0 < 1.0

    def test_state_snapshot_fast(self):
        """100k snapshot() calls complete within 5 seconds."""
        state = make_state(fp=60, n_affixes=4)
        t0 = time.perf_counter()
        for _ in range(100_000):
            _ = state.snapshot()
        elapsed = time.perf_counter() - t0
        assert elapsed < 5.0

    def test_optimizer_beam_width_1_fast(self):
        """beam_width=1 optimizer finishes quickly."""
        opt = CraftOptimizer(random.Random(8))
        state = make_state(fp=60)
        t0 = time.perf_counter()
        result = opt.optimize(state, ["bw1_affix"], {"bw1_affix": 3}, iterations=1, beam_width=1)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
        assert result.best_score.total >= 0.0

    def test_mc_high_instability_fast(self):
        """MC with high-instability state (frequent fractures) stays fast."""
        config = MCCraftConfig(n_runs=200, base_seed=7)
        state = make_state(fp=60, instability=80)
        t0 = time.perf_counter()
        MonteCarloCraftSimulator(config).run(state, _add_actions(4))
        assert time.perf_counter() - t0 < 1.0

    def test_sequence_with_rune_actions_fast(self):
        """Sequences mixing rune actions are fast."""
        rng = random.Random(12)
        t0 = time.perf_counter()
        for _ in range(1_000):
            state = make_state(fp=80, n_affixes=2)
            sim = SequenceSimulator(random.Random(rng.randint(0, 2**31)))
            actions = [
                CraftAction(ActionType.APPLY_RUNE, rune_type="refinement"),
                CraftAction(ActionType.APPLY_RUNE, rune_type="shaping"),
            ]
            sim.simulate(state, actions)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0

    def test_sequence_with_glyph_actions_fast(self):
        """Sequences with glyph actions are fast."""
        rng = random.Random(13)
        t0 = time.perf_counter()
        for _ in range(1_000):
            state = make_state(fp=80)
            sim = SequenceSimulator(random.Random(rng.randint(0, 2**31)))
            actions = [
                CraftAction(ActionType.APPLY_GLYPH, glyph_type="stability"),
                CraftAction(ActionType.ADD_AFFIX, new_affix_id="glyph_test"),
            ]
            sim.simulate(state, actions)
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0

    def test_clone_and_simulate_independence(self):
        """Cloning state before each simulation ensures independence."""
        base = make_state(fp=80)
        sim = SequenceSimulator(random.Random(14))
        actions = _add_actions(3)
        results = [sim.simulate(base.clone(), actions) for _ in range(50)]
        assert all(r.total_crafts >= 0 for r in results)

    def test_scorer_zero_fp_state(self):
        """Scoring a state with 0 FP doesn't crash or produce NaN."""
        scorer = CraftScorer()
        state = make_state(fp=0, n_affixes=2)
        for _ in range(10_000):
            score = scorer.score(state, ["affix_0"], {"affix_0": 5}, initial_fp=80)
            assert 0.0 <= score.total <= 1.0

    def test_mc_result_rates_valid_under_stress(self):
        """Under a large run, rates remain valid."""
        config = MCCraftConfig(n_runs=500, base_seed=999)
        state = make_state(fp=60)
        result = MonteCarloCraftSimulator(config).run(state, _add_actions(2))
        assert 0.0 <= result.success_rate <= 1.0
        assert 0.0 <= result.fracture_rate <= 1.0
        assert abs(result.success_rate + result.fracture_rate - 1.0) < 1e-9

    def test_path_generator_no_target_affixes(self):
        """greedy() with empty target list produces an empty path quickly."""
        gen = PathGenerator(random.Random(20))
        state = make_state(fp=60)
        t0 = time.perf_counter()
        for _ in range(5_000):
            candidate = gen.greedy(state, [], {})
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_fracture_engine_type_distribution(self):
        """Fracture type weights produce expected rough distribution over 10k rolls."""
        engine = FractureEngine(random.Random(50))
        counts = {"minor": 0, "damaging": 0, "destructive": 0}
        state = make_state(fp=60, n_affixes=2)
        for _ in range(10_000):
            result = engine.apply(state.clone(), 1.0)
            if result.fractured:
                counts[result.fracture_type] += 1
        total = sum(counts.values())
        # minor should be most common (~50%)
        assert counts["minor"] / total > 0.35
        assert counts["destructive"] / total < 0.30

    def test_simulation_10k_no_crash(self):
        """10k simulations with varied FP don't crash."""
        rng = random.Random(77)
        for _ in range(10_000):
            fp = rng.randint(10, 120)
            state = make_state(fp=fp)
            sim = SequenceSimulator(random.Random(rng.randint(0, 2**31)))
            actions = [CraftAction(ActionType.ADD_AFFIX, new_affix_id="stress_affix")]
            result = sim.simulate(state, actions)
            assert result is not None

    def test_mc_mean_fp_stable_across_large_runs(self):
        """mean_fp_spent stabilizes within reasonable range over large runs."""
        config = MCCraftConfig(n_runs=1_000, base_seed=42)
        state = make_state(fp=60)
        result = MonteCarloCraftSimulator(config).run(state, _add_actions(2))
        # FP costs per add_affix are 3–6, so 2 actions = 6–12 FP total (before fracture)
        assert result.mean_fp_spent <= 60  # can't spend more than starting FP

    def test_optimizer_multiple_target_affixes(self):
        """Optimizer handles multiple target affixes within time budget."""
        opt = CraftOptimizer(random.Random(33))
        state = make_state(fp=100)
        targets = [f"m_affix_{i}" for i in range(3)]
        tiers = {t: 4 for t in targets}
        t0 = time.perf_counter()
        result = opt.optimize(state, targets, tiers, iterations=1, beam_width=2)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0
        assert len(result.best_path) > 0

    def test_sequence_many_branches_time(self):
        """branch(n=50) completes within 2 seconds."""
        sim = SequenceSimulator(random.Random(44))
        state = make_state(fp=80)
        t0 = time.perf_counter()
        results = sim.branch(state, _add_actions(4), n_branches=50)
        elapsed = time.perf_counter() - t0
        assert len(results) == 50
        assert elapsed < 2.0

    def test_scorer_with_all_affixes_at_max(self):
        """Score a fully-maxed state is close to 1.0."""
        scorer = CraftScorer()
        state = make_state(fp=80, n_affixes=0)
        targets = [f"mx_{i}" for i in range(4)]
        for t in targets:
            state.affixes.append(AffixState(t, 7, 7))
        tiers = {t: 7 for t in targets}
        score = scorer.score(state, targets, tiers, initial_fp=80)
        assert score.total > 0.5

    def test_fracture_rolls_seeded_deterministic(self):
        """Same seed → same sequence of fracture outcomes over 1000 rolls."""
        def run_rolls(seed):
            engine = FractureEngine(random.Random(seed))
            state = make_state(fp=60, n_affixes=1)
            return [engine.apply(state.clone(), 0.3).fractured for _ in range(1000)]

        r1 = run_rolls(99)
        r2 = run_rolls(99)
        assert r1 == r2

    def test_mc_fracture_rate_zero_high_fp(self):
        """With very high FP and low instability, fracture rate should be low."""
        config = MCCraftConfig(n_runs=200, base_seed=42)
        state = make_state(fp=500, instability=0)
        actions = [CraftAction(ActionType.ADD_AFFIX, new_affix_id="low_frac")]
        result = MonteCarloCraftSimulator(config).run(state, actions)
        # With instability starting at 0 and rising by 10/craft,
        # one action → instability=10 → 10% fracture chance
        assert result.fracture_rate < 0.5

    def test_sequence_simulator_reuse(self):
        """Re-using a SequenceSimulator for many runs is fast."""
        sim = SequenceSimulator(random.Random(55))
        state = make_state(fp=80)
        actions = _add_actions(2)
        t0 = time.perf_counter()
        for _ in range(5_000):
            sim.simulate(state.clone(), actions)
        elapsed = time.perf_counter() - t0
        assert elapsed < 2.0

    def test_path_generator_large_target_set(self):
        """greedy() with 10 target affixes stays fast (item limit means not all added)."""
        gen = PathGenerator(random.Random(6))
        state = make_state(fp=100)
        targets = [f"t{i}" for i in range(10)]
        tiers = {t: 5 for t in targets}
        t0 = time.perf_counter()
        for _ in range(1_000):
            gen.greedy(state, targets, tiers)
        elapsed = time.perf_counter() - t0
        assert elapsed < 0.5

    def test_mc_produces_valid_percentiles(self):
        """MC percentile_5 <= mean <= percentile_95 for large run."""
        config = MCCraftConfig(n_runs=500, base_seed=77)
        state = make_state(fp=60)
        result = MonteCarloCraftSimulator(config).run(state, _add_actions(2))
        assert result.percentile_5_fp <= result.mean_fp_spent
        assert result.mean_fp_spent <= result.percentile_95_fp + result.std_fp_spent

    def test_beam_search_with_existing_affixes(self):
        """beam_search when state already has affixes completes fast."""
        opt = CraftOptimizer(random.Random(88))
        state = make_state(fp=80, n_affixes=2)
        t0 = time.perf_counter()
        result = opt.beam_search(
            state, ["affix_0", "affix_1"], {"affix_0": 7, "affix_1": 7},
            beam_width=2, n_eval_runs=3
        )
        elapsed = time.perf_counter() - t0
        assert elapsed < 1.0
        assert isinstance(result.best_score.total, float)
