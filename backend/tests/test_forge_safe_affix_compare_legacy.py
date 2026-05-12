from pathlib import Path

import pytest


SENTINEL_AFFIX_ID = 99999999
SENTINEL_AFFIX_NAME = "__SENTINEL_FORGE_SAFE_DO_NOT_CONSUME__"
SENTINEL_MODIFIER_ID = "__SENTINEL_MODIFIER_DO_NOT_CONSUME__"
SENTINEL_BUNDLE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "forge_safe_affix_bundle_sentinel.json"
)


@pytest.fixture(autouse=True)
def reset_forge_safe_affix_catalog_config(app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = ""
    yield
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = ""


def test_compare_legacy_endpoint_disabled_by_default(client):
    response = client.get("/experimental/forge-safe-affixes/compare-legacy")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "experimental_catalog_disabled"


def test_compare_legacy_endpoint_requires_bundle_mode(app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True

    response = app.test_client().get("/experimental/forge-safe-affixes/compare-legacy")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "bundle_catalog_disabled"


def test_compare_legacy_endpoint_reports_sentinel_missing_in_legacy(app):
    _enable_sentinel_bundle(app)

    response = app.test_client().get("/experimental/forge-safe-affixes/compare-legacy?limit=5")

    assert response.status_code == 200
    body = response.get_json()
    comparison = body["comparison"]

    assert body["success"] is True
    assert body["experimental"] is True
    assert body["read_only"] is True
    assert body["production_consumer"] is False
    assert body["data_source"] == "legacy_vs_forge_safe_bundle"
    assert comparison["metadata"]["read_only"] is True
    assert comparison["metadata"]["experimental"] is True
    assert comparison["metadata"]["production_consumer"] is False
    assert comparison["metadata"]["production_safe"] is False
    assert comparison["metadata"]["match_strategy"] == "exact_affix_id"

    assert comparison["summary"]["bundle_affix_count"] == 1
    assert comparison["summary"]["missing_in_legacy_count"] == 1
    assert comparison["missing_in_legacy"][0]["affix_id"] == SENTINEL_AFFIX_ID
    assert comparison["missing_in_legacy"][0]["name"] == SENTINEL_AFFIX_NAME


def test_compare_legacy_endpoint_reports_legacy_only_affixes(app):
    _enable_sentinel_bundle(app)

    response = app.test_client().get("/experimental/forge-safe-affixes/compare-legacy?limit=3")

    assert response.status_code == 200
    comparison = response.get_json()["comparison"]
    assert comparison["summary"]["legacy_affix_count"] > 0
    assert comparison["summary"]["missing_in_bundle_count"] > 0
    assert 0 < len(comparison["missing_in_bundle"]) <= 3


def test_compare_legacy_endpoint_does_not_affect_ref_affixes(app):
    _enable_sentinel_bundle(app)
    client = app.test_client()

    compare_response = client.get("/experimental/forge-safe-affixes/compare-legacy?limit=5")
    ref_response = client.get("/api/ref/affixes?tag=__production_non_consumption_guard__")

    assert compare_response.status_code == 200
    assert ref_response.status_code == 200
    ref_body = ref_response.get_json()
    assert ref_body["errors"] is None
    assert isinstance(ref_body["data"], list)
    assert SENTINEL_AFFIX_NAME not in str(ref_body["data"])
    assert SENTINEL_MODIFIER_ID not in str(ref_body["data"])


def test_compare_legacy_endpoint_honors_limit(app):
    _enable_sentinel_bundle(app)

    response = app.test_client().get("/experimental/forge-safe-affixes/compare-legacy?limit=1")

    assert response.status_code == 200
    comparison = response.get_json()["comparison"]
    assert len(comparison["missing_in_legacy"]) <= 1
    assert len(comparison["missing_in_bundle"]) <= 1
    assert len(comparison["differences"]) <= 1
    assert comparison["metadata"]["limit"] == 1
    assert comparison["metadata"]["truncated"]["missing_in_bundle"] is True


def test_compare_legacy_endpoint_rejects_invalid_limit(app):
    _enable_sentinel_bundle(app)

    response = app.test_client().get("/experimental/forge-safe-affixes/compare-legacy?limit=nope")

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "invalid_query"
    assert "limit must be an integer" in body["message"]


def _enable_sentinel_bundle(app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = str(SENTINEL_BUNDLE_PATH)
