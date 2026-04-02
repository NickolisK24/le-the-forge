"""
E6 — Tests for PassiveSystem.
"""

import pytest
from builds.passive_system import PassiveNode, PassiveSystem


def _make_system(*nodes: PassiveNode) -> PassiveSystem:
    return PassiveSystem(list(nodes))


class TestPassiveNode:
    def test_to_dict(self):
        n = PassiveNode(node_id=5, name="Life Node", node_type="minor")
        d = n.to_dict()
        assert d == {"id": 5, "type": "minor", "name": "Life Node"}

    def test_from_dict(self):
        n = PassiveNode.from_dict({"id": 7, "type": "notable", "name": "Power",
                                    "dependencies": [3]})
        assert n.node_id == 7
        assert n.node_type == "notable"
        assert n.dependencies == [3]


class TestPassiveSystem:
    def test_empty_system(self):
        ps = PassiveSystem()
        assert ps.get_allocated_ids() == []

    def test_allocate_unknown_node(self):
        ps = PassiveSystem()
        ps.allocate(999)
        assert ps.is_allocated(999)

    def test_allocate_known_node_no_deps(self):
        ps = _make_system(PassiveNode(1, "A"))
        ps.allocate(1)
        assert ps.is_allocated(1)

    def test_dependency_validation_passes(self):
        ps = _make_system(
            PassiveNode(1, "A"),
            PassiveNode(2, "B", dependencies=[1]),
        )
        ps.allocate(1)
        ps.allocate(2)  # should not raise
        assert ps.is_allocated(2)

    def test_dependency_validation_fails(self):
        ps = _make_system(
            PassiveNode(1, "A"),
            PassiveNode(2, "B", dependencies=[1]),
        )
        with pytest.raises(ValueError, match="missing dependencies"):
            ps.allocate(2)  # 1 not yet allocated

    def test_deallocate(self):
        ps = _make_system(PassiveNode(1))
        ps.allocate(1)
        ps.deallocate(1)
        assert not ps.is_allocated(1)

    def test_get_allocated_ids_sorted(self):
        ps = PassiveSystem()
        ps.allocate(30)
        ps.allocate(5)
        ps.allocate(15)
        assert ps.get_allocated_ids() == [5, 15, 30]

    def test_to_node_dicts(self):
        ps = _make_system(
            PassiveNode(1, "A", "minor"),
            PassiveNode(2, "B", "keystone"),
        )
        dicts = ps.to_node_dicts()
        assert len(dicts) == 2
        ids = {d["id"] for d in dicts}
        assert ids == {1, 2}

    def test_circular_dependency_prevented(self):
        ps = _make_system(PassiveNode(1, "A", dependencies=[2]))
        node_b = PassiveNode(2, "B", dependencies=[1])
        with pytest.raises(ValueError, match="Circular dependency"):
            ps.register(node_b)

    def test_stacking_behavior_multiple_allocations(self):
        ps = _make_system(
            PassiveNode(1), PassiveNode(2), PassiveNode(3),
        )
        for nid in [1, 2, 3]:
            ps.allocate(nid)
        assert ps.get_allocated_ids() == [1, 2, 3]
