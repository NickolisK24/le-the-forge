"""
Tests for Combat Timeline Integration (Step 9).

Validates:
  - CombatTimeline: tick advancement, ailment damage accumulation
  - Buff DAMAGE_MULTIPLIER applied per tick
  - Stack limits respected through apply_ailment
  - Status interactions (shock) amplify damage
  - Enemy behavior uptime scales total damage
  - CombatResult fields and average_dps
"""

import pytest
from app.domain.ailments import AilmentType
from app.domain.timeline import BuffInstance, BuffType
from app.domain.enemy_behavior import EnemyBehaviorProfile
from app.domain.combat_timeline import CombatTimeline, CombatResult


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _simple_timeline(tick_size: float = 0.1) -> CombatTimeline:
    return CombatTimeline(tick_size=tick_size)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

class TestCombatTimelineInit:
    def test_starts_with_zero_elapsed(self):
        tl = _simple_timeline()
        assert tl.elapsed == pytest.approx(0.0)

    def test_invalid_tick_size_zero_raises(self):
        with pytest.raises(ValueError, match="tick_size"):
            CombatTimeline(tick_size=0.0)

    def test_invalid_tick_size_negative_raises(self):
        with pytest.raises(ValueError, match="tick_size"):
            CombatTimeline(tick_size=-0.1)


# ---------------------------------------------------------------------------
# Ailment application and basic ticking
# ---------------------------------------------------------------------------

class TestCombatTimelineAilments:
    def test_no_ailments_zero_damage(self):
        tl = _simple_timeline()
        tl.advance(5.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(0.0)

    def test_single_ailment_damage_accumulates(self):
        # 50 dps bleed for 2s = 100 total
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.advance(2.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(100.0, rel=1e-3)

    def test_ailment_expires_stops_damage(self):
        # Apply 1s bleed (dpt=50), advance 3s — damage ~50 (1s × 50 dps).
        # Allow ±1 tick (5.0) tolerance for float accumulation in the loop.
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=1.0)
        tl.advance(3.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(50.0, abs=5.5)

    def test_multiple_ailment_types_sum(self):
        # 50 dps bleed + 100 dps ignite for 2s = 300 total
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.apply_ailment(AilmentType.IGNITE, damage_per_tick=100.0, duration=2.0)
        tl.advance(2.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(300.0, rel=1e-3)

    def test_damage_by_ailment_tracked_separately(self):
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.apply_ailment(AilmentType.IGNITE, damage_per_tick=100.0, duration=2.0)
        tl.advance(2.0)
        result = tl.get_result()
        assert "bleed" in result.damage_by_ailment
        assert "ignite" in result.damage_by_ailment
        assert result.damage_by_ailment["bleed"] < result.damage_by_ailment["ignite"]

    def test_stack_limit_respected(self):
        # Bleed limit = 8; apply 10, only 8 should be active
        tl = _simple_timeline(tick_size=0.1)
        for _ in range(10):
            tl.apply_ailment(AilmentType.BLEED, damage_per_tick=10.0, duration=5.0)
        active = tl.state.active_ailments
        bleeds = [i for i in active if i.ailment_type is AilmentType.BLEED]
        assert len(bleeds) == 8

    def test_apply_ailment_mid_advance(self):
        # Apply at t=0, advance 1s, apply again, advance 1s
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.POISON, damage_per_tick=20.0, duration=3.0)
        tl.advance(1.0)
        tl.apply_ailment(AilmentType.POISON, damage_per_tick=20.0, duration=3.0)
        tl.advance(1.0)
        result = tl.get_result()
        # First 1s: 20 dps × 1s = 20; second 1s: 40 dps × 1s = 40 → total 60
        assert result.total_damage == pytest.approx(60.0, rel=1e-2)


# ---------------------------------------------------------------------------
# Buff integration
# ---------------------------------------------------------------------------

class TestCombatTimelineBuffs:
    def test_damage_multiplier_buff_scales_damage(self):
        # 50 dps bleed, +100% damage buff (×2), 2s = 200 total
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 100.0, duration=2.0))
        tl.advance(2.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(200.0, rel=1e-2)

    def test_buff_expiry_stops_bonus(self):
        # 50 dps bleed, +100% damage buff for 1s, then plain for 1s.
        # Expected ≈150 (100 + 50). Allow ±1 tick (10.0) for float accumulation.
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 100.0, duration=1.0))
        tl.advance(2.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(150.0, abs=10.1)

    def test_no_buff_on_non_damage_multiplier_type(self):
        # ATTACK_SPEED buff should not affect ailment damage
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 100.0, duration=2.0))
        tl.advance(2.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(100.0, rel=1e-2)


# ---------------------------------------------------------------------------
# Status interactions
# ---------------------------------------------------------------------------

class TestCombatTimelineInteractions:
    def test_shock_amplifies_bleed_damage(self):
        from app.domain.status_interactions import SHOCK_DAMAGE_BONUS_PER_STACK
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=50.0, duration=2.0)
        tl.apply_ailment(AilmentType.SHOCK, damage_per_tick=0.0, duration=2.0)
        tl.advance(2.0)
        result = tl.get_result()
        # Shock adds SHOCK_DAMAGE_BONUS_PER_STACK% to bleed; shock itself deals 0
        expected_bleed = 50.0 * 2.0 * (1.0 + SHOCK_DAMAGE_BONUS_PER_STACK / 100.0)
        # shock also benefits from shock (target=None), but dmg=0 so contributes 0
        assert result.total_damage == pytest.approx(expected_bleed, rel=1e-2)


