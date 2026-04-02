"""
Build Snapshot Testing (Step 94).

Locks known-good build configurations and verifies that all outputs
(stat totals, skill damage, rotation results) remain stable.

Snapshot values were captured from a verified reference run and must
remain stable across future refactors.

Builds under test:
  - Fire Mage   — fire/spell passives, fire gear, fireball + frostbolt rotation
  - Cold Archer — cold/bow passives, attack gear, frostshot + ice_volley rotation
"""

import pytest

from app.domain.item import Affix, Item
from build.build_model import Build, BuildSkill
from build.passive_aggregator import PassiveNode
from build.rotation_engine import BuildRotation, RotationSkill


# ---------------------------------------------------------------------------
# Fire Mage build fixture
# ---------------------------------------------------------------------------

def _fire_mage_build() -> Build:
    nodes = [
        PassiveNode("n1", "Fire Mastery",    {"fire_damage_pct": 30.0}),
        PassiveNode("n2", "Spell Power",     {"spell_damage_pct": 20.0}),
        PassiveNode("n3", "Crit Training",   {"crit_chance_pct": 5.0}),
        PassiveNode("n4", "Mana Flow",       {"mana_regen_pct": 15.0}),
        PassiveNode("n5", "Elemental Surge", {"fire_damage_pct": 15.0, "spell_damage_pct": 10.0}),
    ]
    gear = [
        Item("amulet", "Ember Amulet", "Rare", affixes=[
            Affix("Fire Damage",  "fire_damage_pct",  18.0),
            Affix("Crit Chance",  "crit_chance_pct",   3.0),
        ]),
        Item("ring", "Spell Ring", "Magic", affixes=[
            Affix("Spell Power", "spell_damage_pct", 12.0),
        ]),
    ]
    skills = [
        BuildSkill("fireball",    ("fire", "spell"), 150.0),
        BuildSkill("frostbolt",   ("cold", "spell"),  50.0),
        BuildSkill("ignite_aura", ("fire",),           0.0),
    ]
    return Build.assemble(nodes, gear, skills)


def _fire_mage_rotation(build: Build):
    fireball  = next(s for s in build.skills if s.name == "fireball")
    frostbolt = next(s for s in build.skills if s.name == "frostbolt")
    rot_skills = [
        RotationSkill("fireball",  cooldown=2.0, mana_cost=30.0, priority=1,
                      base_damage=build.damage_for(fireball)),
        RotationSkill("frostbolt", cooldown=0.5, mana_cost=10.0, priority=2,
                      base_damage=build.damage_for(frostbolt)),
    ]
    return BuildRotation(rot_skills, fight_duration=60.0, max_mana=200.0,
                         mana_regen_rate=20.0, tick_size=0.05).run()


# ---------------------------------------------------------------------------
# Cold Archer build fixture
# ---------------------------------------------------------------------------

def _cold_archer_build() -> Build:
    nodes = [
        PassiveNode("a1", "Cold Mastery", {"cold_damage_pct": 25.0}),
        PassiveNode("a2", "Bow Training", {"bow_damage_pct":  20.0}),
        PassiveNode("a3", "Precision",    {"crit_chance_pct":  8.0}),
    ]
    gear = [
        Item("bow", "Frost Bow", "Rare", affixes=[
            Affix("Cold Damage", "cold_damage_pct", 15.0),
            Affix("Bow Damage",  "bow_damage_pct",  10.0),
        ]),
    ]
    skills = [
        BuildSkill("frostshot",  ("cold", "bow"), 80.0),
        BuildSkill("ice_volley", ("cold", "bow"), 40.0),
    ]
    return Build.assemble(nodes, gear, skills)


def _cold_archer_rotation(build: Build):
    frostshot  = next(s for s in build.skills if s.name == "frostshot")
    ice_volley = next(s for s in build.skills if s.name == "ice_volley")
    rot_skills = [
        RotationSkill("frostshot",  cooldown=1.5, mana_cost=20.0, priority=1,
                      base_damage=build.damage_for(frostshot)),
        RotationSkill("ice_volley", cooldown=0.3, mana_cost=5.0,  priority=2,
                      base_damage=build.damage_for(ice_volley)),
    ]
    return BuildRotation(rot_skills, fight_duration=60.0, max_mana=150.0,
                         mana_regen_rate=15.0, tick_size=0.05).run()


# ---------------------------------------------------------------------------
# Fire Mage — stat pool snapshots
# ---------------------------------------------------------------------------

