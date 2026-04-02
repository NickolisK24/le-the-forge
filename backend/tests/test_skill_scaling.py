"""
Tests for skill_scaling (Step 90).

Validates tag-based damage scaling from stat pools.
"""

import pytest

from build.skill_scaling import ScalingTag, effective_damage, scale_skill


class TestScalingTag:
    def test_stat_key_format(self):
        assert ScalingTag.stat_key("fire")     == "fire_damage_pct"
        assert ScalingTag.stat_key("spell")    == "spell_damage_pct"
        assert ScalingTag.stat_key("physical") == "physical_damage_pct"

    def test_stat_key_case_insensitive(self):
        assert ScalingTag.stat_key("FIRE") == "fire_damage_pct"
        assert ScalingTag.stat_key("Fire") == "fire_damage_pct"


class TestScaleSkill:
    def test_no_tags_returns_base(self):
        result = scale_skill(100.0, [], {"fire_damage_pct": 50.0})
        assert result == pytest.approx(100.0)

    def test_empty_stat_pool_returns_base(self):
        result = scale_skill(100.0, ["fire"], {})
        assert result == pytest.approx(100.0)

    def test_single_tag_single_matching_stat(self):
        # 100 base, 50% fire bonus -> 150
        result = scale_skill(100.0, ["fire"], {"fire_damage_pct": 50.0})
        assert result == pytest.approx(150.0)

    def test_single_tag_no_matching_stat(self):
        result = scale_skill(100.0, ["fire"], {"cold_damage_pct": 50.0})
        assert result == pytest.approx(100.0)

    def test_multiple_tags_same_stat_not_double_counted(self):
        # "fire" and "elemental" both present; each has own stat key
        stat_pool = {"fire_damage_pct": 20.0, "elemental_damage_pct": 10.0}
        result = scale_skill(100.0, ["fire", "elemental"], stat_pool)
        # total_bonus = 20 + 10 = 30 -> 130
        assert result == pytest.approx(130.0)

    def test_multiple_tags_stack_additively(self):
        stat_pool = {"fire_damage_pct": 20.0, "spell_damage_pct": 15.0}
        result = scale_skill(100.0, ["fire", "spell"], stat_pool)
        # total_bonus = 35 -> 135
        assert result == pytest.approx(135.0)

    def test_non_matching_tags_ignored(self):
        stat_pool = {"cold_damage_pct": 100.0, "physical_damage_pct": 100.0}
        result = scale_skill(100.0, ["fire", "spell"], stat_pool)
        # no fire or spell stat → no bonus
        assert result == pytest.approx(100.0)

    def test_zero_bonus_no_change(self):
        result = scale_skill(100.0, ["fire"], {"fire_damage_pct": 0.0})
        assert result == pytest.approx(100.0)

    def test_negative_bonus_reduces_damage(self):
        result = scale_skill(100.0, ["fire"], {"fire_damage_pct": -25.0})
        assert result == pytest.approx(75.0)

    def test_scaling_proportional_to_base(self):
        result_a = scale_skill(200.0, ["fire"], {"fire_damage_pct": 50.0})
        result_b = scale_skill(100.0, ["fire"], {"fire_damage_pct": 50.0})
        assert result_a == pytest.approx(result_b * 2)

    def test_large_bonus_stack(self):
        # 10 stats each +30% = +300% total -> base * 4
        stat_pool = {f"tag{i}_damage_pct": 30.0 for i in range(10)}
        tags = [f"tag{i}" for i in range(10)]
        result = scale_skill(100.0, tags, stat_pool)
        assert result == pytest.approx(400.0)

    def test_zero_base_damage(self):
        result = scale_skill(0.0, ["fire"], {"fire_damage_pct": 100.0})
        assert result == pytest.approx(0.0)

    def test_stat_pool_keys_not_matching_any_tag_ignored(self):
        stat_pool = {
            "fire_damage_pct":   30.0,
            "mana_regen_rate":   10.0,
            "movement_speed_pct": 5.0,
        }
        result = scale_skill(100.0, ["fire"], stat_pool)
        assert result == pytest.approx(130.0)


class TestEffectiveDamage:
    def test_extra_flat_added_before_scaling(self):
        # (100 + 20) base, 50% fire -> 120 * 1.5 = 180
        result = effective_damage(100.0, ["fire"], {"fire_damage_pct": 50.0}, extra_flat=20.0)
        assert result == pytest.approx(180.0)

    def test_no_extra_flat_same_as_scale_skill(self):
        pool = {"fire_damage_pct": 40.0}
        assert effective_damage(100.0, ["fire"], pool) == pytest.approx(
            scale_skill(100.0, ["fire"], pool)
        )

    def test_zero_extra_flat(self):
        result = effective_damage(100.0, ["fire"], {"fire_damage_pct": 50.0}, extra_flat=0.0)
        assert result == pytest.approx(150.0)
