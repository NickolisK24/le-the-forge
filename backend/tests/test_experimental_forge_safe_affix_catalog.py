import json

import pytest


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


def test_endpoint_disabled_by_default(client):
    response = client.get("/experimental/forge-safe-affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "experimental_catalog_disabled"


def test_endpoint_succeeds_when_enabled(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1), _record(2)]))

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["experimental"] is True
    assert body["read_only"] is True
    assert body["production_consumer"] is False
    assert body["data_source"] == "forge_safe_canonical_affixes"
    assert body["result_count"] == 2
    assert body["total_loaded_count"] == 2
    assert body["export_policy"] == "deterministic_affix_only"
    assert body["export_status"] == "warning"
    assert body["total_affix_records_seen"] == 2
    assert body["excluded_affix_records"] == 0
    assert [record["affix_id"] for record in body["records"]] == [1, 2]


def test_limit_and_offset_work(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1), _record(2), _record(3)]))

    response = app.test_client().get("/experimental/forge-safe-affixes?limit=1&offset=1")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["limit"] == 1
    assert body["query"]["offset"] == 1
    assert body["result_count"] == 1
    assert body["records"][0]["affix_id"] == 2


def test_q_search_works(app, tmp_path):
    _enable_catalog(
        app,
        _write_export(tmp_path, [_record(1, name="Void Penetration"), _record(2, name="Armor")]),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes?q=void")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["q"] == "void"
    assert [record["affix_id"] for record in body["records"]] == [1]


def test_affix_id_lookup_works(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1), _record(7)]))

    response = app.test_client().get("/experimental/forge-safe-affixes?affix_id=7")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["affix_id"] == "7"
    assert body["result_count"] == 1
    assert body["records"][0]["affix_id"] == 7


def test_source_type_filter_works(app, tmp_path):
    _enable_catalog(
        app,
        _write_export(tmp_path, [_record(1, source_type="equipment"), _record(2, source_type="idol")]),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes?source_type=idol")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["source_type"] == "idol"
    assert [record["affix_id"] for record in body["records"]] == [2]


def test_item_type_filter_works(app, tmp_path):
    _enable_catalog(
        app,
        _write_export(
            tmp_path,
            [
                _record(1, item_type="Equipment", eligible_item_types=["AMULET"]),
                _record(2, item_type="Idol", eligible_item_types=["IDOL_1X1"]),
            ],
        ),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes?item_type=IDOL_1X1")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["item_type"] == "IDOL_1X1"
    assert [record["affix_id"] for record in body["records"]] == [2]


def test_invalid_limit_returns_clean_400(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1)]))

    response = app.test_client().get("/experimental/forge-safe-affixes?limit=nope")

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "invalid_query"
    assert "limit must be an integer" in body["message"]


def test_invalid_export_path_fails_cleanly(app, tmp_path):
    _enable_catalog(app, tmp_path / "missing.json")

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "export_file_missing"


def test_invalid_export_validation_fails_cleanly(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1, forge_safe=False)]))

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "export_validation_failed"
    assert "forge_safe=true" in body["message"]


def test_endpoint_does_not_mutate_existing_affix_registry(app, tmp_path):
    _enable_catalog(app, _write_export(tmp_path, [_record(1)]))
    registry_before = app.extensions["affix_registry"]

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 200
    assert app.extensions["affix_registry"] is registry_before


