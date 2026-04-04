"""
Tests for Multi-Hit Skill Support (Step 6).

Validates:
  - SkillStatDef has hit_count and hit_interval fields with correct defaults
  - from_dict parses hit_count and hit_interval from JSON
  - calculate_multi_hit_dps: formula, edge cases, error handling
"""

import pytest
from app.domain.skill import SkillStatDef, calculate_multi_hit_dps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_skill(
    hit_count: int = 1,
    hit_interval: float = 0.0,
    attack_speed: float = 1.0,
    base_damage: float = 100.0,
) -> SkillStatDef:
    return SkillStatDef(
        base_damage=base_damage,
        level_scaling=0.05,
        attack_speed=attack_speed,
        scaling_stats=(),
        data_version="test",
        hit_count=hit_count,
        hit_interval=hit_interval,
    )


# ---------------------------------------------------------------------------
# Field defaults
# ---------------------------------------------------------------------------

class TestSkillStatDefMultiHitFields:
    def test_hit_count_default_one(self):
        skill = SkillStatDef(
            base_damage=100.0, level_scaling=0.0, attack_speed=1.0,
            scaling_stats=(), data_version="test",
        )
        assert skill.hit_count == 1

    def test_hit_interval_default_zero(self):
        skill = SkillStatDef(
            base_damage=100.0, level_scaling=0.0, attack_speed=1.0,
            scaling_stats=(), data_version="test",
        )
        assert skill.hit_interval == 0.0

    def test_hit_count_stored(self):
        skill = _make_skill(hit_count=3)
        assert skill.hit_count == 3

    def test_hit_interval_stored(self):
        skill = _make_skill(hit_interval=0.15)
        assert skill.hit_interval == pytest.approx(0.15)

    def test_is_frozen(self):
        skill = _make_skill(hit_count=3)
        with pytest.raises((AttributeError, TypeError)):
            skill.hit_count = 5  # type: ignore[misc]


# ---------------------------------------------------------------------------
# from_dict
# ---------------------------------------------------------------------------

class TestSkillStatDefFromDict:
    def _base_dict(self) -> dict:
        return {
            "base_damage": 100.0,
            "level_scaling": 0.05,
            "attack_speed": 1.0,
            "scaling_stats": [],
        }

    def test_from_dict_default_hit_count(self):
        skill = SkillStatDef.from_dict(self._base_dict(), data_version="test")
        assert skill.hit_count == 1

    def test_from_dict_default_hit_interval(self):
        skill = SkillStatDef.from_dict(self._base_dict(), data_version="test")
        assert skill.hit_interval == pytest.approx(0.0)

    def test_from_dict_parses_hit_count(self):
        d = {**self._base_dict(), "hit_count": 3}
        skill = SkillStatDef.from_dict(d, data_version="test")
        assert skill.hit_count == 3

    def test_from_dict_parses_hit_interval(self):
        d = {**self._base_dict(), "hit_interval": 0.15}
        skill = SkillStatDef.from_dict(d, data_version="test")
        assert skill.hit_interval == pytest.approx(0.15)

    def test_from_dict_hit_count_zero_stored_as_zero(self):
        # Validation is at the calculator layer, not construction
        d = {**self._base_dict(), "hit_count": 0}
        skill = SkillStatDef.from_dict(d, data_version="test")
        assert skill.hit_count == 0


# ---------------------------------------------------------------------------
# calculate_multi_hit_dps
# ---------------------------------------------------------------------------

class TestCalculateMultiHitDPS:
    def test_single_hit_skill(self):
        skill = _make_skill(hit_count=1, attack_speed=2.0)
        assert calculate_multi_hit_dps(skill, 100.0) == pytest.approx(200.0)

    def test_multi_hit_multiplies(self):
        # 3 hits × 100 damage × 1.0 attacks/s = 300 DPS
        skill = _make_skill(hit_count=3, attack_speed=1.0)
        assert calculate_multi_hit_dps(skill, 100.0) == pytest.approx(300.0)

    def test_hit_count_and_attack_speed_combined(self):
        # 4 hits × 50 damage × 2.0 attacks/s = 400 DPS
        skill = _make_skill(hit_count=4, attack_speed=2.0)
        assert calculate_multi_hit_dps(skill, 50.0) == pytest.approx(400.0)

    def test_hit_interval_does_not_affect_dps(self):
        # DPS should be the same regardless of hit_interval
        skill_a = _make_skill(hit_count=3, attack_speed=1.0, hit_interval=0.0)
        skill_b = _make_skill(hit_count=3, attack_speed=1.0, hit_interval=0.5)
        dps_a = calculate_multi_hit_dps(skill_a, 100.0)
        dps_b = calculate_multi_hit_dps(skill_b, 100.0)
        assert dps_a == pytest.approx(dps_b)

    def test_zero_per_hit_damage(self):
        skill = _make_skill(hit_count=5, attack_speed=2.0)
        assert calculate_multi_hit_dps(skill, 0.0) == pytest.approx(0.0)

    def test_fractional_attack_speed(self):
        # 2 hits × 100 damage × 0.5 attacks/s = 100 DPS
        skill = _make_skill(hit_count=2, attack_speed=0.5)
        assert calculate_multi_hit_dps(skill, 100.0) == pytest.approx(100.0)

    def test_invalid_hit_count_zero_raises(self):
        skill = _make_skill(hit_count=0, attack_speed=1.0)
        with pytest.raises(ValueError, match="hit_count"):
            calculate_multi_hit_dps(skill, 100.0)

    def test_invalid_hit_count_negative_raises(self):
        skill = _make_skill(hit_count=-1, attack_speed=1.0)
        with pytest.raises(ValueError, match="hit_count"):
            calculate_multi_hit_dps(skill, 100.0)

    def test_invalid_attack_speed_zero_raises(self):
        skill = _make_skill(hit_count=1, attack_speed=0.0)
        with pytest.raises(ValueError, match="attack_speed"):
            calculate_multi_hit_dps(skill, 100.0)

    def test_invalid_attack_speed_negative_raises(self):
        skill = _make_skill(hit_count=1, attack_speed=-1.0)
        with pytest.raises(ValueError, match="attack_speed"):
            calculate_multi_hit_dps(skill, 100.0)

    def test_high_hit_count(self):
        # 10 hits × 25 damage × 3.0 attacks/s = 750 DPS
        skill = _make_skill(hit_count=10, attack_speed=3.0)
        assert calculate_multi_hit_dps(skill, 25.0) == pytest.approx(750.0)
