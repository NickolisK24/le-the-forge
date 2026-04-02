"""
Build Regression Anchors (Step 95).

Locks known-good build-level outputs as permanent regression anchors.
Any future change that alters these values must be intentional and this
file must be updated.

Values were captured from verified reference runs. Tolerances are tight
(rel=1e-3) for numerical outputs; exact equality for integer counts.

Builds covered:
  - Fire Mage         (regression on stat totals, skill damage, rotation)
  - Cold Archer       (regression on stat totals and skill damage)
  - Poison Necromancer(regression on 3-skill rotation with mana pressure)

Also covers:
  - aggregate correctness: passive + gear stat totals
  - scale_skill formula anchor: base * (1 + total_bonus / 100)
  - routing anchor: known stat keys assigned to expected ModifierLayer
"""

import pytest

from app.domain.item import Affix, Item
from build.build_model import Build, BuildSkill
from build.gear_aggregator import aggregate_gear
from build.global_modifiers import ModifierLayer, route_modifier
from build.passive_aggregator import PassiveNode, aggregate_passives
from build.rotation_engine import BuildRotation, RotationSkill
from build.skill_scaling import scale_skill


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _node(nid: str, **stats) -> PassiveNode:
    return PassiveNode(nid, f"Node {nid}", stats)

def _item(slot: str, **kv) -> Item:
    return Item(slot, f"Item {slot}", "Magic",
                affixes=[Affix(k, k, v) for k, v in kv.items()])

def _bskill(name, tags, damage) -> BuildSkill:
    return BuildSkill(name, tuple(tags), damage)

def _rskill(name, cd, cost, pri, damage) -> RotationSkill:
    return RotationSkill(name, cd, cost, pri, damage)


# ---------------------------------------------------------------------------
# Passive aggregator formula
# ---------------------------------------------------------------------------

class TestPassiveAggregatorRegression:
    def test_five_nodes_fire_total(self):
        nodes = [_node(f"n{i}", fire_damage_pct=10.0) for i in range(5)]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"] == pytest.approx(50.0)

    def test_mixed_nodes_totals(self):
        nodes = [
            _node("n1", fire_damage_pct=20.0, spell_damage_pct=10.0),
            _node("n2", fire_damage_pct=15.0, crit_chance_pct=5.0),
        ]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"]  == pytest.approx(35.0)
        assert result["spell_damage_pct"] == pytest.approx(10.0)
        assert result["crit_chance_pct"]  == pytest.approx(5.0)


# ---------------------------------------------------------------------------
# Gear aggregator formula
# ---------------------------------------------------------------------------

class TestGearAggregatorRegression:
    def test_two_items_same_stat(self):
        items = [_item("ring", fire_damage_pct=12.0), _item("amulet", fire_damage_pct=8.0)]
        result = aggregate_gear(items)
        assert result["fire_damage_pct"] == pytest.approx(20.0)


# ---------------------------------------------------------------------------
# Skill scaling formula anchor
# ---------------------------------------------------------------------------

class TestSkillScalingRegression:
    def test_100_base_50pct_bonus_gives_150(self):
        assert scale_skill(100.0, ["fire"], {"fire_damage_pct": 50.0}) == pytest.approx(150.0)

    def test_200_base_105pct_bonus_gives_410(self):
        assert scale_skill(200.0, ["fire", "spell"],
                           {"fire_damage_pct": 60.0, "spell_damage_pct": 45.0}) == pytest.approx(410.0)


# ---------------------------------------------------------------------------
# Modifier routing regression
# ---------------------------------------------------------------------------

class TestModifierRoutingRegression:
    def test_fire_damage_routes_to_increased(self):
        assert route_modifier("fire_damage_pct") == ModifierLayer.DAMAGE_INCREASED

    def test_crit_chance_routes_to_crit(self):
        assert route_modifier("crit_chance_pct") == ModifierLayer.CRIT

    def test_armor_flat_routes_to_defense(self):
        assert route_modifier("armor_flat") == ModifierLayer.DEFENSE

    def test_mana_regen_routes_to_resource(self):
        assert route_modifier("mana_regen_flat") == ModifierLayer.RESOURCE

    def test_ailment_damage_routes_to_ailment(self):
        assert route_modifier("ailment_damage_pct") == ModifierLayer.AILMENT

    def test_cast_speed_routes_to_speed(self):
        assert route_modifier("cast_speed_pct") == ModifierLayer.SPEED


