"""
Combat Regression Suite (Step 87).

Locks known-good outputs into permanent regression tests. Any future change
that alters these values must be intentional and this file must be updated.

Locked values were captured from a verified reference run and must remain
stable across all future refactors.

Coverage:
  - FullCombatLoop (sustain and ailment) — total damage, DPS, casts
  - Hit pipeline — basic hit, fire resistance, physical→fire conversion,
    crit, block, shield, leech, reflection
  - Accuracy / dodge / block systems — specific probability outputs
  - Armor formula — specific mitigation values
  - Resistance formula — specific damage outputs
"""

import pytest

from app.domain.accuracy import calculate_hit_chance
from app.domain.armor import apply_armor, armor_mitigation_pct
from app.domain.block import block_result
from app.domain.calculators.damage_type_router import DamageType
from app.domain.combat_validation import HitInput, resolve_hit
from app.domain.damage_conversion import ConversionRule
from app.domain.dodge import dodge_chance
from app.domain.enemy import EnemyInstance, EnemyStats
from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.ailments import AilmentType
from app.domain.overkill import overkill_amount
from app.domain.penetration import effective_resistance
from app.domain.reflection import apply_reflection
from app.domain.resistance import apply_resistance
from app.domain.shields import AbsorptionShield


# ---------------------------------------------------------------------------
# FullCombatLoop regression
# ---------------------------------------------------------------------------

class TestLoopRegression:
    def _sustain_60s(self) -> SimConfig:
        return SimConfig(
            tick_size=0.1,
            fight_duration=60.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            ailment_damage_pct=50.0,
            skills=(
                SkillSpec("fireball",  mana_cost=30.0, cooldown=2.0, base_damage=150.0, priority=1),
                SkillSpec("frostbolt", mana_cost=10.0, cooldown=0.5, base_damage=50.0,  priority=2),
            ),
        )

    def _ailment_30s(self) -> SimConfig:
        return SimConfig(
            tick_size=0.1,
            fight_duration=30.0,
            max_mana=300.0,
            mana_regen_rate=15.0,
            ailment_damage_pct=75.0,
            ailment_duration_pct=50.0,
            skills=(
                SkillSpec(
                    name="bleed",
                    mana_cost=15.0,
                    cooldown=1.0,
                    base_damage=0.0,
                    ailment_type=AilmentType.BLEED,
                    ailment_base_dmg=30.0,
                    ailment_duration=5.0,
                    priority=1,
                ),
            ),
        )

    # --- sustain ---

    def test_sustain_60s_total_damage(self):
        assert FullCombatLoop(self._sustain_60s()).run().total_damage == pytest.approx(6950.0)

    def test_sustain_60s_average_dps(self):
        dps = FullCombatLoop(self._sustain_60s()).run().average_dps
        assert dps == pytest.approx(115.833, rel=1e-3)

    def test_sustain_60s_ticks_simulated(self):
        assert FullCombatLoop(self._sustain_60s()).run().ticks_simulated == 600

    def test_sustain_60s_fireball_casts(self):
        assert FullCombatLoop(self._sustain_60s()).run().casts_per_skill["fireball"] == 15

    def test_sustain_60s_frostbolt_casts(self):
        assert FullCombatLoop(self._sustain_60s()).run().casts_per_skill["frostbolt"] == 94

    def test_sustain_60s_accounting_identity(self):
        r = FullCombatLoop(self._sustain_60s()).run()
        assert r.total_damage == pytest.approx(r.hit_damage_total + r.ailment_damage_total, rel=1e-6)

    # --- ailment ---

    def test_ailment_30s_total_damage(self):
        r = FullCombatLoop(self._ailment_30s()).run()
        assert r.total_damage == pytest.approx(16978.5, rel=1e-4)

    def test_ailment_30s_bleed_casts(self):
        assert FullCombatLoop(self._ailment_30s()).run().casts_per_skill["bleed"] == 28

    def test_ailment_30s_all_damage_from_ailments(self):
        r = FullCombatLoop(self._ailment_30s()).run()
        assert r.hit_damage_total == pytest.approx(0.0)
        assert r.ailment_damage_total == pytest.approx(r.total_damage, rel=1e-6)


# ---------------------------------------------------------------------------
# Hit pipeline regression
# ---------------------------------------------------------------------------