def test_bundle_enabled_returns_bundle_source(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(
            tmp_path,
            [_bundle_affix(1), _bundle_affix(2)],
            [_bundle_modifier("equipment:1", "equipment:1"), _bundle_modifier("equipment:2", "equipment:2")],
        ),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["data_source"] == "forge_safe_affix_bundle"
    assert body["read_only"] is True
    assert body["production_consumer"] is False
    assert body["total_affixes"] == 2
    assert body["total_modifiers"] == 2
    assert body["result_count"] == 2
    assert body["export_policy"] == "deterministic_affix_bundle"
    assert body["bundle_summary"]["affix_count"] == 2
    assert body["records"][0]["modifier_count"] == 1
    assert "modifiers" not in body["records"][0]


def test_bundle_include_modifiers_works(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(
            tmp_path,
            [_bundle_affix(1)],
            [
                _bundle_modifier("equipment:1-a", "equipment:1"),
                _bundle_modifier("equipment:1-b", "equipment:1"),
            ],
        ),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes?include_modifiers=true")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["include_modifiers"] is True
    assert body["records"][0]["modifier_count"] == 2
    assert [modifier["modifier_id"] for modifier in body["records"][0]["modifiers"]] == [
        "equipment:1-a",
        "equipment:1-b",
    ]


def test_bundle_detail_endpoint_returns_affix_with_modifiers(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(
            tmp_path,
            [_bundle_affix(7, name="Void Penetration")],
            [_bundle_modifier("equipment:7", "equipment:7")],
        ),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes/7?include_modifiers=true")

    assert response.status_code == 200
    body = response.get_json()
    assert body["query"]["affix_id"] == "7"
    assert body["records"][0]["affix_name"] == "Void Penetration"
    assert body["records"][0]["modifiers"][0]["modifier_id"] == "equipment:7"


def test_bundle_limit_offset_search_and_filters(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(
            tmp_path,
            [
                _bundle_affix(1, name="Void Penetration", eligible_item_types=["AMULET"]),
                _bundle_affix(2, name="Armor", source_type="idol", item_type="Idol", eligible_item_types=["IDOL_1X1"]),
                _bundle_affix(3, name="Cast Speed"),
            ],
            [
                _bundle_modifier("equipment:1", "equipment:1"),
                _bundle_modifier("idol:2", "idol:2"),
                _bundle_modifier("equipment:3", "equipment:3"),
            ],
        ),
    )

    client = app.test_client()
    assert [record["affix_id"] for record in client.get("/experimental/forge-safe-affixes?limit=1&offset=1").get_json()["records"]] == [2]
    assert [record["affix_id"] for record in client.get("/experimental/forge-safe-affixes?q=void").get_json()["records"]] == [1]
    assert [record["affix_id"] for record in client.get("/experimental/forge-safe-affixes?affix_id=3").get_json()["records"]] == [3]
    assert [record["affix_id"] for record in client.get("/experimental/forge-safe-affixes?source_type=idol").get_json()["records"]] == [2]
    assert [record["affix_id"] for record in client.get("/experimental/forge-safe-affixes?item_type=IDOL_1X1").get_json()["records"]] == [2]


def test_bundle_invalid_path_fails_cleanly(app, tmp_path):
    _enable_bundle(app, tmp_path / "missing.json")

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "bundle_file_missing"


def test_bundle_validation_failure_fails_cleanly(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(
            tmp_path,
            [_bundle_affix(1, forge_safe=False)],
            [_bundle_modifier("equipment:1", "equipment:1")],
        ),
    )

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "bundle_validation_failed"
    assert "forge_safe=true" in body["message"]


def test_bundle_endpoint_does_not_mutate_existing_affix_registry(app, tmp_path):
    _enable_bundle(
        app,
        _write_bundle(tmp_path, [_bundle_affix(1)], [_bundle_modifier("equipment:1", "equipment:1")]),
    )
    registry_before = app.extensions["affix_registry"]

    response = app.test_client().get("/experimental/forge-safe-affixes")

    assert response.status_code == 200
    assert app.extensions["affix_registry"] is registry_before


def _enable_catalog(app, path):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)


def _enable_bundle(app, path):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_BUNDLE_PATH"] = str(path)


def _write_export(tmp_path, records):
    path = tmp_path / "forge_safe_affixes.json"
    path.write_text(json.dumps(_payload(records)), encoding="utf-8")
    return path


def _write_bundle(tmp_path, affixes, modifiers):
    path = tmp_path / "forge_safe_affix_bundle.json"
    path.write_text(json.dumps(_bundle_payload(affixes, modifiers)), encoding="utf-8")
    return path


def _payload(records):
    return {
        "artifact": "forge_safe_canonical_affixes",
        "export_policy": "deterministic_affix_only",
        "production_safe": False,
        "records": records,
        "summary": {
            "export_status": "warning",
            "exported_affix_records": len(records),
            "excluded_affix_records": 0,
            "forge_safe_records_only": True,
            "production_safe": False,
            "total_affix_records_seen": len(records),
        },
    }


def _bundle_payload(affixes, modifiers):
    return {
        "schema_version": "1.0",
        "artifact": "forge_safe_affix_bundle",
        "artifact_type": "forge_safe_affix_bundle",
        "diagnostic_only": False,
        "export_policy": "deterministic_affix_bundle",
        "production_safe": False,
        "records": {
            "affixes": affixes,
            "modifiers": modifiers,
        },
        "summary": {
            "affix_count": len(affixes),
            "modifier_count": len(modifiers),
            "export_status": "pass",
            "forge_safe_records_only": True,
            "production_safe": False,
            "total_affix_records_seen": len(affixes),
            "total_modifier_records_seen": len(modifiers),
            "excluded_record_count": 0,
        },
        "cross_reference_validation": {
            "status": "pass",
            "unmatched_affix_count": 0,
            "unmatched_modifier_count": 0,
            "duplicate_affix_id_count": 0,
            "duplicate_modifier_id_count": 0,
        },
    }


def _record(
    affix_id,
    *,
    name=None,
    display_name=None,
    source_type="equipment",
    item_type="Equipment",
    eligible_item_types=None,
    forge_safe=True,
):
    affix_name = name or f"Affix {affix_id}"
    return {
        "affix_id": affix_id,
        "affix_name": affix_name,
        "display_name": display_name or affix_name,
        "source_type": source_type,
        "item_type": item_type,
        "eligible_item_types": eligible_item_types if eligible_item_types is not None else ["AMULET"],
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }


def _bundle_affix(
    affix_id,
    *,
    name=None,
    source_type="equipment",
    item_type="Equipment",
    eligible_item_types=None,
    forge_safe=True,
):
    affix_name = name or f"Affix {affix_id}"
    source_identity = f"{source_type}:{affix_id}"
    return {
        "affix_id": affix_id,
        "affix_name": affix_name,
        "display_name": affix_name,
        "source_type": source_type,
        "item_type": item_type,
        "eligible_item_types": eligible_item_types if eligible_item_types is not None else ["AMULET"],
        "provenance": {
            "source_affix_identity": source_identity,
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }


def _bundle_modifier(modifier_id, source_affix_identity):
    return {
        "modifier_id": modifier_id,
        "modifier_name": f"Modifier {modifier_id}",
        "source": {
            "source_affix_identity": source_affix_identity,
            "source_type": source_affix_identity.split(":", 1)[0],
        },
        "provenance": {
            "source_affix_identity": source_affix_identity,
            "source_path": "exports_json/affixes.json",
        },
        "safety": {
            "export_policy": "deterministic_modifier_only",
            "forge_safe": True,
            "production_safe": False,
        },
    }
