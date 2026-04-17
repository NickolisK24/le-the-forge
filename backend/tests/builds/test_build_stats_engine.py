"""
E3 — Tests for BuildStatsEngine.

These tests require game data (affixes.json / classes.json) which is
loaded via the module-level fallback in game_data_loader — no Flask context needed.
"""

import pytest
from builds.build_definition  import BuildDefinition
from builds.build_stats_engine import BuildStatsEngine
from builds.gear_system        import GearItem, GearAffix
from builds.buff_system        import Buff


def _lich_build(**kwargs) -> BuildDefinition:
    defaults = dict(character_class="Acolyte", mastery="Lich")
    return BuildDefinition(**{**defaults, **kwargs})


def _sorcerer_build(**kwargs) -> BuildDefinition:
    # updated: verified in-game data — Mage base_damage now comes from the
    # selected skill, not the class. Fireball's base_damage is 110.
    defaults = dict(character_class="Mage", mastery="Sorcerer",
                    skill_id="Fireball")
    return BuildDefinition(**{**defaults, **kwargs})


class TestBaseStatsComputed:
    def test_acolyte_base_damage(self):
        eng = BuildStatsEngine()
        stats = eng.compile(_lich_build())
        assert stats.base_damage == 80.0  # Acolyte base

    def test_mage_base_damage(self):
        # updated: verified in-game data — base_damage is now sourced from
        # the skill, not the class. Fireball's base_damage is 110.
        eng = BuildStatsEngine()
        stats = eng.compile(_sorcerer_build())
        assert stats.base_damage == 110.0

    def test_base_crit_chance(self):
        eng = BuildStatsEngine()
        stats = eng.compile(_lich_build())
        assert stats.crit_chance == pytest.approx(0.05, abs=0.01)

    def test_base_health_positive(self):
        eng = BuildStatsEngine()
        stats = eng.compile(_lich_build())
        assert stats.max_health > 0


class TestModifiersApplied:
    def test_gear_spell_damage_increases_stat(self):
        eng = BuildStatsEngine()
        build_bare = _lich_build()
        build_gear = _lich_build()
        # Use the correct affix name from affixes.json
        build_gear.add_gear(GearItem("weapon", [GearAffix("Increased Spell Damage", 4)]))

        bare = eng.compile(build_bare)
        with_gear = eng.compile(build_gear)
        assert with_gear.spell_damage_pct > bare.spell_damage_pct

    def test_zero_modifier_safe(self):
        eng = BuildStatsEngine()
        build = _lich_build()
        build.add_gear(GearItem("body"))  # no affixes
        stats = eng.compile(build)
        assert stats.base_damage == 80.0

    def test_buff_modifier_applied(self):
        eng = BuildStatsEngine()
        build = _lich_build()
        build.add_buff(Buff("power", {"base_damage": 100.0}))
        stats = eng.compile(build)
        assert stats.base_damage == 180.0  # 80 base + 100 buff

    def test_multiple_gear_affixes_stack(self):
        eng = BuildStatsEngine()
        build = _lich_build()
        build.add_gear(GearItem("weapon", [GearAffix("Increased Spell Damage", 4)]))
        build.add_gear(GearItem("head",   [GearAffix("Increased Spell Damage", 4)]))
        stats = eng.compile(build)
        single = BuildStatsEngine().compile(
            BuildDefinition("Acolyte", "Lich",
                gear=[GearItem("weapon", [GearAffix("Increased Spell Damage", 4)])])
        )
        assert stats.spell_damage_pct > single.spell_damage_pct


class TestStatBoundsValidated:
    def test_crit_chance_between_0_and_1(self):
        eng = BuildStatsEngine()
        stats = eng.compile(_lich_build())
        assert 0.0 <= stats.crit_chance <= 1.0

    def test_attack_speed_positive(self):
        eng = BuildStatsEngine()
        stats = eng.compile(_lich_build())
        assert stats.attack_speed > 0


class TestToEncounterParams:
    def test_returns_required_keys(self):
        eng = BuildStatsEngine()
        params = eng.to_encounter_params(_lich_build())
        assert "base_damage"     in params
        assert "crit_chance"     in params
        assert "crit_multiplier" in params

    def test_base_damage_at_least_raw_base(self):
        eng = BuildStatsEngine()
        build = _lich_build()
        stats  = eng.compile(build)
        params = eng.to_encounter_params(build)
        # Effective damage >= raw because percent pools are additive multipliers
        assert params["base_damage"] >= stats.base_damage
