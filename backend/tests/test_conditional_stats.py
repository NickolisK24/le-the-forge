"""
Tests for the conditional stat resolution layer (Layer 8).

Verifies:
  - RuntimeContext correctly bridges to SimulationState
  - Conditional modifiers activate/deactivate based on context
  - Moving state enables movement bonuses
  - Frozen enemy enables damage bonuses
  - Ward presence enables defensive bonuses
  - Low health enables survival bonuses
  - Boss context enables boss damage bonuses
  - Pipeline Layer 8 integrates correctly
  - Debug snapshots capture condition evaluation
"""

import pytest

from app.engines.stat_engine import BuildStats
from app.stats.runtime_context import RuntimeContext, DEFAULT_CONTEXT
from app.stats.conditional_stats import (
    apply_conditional_stats,
    moving_bonus,
    ward_bonus,
    frozen_enemy_bonus,
    boss_bonus,
    low_health_bonus,
    ConditionalStatSnapshot,
)
from conditions.models.condition import Condition
from modifiers.models.conditional_modifier import ConditionalModifier


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stats(**overrides: float) -> BuildStats:
    s = BuildStats()
    for k, v in overrides.items():
        setattr(s, k, v)
    return s


# ---------------------------------------------------------------------------
# RuntimeContext
# ---------------------------------------------------------------------------

class TestRuntimeContext:
    def test_default_context_all_false(self):
        ctx = DEFAULT_CONTEXT
        assert not ctx.is_moving
        assert not ctx.has_ward
        assert not ctx.enemy_frozen
        assert not ctx.against_boss

    def test_to_simulation_state_moving(self):
        ctx = RuntimeContext(is_moving=True)
        state = ctx.to_simulation_state()
        assert "is_moving" in state.active_buffs

    def test_to_simulation_state_ward(self):
        ctx = RuntimeContext(has_ward=True)
        state = ctx.to_simulation_state()
        assert "has_ward" in state.active_buffs

    def test_to_simulation_state_frozen(self):
        ctx = RuntimeContext(enemy_frozen=True)
        state = ctx.to_simulation_state()
        assert "frozen" in state.active_status_effects

    def test_to_simulation_state_stunned(self):
        ctx = RuntimeContext(enemy_stunned=True)
        state = ctx.to_simulation_state()
        assert "stunned" in state.active_status_effects

    def test_to_simulation_state_boss(self):
        ctx = RuntimeContext(against_boss=True)
        state = ctx.to_simulation_state()
        assert "against_boss" in state.active_buffs

    def test_to_simulation_state_health_pct(self):
        ctx = RuntimeContext(player_health_pct=0.3)
        state = ctx.to_simulation_state(max_health=1000.0)
        assert abs(state.player_health - 300.0) < 0.01
        assert abs(state.player_health_pct - 0.3) < 0.01

    def test_to_simulation_state_enemy_health_pct(self):
        ctx = RuntimeContext(enemy_health_pct=0.5)
        state = ctx.to_simulation_state(max_health=2000.0)
        assert abs(state.target_health - 1000.0) < 0.01

    def test_assumed_buffs_included(self):
        ctx = RuntimeContext(assumed_buffs=("haste", "rage"))
        state = ctx.to_simulation_state()
        assert "haste" in state.active_buffs
        assert "rage" in state.active_buffs

    def test_serialization_roundtrip(self):
        ctx = RuntimeContext(is_moving=True, enemy_frozen=True, against_boss=True)
        d = ctx.to_dict()
        ctx2 = RuntimeContext.from_dict(d)
        assert ctx2.is_moving
        assert ctx2.enemy_frozen
        assert ctx2.against_boss

    def test_channeling(self):
        ctx = RuntimeContext(is_channeling=True)
        state = ctx.to_simulation_state()
        assert "is_channeling" in state.active_buffs


# ---------------------------------------------------------------------------
# Convenience modifier builders
# ---------------------------------------------------------------------------