# ---------------------------------------------------------------------------
# Fire Mage regression
# ---------------------------------------------------------------------------

def _fire_mage() -> Build:
    nodes = [
        PassiveNode("n1", "Fire Mastery",    {"fire_damage_pct": 30.0}),
        PassiveNode("n2", "Spell Power",     {"spell_damage_pct": 20.0}),
        PassiveNode("n3", "Crit Training",   {"crit_chance_pct": 5.0}),
        PassiveNode("n4", "Mana Flow",       {"mana_regen_pct": 15.0}),
        PassiveNode("n5", "Elemental Surge", {"fire_damage_pct": 15.0, "spell_damage_pct": 10.0}),
    ]
    gear = [
        Item("amulet", "Ember Amulet", "Rare", affixes=[
            Affix("Fire",  "fire_damage_pct",  18.0),
            Affix("Crit",  "crit_chance_pct",   3.0),
        ]),
        Item("ring", "Spell Ring", "Magic", affixes=[
            Affix("Spell", "spell_damage_pct", 12.0),
        ]),
    ]
    skills = [
        _bskill("fireball",    ["fire", "spell"], 150.0),
        _bskill("frostbolt",   ["cold", "spell"],  50.0),
        _bskill("ignite_aura", ["fire"],             0.0),
    ]
    return Build.assemble(nodes, gear, skills)


class TestFireMageRegression:
    def test_fire_damage_pct_63(self):
        assert _fire_mage().stat("fire_damage_pct") == pytest.approx(63.0)

    def test_spell_damage_pct_42(self):
        assert _fire_mage().stat("spell_damage_pct") == pytest.approx(42.0)

    def test_crit_chance_pct_8(self):
        assert _fire_mage().stat("crit_chance_pct") == pytest.approx(8.0)

    def test_fireball_damage_307_5(self):
        build = _fire_mage()
        fb = next(s for s in build.skills if s.name == "fireball")
        assert build.damage_for(fb) == pytest.approx(307.5)

    def test_frostbolt_damage_71(self):
        build = _fire_mage()
        fb = next(s for s in build.skills if s.name == "frostbolt")
        assert build.damage_for(fb) == pytest.approx(71.0)

    def test_rotation_total_damage(self):
        build = _fire_mage()
        fb = next(s for s in build.skills if s.name == "fireball")
        ft = next(s for s in build.skills if s.name == "frostbolt")
        result = BuildRotation([
            _rskill("fireball",  2.0, 30.0, 1, build.damage_for(fb)),
            _rskill("frostbolt", 0.5, 10.0, 2, build.damage_for(ft)),
        ], fight_duration=60.0, max_mana=200.0, mana_regen_rate=20.0, tick_size=0.05).run()
        assert result.total_damage     == pytest.approx(10908.5, rel=1e-3)
        assert result.total_casts      == 117
        assert result.casts_per_skill["fireball"]  == 11
        assert result.casts_per_skill["frostbolt"] == 106


# ---------------------------------------------------------------------------
# Cold Archer regression
# ---------------------------------------------------------------------------

def _cold_archer() -> Build:
    nodes = [
        PassiveNode("a1", "Cold Mastery", {"cold_damage_pct": 25.0}),
        PassiveNode("a2", "Bow Training", {"bow_damage_pct":  20.0}),
        PassiveNode("a3", "Precision",    {"crit_chance_pct":  8.0}),
    ]
    gear = [Item("bow", "Frost Bow", "Rare", affixes=[
        Affix("Cold", "cold_damage_pct", 15.0),
        Affix("Bow",  "bow_damage_pct",  10.0),
    ])]
    skills = [
        _bskill("frostshot",  ["cold", "bow"], 80.0),
        _bskill("ice_volley", ["cold", "bow"], 40.0),
    ]
    return Build.assemble(nodes, gear, skills)


