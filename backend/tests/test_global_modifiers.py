"""
Tests for global_modifiers (Step 91).

Validates routing of stat keys to the correct ModifierLayer.
"""

import pytest

from build.global_modifiers import ModifierLayer, route_modifier, route_stat_pool


class TestRouteModifier:
    # --- Exact matches ---

    def test_damage_increased_exact(self):
        assert route_modifier("fire_damage_pct")        == ModifierLayer.DAMAGE_INCREASED
        assert route_modifier("cold_damage_pct")        == ModifierLayer.DAMAGE_INCREASED
        assert route_modifier("spell_damage_pct")       == ModifierLayer.DAMAGE_INCREASED
        assert route_modifier("physical_damage_pct")    == ModifierLayer.DAMAGE_INCREASED

    def test_damage_more_exact(self):
        assert route_modifier("more_damage_pct") == ModifierLayer.DAMAGE_MORE

    def test_crit_exact(self):
        assert route_modifier("crit_chance_pct")                == ModifierLayer.CRIT
        assert route_modifier("crit_multiplier_pct")            == ModifierLayer.CRIT
        assert route_modifier("crit_chance_bonus_pct")          == ModifierLayer.CRIT
        assert route_modifier("increased_crit_multiplier_pct")  == ModifierLayer.CRIT

    def test_speed_exact(self):
        assert route_modifier("cast_speed_pct")      == ModifierLayer.SPEED
        assert route_modifier("attack_speed_pct")    == ModifierLayer.SPEED
        assert route_modifier("movement_speed_pct")  == ModifierLayer.SPEED

    def test_defense_resistance_exact(self):
        assert route_modifier("fire_resistance_pct")      == ModifierLayer.DEFENSE
        assert route_modifier("cold_resistance_pct")      == ModifierLayer.DEFENSE
        assert route_modifier("all_resistance_pct")       == ModifierLayer.DEFENSE

    def test_defense_armor_and_health(self):
        assert route_modifier("armor_flat")       == ModifierLayer.DEFENSE
        assert route_modifier("armor_pct")        == ModifierLayer.DEFENSE
        assert route_modifier("max_health_flat")  == ModifierLayer.DEFENSE
        assert route_modifier("max_health_pct")   == ModifierLayer.DEFENSE
        assert route_modifier("dodge_rating")     == ModifierLayer.DEFENSE
        assert route_modifier("block_chance_pct") == ModifierLayer.DEFENSE

    def test_resource_exact(self):
        assert route_modifier("max_mana_flat")    == ModifierLayer.RESOURCE
        assert route_modifier("mana_regen_flat")  == ModifierLayer.RESOURCE
        assert route_modifier("mana_regen_pct")   == ModifierLayer.RESOURCE
        assert route_modifier("health_regen_flat") == ModifierLayer.RESOURCE
        assert route_modifier("leech_pct")        == ModifierLayer.RESOURCE

    def test_ailment_exact(self):
        assert route_modifier("ailment_damage_pct")    == ModifierLayer.AILMENT
        assert route_modifier("ailment_duration_pct")  == ModifierLayer.AILMENT
        assert route_modifier("bleed_damage_pct")      == ModifierLayer.AILMENT
        assert route_modifier("poison_damage_pct")     == ModifierLayer.AILMENT
        assert route_modifier("ignite_duration_pct")   == ModifierLayer.AILMENT

    # --- Suffix fallback ---

    def test_unknown_damage_pct_suffix_routes_to_increased(self):
        assert route_modifier("chaos_damage_pct")   == ModifierLayer.DAMAGE_INCREASED
        assert route_modifier("minion_damage_pct")  == ModifierLayer.DAMAGE_INCREASED

    def test_unknown_resistance_suffix_routes_to_defense(self):
        assert route_modifier("chaos_resistance_pct") == ModifierLayer.DEFENSE

    def test_unknown_speed_suffix_routes_to_speed(self):
        assert route_modifier("minion_speed_pct") == ModifierLayer.SPEED

    def test_unknown_duration_suffix_routes_to_ailment(self):
        assert route_modifier("custom_duration_pct") == ModifierLayer.AILMENT

    # --- Unknown key ---

    def test_unknown_key_routes_to_utility(self):
        assert route_modifier("totally_unknown_stat") == ModifierLayer.UTILITY
        assert route_modifier("xp_bonus_pct")         == ModifierLayer.UTILITY


class TestRouteStatPool:
    def test_empty_pool_returns_empty(self):
        assert route_stat_pool({}) == {}

    def test_single_stat_correct_layer(self):
        result = route_stat_pool({"fire_damage_pct": 20.0})
        assert ModifierLayer.DAMAGE_INCREASED in result
        assert result[ModifierLayer.DAMAGE_INCREASED]["fire_damage_pct"] == pytest.approx(20.0)

    def test_mixed_pool_split_into_layers(self):
        pool = {
            "fire_damage_pct":   20.0,
            "crit_chance_pct":   5.0,
            "armor_flat":        100.0,
            "mana_regen_flat":   10.0,
            "ailment_damage_pct": 30.0,
        }
        result = route_stat_pool(pool)

        assert result[ModifierLayer.DAMAGE_INCREASED]["fire_damage_pct"] == pytest.approx(20.0)
        assert result[ModifierLayer.CRIT]["crit_chance_pct"]             == pytest.approx(5.0)
        assert result[ModifierLayer.DEFENSE]["armor_flat"]               == pytest.approx(100.0)
        assert result[ModifierLayer.RESOURCE]["mana_regen_flat"]         == pytest.approx(10.0)
        assert result[ModifierLayer.AILMENT]["ailment_damage_pct"]       == pytest.approx(30.0)

    def test_all_stats_same_layer_no_extra_layers(self):
        pool = {"fire_damage_pct": 10.0, "cold_damage_pct": 8.0}
        result = route_stat_pool(pool)
        assert list(result.keys()) == [ModifierLayer.DAMAGE_INCREASED]

    def test_utility_layer_only_for_unknown(self):
        pool = {"completely_unknown": 1.0}
        result = route_stat_pool(pool)
        assert list(result.keys()) == [ModifierLayer.UTILITY]

    def test_values_preserved(self):
        pool = {"fire_damage_pct": 42.5, "cold_damage_pct": -3.0}
        result = route_stat_pool(pool)
        layer = result[ModifierLayer.DAMAGE_INCREASED]
        assert layer["fire_damage_pct"] == pytest.approx(42.5)
        assert layer["cold_damage_pct"] == pytest.approx(-3.0)

    def test_layers_with_no_stats_omitted(self):
        # only damage stats → no CRIT, SPEED, etc. keys
        pool = {"fire_damage_pct": 10.0}
        result = route_stat_pool(pool)
        assert ModifierLayer.CRIT    not in result
        assert ModifierLayer.SPEED   not in result
        assert ModifierLayer.DEFENSE not in result
