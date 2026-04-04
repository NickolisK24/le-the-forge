"""
Long-Fight Stress Validation (Step 81).

Runs extended combat simulations to verify numerical stability and
correctness over long durations: 60s, 300s, 600s, and 1800s.

Invariants checked at every duration:
  - mana_floor >= 0.0               (no negative mana)
  - cooldown_floor >= 0.0           (no negative cooldowns)
  - total_damage >= 0.0             (no negative damage accumulation)
  - hit_damage + ailment_damage == total_damage  (accounting identity)
  - average_dps > 0                 (simulation is actually dealing damage)
"""

import pytest
from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.ailments import AilmentType
from app.domain.stability import SimStats


# ---------------------------------------------------------------------------
# Shared simulation configs
# ---------------------------------------------------------------------------

def _sustain_config(fight_duration: float) -> SimConfig:
    return SimConfig(
        tick_size=0.1,
        fight_duration=fight_duration,
        max_mana=200.0,
        mana_regen_rate=20.0,
        ailment_damage_pct=50.0,
        skills=(
            SkillSpec("fireball",  mana_cost=30.0, cooldown=2.0, base_damage=150.0, priority=1),
            SkillSpec("frostbolt", mana_cost=10.0, cooldown=0.5, base_damage=50.0,  priority=2),
        ),
    )


def _ailment_config(fight_duration: float) -> SimConfig:
    return SimConfig(
        tick_size=0.1,
        fight_duration=fight_duration,
        max_mana=300.0,
        mana_regen_rate=15.0,
        ailment_damage_pct=75.0,
        ailment_duration_pct=50.0,
        skills=(
            SkillSpec(
                name="bleed_strike",
                mana_cost=15.0,
                cooldown=1.0,
                base_damage=0.0,
                ailment_type=AilmentType.BLEED,
                ailment_base_dmg=30.0,
                ailment_duration=5.0,
                priority=1,
            ),
            SkillSpec(
                name="poison_bolt",
                mana_cost=10.0,
                cooldown=0.5,
                base_damage=0.0,
                ailment_type=AilmentType.POISON,
                ailment_base_dmg=20.0,
                ailment_duration=4.0,
                priority=2,
            ),
        ),
    )


def _assert_invariants(result, label: str) -> None:
    assert result.mana_floor >= 0.0,      f"{label}: mana_floor < 0"
    assert result.cooldown_floor >= 0.0,  f"{label}: cooldown_floor < 0"
    assert result.total_damage >= 0.0,    f"{label}: negative total_damage"
    assert result.hit_damage_total >= 0.0
    assert result.ailment_damage_total >= 0.0
    assert result.total_damage == pytest.approx(
        result.hit_damage_total + result.ailment_damage_total, rel=1e-6
    ), f"{label}: total != hit + ailment"
    assert result.average_dps > 0.0,      f"{label}: zero DPS"


# ---------------------------------------------------------------------------
# 60-second fights
# ---------------------------------------------------------------------------

class TestStress60s:
    def test_sustain_60s_invariants(self):
        _assert_invariants(FullCombatLoop(_sustain_config(60.0)).run(), "sustain_60s")

    def test_ailment_60s_invariants(self):
        _assert_invariants(FullCombatLoop(_ailment_config(60.0)).run(), "ailment_60s")

    def test_60s_has_casts(self):
        result = FullCombatLoop(_sustain_config(60.0)).run()
        assert sum(result.casts_per_skill.values()) > 0


# ---------------------------------------------------------------------------
# 300-second fights
# ---------------------------------------------------------------------------

class TestStress300s:
    def test_sustain_300s_invariants(self):
        _assert_invariants(FullCombatLoop(_sustain_config(300.0)).run(), "sustain_300s")

    def test_ailment_300s_invariants(self):
        _assert_invariants(FullCombatLoop(_ailment_config(300.0)).run(), "ailment_300s")

    def test_damage_scales_with_duration(self):
        r60  = FullCombatLoop(_sustain_config(60.0)).run()
        r300 = FullCombatLoop(_sustain_config(300.0)).run()
        assert r300.total_damage > r60.total_damage * 4.0


# ---------------------------------------------------------------------------
# 600-second fights
# ---------------------------------------------------------------------------

class TestStress600s:
    def test_sustain_600s_invariants(self):
        _assert_invariants(FullCombatLoop(_sustain_config(600.0)).run(), "sustain_600s")

    def test_dps_stable_across_halves(self):
        # DPS should be the same regardless of fight length (steady state)
        r_300 = FullCombatLoop(_sustain_config(300.0)).run()
        r_600 = FullCombatLoop(_sustain_config(600.0)).run()
        assert abs(r_600.average_dps - r_300.average_dps) / r_300.average_dps < 0.05


# ---------------------------------------------------------------------------
# 1800-second fights (coarse tick for speed)
# ---------------------------------------------------------------------------

class TestStress1800s:
    def _cfg(self, fight_duration: float) -> SimConfig:
        return SimConfig(
            tick_size=0.5,
            fight_duration=fight_duration,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(
                SkillSpec("primary", mana_cost=20.0, cooldown=2.0, base_damage=100.0, priority=1),
                SkillSpec("filler",  mana_cost=5.0,  cooldown=0.5, base_damage=30.0,  priority=2),
            ),
        )

    def test_sustain_1800s_invariants(self):
        _assert_invariants(FullCombatLoop(self._cfg(1800.0)).run(), "sustain_1800s")

    def test_1800s_mana_non_negative(self):
        cfg = SimConfig(
            tick_size=0.5,
            fight_duration=1800.0,
            max_mana=100.0,
            mana_regen_rate=10.0,
            skills=(SkillSpec("blast", mana_cost=30.0, cooldown=2.0, base_damage=80.0),),
        )
        assert FullCombatLoop(cfg).run().mana_floor >= 0.0


# ---------------------------------------------------------------------------
# SimStats tick-level drift detection
# ---------------------------------------------------------------------------

class TestTickLevelStability:
    def test_constant_damage_per_cast_exact(self):
        cfg = SimConfig(
            tick_size=0.1,
            fight_duration=30.0,
            max_mana=1_000_000.0,
            mana_regen_rate=0.0,
            skills=(SkillSpec("spam", mana_cost=0.0, cooldown=0.0, base_damage=10.0),),
        )
        result = FullCombatLoop(cfg).run()
        casts = result.casts_per_skill.get("spam", 0)
        assert result.hit_damage_total == pytest.approx(casts * 10.0)

    def test_simstats_stable_for_constant_values(self):
        s = SimStats()
        for _ in range(300):
            s.record(10.0)
        assert s.is_stable()

    def test_simstats_unstable_on_spike(self):
        s = SimStats()
        for _ in range(299):
            s.record(10.0)
        s.record(10000.0)
        assert not s.is_stable()
