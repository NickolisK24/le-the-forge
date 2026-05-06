"""
Tests for the passive stat resolver service.
"""

import pytest
from app.models import PassiveNode
from app.services.passive_stat_resolver import resolve_passive_stats, _parse_value


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_nodes(db):
    """Seed a handful of passive nodes with known stats for testing."""
    nodes = [
        PassiveNode(
            id="ac_0", raw_node_id=0, character_class="Acolyte",
            name="Bone Aura", node_type="core", x=0, y=0,
            stats=[
                {"key": "Armor", "value": "+20"},
                {"key": "Minion Armor", "value": "+20"},
            ],
        ),
        PassiveNode(
            id="ac_1", raw_node_id=1, character_class="Acolyte",
            name="Forbidden Knowledge", node_type="core", x=1, y=0,
            stats=[
                {"key": "Intelligence", "value": "+1"},
                {"key": "Necrotic Resistance", "value": "+5%"},
            ],
        ),
        PassiveNode(
            id="ac_2", raw_node_id=2, character_class="Acolyte",
            name="Blood Aura", node_type="notable", x=2, y=0,
            stats=[
                {"key": "Increased Damage", "value": "6%"},
                {"key": "Increased Minion Damage", "value": "6%"},
            ],
        ),
        PassiveNode(
            id="ac_5", raw_node_id=5, character_class="Acolyte",
            name="Ethereal Revenant", node_type="keystone", x=5, y=0,
            stats=[
                {"key": "Summons A Revenant", "value": ""},
                {"key": "More Revenant Damage", "value": "50%"},
                {"key": "More Revenant Health", "value": "50%"},
            ],
        ),
        PassiveNode(
            id="ac_7", raw_node_id=7, character_class="Acolyte",
            name="Unnatural Preservation", node_type="core", x=7, y=0,
            stats=[
                {"key": "Ward Retention", "value": "+8%"},
                {"key": "Necrotic Resistance", "value": "+4%"},
                {"key": "Poison Resistance", "value": "+4%"},
            ],
        ),
        PassiveNode(
            id="ac_10", raw_node_id=10, character_class="Acolyte",
            name="Dark Rituals", node_type="notable", x=10, y=0,
            stats=[
                {"key": "All Attributes", "value": "+2"},
            ],
        ),
        PassiveNode(
            id="ac_11", raw_node_id=11, character_class="Acolyte",
            name="Negative Armor Node", node_type="keystone", x=11, y=0,
            stats=[
                {"key": "Armor", "value": "-50"},
                {"key": "Health", "value": "+200"},
            ],
        ),
        # Node with empty stats list
        PassiveNode(
            id="ac_99", raw_node_id=99, character_class="Acolyte",
            name="Empty Node", node_type="mastery_gate", x=99, y=0,
            stats=[],
        ),
    ]
    for n in nodes:
        db.session.add(n)
    db.session.commit()
    return nodes


# ---------------------------------------------------------------------------
# Unit tests for _parse_value
# ---------------------------------------------------------------------------

class TestParseValue:
    def test_positive_flat(self):
        assert _parse_value("+20") == 20.0

    def test_negative_flat(self):
        assert _parse_value("-50") == -50.0

    def test_percentage(self):
        assert _parse_value("6%") == 6.0

    def test_positive_percentage(self):
        assert _parse_value("+5%") == 5.0

    def test_plain_integer(self):
        assert _parse_value("13") == 13.0

    def test_float_value(self):
        assert _parse_value("+2.5") == 2.5

    def test_empty_string(self):
        assert _parse_value("") is None

    def test_non_numeric(self):
        assert _parse_value("Summons A Revenant") is None

    def test_whitespace(self):
        assert _parse_value("  +10  ") == 10.0


# ---------------------------------------------------------------------------
# Integration tests for resolve_passive_stats
# ---------------------------------------------------------------------------

