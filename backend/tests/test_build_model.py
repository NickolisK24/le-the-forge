"""
Tests for build_model (Step 92).

Validates Build assembly from passive nodes, gear, and skills.
"""

import pytest

from app.domain.item import Affix, Item
from build.build_model import Build, BuildSkill
from build.passive_aggregator import PassiveNode


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node(node_id: str, **stats) -> PassiveNode:
    return PassiveNode(node_id, f"Node {node_id}", stats)


def _item(slot: str, **stat_values) -> Item:
    affixes = [Affix(name=k, stat_key=k, value=v) for k, v in stat_values.items()]
    return Item(slot=slot, item_name=f"Test {slot}", rarity="Magic", affixes=affixes)


def _skill(name: str, tags: tuple, base_damage: float) -> BuildSkill:
    return BuildSkill(name=name, tags=tags, base_damage=base_damage)


# ---------------------------------------------------------------------------
# BuildSkill
# ---------------------------------------------------------------------------

class TestBuildSkill:
    def test_basic_construction(self):
        s = BuildSkill("fireball", ("fire", "spell"), 100.0)
        assert s.name == "fireball"
        assert s.tags == ("fire", "spell")
        assert s.base_damage == pytest.approx(100.0)

    def test_negative_base_damage_raises(self):
        with pytest.raises(ValueError):
            BuildSkill("bad", ("fire",), -1.0)

    def test_zero_base_damage_ok(self):
        s = BuildSkill("dot_skill", ("fire",), 0.0)
        assert s.base_damage == pytest.approx(0.0)

    def test_empty_tags_ok(self):
        s = BuildSkill("basic", (), 50.0)
        assert s.tags == ()


# ---------------------------------------------------------------------------
# Build.assemble — stat merging
# ---------------------------------------------------------------------------

class TestBuildAssembly:
    def test_empty_everything(self):
        build = Build.assemble([], [], [])
        assert build.stat_pool == {}
        assert build.skills == []

    def test_passives_only(self):
        nodes = [_node("n1", fire_damage_pct=10.0)]
        build = Build.assemble(nodes, [], [])
        assert build.stat_pool["fire_damage_pct"] == pytest.approx(10.0)

    def test_gear_only(self):
        gear = [_item("ring", crit_chance_pct=5.0)]
        build = Build.assemble([], gear, [])
        assert build.stat_pool["crit_chance_pct"] == pytest.approx(5.0)

    def test_passive_and_gear_same_key_stack(self):
        nodes = [_node("n1", fire_damage_pct=10.0)]
        gear  = [_item("ring", fire_damage_pct=8.0)]
        build = Build.assemble(nodes, gear, [])
        assert build.stat_pool["fire_damage_pct"] == pytest.approx(18.0)

    def test_passive_and_gear_different_keys_merged(self):
        nodes = [_node("n1", spell_damage_pct=15.0)]
        gear  = [_item("ring", crit_chance_pct=5.0)]
        build = Build.assemble(nodes, gear, [])
        assert build.stat_pool["spell_damage_pct"] == pytest.approx(15.0)
        assert build.stat_pool["crit_chance_pct"]  == pytest.approx(5.0)

    def test_skills_attached(self):
        skills = [_skill("fireball", ("fire", "spell"), 100.0)]
        build  = Build.assemble([], [], skills)
        assert len(build.skills) == 1
        assert build.skills[0].name == "fireball"

    def test_multiple_passives_and_gear(self):
        nodes = [
            _node("n1", fire_damage_pct=10.0, spell_damage_pct=5.0),
            _node("n2", fire_damage_pct=8.0),
        ]
        gear = [
            _item("amulet", fire_damage_pct=6.0, crit_chance_pct=3.0),
            _item("ring",   spell_damage_pct=4.0),
        ]
        build = Build.assemble(nodes, gear, [])
        assert build.stat_pool["fire_damage_pct"]  == pytest.approx(24.0)  # 10+8+6
        assert build.stat_pool["spell_damage_pct"] == pytest.approx(9.0)   # 5+4
        assert build.stat_pool["crit_chance_pct"]  == pytest.approx(3.0)


# ---------------------------------------------------------------------------
# Build.damage_for
# ---------------------------------------------------------------------------

class TestDamageFor:
    def test_no_stats_returns_base(self):
        build  = Build.assemble([], [], [])
        skill  = _skill("slam", ("physical",), 100.0)
        assert build.damage_for(skill) == pytest.approx(100.0)

    def test_matching_tag_scales_damage(self):
        nodes  = [_node("n1", fire_damage_pct=50.0)]
        build  = Build.assemble(nodes, [], [])
        skill  = _skill("fireball", ("fire",), 100.0)
        assert build.damage_for(skill) == pytest.approx(150.0)

    def test_non_matching_tag_no_scaling(self):
        nodes  = [_node("n1", cold_damage_pct=50.0)]
        build  = Build.assemble(nodes, [], [])
        skill  = _skill("fireball", ("fire",), 100.0)
        assert build.damage_for(skill) == pytest.approx(100.0)

    def test_multiple_tags_stack(self):
        nodes = [_node("n1", fire_damage_pct=20.0, spell_damage_pct=10.0)]
        build = Build.assemble(nodes, [], [])
        skill = _skill("fireball", ("fire", "spell"), 100.0)
        assert build.damage_for(skill) == pytest.approx(130.0)

    def test_passive_plus_gear_both_contribute(self):
        nodes = [_node("n1", fire_damage_pct=20.0)]
        gear  = [_item("ring", fire_damage_pct=10.0)]
        build = Build.assemble(nodes, gear, [])
        skill = _skill("fireball", ("fire",), 100.0)
        assert build.damage_for(skill) == pytest.approx(130.0)

    def test_zero_base_damage_stays_zero(self):
        nodes = [_node("n1", fire_damage_pct=100.0)]
        build = Build.assemble(nodes, [], [])
        skill = _skill("dot", ("fire",), 0.0)
        assert build.damage_for(skill) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Build.stat helper
# ---------------------------------------------------------------------------

class TestBuildStat:
    def test_present_stat_returned(self):
        build = Build.assemble([_node("n1", fire_damage_pct=15.0)], [], [])
        assert build.stat("fire_damage_pct") == pytest.approx(15.0)

    def test_missing_stat_returns_default(self):
        build = Build.assemble([], [], [])
        assert build.stat("fire_damage_pct") == pytest.approx(0.0)
        assert build.stat("fire_damage_pct", default=5.0) == pytest.approx(5.0)