# ---------------------------------------------------------------------------
# Enemy behavior uptime
# ---------------------------------------------------------------------------

class TestCombatTimelineBehavior:
    def test_50_percent_uptime_halves_damage(self):
        # Enemy attacks 1s, moves 1s = 50% uptime
        profile = EnemyBehaviorProfile(attack_duration=1.0, move_duration=1.0)
        tl = CombatTimeline(tick_size=0.1, behavior_profile=profile)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=100.0, duration=10.0)
        tl.advance(4.0)
        result = tl.get_result()
        # Without uptime: 100 × 4 = 400; with 50% uptime ≈ 200
        assert result.total_damage == pytest.approx(200.0, rel=1e-2)

    def test_full_uptime_stationary(self):
        profile = EnemyBehaviorProfile(attack_duration=1.0, move_duration=0.0, is_stationary=True)
        tl = CombatTimeline(tick_size=0.1, behavior_profile=profile)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=100.0, duration=4.0)
        tl.advance(4.0)
        result = tl.get_result()
        assert result.total_damage == pytest.approx(400.0, rel=1e-2)


# ---------------------------------------------------------------------------
# CombatResult
# ---------------------------------------------------------------------------

class TestCombatResult:
    def test_result_is_frozen(self):
        tl = _simple_timeline()
        tl.advance(1.0)
        r = tl.get_result()
        with pytest.raises((AttributeError, TypeError)):
            r.total_damage = 999.0  # type: ignore[misc]

    def test_average_dps_zero_for_zero_duration(self):
        tl = _simple_timeline()
        r = tl.get_result()
        assert r.average_dps == pytest.approx(0.0)

    def test_average_dps_correct(self):
        tl = _simple_timeline(tick_size=0.1)
        tl.apply_ailment(AilmentType.BLEED, damage_per_tick=100.0, duration=4.0)
        tl.advance(4.0)
        r = tl.get_result()
        assert r.average_dps == pytest.approx(r.total_damage / 4.0, rel=1e-3)

    def test_fight_duration_matches_elapsed(self):
        tl = _simple_timeline(tick_size=0.1)
        tl.advance(3.5)
        r = tl.get_result()
        assert r.fight_duration == pytest.approx(tl.elapsed, rel=1e-9)

    def test_ticks_simulated_count(self):
        # Use tick_size=0.25 and duration=2.0 so 8 exact ticks (0.25 is exact in binary)
        tl = CombatTimeline(tick_size=0.25)
        tl.advance(2.0)
        r = tl.get_result()
        assert r.ticks_simulated == 8

    def test_advance_negative_raises(self):
        tl = _simple_timeline()
        with pytest.raises(ValueError, match="duration"):
            tl.advance(-1.0)