class TestAdditiveStatsSum:
    """Additive stats from multiple nodes should sum correctly."""

    def test_single_node(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["ac_0"])
            assert result["additive"]["armour"] == 20.0

    def test_multiple_nodes_sum(self, app, seed_nodes):
        """ac_0 has Armor +20, ac_11 has Armor -50 → net -30."""
        with app.app_context():
            result = resolve_passive_stats(["ac_0", "ac_11"])
            assert result["additive"]["armour"] == -30.0
            assert result["additive"]["max_health"] == 200.0

    def test_resistance_stacking(self, app, seed_nodes):
        """ac_1 has Necrotic Res +5%, ac_7 has Necrotic Res +4% → 9."""
        with app.app_context():
            result = resolve_passive_stats(["ac_1", "ac_7"])
            assert result["additive"]["necrotic_res"] == 9.0


class TestPercentageValuesParsed:
    """Percentage values like '6%' should be parsed as floats."""

    def test_percentage_damage(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["ac_2"])
            # "Increased Damage" maps to physical_damage_pct
            assert result["additive"]["physical_damage_pct"] == 6.0
            assert result["additive"]["minion_damage_pct"] == 6.0

    def test_ward_retention_percentage(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["ac_7"])
            assert result["additive"]["ward_retention_pct"] == 8.0


class TestNoScalingGoToSpecialEffects:
    """Stats that don't map to BuildStats fields go to special_effects."""

    def test_unmapped_stats(self, app, seed_nodes):
        """ac_5 has 'Summons A Revenant' (empty value) and 'More Revenant Damage'."""
        with app.app_context():
            result = resolve_passive_stats(["ac_5"])
            effects = result["special_effects"]
            keys = [e["key"] for e in effects]
            assert "Summons A Revenant" in keys
            assert "More Revenant Damage" in keys
            assert "More Revenant Health" in keys

    def test_minion_armor_now_mapped(self, app, seed_nodes):
        """Pass 2 added 'Minion Armor' → minion_armour; ac_0 exercises the
        mapping so this regression-tests that the alias lands on the
        additive pool instead of leaking into special_effects."""
        with app.app_context():
            result = resolve_passive_stats(["ac_0"])
            assert result["additive"]["minion_armour"] == 20.0
            effect_keys = [e["key"] for e in result["special_effects"]]
            assert "Minion Armor" not in effect_keys

    def test_special_effects_include_node_info(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["ac_5"])
            for effect in result["special_effects"]:
                assert effect["node_id"] == "ac_5"
                assert effect["node_name"] == "Ethereal Revenant"


