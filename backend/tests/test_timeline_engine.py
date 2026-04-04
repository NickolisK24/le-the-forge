"""
Tests for the Buff/Debuff Timeline Engine (Step 4).

Validates:
  - BuffType enum members exist
  - BuffInstance is frozen with correct fields
  - TimelineEngine: add, tick, expire, query, clear
"""

import pytest
from app.domain.timeline import BuffType, BuffInstance, TimelineEngine


# ---------------------------------------------------------------------------
# BuffType
# ---------------------------------------------------------------------------

class TestBuffType:
    def test_all_types_exist(self):
        expected = {
            "damage_multiplier", "attack_speed", "cast_speed",
            "movement_speed", "resistance_shred", "damage_taken",
            "crit_chance_bonus",
        }
        assert {t.value for t in BuffType} == expected


# ---------------------------------------------------------------------------
# BuffInstance
# ---------------------------------------------------------------------------

class TestBuffInstance:
    def test_fields_accessible(self):
        b = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0, source="fireball")
        assert b.buff_type is BuffType.DAMAGE_MULTIPLIER
        assert b.value == 20.0
        assert b.duration == 5.0
        assert b.source == "fireball"

    def test_source_defaults_to_empty_string(self):
        b = BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0)
        assert b.source == ""

    def test_is_frozen(self):
        b = BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0)
        with pytest.raises((AttributeError, TypeError)):
            b.duration = 99.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# TimelineEngine — add and query
# ---------------------------------------------------------------------------

class TestTimelineEngineAdd:
    def test_starts_empty(self):
        engine = TimelineEngine()
        assert engine.active_buffs == []

    def test_add_buff_appears_in_active(self):
        engine = TimelineEngine()
        b = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0)
        engine.add_buff(b)
        assert len(engine.active_buffs) == 1

    def test_multiple_buffs_added(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0))
        assert len(engine.active_buffs) == 2

    def test_active_buffs_is_snapshot(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        snapshot = engine.active_buffs
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0))
        assert len(snapshot) == 1  # not affected by later add


# ---------------------------------------------------------------------------
# TimelineEngine — tick and expiry
# ---------------------------------------------------------------------------

class TestTimelineEngineTick:
    def test_duration_decreases_after_tick(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.tick(1.0)
        assert engine.active_buffs[0].duration == pytest.approx(4.0)

    def test_expired_buff_removed(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 1.0))
        engine.tick(1.0)
        assert engine.active_buffs == []

    def test_tick_exceeding_duration_removes_buff(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 0.5))
        engine.tick(2.0)
        assert engine.active_buffs == []

    def test_partial_expiry(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 0.5))  # expires
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 5.0))       # survives
        engine.tick(1.0)
        assert len(engine.active_buffs) == 1
        assert engine.active_buffs[0].buff_type is BuffType.ATTACK_SPEED

    def test_tick_returns_expired_buffs(self):
        engine = TimelineEngine()
        b = BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 0.5)
        engine.add_buff(b)
        expired = engine.tick(1.0)
        assert len(expired) == 1
        assert expired[0].buff_type is BuffType.DAMAGE_MULTIPLIER

    def test_tick_returns_empty_when_none_expire(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 10.0))
        expired = engine.tick(1.0)
        assert expired == []

    def test_cumulative_ticks_expire_correctly(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 3.0))
        engine.tick(1.0)
        assert len(engine.active_buffs) == 1
        engine.tick(1.0)
        assert len(engine.active_buffs) == 1
        engine.tick(1.0)
        assert len(engine.active_buffs) == 0

    def test_buff_fields_preserved_after_tick(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0, source="test"))
        engine.tick(1.0)
        b = engine.active_buffs[0]
        assert b.value == pytest.approx(20.0)
        assert b.source == "test"
        assert b.buff_type is BuffType.DAMAGE_MULTIPLIER


# ---------------------------------------------------------------------------
# TimelineEngine — queries
# ---------------------------------------------------------------------------

class TestTimelineEngineQueries:
    def test_buffs_of_type_returns_matching(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0))
        result = engine.buffs_of_type(BuffType.DAMAGE_MULTIPLIER)
        assert len(result) == 1
        assert result[0].buff_type is BuffType.DAMAGE_MULTIPLIER

    def test_buffs_of_type_empty_when_no_match(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0))
        assert engine.buffs_of_type(BuffType.DAMAGE_MULTIPLIER) == []

    def test_total_modifier_single(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        assert engine.total_modifier(BuffType.DAMAGE_MULTIPLIER) == pytest.approx(20.0)

    def test_total_modifier_multiple_same_type(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 15.0, 3.0))
        assert engine.total_modifier(BuffType.DAMAGE_MULTIPLIER) == pytest.approx(35.0)

    def test_total_modifier_zero_when_absent(self):
        engine = TimelineEngine()
        assert engine.total_modifier(BuffType.DAMAGE_MULTIPLIER) == pytest.approx(0.0)

    def test_total_modifier_ignores_other_types(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 100.0, 5.0))
        assert engine.total_modifier(BuffType.DAMAGE_MULTIPLIER) == pytest.approx(20.0)

    def test_has_any_true(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        assert engine.has_any(BuffType.DAMAGE_MULTIPLIER) is True

    def test_has_any_false(self):
        engine = TimelineEngine()
        assert engine.has_any(BuffType.DAMAGE_MULTIPLIER) is False

    def test_has_any_false_after_expiry(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 0.5))
        engine.tick(1.0)
        assert engine.has_any(BuffType.DAMAGE_MULTIPLIER) is False

    def test_negative_value_debuff(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_TAKEN, -20.0, 5.0))
        assert engine.total_modifier(BuffType.DAMAGE_TAKEN) == pytest.approx(-20.0)


# ---------------------------------------------------------------------------
# TimelineEngine — clear
# ---------------------------------------------------------------------------

class TestTimelineEngineClear:
    def test_clear_removes_all(self):
        engine = TimelineEngine()
        engine.add_buff(BuffInstance(BuffType.DAMAGE_MULTIPLIER, 20.0, 5.0))
        engine.add_buff(BuffInstance(BuffType.ATTACK_SPEED, 10.0, 3.0))
        engine.clear()
        assert engine.active_buffs == []

    def test_clear_empty_engine_no_error(self):
        engine = TimelineEngine()
        engine.clear()
        assert engine.active_buffs == []