class TestFireMageStatPool:
    def test_fire_damage_pct_total(self):
        build = _fire_mage_build()
        # passives: 30 + 15 = 45; gear: 18 = total 63
        assert build.stat("fire_damage_pct") == pytest.approx(63.0)

    def test_spell_damage_pct_total(self):
        build = _fire_mage_build()
        # passives: 20 + 10 = 30; gear: 12 = total 42
        assert build.stat("spell_damage_pct") == pytest.approx(42.0)

    def test_crit_chance_pct_total(self):
        build = _fire_mage_build()
        # passives: 5; gear: 3 = total 8
        assert build.stat("crit_chance_pct") == pytest.approx(8.0)

    def test_mana_regen_pct_total(self):
        build = _fire_mage_build()
        assert build.stat("mana_regen_pct") == pytest.approx(15.0)


# ---------------------------------------------------------------------------
# Fire Mage — skill damage snapshots
# ---------------------------------------------------------------------------

class TestFireMageSkillDamage:
    def test_fireball_scaled_damage(self):
        # 150 * (1 + (63+42)/100) = 150 * 2.05 = 307.5
        build = _fire_mage_build()
        fireball = next(s for s in build.skills if s.name == "fireball")
        assert build.damage_for(fireball) == pytest.approx(307.5)

    def test_frostbolt_scaled_damage(self):
        # 50 * (1 + 42/100) = 50 * 1.42 = 71.0 (only spell_damage_pct matches)
        build = _fire_mage_build()
        frostbolt = next(s for s in build.skills if s.name == "frostbolt")
        assert build.damage_for(frostbolt) == pytest.approx(71.0)

    def test_ignite_aura_zero_damage(self):
        build = _fire_mage_build()
        aura = next(s for s in build.skills if s.name == "ignite_aura")
        assert build.damage_for(aura) == pytest.approx(0.0)

    def test_skill_list_integrity(self):
        build = _fire_mage_build()
        names = [s.name for s in build.skills]
        assert "fireball"    in names
        assert "frostbolt"   in names
        assert "ignite_aura" in names


# ---------------------------------------------------------------------------
# Fire Mage — rotation snapshots
# ---------------------------------------------------------------------------

class TestFireMageRotation:
    def test_total_damage(self):
        result = _fire_mage_rotation(_fire_mage_build())
        assert result.total_damage == pytest.approx(10908.5, rel=1e-3)

    def test_total_casts(self):
        result = _fire_mage_rotation(_fire_mage_build())
        assert result.total_casts == 117

    def test_fireball_casts(self):
        result = _fire_mage_rotation(_fire_mage_build())
        assert result.casts_per_skill["fireball"] == 11

    def test_frostbolt_casts(self):
        result = _fire_mage_rotation(_fire_mage_build())
        assert result.casts_per_skill["frostbolt"] == 106

    def test_mana_floor_non_negative(self):
        result = _fire_mage_rotation(_fire_mage_build())
        assert result.mana_floor >= 0.0

    def test_damage_accounting_identity(self):
        result = _fire_mage_rotation(_fire_mage_build())
        per_skill_total = sum(result.damage_per_skill.values())
        assert result.total_damage == pytest.approx(per_skill_total)


# ---------------------------------------------------------------------------
# Cold Archer — stat pool snapshots
# ---------------------------------------------------------------------------

class TestColdArcherStatPool:
    def test_cold_damage_pct_total(self):
        build = _cold_archer_build()
        # passives: 25; gear: 15 = 40
        assert build.stat("cold_damage_pct") == pytest.approx(40.0)

    def test_bow_damage_pct_total(self):
        build = _cold_archer_build()
        # passives: 20; gear: 10 = 30
        assert build.stat("bow_damage_pct") == pytest.approx(30.0)

    def test_crit_chance_pct_total(self):
        build = _cold_archer_build()
        assert build.stat("crit_chance_pct") == pytest.approx(8.0)


# ---------------------------------------------------------------------------
# Cold Archer — skill damage snapshots
# ---------------------------------------------------------------------------

class TestColdArcherSkillDamage:
    def test_frostshot_scaled_damage(self):
        # 80 * (1 + (40+30)/100) = 80 * 1.70 = 136.0
        build = _cold_archer_build()
        frostshot = next(s for s in build.skills if s.name == "frostshot")
        assert build.damage_for(frostshot) == pytest.approx(136.0)

    def test_ice_volley_scaled_damage(self):
        # 40 * (1 + (40+30)/100) = 40 * 1.70 = 68.0
        build = _cold_archer_build()
        ice_volley = next(s for s in build.skills if s.name == "ice_volley")
        assert build.damage_for(ice_volley) == pytest.approx(68.0)
