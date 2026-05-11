import json

import pytest


@pytest.fixture(autouse=True)
def reset_forge_safe_affix_catalog_config(app):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""
    yield
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""


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


def _enable_catalog(app, path):
    app.config["FORGE_SAFE_AFFIX_CATALOG_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)


def _write_export(tmp_path, records):
    path = tmp_path / "forge_safe_affixes.json"
    path.write_text(json.dumps(_payload(records)), encoding="utf-8")
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
