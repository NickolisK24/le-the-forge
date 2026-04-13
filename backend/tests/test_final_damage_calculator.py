"""
Tests for final_damage_calculator — base → increased → more pipeline.

Covers:
  DamageContext.from_build(...)
  calculate_final_damage(ctx)
  DamageResult.damage_by_type
"""

from __future__ import annotations

import pytest

from app.domain.calculators.damage_type_router import DamageType
from app.domain.calculators.final_damage_calculator import (
    DamageContext,
    DamageResult,
    calculate_final_damage,
)
from app.domain.skill import SkillStatDef
from app.engines.stat_engine import BuildStats


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _spell_fire_skill() -> SkillStatDef:
    """Minimal spell/fire skill where sum_increased_damage reads fire_damage_pct,
    elemental_damage_pct, and spell_damage_pct."""
    return SkillStatDef(
        base_damage=100.0,
        level_scaling=0.0,
        attack_speed=1.0,
        scaling_stats=("spell_damage_pct", "fire_damage_pct"),
        data_version="test",
        is_spell=True,
        damage_types=(DamageType.FIRE,),
    )


def _stats(**overrides) -> BuildStats:
    s = BuildStats()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# DamageContext.from_build
# ---------------------------------------------------------------------------

class TestDamageContextFromBuild:
    def test_base_damage_is_passed_through(self):
        skill = _spell_fire_skill()
        stats = _stats()
        ctx = DamageContext.from_build(
            effective_base=123.5,
            stats=stats,
            skill_def=skill,
        )
        assert ctx.base_damage == pytest.approx(123.5)

    def test_increased_damage_uses_sum_increased_damage(self):
        # fire_damage_pct (30) + elemental_damage_pct (20) + spell_damage_pct (10) = 60
        skill = _spell_fire_skill()
        stats = _stats(
            fire_damage_pct=30.0,
            elemental_damage_pct=20.0,
            spell_damage_pct=10.0,
        )
        ctx = DamageContext.from_build(
            effective_base=100.0,
            stats=stats,
            skill_def=skill,
        )
        assert ctx.increased_damage == pytest.approx(60.0)

    def test_extra_more_pct_is_included_in_more_damage_list(self):
        skill = _spell_fire_skill()
        stats = _stats(more_damage_pct=25.0)
        ctx = DamageContext.from_build(
            effective_base=100.0,
            stats=stats,
            skill_def=skill,
            extra_more_pct=15.0,
        )
        assert ctx.more_damage == [25.0, 15.0]

    def test_scaled_dict_is_stored(self):
        skill = _spell_fire_skill()
        stats = _stats()
        scaled = {DamageType.FIRE: 80.0, DamageType.PHYSICAL: 20.0}
        ctx = DamageContext.from_build(
            effective_base=100.0,
            stats=stats,
            skill_def=skill,
            scaled=scaled,
        )
        assert ctx.scaled == scaled

    def test_scaled_defaults_to_empty_dict(self):
        skill = _spell_fire_skill()
        stats = _stats()
        ctx = DamageContext.from_build(
            effective_base=100.0,
            stats=stats,
            skill_def=skill,
        )
        assert ctx.scaled == {}


# ---------------------------------------------------------------------------
# calculate_final_damage — pipeline order and numerical correctness
# ---------------------------------------------------------------------------

class TestCalculateFinalDamage:
    def test_base_only_no_increased_no_more(self):
        ctx = DamageContext(base_damage=100.0, increased_damage=0.0, more_damage=[])
        assert calculate_final_damage(ctx).total == pytest.approx(100.0)

    def test_increased_only(self):
        # 100 × (1 + 50/100) = 150
        ctx = DamageContext(base_damage=100.0, increased_damage=50.0, more_damage=[])
        assert calculate_final_damage(ctx).total == pytest.approx(150.0)

    def test_one_more_at_50_pct(self):
        # 100 × 1.0 × (1.5) = 150
        ctx = DamageContext(base_damage=100.0, increased_damage=0.0, more_damage=[50.0])
        assert calculate_final_damage(ctx).total == pytest.approx(150.0)

    def test_two_mores_stack_multiplicatively(self):
        # 1.5 × 1.5 = 2.25 — NOT 2.0 (which would be additive).
        ctx = DamageContext(
            base_damage=100.0, increased_damage=0.0, more_damage=[50.0, 50.0]
        )
        assert calculate_final_damage(ctx).total == pytest.approx(225.0)

    def test_increased_100_and_one_more_100(self):
        # 100 × 2.0 × 2.0 = 400
        ctx = DamageContext(
            base_damage=100.0, increased_damage=100.0, more_damage=[100.0]
        )
        assert calculate_final_damage(ctx).total == pytest.approx(400.0)

    def test_zero_base_produces_zero(self):
        ctx = DamageContext(
            base_damage=0.0,
            increased_damage=200.0,
            more_damage=[100.0, 50.0],
        )
        assert calculate_final_damage(ctx).total == 0.0

    def test_increased_is_additive_not_chained(self):
        # Two separate incr sources (30 + 20) should combine additively to 50%:
        # 100 × 1.5 = 150 (not 100 × 1.3 × 1.2 = 156).
        ctx = DamageContext(
            base_damage=100.0, increased_damage=50.0, more_damage=[]
        )
        assert calculate_final_damage(ctx).total == pytest.approx(150.0)

    def test_pipeline_order_increased_before_more(self):
        # 100 base, +50% increased, +100% more:
        # after_increased = 100 × 1.5 = 150
        # after_more      = 150 × 2.0 = 300
        ctx = DamageContext(
            base_damage=100.0, increased_damage=50.0, more_damage=[100.0]
        )
        assert calculate_final_damage(ctx).total == pytest.approx(300.0)


# ---------------------------------------------------------------------------
# DamageResult.damage_by_type
# ---------------------------------------------------------------------------

class TestDamageByType:
    def test_scaled_dict_populates_per_type_proportionally(self):
        # Base 100 → 200 total after pipeline; split 80/20 fire/physical.
        scaled = {DamageType.FIRE: 80.0, DamageType.PHYSICAL: 20.0}
        ctx = DamageContext(
            base_damage=100.0,
            increased_damage=100.0,   # ×2.0 → 200
            more_damage=[],
            scaled=scaled,
        )
        result = calculate_final_damage(ctx)
        assert result.total == pytest.approx(200.0)
        assert result.damage_by_type[DamageType.FIRE] == pytest.approx(160.0)
        assert result.damage_by_type[DamageType.PHYSICAL] == pytest.approx(40.0)
        # Per-type split sums to total
        assert sum(result.damage_by_type.values()) == pytest.approx(result.total)

    def test_empty_scaled_produces_empty_damage_by_type(self):
        ctx = DamageContext(
            base_damage=100.0, increased_damage=0.0, more_damage=[], scaled={}
        )
        result = calculate_final_damage(ctx)
        assert result.damage_by_type == {}

    def test_zero_scaled_total_produces_empty_damage_by_type(self):
        # Guard: all-zero scaled values mean we can't proportion the damage.
        ctx = DamageContext(
            base_damage=100.0,
            increased_damage=0.0,
            more_damage=[],
            scaled={DamageType.FIRE: 0.0, DamageType.COLD: 0.0},
        )
        result = calculate_final_damage(ctx)
        assert result.damage_by_type == {}

    def test_damage_result_total_field(self):
        result = DamageResult(total=42.0)
        assert result.total == 42.0
        assert result.damage_by_type == {}
