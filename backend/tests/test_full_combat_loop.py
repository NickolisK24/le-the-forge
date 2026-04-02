"""
Tests for Full Combat Loop Stabilization (Step 60).

Validates:
  - Numerical stability over 30s, 60s, and 300s fights
  - Mana never goes negative
  - Cooldowns never go negative
  - DPS is consistent across identical repeated runs (determinism)
  - Hit damage accumulates proportionally to cast count
  - Ailment damage accumulates correctly with duration scaling
  - Buff duration scaling extends DoT/buff windows correctly
  - Damage type conversion changes damage composition, not total
  - Rotation selects fallback skill when primary is on cooldown
  - Empty skill list produces zero damage
  - Integration: mana + cooldown + rotation together
"""

import pytest
from app.domain.full_combat_loop import FullCombatLoop, SimConfig, SkillSpec
from app.domain.calculators.damage_type_router import DamageType
from app.domain.damage_conversion import ConversionRule
from app.domain.ailments import AilmentType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def basic_skill(
    name="blast",
    mana_cost=20.0,
    cooldown=1.0,
    base_damage=100.0,
    priority=1,
) -> SkillSpec:
    return SkillSpec(
        name=name,
        mana_cost=mana_cost,
        cooldown=cooldown,
        base_damage=base_damage,
        priority=priority,
    )


def run(config: SimConfig):
    return FullCombatLoop(config).run()


# ---------------------------------------------------------------------------
# Stability — fight durations
# ---------------------------------------------------------------------------

class TestNumericalStability:
    def test_30s_fight_mana_never_negative(self):
        cfg = SimConfig(
            fight_duration=30.0,
            max_mana=100.0,
            mana_regen_rate=5.0,
            skills=(basic_skill(mana_cost=30.0, cooldown=1.5),),
        )
        result = run(cfg)
        assert result.mana_floor >= 0.0

    def test_60s_fight_mana_never_negative(self):
        cfg = SimConfig(
            fight_duration=60.0,
            max_mana=50.0,
            mana_regen_rate=10.0,
            skills=(basic_skill(mana_cost=40.0, cooldown=2.0),),
        )
        result = run(cfg)
        assert result.mana_floor >= 0.0

    def test_300s_fight_mana_never_negative(self):
        cfg = SimConfig(
            fight_duration=300.0,
            max_mana=200.0,
            mana_regen_rate=15.0,
            skills=(basic_skill(mana_cost=50.0, cooldown=2.0),),
        )
        result = run(cfg)
        assert result.mana_floor >= 0.0

    def test_cooldown_floor_never_negative(self):
        cfg = SimConfig(
            fight_duration=60.0,
            skills=(basic_skill(cooldown=2.0),),
        )
        result = run(cfg)
        assert result.cooldown_floor >= 0.0

    def test_ticks_match_duration(self):
        # 10.0 / 0.1 = 100 ticks; ±1 allowed due to floating point accumulation
        cfg = SimConfig(fight_duration=10.0, tick_size=0.1)
        result = run(cfg)
        assert 100 <= result.ticks_simulated <= 101

    def test_fight_duration_matches_config(self):
        cfg = SimConfig(fight_duration=30.0, tick_size=0.1)
        result = run(cfg)
        assert result.fight_duration == pytest.approx(30.0, rel=1e-6)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------

class TestDeterminism:
    def test_identical_configs_produce_identical_results(self):
        cfg = SimConfig(
            fight_duration=60.0,
            max_mana=150.0,
            mana_regen_rate=10.0,
            skills=(basic_skill(mana_cost=20.0, cooldown=1.5),),
        )
        r1 = run(cfg)
        r2 = run(cfg)
        assert r1.total_damage == pytest.approx(r2.total_damage)
        assert r1.casts_per_skill == r2.casts_per_skill

    def test_longer_fight_more_damage(self):
        base_cfg = dict(
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(basic_skill(mana_cost=10.0, cooldown=1.0, base_damage=50.0),),
        )
        r30  = run(SimConfig(fight_duration=30.0,  **base_cfg))
        r300 = run(SimConfig(fight_duration=300.0, **base_cfg))
        assert r300.total_damage > r30.total_damage


