"""
Determinism Lock (Step 84).

Confirms that identical inputs always produce identical outputs across
multiple independent simulation runs. Tests both the full combat loop
(FullCombatLoop) and the hit pipeline (resolve_hit), exercising all
systems that involve randomness-seeding or ordering decisions.

Approach:
  - Run the same configuration N times and assert all results are equal.
  - Compare every field of SimResult and HitResult — not just totals.
  - Test determinism for: sustain config, ailment config, crit-heavy config,
    and the full 14-stage hit pipeline.
"""

import pytest

from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.ailments import AilmentType
from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.damage_conversion import ConversionRule
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.on_kill import OnKillEffect, OnKillEffectType, OnKillRegistry
from app.domain.shields import AbsorptionShield


_RUNS = 5   # Number of independent runs per test


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_loop(cfg: SimConfig, runs: int = _RUNS):
    return [FullCombatLoop(cfg).run() for _ in range(runs)]


def _assert_sim_results_identical(results):
    ref = results[0]
    for i, r in enumerate(results[1:], start=2):
        assert r.total_damage     == pytest.approx(ref.total_damage),     f"run {i}: total_damage"
        assert r.hit_damage_total == pytest.approx(ref.hit_damage_total), f"run {i}: hit_damage_total"
        assert r.ailment_damage_total == pytest.approx(ref.ailment_damage_total), f"run {i}: ailment"
        assert r.average_dps      == pytest.approx(ref.average_dps),      f"run {i}: average_dps"
        assert r.ticks_simulated  == ref.ticks_simulated,                  f"run {i}: ticks"
        assert r.casts_per_skill  == ref.casts_per_skill,                  f"run {i}: casts_per_skill"
        assert r.mana_floor       == pytest.approx(ref.mana_floor),        f"run {i}: mana_floor"
        assert r.cooldown_floor   == pytest.approx(ref.cooldown_floor),    f"run {i}: cooldown_floor"


# ---------------------------------------------------------------------------
# FullCombatLoop determinism
# ---------------------------------------------------------------------------