class TestColdArcherRegression:
    def test_cold_damage_pct_40(self):
        assert _cold_archer().stat("cold_damage_pct") == pytest.approx(40.0)

    def test_bow_damage_pct_30(self):
        assert _cold_archer().stat("bow_damage_pct") == pytest.approx(30.0)

    def test_frostshot_damage_136(self):
        build = _cold_archer()
        fs = next(s for s in build.skills if s.name == "frostshot")
        assert build.damage_for(fs) == pytest.approx(136.0)

    def test_ice_volley_damage_68(self):
        build = _cold_archer()
        iv = next(s for s in build.skills if s.name == "ice_volley")
        assert build.damage_for(iv) == pytest.approx(68.0)


# ---------------------------------------------------------------------------
# Poison Necromancer regression (3-skill rotation, mana pressure)
# ---------------------------------------------------------------------------

def _necromancer() -> Build:
    nodes = [
        PassiveNode("p1", "Death Touch",    {"necrotic_damage_pct": 35.0}),
        PassiveNode("p2", "Poison Mastery", {"poison_damage_pct": 25.0, "dot_damage_pct": 10.0}),
        PassiveNode("p3", "Minion Might",   {"minion_damage_pct": 20.0}),
        PassiveNode("p4", "Life Drain",     {"leech_pct": 5.0, "spell_damage_pct": 15.0}),
    ]
    gear = [
        Item("staff", "Plague Staff", "Rare", affixes=[
            Affix("Necrotic", "necrotic_damage_pct", 20.0),
            Affix("Poison",   "poison_damage_pct",   15.0),
        ]),
        Item("ring", "Decay Ring", "Magic", affixes=[
            Affix("Spell",  "spell_damage_pct",  8.0),
            Affix("Poison", "poison_damage_pct", 10.0),
        ]),
    ]
    skills = [
        _bskill("plague_bolt", ["necrotic", "spell"], 120.0),
        _bskill("poison_nova", ["poison"],              80.0),
        _bskill("bone_spike",  ["physical"],            60.0),
    ]
    return Build.assemble(nodes, gear, skills)


class TestNecromancerRegression:
    def test_necrotic_damage_pct_55(self):
        assert _necromancer().stat("necrotic_damage_pct") == pytest.approx(55.0)

    def test_poison_damage_pct_50(self):
        assert _necromancer().stat("poison_damage_pct") == pytest.approx(50.0)

    def test_spell_damage_pct_23(self):
        assert _necromancer().stat("spell_damage_pct") == pytest.approx(23.0)

    def test_plague_bolt_damage_213_6(self):
        build = _necromancer()
        pb = next(s for s in build.skills if s.name == "plague_bolt")
        # 120 * (1 + (55+23)/100) = 120 * 1.78 = 213.6
        assert build.damage_for(pb) == pytest.approx(213.6)

    def test_poison_nova_damage_120(self):
        build = _necromancer()
        pn = next(s for s in build.skills if s.name == "poison_nova")
        # 80 * (1 + 50/100) = 80 * 1.5 = 120.0
        assert build.damage_for(pn) == pytest.approx(120.0)

    def test_bone_spike_no_scaling(self):
        # physical tag, no physical_damage_pct in pool → no scaling
        build = _necromancer()
        bs = next(s for s in build.skills if s.name == "bone_spike")
        assert build.damage_for(bs) == pytest.approx(60.0)

    def test_rotation_total_damage(self):
        build = _necromancer()
        pb = next(s for s in build.skills if s.name == "plague_bolt")
        pn = next(s for s in build.skills if s.name == "poison_nova")
        bs = next(s for s in build.skills if s.name == "bone_spike")
        result = BuildRotation([
            _rskill("plague_bolt", 1.5, 25.0, 1, build.damage_for(pb)),
            _rskill("poison_nova", 3.0, 40.0, 2, build.damage_for(pn)),
            _rskill("bone_spike",  0.5, 10.0, 3, build.damage_for(bs)),
        ], fight_duration=60.0, max_mana=250.0, mana_regen_rate=25.0, tick_size=0.05).run()
        assert result.total_damage               == pytest.approx(11827.2, rel=1e-3)
        assert result.total_casts                == 125
        assert result.casts_per_skill["plague_bolt"] == 27
        assert result.casts_per_skill["poison_nova"] == 3
        assert result.casts_per_skill["bone_spike"]  == 95
        assert result.mana_floor                 >= 0.0
