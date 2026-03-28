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
