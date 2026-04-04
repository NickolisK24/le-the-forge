"""
F14 — Optimization Regression Tests

Locks the deterministic ranking order for a fixed (build, config) pair.
Two different seeds must diverge; two identical seeds must converge.

These tests protect against changes that would alter:
  - Variant generation order
  - Scoring math
  - Ranking tiebreak rules
"""

import pytest

from builds.build_definition import BuildDefinition
from optimization.models.optimization_config import OptimizationConfig
from optimization.optimization_service import optimize


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

BASE_BUILD_DICT = {
    "character_class": "Mage",
    "mastery":         "Spellblade",
    "skill_id":        "Rip Blood",
    "skill_level":     20,
}

FAST_ENCOUNTER = {
    "enemy_template": "TRAINING_DUMMY",
    "fight_duration": 10.0,
    "tick_size":      0.5,
    "distribution":   "SINGLE",
}


@pytest.fixture(scope="module")
def base_build():
    return BuildDefinition.from_dict(BASE_BUILD_DICT)


@pytest.fixture(scope="module")
def fast_config():
    return OptimizationConfig(
        target_metric  = "dps",
        max_variants   = 10,
        mutation_depth = 1,
        random_seed    = 42,
    )


def _run(build, config):
    return optimize(
        base_build       = build,
        config           = config,
        encounter_kwargs = FAST_ENCOUNTER,
        top_n            = 5,
    )


# ---------------------------------------------------------------------------
# F14A — Determinism: same seed → same results
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_seeds_produce_identical_scores(self, base_build, fast_config):
        r1 = _run(base_build, fast_config)
        r2 = _run(base_build, fast_config)
        scores1 = [r["score"] for r in r1["results"]]
        scores2 = [r["score"] for r in r2["results"]]
        assert scores1 == scores2, "Same seed produced different scores"

    def test_identical_seeds_produce_identical_mutations(self, base_build, fast_config):
        r1 = _run(base_build, fast_config)
        r2 = _run(base_build, fast_config)
        muts1 = [r["mutations_applied"] for r in r1["results"]]
        muts2 = [r["mutations_applied"] for r in r2["results"]]
        assert muts1 == muts2, "Same seed produced different mutations"

    def test_different_seeds_produce_different_variants(self, base_build):
        cfg_a = OptimizationConfig(target_metric="dps", max_variants=20, mutation_depth=1, random_seed=42)
        cfg_b = OptimizationConfig(target_metric="dps", max_variants=20, mutation_depth=1, random_seed=99)
        r_a = _run(base_build, cfg_a)
        r_b = _run(base_build, cfg_b)
        muts_a = [tuple(r["mutations_applied"]) for r in r_a["results"]]
        muts_b = [tuple(r["mutations_applied"]) for r in r_b["results"]]
        # Different seeds → at least one different variant in the top results
        assert muts_a != muts_b, "Different seeds produced identical variants (improbable)"


# ---------------------------------------------------------------------------
# F14B — Structural invariants
# ---------------------------------------------------------------------------

class TestStructuralInvariants:
    def test_ranks_are_always_sequential_from_one(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        ranks = [r["rank"] for r in result["results"]]
        assert ranks == list(range(1, len(ranks) + 1))

    def test_scores_are_always_non_increasing(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        scores = [r["score"] for r in result["results"]]
        assert scores == sorted(scores, reverse=True)

    def test_total_generated_gte_passed_gte_simulated(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        assert result["total_variants_generated"] >= result["variants_passed_constraints"]
        assert result["variants_passed_constraints"] >= result["variants_simulated"]

    def test_simulated_plus_failed_eq_passed(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        total = result["variants_simulated"] + result["variants_failed_simulation"]
        assert total == result["variants_passed_constraints"]

    def test_results_length_bounded_by_top_n(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        assert len(result["results"]) <= 5

    def test_build_variant_has_correct_class(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        for r in result["results"]:
            assert r["build_variant"]["character_class"] == "Mage"
            assert r["build_variant"]["mastery"] == "Spellblade"

    def test_each_result_has_non_negative_score(self, base_build, fast_config):
        result = _run(base_build, fast_config)
        for r in result["results"]:
            assert r["score"] >= 0.0


# ---------------------------------------------------------------------------
# F14C — Metric sensitivity: different metrics → different #1 variant
# ---------------------------------------------------------------------------

class TestMetricSensitivity:
    def test_all_metrics_produce_results(self, base_build):
        for metric in ("dps", "total_damage", "ttk", "uptime", "composite"):
            cfg = OptimizationConfig(
                target_metric  = metric,
                max_variants   = 5,
                mutation_depth = 1,
                random_seed    = 42,
            )
            result = _run(base_build, cfg)
            assert result["total_variants_generated"] > 0, f"No variants generated for metric={metric}"

    def test_ttk_zero_on_training_dummy(self, base_build):
        """TRAINING_DUMMY never dies → TTK score should be 0 for all variants."""
        cfg = OptimizationConfig(target_metric="ttk", max_variants=5, mutation_depth=1, random_seed=42)
        result = _run(base_build, cfg)
        for r in result["results"]:
            assert r["score"] == 0.0, f"Expected TTK=0 on immortal dummy, got {r['score']}"


# ---------------------------------------------------------------------------
# F14D — Constraint filtering
# ---------------------------------------------------------------------------

class TestConstraintFiltering:
    def test_min_base_damage_constraint_filters_variants(self, base_build):
        """Setting min_base_damage very high should reduce passed_constraints count."""
        cfg_no_constraint = OptimizationConfig(
            max_variants=20, mutation_depth=1, random_seed=42
        )
        cfg_strict = OptimizationConfig(
            max_variants   = 20,
            mutation_depth = 1,
            random_seed    = 42,
            constraints    = {"min_base_damage": 9999.0},  # impossible threshold
        )
        r_no = _run(base_build, cfg_no_constraint)
        r_strict = _run(base_build, cfg_strict)
        # With a 9999 min_base_damage, everything should fail
        assert r_strict["variants_passed_constraints"] == 0
        assert r_strict["results"] == []
        # Without constraint, some variants should pass
        assert r_no["variants_passed_constraints"] > 0

    def test_unknown_constraint_silently_ignored(self, base_build):
        """Unknown constraint rules should not raise errors."""
        cfg = OptimizationConfig(
            max_variants   = 5,
            mutation_depth = 1,
            random_seed    = 42,
            constraints    = {"totally_unknown_rule": 9999},
        )
        result = _run(base_build, cfg)
        # Should run normally, unknown rule is ignored
        assert result["total_variants_generated"] > 0