class TestLoopDeterminism:
    def _sustain_cfg(self, duration=60.0):
        return SimConfig(
            tick_size=0.1,
            fight_duration=duration,
            max_mana=200.0,
            mana_regen_rate=20.0,
            ailment_damage_pct=50.0,
            skills=(
                SkillSpec("fireball",  mana_cost=30.0, cooldown=2.0, base_damage=150.0, priority=1),
                SkillSpec("frostbolt", mana_cost=10.0, cooldown=0.5, base_damage=50.0,  priority=2),
            ),
        )

    def _ailment_cfg(self, duration=30.0):
        return SimConfig(
            tick_size=0.1,
            fight_duration=duration,
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

    def test_sustain_loop_deterministic(self):
        _assert_sim_results_identical(_run_loop(self._sustain_cfg()))

    def test_ailment_loop_deterministic(self):
        _assert_sim_results_identical(_run_loop(self._ailment_cfg()))

    def test_long_fight_deterministic(self):
        _assert_sim_results_identical(_run_loop(self._sustain_cfg(300.0)))

    def test_single_skill_deterministic(self):
        cfg = SimConfig(
            tick_size=0.1,
            fight_duration=30.0,
            max_mana=1_000_000.0,
            mana_regen_rate=0.0,
            skills=(SkillSpec("spam", mana_cost=0.0, cooldown=0.0, base_damage=10.0),),
        )
        _assert_sim_results_identical(_run_loop(cfg))

    def test_casts_per_skill_same_across_runs(self):
        cfg = self._sustain_cfg()
        results = _run_loop(cfg)
        ref_casts = results[0].casts_per_skill
        for r in results[1:]:
            assert r.casts_per_skill == ref_casts

    def test_mana_floor_deterministic(self):
        cfg = SimConfig(
            tick_size=0.1,
            fight_duration=60.0,
            max_mana=50.0,
            mana_regen_rate=5.0,
            skills=(SkillSpec("blast", mana_cost=30.0, cooldown=2.0, base_damage=80.0),),
        )
        floors = [FullCombatLoop(cfg).run().mana_floor for _ in range(_RUNS)]
        assert all(f == pytest.approx(floors[0]) for f in floors[1:])


# ---------------------------------------------------------------------------
# resolve_hit determinism
# ---------------------------------------------------------------------------

class TestHitPipelineDeterminism:
    def _make_input(self, **kwargs) -> HitInput:
        return HitInput(
            base_damage=100.0,
            rng_hit=0.0,
            rng_crit=0.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            **kwargs,
        )

    def _run_hit(self, inp: HitInput, runs: int = _RUNS):
        return [resolve_hit(inp) for _ in range(runs)]

    def _assert_hit_results_identical(self, results):
        ref = results[0]
        for i, r in enumerate(results[1:], start=2):
            assert r.landed           == ref.landed,                       f"run {i}: landed"
            assert r.is_crit          == ref.is_crit,                      f"run {i}: is_crit"
            assert r.crit_damage      == pytest.approx(ref.crit_damage),   f"run {i}: crit_damage"
            assert r.post_armor       == pytest.approx(ref.post_armor),    f"run {i}: post_armor"
            assert r.post_resistance  == pytest.approx(ref.post_resistance), f"run {i}: post_res"
            assert r.shield_absorbed  == pytest.approx(ref.shield_absorbed), f"run {i}: shield"
            assert r.health_damage    == pytest.approx(ref.health_damage), f"run {i}: health"
            assert r.overkill         == pytest.approx(ref.overkill),      f"run {i}: overkill"
            assert r.mana_leeched     == pytest.approx(ref.mana_leeched),  f"run {i}: leech"
            assert r.reflected_damage == pytest.approx(ref.reflected_damage), f"run {i}: reflect"

    def test_basic_hit_deterministic(self):
        inp = self._make_input()
        self._assert_hit_results_identical(self._run_hit(inp))

    def test_hit_with_enemy_deterministic(self):
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=500, resistances={"fire": 30.0}))
        inp = self._make_input(
            damage_type=DamageType.FIRE,
            enemy=enemy,
        )
        self._assert_hit_results_identical(self._run_hit(inp))

    def test_hit_with_conversion_deterministic(self):
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=500, resistances={"fire": 20.0}))
        inp = self._make_input(
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
            enemy=enemy,
        )
        self._assert_hit_results_identical(self._run_hit(inp))

    def test_hit_with_shield_deterministic(self):
        # AbsorptionShield is mutable; create fresh one per run
        results = []
        for _ in range(_RUNS):
            shield = AbsorptionShield.at_full(60.0)
            inp = HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0, shield=shield)
            results.append(resolve_hit(inp))
        self._assert_hit_results_identical(results)

    def test_hit_leech_and_reflect_deterministic(self):
        inp = self._make_input(leech_pct=15.0, reflect_pct=30.0)
        self._assert_hit_results_identical(self._run_hit(inp))

    def test_miss_always_deterministic(self):
        # rng_hit=1.0 → always misses
        inp = HitInput(base_damage=100.0, rng_hit=1.0)
        results = self._run_hit(inp)
        assert all(not r.landed for r in results)
        assert all(r.health_damage == pytest.approx(0.0) for r in results)

    def test_on_kill_deterministic(self):
        # Fresh enemy + registry each run; rng_on_kill fixed
        results = []
        for _ in range(_RUNS):
            enemy = EnemyInstance.from_stats(EnemyStats(health=50, armor=0))
            reg   = OnKillRegistry()
            reg.register(OnKillEffect(OnKillEffectType.RESTORE_MANA, value=20.0))
            inp = HitInput(
                base_damage=100.0,
                rng_hit=0.0,
                rng_crit=99.0,
                enemy=enemy,
                on_kill_registry=reg,
                rng_on_kill=0.0,
            )
            results.append(resolve_hit(inp))
        ref_effects = len(results[0].on_kill_effects)
        assert all(len(r.on_kill_effects) == ref_effects for r in results)


# ---------------------------------------------------------------------------
# Repeated identical configs produce same results
# ---------------------------------------------------------------------------

class TestRepeatedConfigs:
    def test_10_runs_same_total_damage(self):
        cfg = SimConfig(
            tick_size=0.1,
            fight_duration=20.0,
            max_mana=500.0,
            mana_regen_rate=25.0,
            ailment_damage_pct=40.0,
            skills=(
                SkillSpec("a", mana_cost=20.0, cooldown=1.0, base_damage=80.0, priority=1),
                SkillSpec("b", mana_cost=5.0,  cooldown=0.3, base_damage=25.0, priority=2),
            ),
        )
        totals = [FullCombatLoop(cfg).run().total_damage for _ in range(10)]
        assert all(t == pytest.approx(totals[0]) for t in totals[1:])
