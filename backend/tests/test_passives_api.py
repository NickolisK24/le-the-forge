"""
Tests for the /api/passives endpoints.

These tests seed a small subset of PassiveNode rows directly rather than
relying on data/passives.json being loaded, so they run fully in-memory.
"""

import pytest

from app.models import PassiveNode
from app import db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

# Raw node dicts matching real data/passives.json entries (subset of Acolyte)
_ACOLYTE_NODES = [
    # base class nodes (mastery=None)
    dict(id="ac_0",  raw_node_id=0,  character_class="Acolyte", mastery=None,
         mastery_index=0, mastery_requirement=0,  name="Bone Aura",
         description="", node_type="core",  x=-444.3, y=0.0,
         max_points=8, connections=[], stats=[], ability_granted=None, icon="18457"),
    dict(id="ac_1",  raw_node_id=1,  character_class="Acolyte", mastery=None,
         mastery_index=0, mastery_requirement=0,  name="Forbidden Knowledge",
         description="", node_type="notable", x=-444.3, y=-153.8,
         max_points=1, connections=[], stats=[], ability_granted=None, icon="16743"),
    dict(id="ac_2",  raw_node_id=2,  character_class="Acolyte", mastery=None,
         mastery_index=0, mastery_requirement=0,  name="Blood Aura",
         description="", node_type="core",  x=-444.3, y=153.8,
         max_points=8, connections=[], stats=[], ability_granted=None, icon="19265"),
    # Lich mastery nodes
    dict(id="ac_22", raw_node_id=22, character_class="Acolyte", mastery="Lich",
         mastery_index=2, mastery_requirement=10, name="Hollow Lich",
         description="", node_type="notable", x=0.0, y=0.0,
         max_points=1, connections=["ac_0"], stats=[], ability_granted=None, icon="17530"),
    dict(id="ac_29", raw_node_id=29, character_class="Acolyte", mastery="Lich",
         mastery_index=2, mastery_requirement=0,  name="Dance with Death",
         description="", node_type="notable", x=10.0, y=0.0,
         max_points=1, connections=[], stats=[], ability_granted=None, icon="17947"),
    # Necromancer mastery node
    dict(id="ac_10", raw_node_id=10, character_class="Acolyte", mastery="Necromancer",
         mastery_index=1, mastery_requirement=0,  name="Elixir of Hunger",
         description="", node_type="notable", x=0.0, y=50.0,
         max_points=1, connections=[], stats=[], ability_granted=None, icon="16500"),
    # A Mage base node (different class — useful for cross-class tests)
    dict(id="mg_0",  raw_node_id=0,  character_class="Mage",    mastery=None,
         mastery_index=0, mastery_requirement=0,  name="Arcanist",
         description="", node_type="core",  x=0.0, y=0.0,
         max_points=8, connections=[], stats=[], ability_granted=None, icon="17000"),
]


@pytest.fixture
def seeded_passives(db):
    """Insert a representative subset of PassiveNodes for testing."""
    for row in _ACOLYTE_NODES:
        db.session.add(PassiveNode(**row))
    db.session.commit()
    return _ACOLYTE_NODES


# ---------------------------------------------------------------------------
# GET /api/passives  (with query params)
# ---------------------------------------------------------------------------

class TestListPassives:

    def test_no_filters_returns_all_seeded_nodes(self, client, seeded_passives):
        resp = client.get("/api/passives")
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        assert body["count"] == len(_ACOLYTE_NODES)
        assert len(body["nodes"]) == len(_ACOLYTE_NODES)
        assert body["class"] is None
        assert body["mastery"] is None

    def test_class_filter_returns_correct_nodes(self, client, seeded_passives):
        resp = client.get("/api/passives?class=Acolyte")
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        acolyte_count = sum(1 for n in _ACOLYTE_NODES if n["character_class"] == "Acolyte")
        assert body["count"] == acolyte_count
        assert body["class"] == "Acolyte"
        for node in body["nodes"]:
            assert node["character_class"] == "Acolyte"

    def test_class_and_mastery_filter_returns_mastery_plus_base(self, client, seeded_passives):
        resp = client.get("/api/passives?class=Acolyte&mastery=Lich")
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        expected_ids = {n["id"] for n in _ACOLYTE_NODES
                        if n["character_class"] == "Acolyte"
                        and (n["mastery"] == "Lich" or n["mastery"] is None)}
        returned_ids = {n["id"] for n in body["nodes"]}
        assert returned_ids == expected_ids
        assert body["mastery"] == "Lich"

    def test_unknown_class_returns_400(self, client, seeded_passives):
        resp = client.get("/api/passives?class=Foo")
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("Foo" in e["message"] for e in errors)

    def test_unknown_mastery_for_valid_class_returns_400(self, client, seeded_passives):
        resp = client.get("/api/passives?class=Acolyte&mastery=Runemaster")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# GET /api/passives/<character_class>
# ---------------------------------------------------------------------------