class TestModifierBuilders:
    def test_moving_bonus_creates_valid_modifier(self):
        mod = moving_bonus("movement_speed", 20.0)
        assert mod.stat_target == "movement_speed"
        assert mod.value == 20.0
        assert mod.condition.condition_id == "is_moving"
        assert mod.condition.condition_type == "buff_active"

    def test_ward_bonus_creates_valid_modifier(self):
        mod = ward_bonus("ward_regen", 10.0)
        assert mod.condition.condition_id == "has_ward"

    def test_frozen_enemy_bonus_creates_valid_modifier(self):
        mod = frozen_enemy_bonus("cold_damage_pct", 30.0)
        assert mod.condition.condition_id == "frozen"
        assert mod.condition.condition_type == "status_present"

    def test_boss_bonus_creates_valid_modifier(self):
        mod = boss_bonus("base_damage", 50.0)
        assert mod.condition.condition_id == "against_boss"

    def test_low_health_bonus_creates_valid_modifier(self):
        mod = low_health_bonus("leech", 5.0, threshold=0.35)
        assert mod.condition.condition_type == "player_health_pct"
        assert mod.condition.threshold_value == 0.35
        assert mod.condition.comparison_operator == "le"


# ---------------------------------------------------------------------------
# apply_conditional_stats — unit tests
# ---------------------------------------------------------------------------

class TestApplyConditionalStats:
    def test_moving_bonus_applied_when_moving(self):
        stats = _stats(movement_speed=0.0)
        mod = moving_bonus("movement_speed", 20.0)
        ctx = RuntimeContext(is_moving=True)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.movement_speed == 20.0

    def test_moving_bonus_not_applied_when_stationary(self):
        stats = _stats(movement_speed=0.0)
        mod = moving_bonus("movement_speed", 20.0)
        ctx = RuntimeContext(is_moving=False)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.movement_speed == 0.0

    def test_frozen_enemy_bonus_applied(self):
        stats = _stats(cold_damage_pct=10.0)
        mod = frozen_enemy_bonus("cold_damage_pct", 30.0)
        ctx = RuntimeContext(enemy_frozen=True)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.cold_damage_pct == 40.0

    def test_frozen_enemy_bonus_inactive(self):
        stats = _stats(cold_damage_pct=10.0)
        mod = frozen_enemy_bonus("cold_damage_pct", 30.0)
        ctx = RuntimeContext(enemy_frozen=False)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.cold_damage_pct == 10.0

    def test_ward_bonus_applied(self):
        stats = _stats(ward_regen=0.0)
        mod = ward_bonus("ward_regen", 15.0)
        ctx = RuntimeContext(has_ward=True)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.ward_regen == 15.0

    def test_ward_bonus_inactive_without_ward(self):
        stats = _stats(ward_regen=0.0)
        mod = ward_bonus("ward_regen", 15.0)
        ctx = RuntimeContext(has_ward=False)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.ward_regen == 0.0

    def test_boss_bonus_applied(self):
        stats = _stats(base_damage=100.0)
        mod = boss_bonus("base_damage", 50.0)
        ctx = RuntimeContext(against_boss=True)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.base_damage == 150.0

    def test_low_health_bonus_applied_below_threshold(self):
        stats = _stats(max_health=1000.0, leech=0.0)
        mod = low_health_bonus("leech", 5.0, threshold=0.35)
        ctx = RuntimeContext(player_health_pct=0.2)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.leech == 5.0

    def test_low_health_bonus_inactive_above_threshold(self):
        stats = _stats(max_health=1000.0, leech=0.0)
        mod = low_health_bonus("leech", 5.0, threshold=0.35)
        ctx = RuntimeContext(player_health_pct=0.8)
        apply_conditional_stats(stats, [mod], ctx)
        assert stats.leech == 0.0

    def test_multiple_modifiers_stack(self):
        stats = _stats(cold_damage_pct=0.0, movement_speed=0.0)
        mods = [
            frozen_enemy_bonus("cold_damage_pct", 20.0),
            moving_bonus("movement_speed", 15.0),
        ]
        ctx = RuntimeContext(enemy_frozen=True, is_moving=True)
        apply_conditional_stats(stats, mods, ctx)
        assert stats.cold_damage_pct == 20.0
        assert stats.movement_speed == 15.0

    def test_no_modifiers_is_noop(self):
        stats = _stats(base_damage=100.0)
        apply_conditional_stats(stats, [], RuntimeContext())
        assert stats.base_damage == 100.0

    def test_default_context_used_when_none(self):
        stats = _stats(movement_speed=0.0)
        mod = moving_bonus("movement_speed", 20.0)
        apply_conditional_stats(stats, [mod], context=None)
        # Default context has is_moving=False, so bonus should not apply
        assert stats.movement_speed == 0.0


