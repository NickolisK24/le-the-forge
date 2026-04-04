"""J7 — Tests for passive_tree_model.py"""

import pytest
from data.models.passive_tree_model import PassiveTreeModel


class TestNodeCreation:
    def test_basic_creation(self):
        node = PassiveTreeModel(node_id="n1", stat_modifiers={"strength": 5.0})
        assert node.node_id == "n1"
        assert node.stat_modifiers["strength"] == 5.0

    def test_root_node(self):
        node = PassiveTreeModel(node_id="root")
        assert node.is_root() is True

    def test_grants_stat(self):
        node = PassiveTreeModel("n1", stat_modifiers={"fire_damage": 10.0})
        assert node.grants_stat("fire_damage") is True
        assert node.grants_stat("cold_damage") is False


class TestDependencyValidation:
    def test_dependencies_stored_as_tuple(self):
        node = PassiveTreeModel("n1", dependencies=["n0", "root"])
        assert isinstance(node.dependencies, tuple)
        assert "n0" in node.dependencies

    def test_empty_node_id_raises(self):
        with pytest.raises(ValueError, match="node_id"):
            PassiveTreeModel(node_id="")

    def test_to_dict(self):
        node = PassiveTreeModel("n1", {"str": 5.0}, ["n0"])
        d = node.to_dict()
        assert d["node_id"] == "n1"
        assert isinstance(d["dependencies"], list)