class TestEmptyNodeList:
    """Empty input should return empty dicts."""

    def test_empty_list(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats([])
            assert result == {"additive": {}, "special_effects": []}

    def test_node_with_empty_stats(self, app, seed_nodes):
        """ac_99 has an empty stats list."""
        with app.app_context():
            result = resolve_passive_stats(["ac_99"])
            assert result["additive"] == {}
            assert result["special_effects"] == []


class TestUnknownNodeIds:
    """Unknown node IDs should be skipped gracefully."""

    def test_all_unknown(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["xx_999", "yy_888"])
            assert result["additive"] == {}
            assert result["special_effects"] == []

    def test_mix_known_unknown(self, app, seed_nodes):
        """Known nodes should still resolve; unknowns are skipped."""
        with app.app_context():
            result = resolve_passive_stats(["ac_0", "xx_999"])
            assert result["additive"]["armour"] == 20.0


class TestAllAttributes:
    """'All Attributes' should fan out to all 5 attribute fields."""

    def test_all_attributes_expansion(self, app, seed_nodes):
        with app.app_context():
            result = resolve_passive_stats(["ac_10"])
            for attr in ("strength", "intelligence", "dexterity", "vitality", "attunement"):
                assert result["additive"][attr] == 2.0


# ---------------------------------------------------------------------------
# Expanded STAT_KEY_MAP — new aliases and composites added to close the
# passive coverage gap identified in docs/audits/passive_node_audit.md
# (issue #156).
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_new_mapping_nodes(db):
    """Nodes whose stat keys exercise entries added in this patch."""
    from app.models import PassiveNode

    nodes = [
        PassiveNode(
            id="new_0", raw_node_id=200, character_class="Acolyte",
            name="Crit Aliases", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Critical Multiplier", "value": "+10%"},
                {"key": "Increased Critical Chance", "value": "12%"},
                {"key": "Crit Avoidance", "value": "+5%"},
            ],
        ),
        PassiveNode(
            id="new_1", raw_node_id=201, character_class="Acolyte",
            name="Defensive Aliases", node_type="core", x=0, y=0,
            stats=[
                {"key": "Increased Armor", "value": "4%"},
                {"key": "Glancing Blow Chance", "value": "3%"},
                {"key": "Ward Per Second", "value": "+5"},
            ],
        ),
        PassiveNode(
            id="new_2", raw_node_id=202, character_class="Acolyte",
            name="Flat Melee Adds", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Melee Physical Damage", "value": "+2"},
                {"key": "Melee Lightning Damage", "value": "+1"},
                {"key": "Melee Cold Damage", "value": "+1"},
                {"key": "Melee Fire Damage", "value": "+1"},
            ],
        ),
        PassiveNode(
            id="new_3", raw_node_id=203, character_class="Acolyte",
            name="Utility / Speed Aliases", node_type="core", x=0, y=0,
            stats=[
                {"key": "Increased Movespeed", "value": "1%"},
                {"key": "Movespeed", "value": "+1%"},
                {"key": "Increased Cooldown Recovery Speed", "value": "5%"},
                {"key": "Increased Melee Attack Speed", "value": "3%"},
                {"key": "Increased Area For Area Skills", "value": "4%"},
            ],
        ),
        PassiveNode(
            id="new_4", raw_node_id=204, character_class="Acolyte",
            name="Leech + Healing Aliases", node_type="core", x=0, y=0,
            stats=[
                {"key": "Health Leech", "value": "+0.25%"},
                {"key": "Melee Damage Leeched as Health", "value": "0.5%"},
                {"key": "Increased Healing Effectiveness", "value": "5%"},
                {"key": "Increased Healing", "value": "10%"},
            ],
        ),
        PassiveNode(
            id="new_5", raw_node_id=205, character_class="Acolyte",
            name="All Resistances", node_type="notable", x=0, y=0,
            stats=[
                {"key": "All Resistances", "value": "+2%"},
            ],
        ),
        PassiveNode(
            id="new_6", raw_node_id=206, character_class="Acolyte",
            name="Minion Conditional Unmapped", node_type="core", x=0, y=0,
            stats=[
                # These remain intentionally unmapped — conditional
                # mechanics, ability-proc triggers, and equipment flags
                # with no clean BuildStats analogue. They should route
                # to special_effects instead of polluting additive totals.
                {"key": "Freeze Rate Multiplier", "value": "+20%"},
                {"key": "Can Equip Swords in Offhand", "value": ""},
                {"key": "Attack And Cast Speed While Dual Wielding", "value": "5%"},
            ],
        ),
        PassiveNode(
            id="new_7", raw_node_id=207, character_class="Acolyte",
            name="Throwing + Shock", node_type="core", x=0, y=0,
            stats=[
                {"key": "Throwing Attack Damage", "value": "6%"},
                {"key": "Increased Throwing Attack Damage", "value": "7%"},
                {"key": "Throwing Physical Damage", "value": "+2"},
                {"key": "Electrify Chance", "value": "+7%"},
            ],
        ),
    ]
    for n in nodes:
        db.session.add(n)
    db.session.commit()
    return nodes