# ---------------------------------------------------------------------------
# Debug snapshots
# ---------------------------------------------------------------------------

class TestConditionalSnapshots:
    def test_capture_returns_snapshot(self):
        stats = _stats(movement_speed=0.0)
        mod = moving_bonus("movement_speed", 20.0)
        ctx = RuntimeContext(is_moving=True)
        snap = apply_conditional_stats(stats, [mod], ctx, capture=True)
        assert snap is not None
        assert isinstance(snap, ConditionalStatSnapshot)
        assert snap.active_ids == [mod.modifier_id]
        assert "movement_speed" in snap.stat_deltas

    def test_capture_records_inactive(self):
        stats = _stats()
        mod = moving_bonus("movement_speed", 20.0)
        ctx = RuntimeContext(is_moving=False)
        snap = apply_conditional_stats(stats, [mod], ctx, capture=True)
        assert snap.active_ids == []
        assert snap.stat_deltas == {}

    def test_capture_false_returns_none(self):
        stats = _stats()
        result = apply_conditional_stats(stats, [], RuntimeContext(), capture=False)
        assert result is None

    def test_snapshot_context_serialized(self):
        ctx = RuntimeContext(is_moving=True, enemy_frozen=True)
        snap = apply_conditional_stats(
            _stats(),
            [moving_bonus("movement_speed", 10.0)],
            ctx,
            capture=True,
        )
        assert snap.context["is_moving"] is True
        assert snap.context["enemy_frozen"] is True


# ---------------------------------------------------------------------------
# Pipeline integration (Layer 8)
# ---------------------------------------------------------------------------

class TestPipelineLayer8Integration:
    def test_layer8_no_modifiers_backward_compatible(self):
        """Without conditional_modifiers, pipeline works as before."""
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats({
            "character_class": "Sentinel",
            "mastery": "",
            "passive_tree": [],
            "gear_affixes": [],
        })
        assert "8_conditional_stats" in result.resolution_order
        assert result.stats is not None

    def test_layer8_applies_modifier_in_pipeline(self):
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        mod = moving_bonus("movement_speed", 25.0)
        ctx = RuntimeContext(is_moving=True)

        result_with = resolve_final_stats(
            {"character_class": "Sentinel", "mastery": "", "passive_tree": [], "gear_affixes": []},
            conditional_modifiers=[mod],
            runtime_context=ctx,
        )
        result_without = resolve_final_stats(
            {"character_class": "Sentinel", "mastery": "", "passive_tree": [], "gear_affixes": []},
        )
        assert result_with.stats.movement_speed > result_without.stats.movement_speed

    def test_layer8_snapshot_captured(self):
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        mod = frozen_enemy_bonus("cold_damage_pct", 30.0)
        ctx = RuntimeContext(enemy_frozen=True)

        result = resolve_final_stats(
            {"character_class": "Mage", "mastery": "", "passive_tree": [], "gear_affixes": []},
            conditional_modifiers=[mod],
            runtime_context=ctx,
            capture_snapshots=True,
        )
        assert "8_conditional_stats" in result.layer_snapshots
        layer8 = result.layer_snapshots["8_conditional_stats"]
        assert "_conditional" in layer8
        assert len(layer8["_conditional"]["active_ids"]) == 1

    def test_resolution_order_includes_layer8(self):
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        result = resolve_final_stats({
            "character_class": "Sentinel", "mastery": "",
            "passive_tree": [], "gear_affixes": [],
        })
        assert "8_conditional_stats" in result.resolution_order

    def test_layer8_inactive_modifier_doesnt_change_stats(self):
        from app.engines.stat_resolution_pipeline import resolve_final_stats

        mod = moving_bonus("movement_speed", 50.0)
        ctx = RuntimeContext(is_moving=False)  # not moving

        result = resolve_final_stats(
            {"character_class": "Sentinel", "mastery": "", "passive_tree": [], "gear_affixes": []},
            conditional_modifiers=[mod],
            runtime_context=ctx,
        )
        baseline = resolve_final_stats(
            {"character_class": "Sentinel", "mastery": "", "passive_tree": [], "gear_affixes": []},
        )
        assert result.stats.movement_speed == baseline.stats.movement_speed
