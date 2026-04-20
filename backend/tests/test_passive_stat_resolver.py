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

    def test_unmapped_minion_armor(self, app, seed_nodes):
        """ac_0 has 'Minion Armor' which is not in STAT_KEY_MAP."""
        with app.app_context():
            result = resolve_passive_stats(["ac_0"])
            effect_keys = [e["key"] for e in result["special_effects"]]
            assert "Minion Armor" in effect_keys

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
                # These remain intentionally unmapped and should route to
                # special_effects instead of polluting additive totals.
                {"key": "Increased Minion Cold Damage", "value": "7%"},
                {"key": "Freeze Rate Multiplier", "value": "+20%"},
                {"key": "Can Equip Swords in Offhand", "value": ""},
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
            assert "Increased Minion Cold Damage" in keys
            assert "Freeze Rate Multiplier" in keys
            assert "Can Equip Swords in Offhand" in keys

    def test_throwing_and_shock_aliases(self, app, seed_new_mapping_nodes):
        with app.app_context():
            result = resolve_passive_stats(["new_7"])
            # Two throwing damage % aliases stack on throwing_damage_pct.
            assert result["additive"]["throwing_damage_pct"] == 13.0
            assert result["additive"]["added_throw_physical"] == 2.0
            # Electrify is the legacy in-game name for Shock.
            assert result["additive"]["shock_chance_pct"] == 7.0


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

        assert overall_pct >= 25.0, (
            f"Overall passive-key coverage dropped to {overall_pct:.1f}%; "
            f"expected ≥25% (was 31.8% at patch time)"
        )
        assert freq2_pct >= 60.0, (
            f"freq>=2 passive-key coverage dropped to {freq2_pct:.1f}%; "
            f"expected ≥60% (was 69.7% at patch time)"
        )