class TestExpandedMappings:
    """Every key added in this patch lands on its BuildStats field."""

    def test_crit_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_0"])
            assert result["additive"]["crit_multiplier_pct"] == 10.0
            assert result["additive"]["crit_chance_pct"] == 12.0
            assert result["additive"]["crit_avoidance"] == 5.0

    def test_defensive_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_1"])
            assert result["additive"]["armour_pct"] == 4.0
            assert result["additive"]["glancing_blow"] == 3.0
            assert result["additive"]["ward_regen"] == 5.0

    def test_flat_melee_adds(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_2"])
            assert result["additive"]["added_melee_physical"] == 2.0
            assert result["additive"]["added_melee_lightning"] == 1.0
            assert result["additive"]["added_melee_cold"] == 1.0
            assert result["additive"]["added_melee_fire"] == 1.0

    def test_movement_and_area_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_3"])
            # Both Movespeed and Increased Movespeed stack onto movement_speed.
            assert result["additive"]["movement_speed"] == 2.0
            assert result["additive"]["cooldown_recovery_speed"] == 5.0
            assert result["additive"]["attack_speed_pct"] == 3.0
            assert result["additive"]["area_pct"] == 4.0

    def test_leech_and_healing_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_4"])
            # Both leech aliases stack on the same field.
            assert result["additive"]["leech"] == pytest.approx(0.75)
            # Both healing aliases stack too.
            assert result["additive"]["healing_effectiveness_pct"] == 15.0

    def test_all_resistances_composite(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_5"])
            for res in ("fire_res", "cold_res", "lightning_res",
                        "void_res", "necrotic_res", "poison_res",
                        "physical_res"):
                assert result["additive"][res] == 2.0

    def test_unmapped_keys_still_route_to_special_effects(
        self, app, seed_new_mapping_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["new_6"])
            assert result["additive"] == {}
            keys = {e["key"] for e in result["special_effects"]}
            assert "Freeze Rate Multiplier" in keys
            assert "Can Equip Swords in Offhand" in keys
            assert "Attack And Cast Speed While Dual Wielding" in keys

    def test_throwing_and_shock_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_7"])
            # Two throwing damage % aliases stack on throwing_damage_pct.
            assert result["additive"]["throwing_damage_pct"] == 13.0
            assert result["additive"]["added_throw_physical"] == 2.0
            # Electrify is the legacy in-game name for Shock.
            assert result["additive"]["shock_chance_pct"] == 7.0


# ---------------------------------------------------------------------------
# Pass 2 — meta-build priority + high-frequency alias sweep.
# Groups mirror the categories used inside STAT_KEY_MAP so the intent of
# each new alias is easy to inspect in the test report.
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_pass2_nodes(db):
    """Nodes whose stat keys exercise the pass-2 STAT_KEY_MAP additions."""
    from app.models import PassiveNode

    nodes = [
        # Resource regen / pool — new pct fields.
        PassiveNode(
            id="p2_resource", raw_node_id=300, character_class="Acolyte",
            name="Resource Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Increased Mana Regen", "value": "12%"},
                {"key": "Increased Mana Regeneration", "value": "3%"},
                {"key": "Increased Health Regen", "value": "+5%"},
                {"key": "Increased Health Regeneration", "value": "+2%"},
                {"key": "Increased Mana", "value": "8%"},
                {"key": "Increased Leech Rate", "value": "+10%"},
            ],
        ),
        # Defense — pct dodge rating + ward decay threshold.
        PassiveNode(
            id="p2_defense", raw_node_id=301, character_class="Rogue",
            name="Defense Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Increased Dodge Rating", "value": "6%"},
                {"key": "Ward Decay Threshold", "value": "+40"},
                {"key": "Ward per Second", "value": "+3"},
                {"key": "Ward per second", "value": "+2"},
            ],
        ),
        # Minion specialisation fields.
        PassiveNode(
            id="p2_minion", raw_node_id=302, character_class="Acolyte",
            name="Minion Pass", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Increased Minion Cold Damage", "value": "7%"},
                {"key": "Minion Cold Damage", "value": "3%"},
                {"key": "Increased Minion Necrotic Damage", "value": "5%"},
                {"key": "Minion Necrotic Damage", "value": "4%"},
                {"key": "Increased Minion Attack Speed", "value": "6%"},
                {"key": "Minion Attack Speed", "value": "2%"},
                {"key": "Increased Minion Cast Speed", "value": "5%"},
                {"key": "Minion Increased Cast Speed", "value": "3%"},
                {"key": "Minion Armor", "value": "+40"},
                {"key": "Minion Armour", "value": "+20"},
                {"key": "Minion Critical Multiplier", "value": "+15%"},
                {"key": "Increased Minion Movement Speed", "value": "4%"},
            ],
        ),
        # Damage-type aliases (no "Increased" prefix) and elemental composites.
        PassiveNode(
            id="p2_damage", raw_node_id=303, character_class="Mage",
            name="Damage Alias Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Bow Damage", "value": "5%"},
                {"key": "Melee Damage", "value": "4%"},
                {"key": "Throwing Damage", "value": "3%"},
                {"key": "Fire Damage", "value": "6%"},
                {"key": "Cold Damage", "value": "6%"},
                {"key": "Physical Damage", "value": "6%"},
                {"key": "Necrotic Damage", "value": "6%"},
                {"key": "Void Damage", "value": "6%"},
                {"key": "Elemental Damage", "value": "4%"},
                {"key": "Damage Over Time", "value": "7%"},
                {"key": "Global Damage Over Time", "value": "3%"},
                {"key": "Global Increased Lightning Damage", "value": "8%"},
                {"key": "Elemental Resistances", "value": "+3%"},
            ],
        ),
        # Type-scoped ailment / crit aliases — route to the generic chance pool.
        PassiveNode(
            id="p2_ailment", raw_node_id=304, character_class="Sentinel",
            name="Ailment Alias Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Melee Bleed Chance", "value": "+5%"},
                {"key": "Throwing Bleed Chance", "value": "+3%"},
                {"key": "Throwing Attack Bleed Chance", "value": "+2%"},
                {"key": "Melee Poison Chance", "value": "+4%"},
                {"key": "Spell Poison Chance", "value": "+2%"},
                {"key": "Melee Ignite Chance", "value": "+6%"},
                {"key": "Increased Melee Critical Strike Chance", "value": "+8%"},
                {"key": "Slow Chance", "value": "+3%"},
            ],
        ),
        # Duration aliases — every elemental/poison duration rolls up into
        # ailment_duration_pct (BuildStats does not distinguish per-ailment).
        PassiveNode(
            id="p2_duration", raw_node_id=305, character_class="Mage",
            name="Duration Alias Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Ignite Duration", "value": "10%"},
                {"key": "Chill Duration", "value": "5%"},
                {"key": "Shock Duration", "value": "5%"},
                {"key": "Electrify Duration", "value": "5%"},
                {"key": "Poison Duration", "value": "10%"},
                {"key": "Increased Poison Duration", "value": "+5%"},
                {"key": "Increased Slow Duration", "value": "+5%"},
                {"key": "Buff Duration", "value": "+5%"},
            ],
        ),
        # Attack / shred aliases.
        PassiveNode(
            id="p2_misc", raw_node_id=306, character_class="Rogue",
            name="Misc Alias Pass", node_type="core", x=0, y=0,
            stats=[
                {"key": "Melee Attack Speed", "value": "5%"},
                {"key": "Increased Bow Attack Speed", "value": "4%"},
                {"key": "Increased Throwing Attack Speed", "value": "6%"},
                {"key": "Throwing Attack Speed", "value": "2%"},
                {"key": "Throwing Armor Shred Chance", "value": "+8%"},
                {"key": "Lightning Res Shred Chance", "value": "+5%"},
                {"key": "Healing", "value": "+4%"},
                {"key": "Health Gained On Block", "value": "+5"},
                {"key": "Health Gained on Block", "value": "+3"},
            ],
        ),
    ]
    for n in nodes:
        db.session.add(n)
    db.session.commit()
    return nodes


