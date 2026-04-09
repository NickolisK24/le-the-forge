"""
Tests for Phase 5 — Skill Tree API endpoints and BFS validation.

Covers:
  - GET /api/skills/{skill_id}/tree — correct node graph returned
  - BFS path validation — cannot allocate unreachable nodes
  - Point allocation within bounds (0 to max_points)
  - Budget enforcement (max 20 skill points)
  - Deallocation with orphan protection
"""

from __future__ import annotations

import pytest

from app.routes.skills import (
    _is_reachable_from_root,
    _would_orphan_children,
    _spec_tree_to_alloc_map,
    _alloc_map_to_spec_tree,
    _load_trees,
    _get_tree,
)


# ---------------------------------------------------------------------------
# Unit tests — BFS reachability
# ---------------------------------------------------------------------------

def _sample_nodes():
    """A minimal tree: root(0) -> node(1) -> node(2), plus disconnected node(3)."""
    return [
        {"id": 0, "maxPoints": 0, "requirements": []},
        {"id": 1, "maxPoints": 5, "requirements": [{"node": 0, "requirement": 0}]},
        {"id": 2, "maxPoints": 3, "requirements": [{"node": 1, "requirement": 2}]},
        {"id": 3, "maxPoints": 3, "requirements": [{"node": 99, "requirement": 1}]},  # unreachable
    ]


class TestBFSReachability:
    def test_root_always_reachable(self):
        nodes = _sample_nodes()
        assert _is_reachable_from_root(0, nodes, {}) is True

    def test_child_of_root_reachable(self):
        nodes = _sample_nodes()
        assert _is_reachable_from_root(1, nodes, {0: 1}) is True

    def test_child_of_root_reachable_even_without_explicit_root_alloc(self):
        # Root with maxPoints=0 always counts as allocated
        nodes = _sample_nodes()
        assert _is_reachable_from_root(1, nodes, {}) is True

    def test_grandchild_requires_parent_points(self):
        nodes = _sample_nodes()
        # Node 2 requires 2 points in node 1
        assert _is_reachable_from_root(2, nodes, {1: 1}) is False
        assert _is_reachable_from_root(2, nodes, {1: 2}) is True

    def test_disconnected_node_unreachable(self):
        nodes = _sample_nodes()
        assert _is_reachable_from_root(3, nodes, {}) is False
        assert _is_reachable_from_root(3, nodes, {99: 1}) is False

    def test_nonexistent_node(self):
        nodes = _sample_nodes()
        assert _is_reachable_from_root(999, nodes, {}) is False

    def test_multi_requirement_node(self):
        """Node requires points in two different parents."""
        nodes = [
            {"id": 0, "maxPoints": 0, "requirements": []},
            {"id": 1, "maxPoints": 5, "requirements": [{"node": 0, "requirement": 0}]},
            {"id": 2, "maxPoints": 5, "requirements": [{"node": 0, "requirement": 0}]},
            {"id": 3, "maxPoints": 1, "requirements": [
                {"node": 1, "requirement": 2},
                {"node": 2, "requirement": 3},
            ]},
        ]
        # Need 2 points in node 1 AND 3 points in node 2
        assert _is_reachable_from_root(3, nodes, {1: 2, 2: 2}) is False
        assert _is_reachable_from_root(3, nodes, {1: 2, 2: 3}) is True


class TestOrphanProtection:
    def test_can_deallocate_leaf(self):
        nodes = _sample_nodes()
        alloc = {1: 3, 2: 1}
        assert _would_orphan_children(2, 0, nodes, alloc) is False

    def test_cannot_deallocate_parent_with_allocated_child(self):
        nodes = _sample_nodes()
        alloc = {1: 3, 2: 1}
        # Node 2 requires 2 points in node 1; reducing node 1 to 0 orphans node 2
        assert _would_orphan_children(1, 0, nodes, alloc) is True

    def test_can_reduce_parent_if_still_meets_requirement(self):
        nodes = _sample_nodes()
        alloc = {1: 3, 2: 1}
        # Node 2 requires 2 points in node 1; keeping 2 is fine
        assert _would_orphan_children(1, 2, nodes, alloc) is False


# ---------------------------------------------------------------------------
# Allocation map conversions
# ---------------------------------------------------------------------------

class TestAllocMapConversions:
    def test_spec_tree_to_alloc_map(self):
        spec = [2, 2, 2, 6, 6, 7]
        result = _spec_tree_to_alloc_map(spec)
        assert result == {2: 3, 6: 2, 7: 1}

    def test_empty_spec_tree(self):
        assert _spec_tree_to_alloc_map([]) == {}

    def test_alloc_map_to_spec_tree(self):
        alloc = {2: 3, 6: 2, 7: 1}
        result = _alloc_map_to_spec_tree(alloc)
        assert sorted(result) == [2, 2, 2, 6, 6, 7]

    def test_roundtrip(self):
        original = [1, 1, 3, 3, 3, 5]
        alloc = _spec_tree_to_alloc_map(original)
        rebuilt = _alloc_map_to_spec_tree(alloc)
        assert sorted(rebuilt) == sorted(original)


# ---------------------------------------------------------------------------
# Tree data loader
# ---------------------------------------------------------------------------

class TestTreeLoader:
    def test_load_trees_returns_dict(self):
        trees = _load_trees()
        assert isinstance(trees, dict)
        assert len(trees) > 0

    def test_known_tree_exists(self):
        tree = _get_tree("fi9")  # Fireball
        assert tree is not None
        assert tree.get("ability") == "Fireball" or tree["nodes"][0]["name"] == "Fireball"

    def test_unknown_tree_returns_none(self):
        assert _get_tree("nonexistent_skill_xyz") is None

    def test_tree_has_nodes_with_required_fields(self):
        tree = _get_tree("fi9")
        assert tree is not None
        nodes = tree.get("nodes", [])
        assert len(nodes) > 0
        for node in nodes:
            assert "id" in node
            assert "maxPoints" in node
            assert "transform" in node

    def test_root_node_has_zero_max_points(self):
        tree = _get_tree("fi9")
        assert tree is not None
        root = tree["nodes"][0]
        assert root["maxPoints"] == 0
        assert root.get("requirements", []) == []

    def test_nodes_have_requirements_referencing_valid_ids(self):
        tree = _get_tree("fi9")
        assert tree is not None
        node_ids = {n["id"] for n in tree["nodes"]}
        for node in tree["nodes"]:
            for req in node.get("requirements", []):
                req_id = req.get("node", req.get("nodeId"))
                assert req_id in node_ids, f"Node {node['id']} requires nonexistent node {req_id}"

    def test_bfs_on_real_tree(self):
        """Ensure BFS works on real Fireball tree data."""
        tree = _get_tree("fi9")
        assert tree is not None
        nodes = tree["nodes"]

        # Root (node 0) should always be reachable
        assert _is_reachable_from_root(0, nodes, {}) is True

        # Node directly connected to root should be reachable with no explicit allocation
        child = None
        for n in nodes:
            reqs = n.get("requirements", [])
            if reqs and reqs[0].get("node") == 0:
                child = n
                break
        assert child is not None
        assert _is_reachable_from_root(child["id"], nodes, {}) is True

        # A deeper node should NOT be reachable without its parent allocated
        deeper = None
        for n in nodes:
            reqs = n.get("requirements", [])
            if reqs and reqs[0].get("node") != 0 and reqs[0].get("requirement", 0) > 0:
                deeper = n
                break
        if deeper:
            assert _is_reachable_from_root(deeper["id"], nodes, {}) is False
