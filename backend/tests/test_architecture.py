"""
Architecture freeze tests — lock public interfaces and calculator boundaries.

These tests are NOT about correctness (covered by test_regression_suite.py)
but about shape stability:
  - Dataclass fields must not be added, removed, or reordered silently
  - Public function signatures must not change without a deliberate update
  - Domain objects that must be immutable are frozen=True and reject mutation
  - Calculator modules are pure: importable without Flask, no shared state

When a deliberate interface change is made, update this file in the same
commit and document why. A failure here is not always a bug — it is always
a conversation that needs to happen before the change lands.
"""

import dataclasses
import inspect
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _params(fn) -> list[str]:
    return list(inspect.signature(fn).parameters.keys())


def _fields(cls) -> list[str]:
    return [f.name for f in dataclasses.fields(cls)]


def _is_frozen(cls) -> bool:
    return cls.__dataclass_params__.frozen


# ---------------------------------------------------------------------------
# Dataclass field freeze
# ---------------------------------------------------------------------------

class TestDataclassFields:
    """
    Exact field lists for every public dataclass.

    Adding, removing, or reordering a field changes the serialised contract
    (to_dict / JSON responses) and all downstream consumers. Update here
    deliberately with a comment in the commit.
    """

    def test_dps_result_fields(self):
        from app.engines.combat_engine import DPSResult
        assert _fields(DPSResult) == [
            "hit_damage", "average_hit", "dps", "effective_attack_speed",
            "crit_contribution_pct", "flat_damage_added",
            "bleed_dps", "ignite_dps", "poison_dps",
            "ailment_dps", "total_dps", "damage_by_type",
        ]

    def test_monte_carlo_dps_fields(self):
        from app.engines.combat_engine import MonteCarloDPS
        assert _fields(MonteCarloDPS) == [
            "mean_dps", "min_dps", "max_dps", "std_dev",
            "percentile_25", "percentile_75", "n_simulations",
        ]

    def test_enemy_aware_dps_fields(self):
        from app.engines.combat_engine import EnemyAwareDPS
        assert _fields(EnemyAwareDPS) == [
            "skill_name", "enemy_id", "raw_dps", "effective_dps",
            "armor_reduction_pct", "avg_res_reduction_pct", "penetration_applied",
        ]

    def test_profiler_result_fields(self):
        from app.utils.profiling import ProfilerResult
        assert _fields(ProfilerResult) == [
            "n", "mean_ms", "min_ms", "max_ms",
            "p50_ms", "p95_ms", "p99_ms", "total_ms",
        ]

    def test_damage_conversion_fields(self):
        from app.domain.calculators.conversion_calculator import DamageConversion
        assert _fields(DamageConversion) == ["source", "target", "pct", "priority"]

    def test_condition_context_fields(self):
        from app.domain.calculators.conditional_modifier_calculator import ConditionContext
        assert _fields(ConditionContext) == [
            "target_health_pct", "is_crit", "target_stunned", "target_frozen",
        ]

    def test_conditional_modifier_fields(self):
        from app.domain.calculators.conditional_modifier_calculator import ConditionalModifier
        assert _fields(ConditionalModifier) == ["condition", "bonus_pct", "threshold"]

    def test_enemy_profile_fields(self):
        from app.domain.enemy import EnemyProfile
        assert _fields(EnemyProfile) == [
            "id", "name", "category", "data_version", "description",
            "health", "armor", "resistances",
            "crit_chance", "crit_multiplier", "tags",
        ]


# ---------------------------------------------------------------------------
# Frozen / mutable contract
# ---------------------------------------------------------------------------

class TestFrozenContract:
    """
    Domain value objects must be frozen=True (immutable after construction).
    Result/output dataclasses may be mutable.

    Frozen status is part of the public contract: callers may cache frozen
    objects, use them as dict keys, or pass them between threads without
    copying.
    """

    def test_profiler_result_is_frozen(self):
        from app.utils.profiling import ProfilerResult
        assert _is_frozen(ProfilerResult)

    def test_damage_conversion_is_frozen(self):
        from app.domain.calculators.conversion_calculator import DamageConversion
        assert _is_frozen(DamageConversion)

    def test_condition_context_is_frozen(self):
        from app.domain.calculators.conditional_modifier_calculator import ConditionContext
        assert _is_frozen(ConditionContext)

    def test_conditional_modifier_is_frozen(self):
        from app.domain.calculators.conditional_modifier_calculator import ConditionalModifier
        assert _is_frozen(ConditionalModifier)

    def test_enemy_profile_is_frozen(self):
        from app.domain.enemy import EnemyProfile
        assert _is_frozen(EnemyProfile)

    def test_dps_result_is_mutable(self):
        # DPSResult is a plain dataclass (not frozen) — callers may patch
        # fields for testing without going through the full engine.
        from app.engines.combat_engine import DPSResult
        assert not _is_frozen(DPSResult)

    def test_frozen_profiler_result_rejects_mutation(self):
        from app.utils.profiling import ProfilerResult
        r = ProfilerResult(n=1, mean_ms=1.0, min_ms=1.0, max_ms=1.0,
                           p50_ms=1.0, p95_ms=1.0, p99_ms=1.0, total_ms=1.0)
        with pytest.raises((AttributeError, TypeError)):
            r.mean_ms = 999.0  # type: ignore[misc]

    def test_frozen_damage_conversion_rejects_mutation(self):
        from app.domain.calculators.conversion_calculator import DamageConversion
        from app.domain.calculators.damage_type_router import DamageType
        c = DamageConversion(DamageType.PHYSICAL, DamageType.FIRE, 50.0)
        with pytest.raises((AttributeError, TypeError)):
            c.pct = 100.0  # type: ignore[misc]

    def test_frozen_enemy_profile_rejects_mutation(self):
        from app.domain.enemy import EnemyProfile
        e = EnemyProfile(id="x", name="X", category="c", data_version="v")
        with pytest.raises((AttributeError, TypeError)):
            e.armor = 9999  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Function signature freeze