class TestPass2ResourceMapping:
    """Resource regen / pool aliases backed by new BuildStats fields."""

    def test_mana_regen_pct_stacks(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_resource"])
            # Increased Mana Regen (12) + Increased Mana Regeneration (3)
            assert result["additive"]["mana_regen_pct"] == 15.0

    def test_health_regen_pct_stacks(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_resource"])
            assert result["additive"]["health_regen_pct"] == 7.0

    def test_mana_pct_and_leech_rate(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_resource"])
            assert result["additive"]["mana_pct"] == 8.0
            assert result["additive"]["leech_rate_pct"] == 10.0


class TestPass2DefenseMapping:
    """Dodge rating pct + ward decay threshold + case-aliased ward regen."""

    def test_dodge_rating_pct(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_defense"])
            assert result["additive"]["dodge_rating_pct"] == 6.0

    def test_ward_decay_threshold(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_defense"])
            assert result["additive"]["ward_decay_threshold"] == 40.0

    def test_ward_per_second_case_aliases_stack(self, app, seed_pass2_nodes):
        """'Ward per Second' and 'Ward per second' both collapse to ward_regen."""
        with app.app_context():
            result = resolve_passive_stats(["p2_defense"])
            assert result["additive"]["ward_regen"] == 5.0


class TestPass2MinionMapping:
    """Minion specialisation stats now have dedicated fields."""

    def test_minion_damage_types(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_minion"])
            assert result["additive"]["minion_cold_damage_pct"] == 10.0
            assert result["additive"]["minion_necrotic_damage_pct"] == 9.0

    def test_minion_speeds(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_minion"])
            assert result["additive"]["minion_attack_speed_pct"] == 8.0
            assert result["additive"]["minion_cast_speed_pct"] == 8.0
            assert result["additive"]["minion_speed_pct"] == 4.0

    def test_minion_armour_and_crit(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_minion"])
            assert result["additive"]["minion_armour"] == 60.0
            assert result["additive"]["minion_crit_multiplier_pct"] == 15.0


class TestPass2DamageAliases:
    """Plain-named damage keys ('Bow Damage' etc.) alias onto the
    existing Increased-* pools; Elemental Resistances (plural) fans
    out via the _elemental_res composite handler."""

    def test_damage_type_aliases(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_damage"])
            assert result["additive"]["bow_damage_pct"] == 5.0
            assert result["additive"]["melee_damage_pct"] == 4.0
            assert result["additive"]["throwing_damage_pct"] == 3.0
            assert result["additive"]["fire_damage_pct"] == 6.0
            assert result["additive"]["cold_damage_pct"] == 6.0
            assert result["additive"]["physical_damage_pct"] == 6.0
            assert result["additive"]["necrotic_damage_pct"] == 6.0
            assert result["additive"]["void_damage_pct"] == 6.0
            assert result["additive"]["elemental_damage_pct"] == 4.0

    def test_dot_aliases_stack(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_damage"])
            # Damage Over Time (7) + Global Damage Over Time (3)
            assert result["additive"]["dot_damage_pct"] == 10.0

    def test_global_lightning_alias(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_damage"])
            assert result["additive"]["lightning_damage_pct"] == 8.0

    def test_elemental_resistances_plural_composite(self, app, seed_pass2_nodes):
        """'Elemental Resistances' fans out to fire/cold/lightning."""
        with app.app_context():
            result = resolve_passive_stats(["p2_damage"])
            for res in ("fire_res", "cold_res", "lightning_res"):
                assert result["additive"][res] == 3.0
            # Should NOT bleed into void/necrotic/poison/physical.
            for res in ("void_res", "necrotic_res", "poison_res", "physical_res"):
                assert res not in result["additive"]


class TestPass2AilmentAliases:
    """Type-scoped ailment / crit chance keys collapse onto the generic
    chance pool — BuildStats has no per-hit-source ailment splits."""

    def test_bleed_chance_aliases_stack(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_ailment"])
            # Melee Bleed (5) + Throwing Bleed (3) + Throwing Attack Bleed (2)
            assert result["additive"]["bleed_chance_pct"] == 10.0

    def test_poison_chance_aliases_stack(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_ailment"])
            # Melee Poison (4) + Spell Poison (2)
            assert result["additive"]["poison_chance_pct"] == 6.0

    def test_ignite_chance_alias(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_ailment"])
            assert result["additive"]["ignite_chance_pct"] == 6.0

    def test_melee_crit_chance_alias(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_ailment"])
            assert result["additive"]["crit_chance_pct"] == 8.0

    def test_slow_chance_direct_field(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_ailment"])
            assert result["additive"]["slow_chance_pct"] == 3.0


class TestPass2DurationAliases:
    """Every elemental/poison duration alias feeds ailment_duration_pct."""

    def test_duration_aliases_stack_onto_generic_bucket(
        self, app, seed_pass2_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["p2_duration"])
            # Ignite 10 + Chill 5 + Shock 5 + Electrify 5 + Poison 10
            #   + Increased Poison 5 + Increased Slow 5 = 45
            assert result["additive"]["ailment_duration_pct"] == 45.0

    def test_buff_duration_direct(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_duration"])
            assert result["additive"]["buff_duration_pct"] == 5.0


class TestPass2MiscAliases:
    """Speed / shred / healing aliases that round out the mapping pass."""

    def test_attack_speed_aliases(self, app, seed_pass2_nodes):
        """Melee Attack Speed and Increased Bow Attack Speed both fold into
        the generic attack_speed_pct pool (BuildStats has no type-split)."""
        with app.app_context():
            result = resolve_passive_stats(["p2_misc"])
            # Melee Attack Speed (5) + Increased Bow Attack Speed (4)
            assert result["additive"]["attack_speed_pct"] == 9.0

    def test_throwing_attack_speed_aliases(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_misc"])
            # Increased Throwing Attack Speed (6) + Throwing Attack Speed (2)
            assert result["additive"]["throwing_attack_speed"] == 8.0

    def test_shred_aliases(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_misc"])
            assert result["additive"]["armour_shred_chance"] == 8.0
            assert result["additive"]["lightning_shred_chance"] == 5.0

    def test_healing_alias_and_health_on_block(self, app, seed_pass2_nodes):
        with app.app_context():
            result = resolve_passive_stats(["p2_misc"])
            assert result["additive"]["healing_effectiveness_pct"] == 4.0
            assert result["additive"]["health_on_block"] == 8.0


# ---------------------------------------------------------------------------
# Meta-build smoke — synthesises a mini allocation drawn from the four
# S4 meta archetypes and checks the high-signal stats land on the
# correct BuildStats fields. Guards against a future STAT_KEY_MAP edit
# silently breaking a workhorse mapping for the flagship builds.
# ---------------------------------------------------------------------------

@pytest.fixture
def seed_meta_build_nodes(db):
    from app.models import PassiveNode

    nodes = [
        # Ballista Falconer — bow / throwing + dodge + mana regen
        PassiveNode(
            id="meta_falc", raw_node_id=400, character_class="Rogue",
            mastery="Falconer",
            name="Ballista Mini", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Bow Damage", "value": "8%"},
                {"key": "Increased Dodge Rating", "value": "12%"},
                {"key": "Increased Throwing Attack Damage", "value": "5%"},
                {"key": "Increased Mana Regen", "value": "15%"},
            ],
        ),
        # Warpath Void Knight — melee void/phys + mana pool + healing
        PassiveNode(
            id="meta_vk", raw_node_id=401, character_class="Sentinel",
            mastery="Void Knight",
            name="Warpath Mini", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Increased Physical Damage", "value": "6%"},
                {"key": "Increased Mana", "value": "10%"},
                {"key": "Increased Healing Effectiveness", "value": "8%"},
                {"key": "Increased Health Regen", "value": "5%"},
            ],
        ),
        # Profane Veil Warlock — necrotic DoT + leech + ward regen
        PassiveNode(
            id="meta_wlk", raw_node_id=402, character_class="Acolyte",
            mastery="Warlock",
            name="Profane Veil Mini", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Increased Necrotic Damage", "value": "10%"},
                {"key": "Increased Damage Over Time", "value": "6%"},
                {"key": "Health Leech", "value": "+0.5%"},
                {"key": "Ward per second", "value": "+4"},
            ],
        ),
        # Lightning Blast Runemaster — spell lightning + crit + mana regen
        PassiveNode(
            id="meta_rune", raw_node_id=403, character_class="Mage",
            mastery="Runemaster",
            name="LB Mini", node_type="notable", x=0, y=0,
            stats=[
                {"key": "Increased Lightning Damage", "value": "10%"},
                {"key": "Spell Damage", "value": "8%"},
                {"key": "Critical Multiplier", "value": "+20%"},
                {"key": "Increased Mana Regen", "value": "10%"},
            ],
        ),
    ]
    for n in nodes:
        db.session.add(n)
    db.session.commit()
    return nodes


class TestMetaBuildSmoke:
    def test_ballista_falconer_keys_land_on_fields(
        self, app, seed_meta_build_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["meta_falc"])
            adds = result["additive"]
            assert adds["bow_damage_pct"] == 8.0
            assert adds["dodge_rating_pct"] == 12.0
            assert adds["throwing_damage_pct"] == 5.0
            assert adds["mana_regen_pct"] == 15.0
            # Nothing from this node should leak to special_effects.
            assert result["special_effects"] == []

    def test_warpath_void_knight_keys_land_on_fields(
        self, app, seed_meta_build_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["meta_vk"])
            adds = result["additive"]
            assert adds["physical_damage_pct"] == 6.0
            assert adds["mana_pct"] == 10.0
            assert adds["healing_effectiveness_pct"] == 8.0
            assert adds["health_regen_pct"] == 5.0
            assert result["special_effects"] == []

    def test_profane_veil_warlock_keys_land_on_fields(
        self, app, seed_meta_build_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["meta_wlk"])
            adds = result["additive"]
            assert adds["necrotic_damage_pct"] == 10.0
            assert adds["dot_damage_pct"] == 6.0
            assert adds["leech"] == pytest.approx(0.5)
            assert adds["ward_regen"] == 4.0
            assert result["special_effects"] == []

    def test_lightning_blast_runemaster_keys_land_on_fields(
        self, app, seed_meta_build_nodes
    ):
        with app.app_context():
            result = resolve_passive_stats(["meta_rune"])
            adds = result["additive"]
            assert adds["lightning_damage_pct"] == 10.0
            assert adds["spell_damage_pct"] == 8.0
            assert adds["crit_multiplier_pct"] == 20.0
            assert adds["mana_regen_pct"] == 10.0
            assert result["special_effects"] == []


class TestPassiveCoverageFloor:
    """Sanity-check that the expanded STAT_KEY_MAP still clears the
    coverage floor enforced by scripts/verify_passive_coverage.py.

    Guards against future edits that accidentally remove a widely-used
    mapping entry.
    """

    def test_coverage_floor_against_live_data(self):
        import json
        from collections import Counter
        from pathlib import Path
        from app.services.passive_stat_resolver import STAT_KEY_MAP

        passives_json = (
            Path(__file__).resolve().parents[2] / "data" / "classes" / "passives.json"
        )
        raw = json.loads(passives_json.read_text())
        nodes = raw if isinstance(raw, list) else raw.get("nodes", [])

        counts: Counter[str] = Counter()
        for node in nodes:
            for stat in node.get("stats") or []:
                counts[stat.get("key", "")] += 1

        total = sum(counts.values())
        mapped = sum(c for k, c in counts.items() if k in STAT_KEY_MAP)
        overall_pct = 100.0 * mapped / total if total else 0.0

        freq2 = [(k, c) for k, c in counts.items() if c >= 2]
        freq2_total = sum(c for _, c in freq2)
        freq2_mapped = sum(c for k, c in freq2 if k in STAT_KEY_MAP)
        freq2_pct = 100.0 * freq2_mapped / freq2_total if freq2_total else 0.0

        assert overall_pct >= 37.0, (
            f"Overall passive-key coverage dropped to {overall_pct:.1f}%; "
            f"expected ≥37% (pass 2 reached 39.2%, pass 1 was 31.8%)"
        )
        assert freq2_pct >= 77.0, (
            f"freq>=2 passive-key coverage dropped to {freq2_pct:.1f}%; "
            f"expected ≥77% (pass 2 reached 79.8%, pass 1 was 69.7%)"
        )
