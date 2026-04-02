"""
E5 — Tests for BuffSystem.
"""

import pytest
from builds.buff_system import Buff, BuffSystem


class TestBuff:
    def test_permanent_buff_always_active(self):
        b = Buff("power", {}, duration=None)
        assert b.is_active(0.0) is True
        assert b.is_active(9999.0) is True

    def test_timed_buff_expires(self):
        b = Buff("frenzy", {}, duration=5.0)
        assert b.is_active(0.0)   is True
        assert b.is_active(4.99)  is True
        assert b.is_active(5.0)   is False
        assert b.is_active(10.0)  is False

    def test_zero_duration_immediately_expired(self):
        b = Buff("flash", {}, duration=0.0)
        assert b.is_active(0.0) is False

    def test_to_dict_roundtrip(self):
        b = Buff("power", {"spell_damage_pct": 25.0, "crit_chance": 0.05}, duration=10.0)
        b2 = Buff.from_dict(b.to_dict())
        assert b2.buff_id == "power"
        assert b2.duration == 10.0
        assert b2.modifiers["spell_damage_pct"] == 25.0


class TestBuffSystem:
    def test_empty_system(self):
        bs = BuffSystem()
        assert len(bs) == 0
        assert bs.aggregate_modifiers() == {}

    def test_add_buff(self):
        bs = BuffSystem()
        bs.add_buff(Buff("a", {"base_damage": 100.0}))
        assert len(bs) == 1

    def test_add_buff_replaces_same_id(self):
        bs = BuffSystem()
        bs.add_buff(Buff("a", {"base_damage": 50.0}))
        bs.add_buff(Buff("a", {"base_damage": 200.0}))
        assert len(bs) == 1
        assert bs.aggregate_modifiers()["base_damage"] == 200.0

    def test_remove_buff(self):
        bs = BuffSystem([Buff("a", {"x": 1.0}), Buff("b", {"y": 2.0})])
        bs.remove_buff("a")
        assert len(bs) == 1
        assert "x" not in bs.aggregate_modifiers()

    def test_multiple_buffs_stack(self):
        bs = BuffSystem([
            Buff("a", {"spell_damage_pct": 10.0}),
            Buff("b", {"spell_damage_pct": 20.0}),
        ])
        result = bs.aggregate_modifiers()
        assert result["spell_damage_pct"] == 30.0

    def test_expired_buffs_excluded(self):
        bs = BuffSystem([
            Buff("perm",    {"base_damage": 100.0}, duration=None),
            Buff("expired", {"base_damage": 50.0},  duration=3.0),
        ])
        at_5s = bs.aggregate_modifiers(elapsed=5.0)
        assert at_5s.get("base_damage") == 100.0  # expired buff excluded

    def test_aggregate_different_stat_keys(self):
        bs = BuffSystem([
            Buff("a", {"spell_damage_pct": 15.0, "crit_chance": 0.05}),
            Buff("b", {"crit_chance": 0.10}),
        ])
        result = bs.aggregate_modifiers()
        assert result["spell_damage_pct"] == 15.0
        assert abs(result["crit_chance"] - 0.15) < 1e-9
