"""
Phase 0 · 0L-1 — Scaffold tests for the Weaver Tree data file.

The tree itself is populated in a follow-up task from user-captured
ground-truth data. These tests lock the scaffold so that:
  - the JSON file exists and declares its field contract in ``_schema``,
  - the pipeline loader accepts the empty-nodes scaffold and strips
    the meta wrapper before exposing data,
  - the validator raises on malformed nodes (missing ids, duplicate ids,
    bad connection lists, bad stat entries, bad max_points),
  - the public accessors return empty results today and a single node
    when the cache is populated in-place.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.game_data.game_data_loader import (
    get_weaver_tree_node,
    get_weaver_tree_nodes,
)
from app.game_data.pipeline import GameDataPipeline


_WEAVER_PATH = (
    Path(__file__).resolve().parents[2]
    / "data" / "progression" / "weaver_tree.json"
)


# ---------------------------------------------------------------------------
# File contract
# ---------------------------------------------------------------------------

class TestWeaverTreeFile:
    def test_file_exists(self):
        assert _WEAVER_PATH.exists(), "weaver_tree.json scaffold must ship"

    def test_schema_block_present(self):
        raw = json.loads(_WEAVER_PATH.read_text())
        assert "_schema" in raw, "weaver_tree.json must carry a _schema block"
        for f in (
            "id", "name", "description", "node_type", "tier",
            "x", "y", "max_points", "connections", "stats",
            "ability_granted", "icon",
        ):
            assert f in raw["_schema"]["node_fields"], (
                f"_schema.node_fields missing {f!r}"
            )

    def test_nodes_list_starts_empty(self):
        """Scaffold ships empty; no guessed node content."""
        raw = json.loads(_WEAVER_PATH.read_text())
        assert raw.get("nodes") == [], (
            "weaver_tree.json nodes must stay empty until ground-truth "
            "capture lands in the follow-up task"
        )


# ---------------------------------------------------------------------------
# Loader behaviour
# ---------------------------------------------------------------------------

class TestLoader:
    def test_exposes_empty_list_for_scaffold(self):
        nodes = get_weaver_tree_nodes()
        assert isinstance(nodes, list)
        assert nodes == []

    def test_accessors_return_none_for_unknown_id(self):
        assert get_weaver_tree_node("does_not_exist") is None


# ---------------------------------------------------------------------------
# Validator contract — uses a fresh pipeline instance, no on-disk writes
# ---------------------------------------------------------------------------

def _node(**overrides) -> dict:
    base = {
        "id": "w_1",
        "name": "Test",
        "max_points": 1,
        "connections": [],
        "stats": [],
    }
    base.update(overrides)
    return base


class TestValidator:
    def _pipeline(self) -> GameDataPipeline:
        return GameDataPipeline()

    def test_accepts_minimal_node(self):
        p = self._pipeline()
        p._validate_weaver_node(_node(), set())

    def test_rejects_missing_id(self):
        p = self._pipeline()
        bad = _node()
        del bad["id"]
        with pytest.raises(RuntimeError, match="missing required fields"):
            p._validate_weaver_node(bad, set())

    def test_rejects_empty_id(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="id must be a non-empty string"):
            p._validate_weaver_node(_node(id=""), set())

    def test_rejects_duplicate_id(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="duplicate node id"):
            p._validate_weaver_node(_node(), {"w_1"})

    def test_rejects_non_list_connections(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="connections must be a list"):
            p._validate_weaver_node(_node(connections="w_2"), set())

    def test_rejects_bad_connection_entry(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="invalid connection entry"):
            p._validate_weaver_node(_node(connections=[""]), set())

    def test_rejects_bad_max_points(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="max_points"):
            p._validate_weaver_node(_node(max_points=0), set())

    def test_rejects_malformed_stat_entry(self):
        p = self._pipeline()
        with pytest.raises(RuntimeError, match="stats entry must be"):
            p._validate_weaver_node(
                _node(stats=[{"only_key": "x"}]), set()
            )

    def test_load_raises_when_nodes_not_list(self, tmp_path, monkeypatch):
        """_load_weaver_tree surfaces structural errors clearly."""
        import app.game_data.pipeline as pipeline_mod
        bad_path = tmp_path / "weaver_tree.json"
        bad_path.write_text(json.dumps({"nodes": "oops"}))
        monkeypatch.setitem(
            pipeline_mod._PATHS, "weaver_tree", str(bad_path)
        )
        p = GameDataPipeline()
        with pytest.raises(RuntimeError, match="'nodes'.*list"):
            p._load_weaver_tree()

    def test_load_accepts_wellformed_nodes(self, tmp_path, monkeypatch):
        """End-to-end: loader returns nodes when the file is valid."""
        import app.game_data.pipeline as pipeline_mod
        good_path = tmp_path / "weaver_tree.json"
        good_path.write_text(json.dumps({
            "nodes": [
                _node(id="w_1", connections=["w_2"]),
                _node(id="w_2", connections=["w_1"],
                      stats=[{"key": "Intelligence", "value": "+1"}]),
            ],
        }))
        monkeypatch.setitem(
            pipeline_mod._PATHS, "weaver_tree", str(good_path)
        )
        p = GameDataPipeline()
        out = p._load_weaver_tree()
        assert [n["id"] for n in out] == ["w_1", "w_2"]