class TestGetClassTree:

    def test_returns_full_class_tree(self, client, seeded_passives):
        resp = client.get("/api/passives/Acolyte")
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        assert body["class"] == "Acolyte"
        assert body["mastery"] is None
        acolyte_count = sum(1 for n in _ACOLYTE_NODES if n["character_class"] == "Acolyte")
        assert body["count"] == acolyte_count

    def test_response_node_shape(self, client, seeded_passives):
        """Every returned node must carry the full schema fields."""
        resp = client.get("/api/passives/Acolyte")
        node = resp.get_json()["data"]["nodes"][0]
        for field in ("id", "raw_node_id", "character_class", "mastery",
                      "mastery_index", "mastery_requirement", "name",
                      "description", "node_type", "x", "y", "max_points",
                      "connections", "stats", "ability_granted", "icon"):
            assert field in node, f"Missing field: {field}"

    def test_response_includes_grouped_field(self, client, seeded_passives):
        """The grouped field must separate nodes by tree section."""
        resp = client.get("/api/passives/Acolyte")
        body = resp.get_json()["data"]
        assert "grouped" in body
        grouped = body["grouped"]
        # Base nodes should be under "__base__"
        assert "__base__" in grouped
        base_ids = {n["id"] for n in grouped["__base__"]}
        assert "ac_0" in base_ids  # Bone Aura is a base node
        # Lich nodes should be under "Lich"
        assert "Lich" in grouped
        lich_ids = {n["id"] for n in grouped["Lich"]}
        assert "ac_22" in lich_ids
        # No overlap between sections
        assert base_ids.isdisjoint(lich_ids)

    def test_unknown_class_returns_400(self, client):
        resp = client.get("/api/passives/Foo")
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("Foo" in e["message"] for e in errors)


# ---------------------------------------------------------------------------
# GET /api/passives/<character_class>/<mastery>
# ---------------------------------------------------------------------------

class TestGetMasteryTree:

    def test_returns_lich_plus_base_nodes(self, client, seeded_passives):
        resp = client.get("/api/passives/Acolyte/Lich")
        assert resp.status_code == 200
        body = resp.get_json()["data"]
        assert body["class"] == "Acolyte"
        assert body["mastery"] == "Lich"
        for node in body["nodes"]:
            assert node["mastery"] in ("Lich", None), (
                f"Unexpected mastery '{node['mastery']}' in Lich tree"
            )

    def test_excludes_other_mastery_nodes(self, client, seeded_passives):
        """Necromancer nodes must not appear in the Lich tree."""
        resp = client.get("/api/passives/Acolyte/Lich")
        nodes = resp.get_json()["data"]["nodes"]
        returned_ids = {n["id"] for n in nodes}
        necro_ids = {n["id"] for n in _ACOLYTE_NODES if n["mastery"] == "Necromancer"}
        assert returned_ids.isdisjoint(necro_ids)

    def test_unknown_class_returns_400(self, client):
        resp = client.get("/api/passives/Foo/Bar")
        assert resp.status_code == 400

    def test_mastery_wrong_class_returns_400(self, client, seeded_passives):
        """Runemaster is a valid mastery but not for Acolyte."""
        resp = client.get("/api/passives/Acolyte/Runemaster")
        assert resp.status_code == 400


# ---------------------------------------------------------------------------
# POST /api/builds — passive tree node ID validation
# ---------------------------------------------------------------------------

class TestBuildPassiveValidation:

    def test_valid_namespaced_ids_accepted(self, client, seeded_passives):
        payload = {
            "name": "Ward Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": ["ac_0", "ac_1", "ac_22"],
        }
        resp = client.post("/api/builds", json=payload)
        assert resp.status_code == 201

    def test_nonexistent_id_returns_400(self, client, seeded_passives):
        payload = {
            "name": "Bad Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": ["ac_0", "ac_999"],
        }
        resp = client.post("/api/builds", json=payload)
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("ac_999" in e["message"] for e in errors)

    def test_wrong_class_id_returns_400(self, client, seeded_passives):
        """mg_0 is a Mage node — should be rejected for an Acolyte build."""
        payload = {
            "name": "Bad Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": ["ac_0", "mg_0"],
        }
        resp = client.post("/api/builds", json=payload)
        assert resp.status_code == 400
        errors = resp.get_json()["errors"]
        assert any("mg_0" in e["message"] for e in errors)

    def test_legacy_integer_ids_are_skipped(self, client, db):
        """Integer IDs pre-date the namespaced system and must not cause 400."""
        payload = {
            "name": "Legacy Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": [1, 5, 12, 20],
        }
        resp = client.post("/api/builds", json=payload)
        assert resp.status_code == 201

    def test_empty_passive_tree_accepted(self, client, db):
        payload = {
            "name": "Empty Lich",
            "character_class": "Acolyte",
            "mastery": "Lich",
            "passive_tree": [],
        }
        resp = client.post("/api/builds", json=payload)
        assert resp.status_code == 201
