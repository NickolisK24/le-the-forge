import json
from pathlib import Path

import pytest

from app.repositories.v2.affix_repository import V2AffixBundleError, V2AffixRepository
from scripts.report_v2_affix_bundle import (
    build_v2_affix_bundle,
    validate_v2_affix_records,
)


def test_v2_affix_bundle_generation_and_reporting(tmp_path):
    source_path = tmp_path / "forge_safe_affix_bundle.json"
    source_path.write_text(json.dumps(_source_bundle()), encoding="utf-8")

    bundle = build_v2_affix_bundle(source_path)

    assert bundle["summary"]["affix_count"] == 1
    assert bundle["summary"]["support_status_counts"] == {"partial": 1}
    assert bundle["summary"]["stable_calculable_count"] == 0
    record = bundle["records"]["affixes"][0]
    assert record["canonical_id"] == "affix:equipment:1"
    assert record["display_name"] == "Test Health"
    assert record["provenance"]["source_path"] == "exports_json/affixes.json"
    assert record["modifier_references"][0]["property"] == "Health"


def test_v2_affix_validation_detects_duplicate_ids():
    payload = _v2_bundle()
    payload["records"]["affixes"].append(dict(payload["records"]["affixes"][0]))

    with pytest.raises(V2AffixBundleError, match="Duplicate canonical_id"):
        V2AffixRepository("<memory>").load_payload(payload)


def test_v2_affix_validation_requires_provenance():
    payload = _v2_bundle()
    payload["records"]["affixes"][0]["provenance"] = {}

    with pytest.raises(V2AffixBundleError, match="provenance.source_path"):
        V2AffixRepository("<memory>").load_payload(payload)


def test_v2_affix_validation_requires_support_status():
    payload = _v2_bundle()
    payload["records"]["affixes"][0].pop("support_status")

    report = validate_v2_affix_records(payload["records"]["affixes"])

    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2AffixBundleError, match="invalid support_status"):
        V2AffixRepository("<memory>").load_payload(payload)


def test_v2_affix_repository_lookup_filter_and_debug_summary():
    repository = V2AffixRepository("<memory>").load_payload(_v2_bundle())

    assert repository.count() == 1
    assert repository.get_affix("affix:equipment:1")["display_name"] == "Test Health"
    assert repository.filter_affixes(slot="helmet")[0]["canonical_id"] == "affix:equipment:1"
    assert repository.filter_affixes(item_type="helmet")[0]["canonical_id"] == "affix:equipment:1"
    assert repository.debug_summary()["support_status_counts"] == {"partial": 1}


def test_v2_affix_routes_list_detail_and_debug(app, tmp_path):
    bundle_path = tmp_path / "v2_affix_bundle.json"
    bundle_path.write_text(json.dumps(_v2_bundle()), encoding="utf-8")
    original_path = app.config.get("V2_AFFIX_BUNDLE_PATH")
    app.config["V2_AFFIX_BUNDLE_PATH"] = str(bundle_path)
    try:
        client = app.test_client()

        list_response = client.get("/experimental/v2/affixes?slot=HELMET")
        assert list_response.status_code == 200
        list_payload = list_response.get_json()
        assert list_payload["success"] is True
        assert list_payload["production_consumer"] is False
        assert list_payload["records"][0]["canonical_id"] == "affix:equipment:1"

        detail_response = client.get("/experimental/v2/affixes/affix:equipment:1")
        assert detail_response.status_code == 200
        assert detail_response.get_json()["record"]["display_name"] == "Test Health"

        debug_response = client.get("/experimental/v2/affixes/debug")
        assert debug_response.status_code == 200
        assert debug_response.get_json()["debug_summary"]["production_safe"] is False
    finally:
        if original_path is None:
            app.config.pop("V2_AFFIX_BUNDLE_PATH", None)
        else:
            app.config["V2_AFFIX_BUNDLE_PATH"] = original_path


def test_v2_affix_route_reports_missing_bundle(app, tmp_path):
    original_path = app.config.get("V2_AFFIX_BUNDLE_PATH")
    app.config["V2_AFFIX_BUNDLE_PATH"] = str(tmp_path / "missing.json")
    try:
        response = app.test_client().get("/experimental/v2/affixes")

        assert response.status_code == 404
        assert response.get_json()["error"]["code"] == "v2_affix_bundle_missing"
    finally:
        if original_path is None:
            app.config.pop("V2_AFFIX_BUNDLE_PATH", None)
        else:
            app.config["V2_AFFIX_BUNDLE_PATH"] = original_path


def test_v2_affix_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "affix_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "app" / "repositories" / "v2" / "paths.py",
        root / "backend" / "app" / "repositories" / "v2" / "registry.py",
        root / "backend" / "scripts" / "report_v2_affix_bundle.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_affix_bundle.json", "V2AffixRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _source_bundle() -> dict:
    return {
        "schema_version": "1.0.0",
        "export_policy": "deterministic_affix_bundle",
        "summary": {
            "production_safe": False,
            "forge_safe_records_only": True,
            "affix_count": 1,
            "modifier_count": 1,
        },
        "cross_reference_validation": {
            "status": "pass",
            "unmatched_affix_count": 0,
            "unmatched_modifier_count": 0,
            "duplicate_affix_id_count": 0,
            "duplicate_modifier_id_count": 0,
        },
        "records": {
            "affixes": [
                {
                    "affix_id": 1,
                    "affix_name": "Test Health",
                    "display_name": "Test Health",
                    "source_type": "equipment",
                    "item_type": "Equipment",
                    "eligible_item_types": ["HELMET"],
                    "categories": ["PREFIX"],
                    "tags": ["Health"],
                    "tier_data": [
                        {"tier": 1, "minRoll": 5, "maxRoll": 10, "tier_group": "T1"}
                    ],
                    "provenance": {
                        "source_affix_identity": "equipment:1",
                        "source_path": "exports_json/affixes.json",
                    },
                    "safety": {"forge_safe": True, "production_safe": False},
                }
            ],
            "modifiers": [
                {
                    "modifier_id": "equipment:1",
                    "modifier_type": "ADDED",
                    "property": "Health",
                    "tags": ["Health"],
                    "source": {"source_affix_identity": "equipment:1"},
                    "safety": {"forge_safe": True, "production_safe": False},
                }
            ],
        },
    }


def _v2_bundle() -> dict:
    return {
        "schema_version": "v2.affix_bundle.1",
        "summary": {
            "affix_count": 1,
            "source_modifier_count": 1,
            "records_with_warnings_count": 1,
            "validation_error_count": 0,
        },
        "records": {
            "affixes": [
                {
                    "canonical_id": "affix:equipment:1",
                    "display_name": "Test Health",
                    "source_id": "equipment:1",
                    "source_type": "equipment",
                    "support_status": "partial",
                    "trust_level": "generated_from_game_data",
                    "provenance": {
                        "source_path": "exports_json/affixes.json",
                        "source_type": "equipment",
                        "source_id": "equipment:1",
                        "extraction_method": "test_fixture",
                        "schema_version": "v2.affix_bundle.1",
                    },
                    "affix_domain": "equipment",
                    "item_applicability": ["HELMET"],
                    "slot_restrictions": ["HELMET"],
                    "item_type_restrictions": ["HELMET"],
                    "class_restrictions": [],
                    "mastery_restrictions": [],
                    "tier_ranges": [{"tier": 1, "min_value": 5, "max_value": 10}],
                    "modifier_references": [{"modifier_id": "equipment:1", "property": "Health"}],
                    "stable_calculable": False,
                }
            ]
        },
    }
