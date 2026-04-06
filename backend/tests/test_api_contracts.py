"""
API Contract Tests — validates that every endpoint returns the correct schema.

These tests run against a live database and verify:
  - Response status codes
  - Response envelope structure ({data, meta, errors})
  - Field presence and types per canonical schema
  - Expected record counts (sanity checks)

Run with: pytest tests/test_api_contracts.py -v

NOTE: These tests require a seeded PostgreSQL database. They are skipped
automatically when FLASK_ENV=testing (which uses in-memory SQLite).
"""

import os
import pytest

# Skip the entire module in CI testing mode (no seeded DB available)
pytestmark = pytest.mark.skipif(
    os.environ.get("FLASK_ENV") == "testing",
    reason="Contract tests require a seeded PostgreSQL database, not SQLite"
)

# Use the dev database for contract tests (not sqlite)
os.environ.setdefault("DATABASE_URL", "postgresql://forge:forgedev@127.0.0.1:5432/the_forge")

from app import create_app
from app.schemas.api_contracts import (
    AFFIX_FIELDS,
    PASSIVE_NODE_FIELDS,
    ITEM_TYPE_FIELDS,
    BASE_ITEM_FIELDS,
    BUILD_LIST_FIELDS,
    CLASS_META_FIELDS,
    ENEMY_PROFILE_FIELDS,
    validate_record,
)


@pytest.fixture(scope="module")
def client():
    app = create_app("development")
    app.config["TESTING"] = True
    with app.test_client() as c:
        with app.app_context():
            yield c


def _get_json(client, path):
    r = client.get(path)
    assert r.status_code == 200, f"{path} returned {r.status_code}"
    data = r.get_json()
    assert data is not None, f"{path} returned no JSON"
    assert "data" in data, f"{path} missing 'data' envelope key"
    return data


# ---------------------------------------------------------------------------
# Envelope structure
# ---------------------------------------------------------------------------

class TestEnvelopeStructure:
    """Every API response must have {data, meta, errors} keys."""

    @pytest.mark.parametrize("endpoint", [
        "/api/ref/affixes",
        "/api/ref/base-items",
        "/api/ref/classes",
        "/api/ref/item-types",
        "/api/passives/Acolyte",
        "/api/builds",
    ])
    def test_envelope_keys(self, client, endpoint):
        data = _get_json(client, endpoint)
        assert "data" in data
        assert "errors" in data
        assert "meta" in data


# ---------------------------------------------------------------------------
# Affix contract
# ---------------------------------------------------------------------------

