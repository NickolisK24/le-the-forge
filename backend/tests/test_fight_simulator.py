"""
Tests for Realistic Fight Simulation (Step 10).

Validates:
  - FightConfig validation (durations, intervals)
  - AilmentApplication fields
  - simulate_fight: cast count, damage accumulation, buff integration,
    behavior uptime, stacks_per_cast, repeated ailment application
  - FightResult fields are frozen
"""

import pytest
from app.domain.ailments import AilmentType
from app.domain.timeline import BuffInstance, BuffType
from app.domain.enemy_behavior import EnemyBehaviorProfile
from app.domain.fight_simulator import (
    AilmentApplication,
    FightConfig,
    FightResult,
    simulate_fight,
)


# ---------------------------------------------------------------------------
# AilmentApplication
# ---------------------------------------------------------------------------

class TestAilmentApplication:
    def test_fields_stored(self):
        a = AilmentApplication(AilmentType.BLEED, 50.0, 4.0, stacks_per_cast=2)
        assert a.ailment_type is AilmentType.BLEED
        assert a.damage_per_tick == pytest.approx(50.0)
        assert a.duration == pytest.approx(4.0)
        assert a.stacks_per_cast == 2

    def test_stacks_per_cast_defaults_one(self):
        a = AilmentApplication(AilmentType.IGNITE, 100.0, 3.0)
        assert a.stacks_per_cast == 1

    def test_is_frozen(self):
        a = AilmentApplication(AilmentType.BLEED, 50.0, 4.0)
        with pytest.raises((AttributeError, TypeError)):
            a.damage_per_tick = 999.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# FightConfig validation
# ---------------------------------------------------------------------------

class TestFightConfigValidation:
    def _base_config(self, **kwargs) -> FightConfig:
        defaults = dict(fight_duration=10.0, cast_interval=1.0)
        defaults.update(kwargs)
        return FightConfig(**defaults)

    def test_valid_config(self):
        cfg = self._base_config()
        assert cfg.fight_duration == pytest.approx(10.0)

    def test_negative_fight_duration_raises(self):
        with pytest.raises(ValueError, match="fight_duration"):
            self._base_config(fight_duration=-1.0)

    def test_zero_cast_interval_raises(self):
        with pytest.raises(ValueError, match="cast_interval"):
            self._base_config(cast_interval=0.0)

    def test_negative_cast_interval_raises(self):
        with pytest.raises(ValueError, match="cast_interval"):
            self._base_config(cast_interval=-0.5)

    def test_zero_tick_size_raises(self):
        with pytest.raises(ValueError, match="tick_size"):
            self._base_config(tick_size=0.0)

    def test_defaults(self):
        cfg = self._base_config()
        assert cfg.ailments == ()
        assert cfg.initial_buffs == ()
        assert cfg.behavior_profile is None
        assert cfg.tick_size == pytest.approx(0.1)

    def test_is_frozen(self):
        cfg = self._base_config()
        with pytest.raises((AttributeError, TypeError)):
            cfg.fight_duration = 999.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# simulate_fight — basic
# ---------------------------------------------------------------------------

class TestSimulateFightBasic:
    def test_no_ailments_zero_damage(self):
        cfg = FightConfig(fight_duration=5.0, cast_interval=1.0)
        result = simulate_fight(cfg)
        assert result.combat_result.total_damage == pytest.approx(0.0)

    def test_cast_count_matches_casts(self):
        # 10s fight, 1s interval → 10 casts (at t=0,1,...,9)
        cfg = FightConfig(fight_duration=10.0, cast_interval=1.0)
        result = simulate_fight(cfg)
        assert result.total_casts == 10

    def test_cast_count_with_longer_interval(self):
        # 10s fight, 2.5s interval → 4 casts (t=0, 2.5, 5.0, 7.5)
        cfg = FightConfig(fight_duration=10.0, cast_interval=2.5)
        result = simulate_fight(cfg)
        assert result.total_casts == 4

    def test_zero_duration_fight(self):
        cfg = FightConfig(fight_duration=0.0, cast_interval=1.0)
        result = simulate_fight(cfg)
        assert result.combat_result.total_damage == pytest.approx(0.0)

    def test_fight_result_is_frozen(self):
        cfg = FightConfig(fight_duration=5.0, cast_interval=1.0)
        result = simulate_fight(cfg)
        with pytest.raises((AttributeError, TypeError)):
            result.total_casts = 999  # type: ignore[misc]

    def test_config_stored_in_result(self):
        cfg = FightConfig(fight_duration=5.0, cast_interval=1.0)
        result = simulate_fight(cfg)
        assert result.config is cfg


# ---------------------------------------------------------------------------
# simulate_fight — damage accumulation
# ---------------------------------------------------------------------------