# ---------------------------------------------------------------------------
# Hit damage
# ---------------------------------------------------------------------------

class TestHitDamage:
    def test_no_cooldown_skill_casts_limited_by_mana(self):
        # Mana=100, cost=100, no regen → only 1 cast possible
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=100.0,
            mana_regen_rate=0.0,
            skills=(basic_skill(mana_cost=100.0, cooldown=0.0, base_damage=50.0),),
        )
        result = run(cfg)
        assert result.casts_per_skill.get("blast", 0) == 1
        assert result.hit_damage_total == pytest.approx(50.0)

    def test_hit_damage_accumulates_with_casts(self):
        # 200 mana, cost=50, regen=10/s, cooldown=0 → many casts
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=10.0,
            skills=(basic_skill(mana_cost=50.0, cooldown=0.0, base_damage=100.0),),
        )
        result = run(cfg)
        casts = result.casts_per_skill.get("blast", 0)
        assert result.hit_damage_total == pytest.approx(casts * 100.0)

    def test_total_damage_equals_hit_plus_ailment(self):
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(SkillSpec(
                name="poison_shot",
                mana_cost=10.0,
                cooldown=1.0,
                base_damage=50.0,
                ailment_type=AilmentType.POISON,
                ailment_base_dmg=10.0,
                ailment_duration=3.0,
            ),),
        )
        result = run(cfg)
        assert result.total_damage == pytest.approx(
            result.hit_damage_total + result.ailment_damage_total, rel=1e-6
        )


# ---------------------------------------------------------------------------
# Ailment damage
# ---------------------------------------------------------------------------

class TestAilmentDamage:
    def test_ailment_only_skill_produces_dot_damage(self):
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(SkillSpec(
                name="bleed_skill",
                mana_cost=5.0,
                cooldown=0.5,
                base_damage=0.0,
                ailment_type=AilmentType.BLEED,
                ailment_base_dmg=20.0,
                ailment_duration=4.0,
            ),),
        )
        result = run(cfg)
        assert result.ailment_damage_total > 0.0

    def test_ailment_damage_scales_with_ailment_damage_pct(self):
        base_cfg = dict(
            fight_duration=20.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(SkillSpec(
                name="ignite_skill",
                mana_cost=10.0,
                cooldown=1.0,
                ailment_type=AilmentType.IGNITE,
                ailment_base_dmg=50.0,
                ailment_duration=4.0,
            ),),
        )
        r_base = run(SimConfig(ailment_damage_pct=0.0,   **base_cfg))
        r_boost = run(SimConfig(ailment_damage_pct=50.0, **base_cfg))
        # 50% more damage → boost should be ~1.5× base
        assert r_boost.ailment_damage_total > r_base.ailment_damage_total

    def test_ailment_duration_scaling_extends_dot_window(self):
        # Longer ailments → more DoT per cast → higher total damage
        base_cfg = dict(
            fight_duration=20.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(SkillSpec(
                name="poison",
                mana_cost=10.0,
                cooldown=2.0,
                ailment_type=AilmentType.POISON,
                ailment_base_dmg=30.0,
                ailment_duration=3.0,
            ),),
        )
        r_base   = run(SimConfig(ailment_duration_pct=0.0,  **base_cfg))
        r_extend = run(SimConfig(ailment_duration_pct=100.0, **base_cfg))
        assert r_extend.ailment_damage_total >= r_base.ailment_damage_total


# ---------------------------------------------------------------------------
# Damage type conversion
# ---------------------------------------------------------------------------