class TestAffixContract:

    def test_affixes_return_data(self, client):
        data = _get_json(client, "/api/ref/affixes")
        affixes = data["data"]
        assert isinstance(affixes, list)
        assert len(affixes) >= 1000, f"Expected 1000+ affixes, got {len(affixes)}"

    def test_affix_schema(self, client):
        data = _get_json(client, "/api/ref/affixes")
        affixes = data["data"]
        for i, affix in enumerate(affixes[:20]):
            errors = validate_record(affix, AFFIX_FIELDS, f"affix[{i}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"

    def test_affix_type_values(self, client):
        data = _get_json(client, "/api/ref/affixes")
        types = set(a["type"] for a in data["data"])
        assert types <= {"prefix", "suffix"}, f"Unexpected affix types: {types}"

    def test_affix_prefix_filter(self, client):
        data = _get_json(client, "/api/ref/affixes?type=prefix")
        assert all(a["type"] == "prefix" for a in data["data"])

    def test_affix_suffix_filter(self, client):
        data = _get_json(client, "/api/ref/affixes?type=suffix")
        assert all(a["type"] == "suffix" for a in data["data"])

    def test_affix_tiers_structure(self, client):
        data = _get_json(client, "/api/ref/affixes")
        for affix in data["data"][:10]:
            for tier in affix["tiers"]:
                assert "tier" in tier
                assert "min" in tier
                assert "max" in tier
                assert isinstance(tier["tier"], int)


# ---------------------------------------------------------------------------
# Slot normalization contract
# ---------------------------------------------------------------------------

class TestSlotNormalization:
    """Frontend and DB slot names must both return results."""

    @pytest.mark.parametrize("frontend_slot,db_slot", [
        ("helmet", "helm"),
        ("head", "helm"),
        ("body", "chest"),
    ])
    def test_affix_slot_aliases_match(self, client, frontend_slot, db_slot):
        """Frontend slot name and DB slot name must return identical affix sets."""
        r1 = _get_json(client, f"/api/ref/affixes?slot={frontend_slot}")
        r2 = _get_json(client, f"/api/ref/affixes?slot={db_slot}")
        ids1 = sorted(a["id"] for a in r1["data"])
        ids2 = sorted(a["id"] for a in r2["data"])
        assert ids1 == ids2, f"slot={frontend_slot} returned {len(ids1)} affixes, slot={db_slot} returned {len(ids2)}"

    @pytest.mark.parametrize("slot", ["helmet", "helm", "chest", "boots", "gloves", "belt", "ring", "amulet"])
    def test_affix_slot_returns_results(self, client, slot):
        """Common slot names must return non-empty affix lists."""
        data = _get_json(client, f"/api/ref/affixes?slot={slot}")
        assert len(data["data"]) > 0, f"slot={slot} returned 0 affixes"

    @pytest.mark.parametrize("slot", ["helmet", "helm", "boots", "gloves", "belt"])
    def test_unique_slot_returns_results(self, client, slot):
        """Common slot names must return non-empty unique item lists."""
        data = _get_json(client, f"/api/ref/uniques?slot={slot}")
        assert len(data["data"]) > 0, f"slot={slot} returned 0 uniques"

    def test_base_items_helmet_alias(self, client):
        """?slot=helmet should return results (maps to 'helmet' key in base items)."""
        data = _get_json(client, "/api/ref/base-items?slot=helmet")
        assert len(data["data"]) > 0, "slot=helmet returned 0 base items"

    def test_meta_slot_weapon(self, client):
        """?slot=weapon should return items across all weapon types."""
        data = _get_json(client, "/api/ref/affixes?slot=weapon")
        assert len(data["data"]) > 50, f"slot=weapon returned only {len(data['data'])} affixes"

    def test_meta_slot_offhand(self, client):
        """?slot=offhand should return items across shield/quiver/catalyst."""
        data = _get_json(client, "/api/ref/affixes?slot=offhand")
        assert len(data["data"]) > 0, f"slot=offhand returned 0 affixes"


# ---------------------------------------------------------------------------
# Passive node contract
# ---------------------------------------------------------------------------

class TestPassiveNodeContract:

    @pytest.mark.parametrize("cls,min_count", [
        ("Acolyte", 100),
        ("Mage", 100),
        ("Primalist", 100),
        ("Sentinel", 100),
        ("Rogue", 100),
    ])
    def test_class_returns_nodes(self, client, cls, min_count):
        data = _get_json(client, f"/api/passives/{cls}")
        nodes = data["data"]["nodes"]
        assert len(nodes) >= min_count, f"{cls}: expected {min_count}+ nodes, got {len(nodes)}"

    def test_passive_schema(self, client):
        data = _get_json(client, "/api/passives/Acolyte")
        nodes = data["data"]["nodes"]
        for i, node in enumerate(nodes[:20]):
            errors = validate_record(node, PASSIVE_NODE_FIELDS, f"passive[{i}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"

    def test_passive_icons_populated(self, client):
        data = _get_json(client, "/api/passives/Acolyte")
        nodes = data["data"]["nodes"]
        with_icon = sum(1 for n in nodes if n.get("icon"))
        # At least 95% should have icons
        assert with_icon / len(nodes) >= 0.95, f"Only {with_icon}/{len(nodes)} nodes have icons"

    def test_passive_coordinates_populated(self, client):
        data = _get_json(client, "/api/passives/Acolyte")
        nodes = data["data"]["nodes"]
        with_coords = sum(1 for n in nodes if n["x"] != 0 or n["y"] != 0)
        assert with_coords / len(nodes) >= 0.95, f"Only {with_coords}/{len(nodes)} nodes have coordinates"

    def test_mastery_filter(self, client):
        data = _get_json(client, "/api/passives/Acolyte/Lich")
        nodes = data["data"]["nodes"]
        assert len(nodes) > 0
        # Should contain base nodes (mastery=null) and Lich nodes
        masteries = set(n["mastery"] for n in nodes)
        assert None in masteries, "Should include base class nodes"
        assert "Lich" in masteries, "Should include Lich mastery nodes"

    def test_invalid_class_returns_error(self, client):
        r = client.get("/api/passives/FakeClass")
        assert r.status_code == 400

    def test_invalid_mastery_returns_error(self, client):
        r = client.get("/api/passives/Acolyte/FakeMastery")
        assert r.status_code == 400


# ---------------------------------------------------------------------------
# Item types contract
# ---------------------------------------------------------------------------

class TestItemTypeContract:

    def test_item_types_count(self, client):
        data = _get_json(client, "/api/ref/item-types")
        items = data["data"]
        assert len(items) >= 15, f"Expected 15+ item types, got {len(items)}"

    def test_item_type_schema(self, client):
        data = _get_json(client, "/api/ref/item-types")
        for i, item in enumerate(data["data"][:10]):
            errors = validate_record(item, ITEM_TYPE_FIELDS, f"item_type[{i}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"


# ---------------------------------------------------------------------------
# Base items contract
# ---------------------------------------------------------------------------

class TestBaseItemContract:

    def test_base_items_returns_dict(self, client):
        data = _get_json(client, "/api/ref/base-items")
        assert isinstance(data["data"], dict)
        assert len(data["data"]) >= 15, f"Expected 15+ slots, got {len(data['data'])}"

    def test_base_item_schema(self, client):
        data = _get_json(client, "/api/ref/base-items")
        for slot, items in data["data"].items():
            if not items:
                continue
            for i, item in enumerate(items[:3]):
                errors = validate_record(item, BASE_ITEM_FIELDS, f"base_item[{slot}][{i}]")
                schema_errors = [e for e in errors if "Extra fields" not in e]
                assert not schema_errors, f"Schema errors: {schema_errors}"


# ---------------------------------------------------------------------------
# Builds contract
# ---------------------------------------------------------------------------

class TestBuildContract:

    def test_builds_return_data(self, client):
        data = _get_json(client, "/api/builds")
        builds = data["data"]
        assert isinstance(builds, list)

    def test_build_schema(self, client):
        data = _get_json(client, "/api/builds")
        builds = data["data"]
        if not builds:
            pytest.skip("No builds in database")
        for i, build in enumerate(builds[:5]):
            errors = validate_record(build, BUILD_LIST_FIELDS, f"build[{i}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"

    def test_builds_have_pagination(self, client):
        data = _get_json(client, "/api/builds")
        assert data["meta"] is not None, "Builds endpoint should include pagination meta"


# ---------------------------------------------------------------------------
# Classes contract
# ---------------------------------------------------------------------------

class TestClassContract:

    def test_classes_return_all_five(self, client):
        data = _get_json(client, "/api/ref/classes")
        classes = data["data"]
        expected = {"Acolyte", "Mage", "Primalist", "Rogue", "Sentinel"}
        assert set(classes.keys()) == expected

    def test_class_meta_schema(self, client):
        data = _get_json(client, "/api/ref/classes")
        for cls, meta in data["data"].items():
            errors = validate_record(meta, CLASS_META_FIELDS, f"class[{cls}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"

    def test_each_class_has_three_masteries(self, client):
        data = _get_json(client, "/api/ref/classes")
        for cls, meta in data["data"].items():
            assert len(meta["masteries"]) == 3, f"{cls} has {len(meta['masteries'])} masteries"


# ---------------------------------------------------------------------------
# Enemy profiles contract
# ---------------------------------------------------------------------------

class TestEnemyProfileContract:

    def test_enemy_profiles_exist(self, client):
        data = _get_json(client, "/api/ref/enemy-profiles")
        profiles = data["data"]
        assert len(profiles) >= 5, f"Expected 5+ profiles, got {len(profiles)}"

    def test_enemy_schema(self, client):
        data = _get_json(client, "/api/ref/enemy-profiles")
        for i, profile in enumerate(data["data"][:5]):
            errors = validate_record(profile, ENEMY_PROFILE_FIELDS, f"enemy[{i}]")
            schema_errors = [e for e in errors if "Extra fields" not in e]
            assert not schema_errors, f"Schema errors: {schema_errors}"


# ---------------------------------------------------------------------------
# POST endpoint contracts
# ---------------------------------------------------------------------------

class TestPostEndpoints:

    def test_craft_predict(self, client):
        r = client.post("/api/craft/predict", json={
            "forge_potential": 28,
            "affixes": [],
            "n_simulations": 100,
        })
        assert r.status_code == 200
        data = r.get_json()
        assert "data" in data

    def test_encounter_simulate(self, client):
        r = client.post("/api/simulate/encounter", json={
            "base_damage": 500,
            "fight_duration": 10,
            "tick_size": 0.1,
            "enemy_template": "STANDARD_BOSS",
            "distribution": "SINGLE",
            "crit_chance": 0.05,
            "crit_multiplier": 2.0,
        })
        assert r.status_code == 200
        data = r.get_json()
        assert "data" in data
