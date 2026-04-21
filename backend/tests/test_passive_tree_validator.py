"""
Phase 0 · 0E-3 — Tests for the passive tree allocation validator.

Mini-tree used by most cases:

    A (entry, max=5)
     |
     v
    B (requires A>=1, max=3)
     |
     v
    C (requires B>=2, max=2)

Plus an isolated node X with no edges (must be allocated via entry) and a
second entry D (parallel start).
"""

from __future__ import annotations

import pytest

from app.game_data.passive_tree_validator import validate_allocation


def _tree() -> list[dict]:
    return [
        {"id": "A", "max_points": 5, "connections": ["B"], "requires": []},
        {"id": "B", "max_points": 3, "connections": ["A", "C"],
         "requires": [{"parent_id": "A", "points": 1}]},
        {"id": "C", "max_points": 2, "connections": ["B"],
         "requires": [{"parent_id": "B", "points": 2}]},
        {"id": "D", "max_points": 4, "connections": [], "requires": []},
        {"id": "X", "max_points": 1, "connections": [],
         "requires": [{"parent_id": "Z", "points": 1}]},  # dangling parent ref
    ]


# ---------------------------------------------------------------------------
# Happy paths
# ---------------------------------------------------------------------------

class TestHappyPaths:
    def test_empty_allocation_is_valid(self):
        assert validate_allocation(_tree(), {}) == []

    def test_allocate_entry_only(self):
        assert validate_allocation(_tree(), {"A": 3}) == []

    def test_allocate_entry_then_child_with_threshold(self):
        assert validate_allocation(_tree(), {"A": 1, "B": 1}) == []

    def test_allocate_full_chain(self):
        assert validate_allocation(_tree(), {"A": 1, "B": 2, "C": 2}) == []

    def test_two_independent_entries(self):
        assert validate_allocation(_tree(), {"A": 1, "D": 2}) == []


# ---------------------------------------------------------------------------
# Rule 1 — unknown ids
# ---------------------------------------------------------------------------

class TestUnknownIds:
    def test_unknown_id_surfaces_error(self):
        errs = validate_allocation(_tree(), {"Q": 1})
        assert any("unknown node id" in e and "'Q'" in e for e in errs)


# ---------------------------------------------------------------------------
# Rule 2 — point ranges
# ---------------------------------------------------------------------------

class TestPointRange:
    def test_points_above_max_rejected(self):
        errs = validate_allocation(_tree(), {"A": 6})
        assert any("exceeds max_points" in e for e in errs)

    def test_zero_points_rejected(self):
        errs = validate_allocation(_tree(), {"A": 0})
        assert any("positive integer" in e for e in errs)

    def test_negative_points_rejected(self):
        errs = validate_allocation(_tree(), {"A": -1})
        assert any("positive integer" in e for e in errs)

    def test_non_integer_points_rejected(self):
        errs = validate_allocation(_tree(), {"A": 1.5})  # type: ignore[dict-item]
        assert any("positive integer" in e for e in errs)


# ---------------------------------------------------------------------------
# Rule 3 — parent thresholds
# ---------------------------------------------------------------------------

class TestParentThreshold:
    def test_child_without_parent_rejected(self):
        errs = validate_allocation(_tree(), {"B": 1})
        assert any("requires parent A" in e for e in errs)

    def test_child_with_insufficient_parent_points_rejected(self):
        # C needs B>=2 but B has only 1.
        errs = validate_allocation(_tree(), {"A": 1, "B": 1, "C": 1})
        assert any("requires parent B to have >= 2" in e for e in errs)

    def test_child_with_exact_threshold_accepted(self):
        assert validate_allocation(_tree(), {"A": 1, "B": 2, "C": 1}) == []


# ---------------------------------------------------------------------------
# Rule 4 — BFS reachability
# ---------------------------------------------------------------------------

class TestReachability:
    def test_orphan_node_with_dangling_parent_rejected(self):
        # X requires Z but Z doesn't exist. Allocating X must fail.
        errs = validate_allocation(_tree(), {"X": 1})
        assert any("not reachable" in e for e in errs) or any(
            "requires parent Z" in e for e in errs
        )

    def test_reachability_through_chain(self):
        assert validate_allocation(_tree(), {"A": 1, "B": 2, "C": 2}) == []

    def test_skipping_middle_node_is_unreachable(self):
        # C needs B; without B, C is unreachable from entry.
        errs = validate_allocation(_tree(), {"A": 1, "C": 1})
        # Rule 3 also fires; Rule 4 may or may not add an extra; either works.
        assert any("requires parent B" in e for e in errs)


# ---------------------------------------------------------------------------
# Rule 5 — total budget
# ---------------------------------------------------------------------------

class TestTotalBudget:
    def test_under_budget_accepted(self):
        assert validate_allocation(_tree(), {"A": 2, "D": 1}, max_total_points=5) == []

    def test_over_budget_rejected(self):
        errs = validate_allocation(_tree(), {"A": 5, "D": 4}, max_total_points=5)
        assert any("exceeds budget 5" in e for e in errs)

    def test_no_budget_ignores_total(self):
        assert validate_allocation(_tree(), {"A": 5, "D": 4}) == []


# ---------------------------------------------------------------------------
# Against the real Primalist payload (if the merge has been applied)
# ---------------------------------------------------------------------------

class TestRealPrimalistTree:
    def _primalist_nodes(self) -> list[dict]:
        import json
        from pathlib import Path
        raw = json.loads(
            (Path(__file__).resolve().parents[2]
             / "data" / "classes" / "passives.json").read_text()
        )
        return [n for n in raw if n.get("character_class") == "Primalist"]

    def test_empty_allocation_valid(self):
        assert validate_allocation(self._primalist_nodes(), {}) == []

    def test_root_node_allocation_valid(self):
        # pr_0 is the Primalist root with no requires.
        nodes = self._primalist_nodes()
        entry_ids = [n["id"] for n in nodes if not (n.get("requires") or [])]
        if not entry_ids:
            pytest.skip("merge script has not populated requires[] yet")
        assert validate_allocation(nodes, {entry_ids[0]: 1}) == []