class TestHitPipelineRegression:
    def test_basic_hit_100_damage(self):
        result = resolve_hit(HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0))
        assert result.health_damage == pytest.approx(100.0)
        assert result.landed is True
        assert result.is_crit is False

    def test_miss_zero_damage(self):
        result = resolve_hit(HitInput(base_damage=100.0, rng_hit=1.0))
        assert result.landed is False
        assert result.health_damage == pytest.approx(0.0)

    def test_crit_2x_gives_200(self):
        result = resolve_hit(HitInput(
            base_damage=100.0,
            crit_chance=1.0,
            crit_multiplier=2.0,
            rng_hit=0.0,
            rng_crit=0.0,
        ))
        assert result.is_crit is True
        assert result.health_damage == pytest.approx(200.0)

    def test_fire_50pct_resistance_gives_50(self):
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=0, resistances={"fire": 50.0}))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.FIRE,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.post_resistance == pytest.approx(50.0)
        assert result.health_damage   == pytest.approx(50.0)

    def test_physical_50pct_to_fire_50pct_res_gives_75(self):
        # 50 physical (no resistance) + 50 fire (50% resist → 25) = 75
        rules = (ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),)
        enemy = EnemyInstance.from_stats(EnemyStats(health=1000, armor=0, resistances={"fire": 50.0}))
        result = resolve_hit(HitInput(
            base_damage=100.0,
            damage_type=DamageType.PHYSICAL,
            conversion_rules=rules,
            rng_hit=0.0,
            rng_crit=99.0,
            enemy=enemy,
        ))
        assert result.health_damage == pytest.approx(75.0)

    def test_shield_50_absorbs_50_overflow_50(self):
        shield = AbsorptionShield.at_full(50.0)
        result = resolve_hit(HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0, shield=shield))
        assert result.shield_absorbed == pytest.approx(50.0)
        assert result.health_damage   == pytest.approx(50.0)

    def test_leech_10pct_of_100_is_10(self):
        result = resolve_hit(HitInput(
            base_damage=100.0, rng_hit=0.0, rng_crit=99.0, leech_pct=10.0
        ))
        assert result.mana_leeched == pytest.approx(10.0)

    def test_reflect_25pct_of_100_is_25(self):
        result = resolve_hit(HitInput(
            base_damage=100.0, rng_hit=0.0, rng_crit=99.0, reflect_pct=25.0
        ))
        assert result.reflected_damage == pytest.approx(25.0)

    def test_overkill_50hp_enemy_hit_100(self):
        enemy = EnemyInstance.from_stats(EnemyStats(health=50, armor=0))
        result = resolve_hit(HitInput(base_damage=100.0, rng_hit=0.0, rng_crit=99.0, enemy=enemy))
        assert result.overkill == pytest.approx(50.0)
        assert not enemy.is_alive


# ---------------------------------------------------------------------------
# Individual system regression
# ---------------------------------------------------------------------------

class TestArmorRegression:
    def test_armor_1000_damage_100_mitigation(self):
        # armor/(armor + K*damage) = 1000/(1000+1000) = 0.5 → 50% mit
        mit = armor_mitigation_pct(1000.0, 100.0)
        assert mit == pytest.approx(0.5)
        assert apply_armor(100.0, 1000.0) == pytest.approx(50.0)

    def test_armor_0_no_mitigation(self):
        assert apply_armor(100.0, 0.0) == pytest.approx(100.0)


class TestResistanceRegression:
    def test_75pct_resistance_leaves_25pct(self):
        assert apply_resistance(100.0, 75.0) == pytest.approx(25.0)

    def test_0pct_resistance_full_damage(self):
        assert apply_resistance(100.0, 0.0) == pytest.approx(100.0)

    def test_neg_50pct_resistance_amplifies(self):
        assert apply_resistance(100.0, -50.0) == pytest.approx(150.0)


class TestPenetrationRegression:
    def test_25pen_on_75res_leaves_50_effective(self):
        assert effective_resistance(75.0, penetration=25.0) == pytest.approx(50.0)

    def test_pen_plus_shred_additive(self):
        assert effective_resistance(75.0, penetration=10.0, shred=15.0) == pytest.approx(50.0)


class TestAccuracyRegression:
    def test_equal_accuracy_evasion_hits_50pct(self):
        # Both 1000 → 1000/(1000+1000)=0.5, clamped to 0.5
        assert calculate_hit_chance(1000.0, 1000.0) == pytest.approx(0.5)

    def test_zero_evasion_hits_ceiling(self):
        from app.domain.accuracy import HIT_CHANCE_MAX
        assert calculate_hit_chance(1000.0, 0.0) == pytest.approx(HIT_CHANCE_MAX)


class TestDodgeRegression:
    def test_zero_dodge_rating(self):
        assert dodge_chance(0.0) == pytest.approx(0.0)


class TestBlockRegression:
    def test_50pct_block_eff_halves_damage(self):
        dmg, blocked = block_result(100.0, 1.0, 0.5, rng_roll=0.0)
        assert blocked is True
        assert dmg == pytest.approx(50.0)

    def test_full_block_eff_zeroes_damage(self):
        dmg, blocked = block_result(100.0, 1.0, 1.0, rng_roll=0.0)
        assert blocked is True
        assert dmg == pytest.approx(0.0)


class TestReflectionRegression:
    def test_50pct_reflect_of_100_is_50(self):
        _, reflected = apply_reflection(100.0, 50.0)
        assert reflected == pytest.approx(50.0)


class TestOverkillRegression:
    def test_100_damage_50_hp_overkill_50(self):
        assert overkill_amount(100.0, 50.0) == pytest.approx(50.0)

    def test_no_overkill_when_more_hp(self):
        assert overkill_amount(50.0, 100.0) == pytest.approx(0.0)
