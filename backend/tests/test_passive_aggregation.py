"""
Tests for passive_aggregator (Step 88).

Validates stat aggregation from passive tree nodes.
"""

import pytest

from build.passive_aggregator import PassiveNode, aggregate_passives


class TestPassiveNode:
    def test_basic_construction(self):
        node = PassiveNode("n1", "Fire Mastery", {"fire_damage_pct": 10.0})
        assert node.node_id == "n1"
        assert node.name == "Fire Mastery"
        assert node.stats == {"fire_damage_pct": 10.0}

    def test_empty_stats(self):
        node = PassiveNode("n0", "Empty", {})
        assert node.stats == {}

    def test_non_numeric_stat_raises(self):
        with pytest.raises((ValueError, TypeError)):
            PassiveNode("n1", "Bad", {"fire_damage_pct": "ten"})

    def test_equality_by_node_id(self):
        a = PassiveNode("n1", "Fire Mastery", {"fire_damage_pct": 10.0})
        b = PassiveNode("n1", "Different Name", {"cold_damage_pct": 5.0})
        assert a == b


class TestAggregatePassives:
    def test_empty_list_returns_empty_dict(self):
        assert aggregate_passives([]) == {}

    def test_single_node_single_stat(self):
        node = PassiveNode("n1", "Fire", {"fire_damage_pct": 10.0})
        result = aggregate_passives([node])
        assert result == {"fire_damage_pct": 10.0}

    def test_single_node_multiple_stats(self):
        node = PassiveNode("n1", "Power", {"fire_damage_pct": 10.0, "spell_damage_pct": 8.0})
        result = aggregate_passives([node])
        assert result == {"fire_damage_pct": 10.0, "spell_damage_pct": 8.0}

    def test_multiple_nodes_same_key_stacks(self):
        nodes = [
            PassiveNode("n1", "A", {"fire_damage_pct": 10.0}),
            PassiveNode("n2", "B", {"fire_damage_pct": 5.0}),
        ]
        result = aggregate_passives(nodes)
        assert result == {"fire_damage_pct": 15.0}

    def test_multiple_nodes_different_keys_merged(self):
        nodes = [
            PassiveNode("n1", "A", {"fire_damage_pct": 10.0}),
            PassiveNode("n2", "B", {"cold_damage_pct": 7.0}),
        ]
        result = aggregate_passives(nodes)
        assert result == {"fire_damage_pct": 10.0, "cold_damage_pct": 7.0}

    def test_multiple_nodes_mixed_keys(self):
        nodes = [
            PassiveNode("n1", "A", {"fire_damage_pct": 10.0, "spell_damage_pct": 5.0}),
            PassiveNode("n2", "B", {"fire_damage_pct": 8.0, "crit_chance_pct": 3.0}),
        ]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"]    == pytest.approx(18.0)
        assert result["spell_damage_pct"]   == pytest.approx(5.0)
        assert result["crit_chance_pct"]    == pytest.approx(3.0)

    def test_negative_stat_handling(self):
        nodes = [
            PassiveNode("n1", "A", {"fire_damage_pct": 20.0}),
            PassiveNode("n2", "B", {"fire_damage_pct": -5.0}),   # penalty node
        ]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"] == pytest.approx(15.0)

    def test_all_negative_stats(self):
        nodes = [
            PassiveNode("n1", "Debuff", {"fire_damage_pct": -10.0}),
        ]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"] == pytest.approx(-10.0)

    def test_many_nodes_accumulate_correctly(self):
        nodes = [
            PassiveNode(f"n{i}", f"Node {i}", {"fire_damage_pct": 1.0})
            for i in range(100)
        ]
        result = aggregate_passives(nodes)
        assert result["fire_damage_pct"] == pytest.approx(100.0)

    def test_zero_value_stat_included(self):
        node = PassiveNode("n1", "A", {"fire_damage_pct": 0.0})
        result = aggregate_passives([node])
        assert "fire_damage_pct" in result
        assert result["fire_damage_pct"] == pytest.approx(0.0)

    def test_original_nodes_not_mutated(self):
        node = PassiveNode("n1", "A", {"fire_damage_pct": 10.0})
        aggregate_passives([node])
        assert node.stats == {"fire_damage_pct": 10.0}