# ---------------------------------------------------------------------------

class TestFunctionSignatures:
    """
    Parameter names for all public engine and calculator functions.

    A rename or reorder breaks callers who use keyword arguments. Adding a
    required parameter is always a breaking change. Update here deliberately.
    """

    def test_calculate_dps_params(self):
        from app.engines.combat_engine import calculate_dps
        assert _params(calculate_dps) == [
            "stats", "skill_name", "skill_level",
            "skill_modifiers", "conversions", "debug",
        ]

    def test_monte_carlo_dps_params(self):
        from app.engines.combat_engine import monte_carlo_dps
        assert _params(monte_carlo_dps) == [
            "stats", "skill_name", "skill_level", "n", "seed",
            "skill_modifiers", "conversions", "workers", "debug",
        ]

    def test_calculate_dps_vs_enemy_params(self):
        from app.engines.combat_engine import calculate_dps_vs_enemy
        assert _params(calculate_dps_vs_enemy) == [
            "stats", "skill_name", "skill_level", "enemy_id",
        ]

    def test_profile_call_params(self):
        from app.utils.profiling import profile_call
        assert _params(profile_call) == ["fn", "args", "n", "warmup", "kwargs"]

    def test_compute_stats_params(self):
        from app.utils.profiling import _compute_stats
        assert _params(_compute_stats) == ["samples_ms"]

    def test_apply_conversions_params(self):
        from app.domain.calculators.conversion_calculator import apply_conversions
        assert _params(apply_conversions) == ["scaled", "conversions"]

    def test_evaluate_modifiers_params(self):
        from app.domain.calculators.conditional_modifier_calculator import evaluate_modifiers
        assert _params(evaluate_modifiers) == ["modifiers", "ctx"]

    def test_apply_penetration_params(self):
        from app.domain.calculators.enemy_mitigation_calculator import apply_penetration
        assert _params(apply_penetration) == ["capped_resistance", "penetration"]

    def test_effective_resistance_params(self):
        from app.domain.calculators.enemy_mitigation_calculator import effective_resistance
        assert _params(effective_resistance) == ["enemy", "damage_type", "penetration"]

    def test_weighted_damage_multiplier_params(self):
        from app.domain.calculators.enemy_mitigation_calculator import weighted_damage_multiplier
        assert _params(weighted_damage_multiplier) == ["enemy", "damage_by_type", "pen_map", "area_level"]

    def test_effective_crit_chance_params(self):
        from app.domain.calculators.crit_calculator import effective_crit_chance
        assert _params(effective_crit_chance) == ["base", "increased_pct"]

    def test_calculate_average_hit_params(self):
        from app.domain.calculators.crit_calculator import calculate_average_hit
        assert _params(calculate_average_hit) == ["hit_damage", "crit_chance", "crit_multiplier"]


# ---------------------------------------------------------------------------
# Calculator module purity
# ---------------------------------------------------------------------------

class TestModulePurity:
    """
    Calculator modules must be pure: no Flask context, no DB, no I/O.

    Each module must be importable in isolation and expose no Flask, SQLAlchemy,
    or route-layer symbols in its public namespace. A violation here means a
    calculator has grown an undeclared side-effect dependency.
    """

    def _assert_pure(self, module_name: str):
        import importlib, sys
        mod = sys.modules.get(module_name) or importlib.import_module(module_name)
        forbidden = {"flask", "sqlalchemy", "db", "route", "request", "current_app"}
        leaked = [
            name for name in vars(mod)
            if any(f in name.lower() for f in forbidden)
        ]
        assert leaked == [], (
            f"{module_name} leaks framework symbols into its namespace: {leaked}"
        )

    def test_conversion_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.conversion_calculator")

    def test_enemy_mitigation_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.enemy_mitigation_calculator")

    def test_conditional_modifier_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.conditional_modifier_calculator")

    def test_crit_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.crit_calculator")

    def test_skill_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.skill_calculator")

    def test_ailment_calculator_is_pure(self):
        self._assert_pure("app.domain.calculators.ailment_calculator")

    def test_profiling_is_pure(self):
        self._assert_pure("app.utils.profiling")


# ---------------------------------------------------------------------------
# Timer interface
# ---------------------------------------------------------------------------

class TestTimerInterface:
    """Timer must behave as a context manager and expose elapsed_ms."""

    def test_timer_is_context_manager(self):
        from app.utils.profiling import Timer
        assert hasattr(Timer, "__enter__") and hasattr(Timer, "__exit__")

    def test_timer_exposes_elapsed_ms(self):
        from app.utils.profiling import Timer
        with Timer() as t:
            pass
        assert hasattr(t, "elapsed_ms")
        assert isinstance(t.elapsed_ms, float)

    def test_timer_elapsed_non_negative(self):
        from app.utils.profiling import Timer
        with Timer() as t:
            pass
        assert t.elapsed_ms >= 0.0
