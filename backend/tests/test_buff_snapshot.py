"""
Tests for Snapshot vs Dynamic Buff Handling (Step 69).
"""

import pytest
from app.domain.buff_snapshot import (
    BuffResolutionMode,
    DynamicBuff,
    SnapshotBuff,
    resolve_buff_value,
    snapshot_from_stats,
)
from app.domain.timeline import BuffType


class TestSnapshotBuff:
    def test_basic_construction(self):
        b = SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=20.0, duration=5.0)
        assert b.value == pytest.approx(20.0)
        assert b.duration == pytest.approx(5.0)
        assert b.mode is BuffResolutionMode.SNAPSHOT

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="duration"):
            SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=10.0, duration=-1.0)

    def test_zero_duration_allowed(self):
        b = SnapshotBuff(BuffType.CAST_SPEED, value=5.0, duration=0.0)
        assert b.duration == pytest.approx(0.0)

    def test_source_field(self):
        b = SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=10.0, duration=3.0, source="passive")
        assert b.source == "passive"


class TestDynamicBuff:
    def test_basic_construction(self):
        b = DynamicBuff(BuffType.CAST_SPEED, stat_field="cast_speed", duration=4.0)
        assert b.stat_field == "cast_speed"
        assert b.mode is BuffResolutionMode.DYNAMIC

    def test_empty_stat_field_raises(self):
        with pytest.raises(ValueError, match="stat_field"):
            DynamicBuff(BuffType.CAST_SPEED, stat_field="", duration=3.0)

    def test_negative_duration_raises(self):
        with pytest.raises(ValueError, match="duration"):
            DynamicBuff(BuffType.CAST_SPEED, stat_field="speed", duration=-0.1)


class TestResolveBuffValue:
    def test_snapshot_returns_locked_value(self):
        b = SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=30.0, duration=5.0)
        assert resolve_buff_value(b) == pytest.approx(30.0)

    def test_snapshot_ignores_stat_accessor(self):
        # Even if the accessor returns something different, snapshot is locked
        b = SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=30.0, duration=5.0)
        accessor = lambda _: 999.0
        assert resolve_buff_value(b, accessor) == pytest.approx(30.0)

    def test_dynamic_calls_stat_accessor(self):
        b = DynamicBuff(BuffType.CAST_SPEED, stat_field="cast_speed", duration=3.0)
        accessor = lambda field: {"cast_speed": 25.0}.get(field, 0.0)
        assert resolve_buff_value(b, accessor) == pytest.approx(25.0)

    def test_dynamic_returns_zero_when_no_accessor(self):
        b = DynamicBuff(BuffType.CAST_SPEED, stat_field="cast_speed", duration=3.0)
        assert resolve_buff_value(b, None) == pytest.approx(0.0)

    def test_dynamic_returns_zero_for_missing_field(self):
        b = DynamicBuff(BuffType.CAST_SPEED, stat_field="nonexistent_stat", duration=3.0)
        accessor = lambda field: (_ for _ in ()).throw(KeyError(field))
        assert resolve_buff_value(b, accessor) == pytest.approx(0.0)

    def test_dynamic_reflects_stat_change(self):
        # Simulate stat changing between calls
        b = DynamicBuff(BuffType.DAMAGE_MULTIPLIER, stat_field="dmg", duration=5.0)
        stats = {"dmg": 10.0}
        accessor = lambda f: stats[f]

        assert resolve_buff_value(b, accessor) == pytest.approx(10.0)

        stats["dmg"] = 50.0
        assert resolve_buff_value(b, accessor) == pytest.approx(50.0)

    def test_snapshot_does_not_reflect_stat_change(self):
        # Snapshot is locked — stat changes after creation have no effect
        b = SnapshotBuff(BuffType.DAMAGE_MULTIPLIER, value=10.0, duration=5.0)
        stats = {"dmg": 10.0}
        accessor = lambda f: stats[f]

        val1 = resolve_buff_value(b, accessor)
        stats["dmg"] = 999.0
        val2 = resolve_buff_value(b, accessor)
        assert val1 == val2 == pytest.approx(10.0)

    def test_unknown_type_raises(self):
        with pytest.raises(TypeError):
            resolve_buff_value("not_a_buff", None)  # type: ignore


class TestSnapshotFromStats:
    def test_captures_current_value(self):
        stats = {"cast_speed": 30.0}
        b = snapshot_from_stats(
            BuffType.CAST_SPEED,
            stat_accessor=lambda f: stats[f],
            stat_field="cast_speed",
            duration=5.0,
        )
        assert b.value == pytest.approx(30.0)
        assert b.mode is BuffResolutionMode.SNAPSHOT

    def test_snapshot_not_affected_by_later_change(self):
        stats = {"cast_speed": 30.0}
        b = snapshot_from_stats(
            BuffType.CAST_SPEED,
            stat_accessor=lambda f: stats[f],
            stat_field="cast_speed",
            duration=5.0,
        )
        stats["cast_speed"] = 100.0
        assert b.value == pytest.approx(30.0)
