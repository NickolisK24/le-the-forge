import json

import pytest


@pytest.fixture(autouse=True)
def reset_forge_safe_affix_debug_config(app):
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""
    yield
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = False
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = ""


def test_debug_endpoint_disabled_by_default(client):
    response = client.get("/debug/forge-safe-affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "debug_endpoint_disabled"


def test_debug_endpoint_works_when_enabled(app, tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(2)]))
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)

    response = app.test_client().get("/debug/forge-safe-affixes")

    assert response.status_code == 200
    body = response.get_json()
    assert body["success"] is True
    assert body["debug_only"] is True
    assert body["read_only"] is True
    assert body["production_consumer"] is False
    assert body["loaded_record_count"] == 2
    assert body["warning_count"] == 0
    assert body["export_policy"] == "deterministic_affix_only"
    assert body["export_status"] == "warning"
    assert body["total_affix_records_seen"] == 2
    assert body["excluded_affix_records"] == 0
    assert [record["affix_id"] for record in body["sample_records"]] == [1, 2]


def test_debug_endpoint_limit_parameter(app, tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(2), _record(3)]))
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)

    response = app.test_client().get("/debug/forge-safe-affixes?limit=2")

    assert response.status_code == 200
    body = response.get_json()
    assert body["sample_count"] == 2
    assert [record["affix_id"] for record in body["sample_records"]] == [1, 2]


def test_debug_endpoint_affix_id_filter(app, tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1), _record(7), _record(8)]))
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)

    response = app.test_client().get("/debug/forge-safe-affixes?affix_id=7")

    assert response.status_code == 200
    body = response.get_json()
    assert body["sample_count"] == 1
    assert body["sample_records"][0]["affix_id"] == 7
    assert body["sample_records"][0]["name"] == "Affix 7"


def test_debug_endpoint_missing_export_file_returns_clean_error(app, tmp_path):
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(tmp_path / "missing.json")

    response = app.test_client().get("/debug/forge-safe-affixes")

    assert response.status_code == 404
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "export_file_missing"


def test_debug_endpoint_invalid_export_returns_clean_error(app, tmp_path):
    path = tmp_path / "invalid.json"
    _write_json(path, _payload(records=[_record(1, forge_safe=False)]))
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)

    response = app.test_client().get("/debug/forge-safe-affixes")

    assert response.status_code == 422
    body = response.get_json()
    assert body["success"] is False
    assert body["error"] == "export_validation_failed"
    assert "forge_safe=true" in body["message"]


def test_debug_endpoint_does_not_mutate_production_affix_registry(app, tmp_path):
    path = tmp_path / "forge_safe_affixes.json"
    _write_json(path, _payload(records=[_record(1)]))
    app.config["FORGE_SAFE_AFFIX_DEBUG_ENDPOINT_ENABLED"] = True
    app.config["FORGE_SAFE_AFFIX_EXPORT_PATH"] = str(path)
    registry_before = app.extensions["affix_registry"]

    response = app.test_client().get("/debug/forge-safe-affixes")

    assert response.status_code == 200
    assert app.extensions["affix_registry"] is registry_before


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


def _record(affix_id, *, forge_safe=True):
    return {
        "affix_id": affix_id,
        "affix_name": f"Affix {affix_id}",
        "source_type": "equipment",
        "item_type": "Equipment",
        "eligible_item_types": ["AMULET"],
        "safety": {
            "export_policy": "deterministic_affix_only",
            "forge_safe": forge_safe,
            "production_safe": False,
        },
    }


def _write_json(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