class TestSimulateFightDamage:
    def test_single_cast_bleed_damage(self):
        # 1 cast, 50 dps bleed, 2s duration, 10s fight
        # damage ≈ 50 × 2 = 100 (bleed expires after 2s)
        cfg = FightConfig(
            fight_duration=10.0,
            cast_interval=10.0,  # only 1 cast
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 2.0),),
            tick_size=0.25,
        )
        result = simulate_fight(cfg)
        assert result.combat_result.total_damage == pytest.approx(100.0, abs=15.0)

    def test_repeated_casts_accumulate_stacks(self):
        # 5 casts of bleed (2s duration each) in 5s fight
        # Each cast adds 1 stack of 50 dps; with overlap, damage > single cast
        cfg = FightConfig(
            fight_duration=5.0,
            cast_interval=1.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 2.0),),
            tick_size=0.25,
        )
        single_cfg = FightConfig(
            fight_duration=5.0,
            cast_interval=5.0,  # single cast only
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 2.0),),
            tick_size=0.25,
        )
        multi_result = simulate_fight(cfg)
        single_result = simulate_fight(single_cfg)
        assert multi_result.combat_result.total_damage > single_result.combat_result.total_damage

    def test_stacks_per_cast_multiplies_damage(self):
        # 2 stacks per cast vs 1 stack per cast — 2× damage
        cfg_single = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 4.0, stacks_per_cast=1),),
            tick_size=0.25,
        )
        cfg_double = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 4.0, stacks_per_cast=2),),
            tick_size=0.25,
        )
        r_single = simulate_fight(cfg_single)
        r_double = simulate_fight(cfg_double)
        assert r_double.combat_result.total_damage == pytest.approx(
            r_single.combat_result.total_damage * 2, rel=1e-3
        )

    def test_ignite_stack_limit_respected(self):
        # Ignite limit = 1; 5 casts should not exceed 1 active ignite
        cfg = FightConfig(
            fight_duration=5.0,
            cast_interval=0.5,
            ailments=(AilmentApplication(AilmentType.IGNITE, 100.0, 10.0),),
            tick_size=0.25,
        )
        result = simulate_fight(cfg)
        # With 1 active ignite of 100 dps, max DPS = 100; shouldn't exceed 525 total
        # (500 + 5% headroom for interaction bonuses from shock-ignite synergy)
        assert result.combat_result.total_damage <= 525.0


# ---------------------------------------------------------------------------
# simulate_fight — buffs
# ---------------------------------------------------------------------------

class TestSimulateFightBuffs:
    def test_initial_buff_scales_damage(self):
        # +100% damage buff for full fight doubles output
        cfg = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 4.0),),
            initial_buffs=(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 100.0, duration=4.0),),
            tick_size=0.25,
        )
        cfg_no_buff = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 4.0),),
            tick_size=0.25,
        )
        r_buff   = simulate_fight(cfg)
        r_no_buff = simulate_fight(cfg_no_buff)
        assert r_buff.combat_result.total_damage == pytest.approx(
            r_no_buff.combat_result.total_damage * 2.0, rel=1e-3
        )


# ---------------------------------------------------------------------------
# simulate_fight — behavior profile
# ---------------------------------------------------------------------------

class TestSimulateFightBehavior:
    def test_50_percent_uptime_halves_damage(self):
        profile = EnemyBehaviorProfile(attack_duration=1.0, move_duration=1.0)
        cfg_uptime = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 100.0, 4.0),),
            behavior_profile=profile,
            tick_size=0.25,
        )
        cfg_full = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 100.0, 4.0),),
            tick_size=0.25,
        )
        r_uptime = simulate_fight(cfg_uptime)
        r_full   = simulate_fight(cfg_full)
        assert r_uptime.combat_result.total_damage == pytest.approx(
            r_full.combat_result.total_damage * 0.5, rel=1e-2
        )


# ---------------------------------------------------------------------------
# CombatResult integration checks
# ---------------------------------------------------------------------------

class TestFightResultCombatResult:
    def test_average_dps_positive_when_damage_dealt(self):
        cfg = FightConfig(
            fight_duration=5.0,
            cast_interval=1.0,
            ailments=(AilmentApplication(AilmentType.BLEED, 50.0, 2.0),),
            tick_size=0.25,
        )
        result = simulate_fight(cfg)
        assert result.combat_result.average_dps > 0.0

    def test_damage_by_ailment_includes_used_types(self):
        cfg = FightConfig(
            fight_duration=4.0,
            cast_interval=4.0,
            ailments=(
                AilmentApplication(AilmentType.BLEED, 50.0, 4.0),
                AilmentApplication(AilmentType.POISON, 30.0, 4.0),
            ),
            tick_size=0.25,
        )
        result = simulate_fight(cfg)
        assert "bleed" in result.combat_result.damage_by_ailment
        assert "poison" in result.combat_result.damage_by_ailment

    def test_fight_duration_matches_config(self):
        cfg = FightConfig(fight_duration=7.5, cast_interval=2.5, tick_size=0.25)
        result = simulate_fight(cfg)
        assert result.combat_result.fight_duration == pytest.approx(7.5, abs=0.5)