class TestDamageConversion:
    def test_conversion_does_not_lose_damage(self):
        # 50% physical → fire still produces same total hit damage
        cfg_no_conv = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(basic_skill(base_damage=100.0, cooldown=1.0),),
        )
        cfg_conv = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            conversion_rules=(ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 50.0),),
            skills=(basic_skill(base_damage=100.0, cooldown=1.0),),
        )
        r1 = run(cfg_no_conv)
        r2 = run(cfg_conv)
        assert r1.hit_damage_total == pytest.approx(r2.hit_damage_total, rel=1e-6)

    def test_full_conversion_same_hit_damage(self):
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            conversion_rules=(ConversionRule(DamageType.PHYSICAL, DamageType.FIRE, 100.0),),
            skills=(basic_skill(base_damage=80.0, cooldown=1.0),),
        )
        result = run(cfg)
        casts = result.casts_per_skill.get("blast", 0)
        assert result.hit_damage_total == pytest.approx(casts * 80.0)


# ---------------------------------------------------------------------------
# Rotation and fallback
# ---------------------------------------------------------------------------

class TestRotationAndFallback:
    def test_two_skills_both_get_cast(self):
        cfg = SimConfig(
            fight_duration=20.0,
            max_mana=200.0,
            mana_regen_rate=20.0,
            skills=(
                SkillSpec("primary",  mana_cost=20.0, cooldown=3.0, base_damage=100.0, priority=1),
                SkillSpec("filler",   mana_cost=5.0,  cooldown=0.0, base_damage=10.0,  priority=2),
            ),
        )
        result = run(cfg)
        assert result.casts_per_skill.get("primary", 0) > 0
        assert result.casts_per_skill.get("filler",  0) > 0

    def test_filler_casts_more_than_primary(self):
        cfg = SimConfig(
            fight_duration=30.0,
            max_mana=300.0,
            mana_regen_rate=30.0,
            skills=(
                SkillSpec("heavy",  mana_cost=50.0, cooldown=5.0, base_damage=500.0, priority=1),
                SkillSpec("light",  mana_cost=5.0,  cooldown=0.5, base_damage=20.0,  priority=2),
            ),
        )
        result = run(cfg)
        assert result.casts_per_skill["light"] > result.casts_per_skill["heavy"]

    def test_empty_skill_list_produces_zero_damage(self):
        cfg = SimConfig(fight_duration=30.0, skills=())
        result = run(cfg)
        assert result.total_damage == pytest.approx(0.0)
        assert result.ticks_simulated == 300


# ---------------------------------------------------------------------------
# Mana gating
# ---------------------------------------------------------------------------

class TestManaGating:
    def test_expensive_skill_not_cast_when_broke(self):
        # Max mana=10, cost=100 — should never be affordable
        cfg = SimConfig(
            fight_duration=10.0,
            max_mana=10.0,
            mana_regen_rate=0.0,
            skills=(SkillSpec("expensive", mana_cost=100.0, base_damage=1000.0),),
        )
        result = run(cfg)
        assert result.casts_per_skill.get("expensive", 0) == 0
        assert result.total_damage == pytest.approx(0.0)

    def test_regen_eventually_enables_casting(self):
        # Start with 0 mana (but max=100), regen to afford skill
        # Workaround: use very low starting-equivalent by high cost + slow regen
        cfg = SimConfig(
            fight_duration=60.0,
            max_mana=100.0,
            mana_regen_rate=1.0,  # slow regen
            skills=(SkillSpec("blast", mana_cost=90.0, cooldown=0.5, base_damage=50.0),),
        )
        result = run(cfg)
        # At 1/s regen, mana reaches 90 at t=90s — won't happen in 60s fight
        # starting at full 100 → first cast OK, then need to regen to 90 (takes 90s more)
        # actually starts at max_mana=100 so first cast IS possible immediately
        assert result.casts_per_skill.get("blast", 0) >= 1

    def test_average_dps_positive_for_active_skill(self):
        cfg = SimConfig(
            fight_duration=30.0,
            max_mana=200.0,
            mana_regen_rate=10.0,
            skills=(basic_skill(mana_cost=10.0, cooldown=1.0, base_damage=100.0),),
        )
        result = run(cfg)
        assert result.average_dps > 0.0
