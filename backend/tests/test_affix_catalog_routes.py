import json


def write_export(tmp_path):
    path = tmp_path / "forge_safe.json"
    path.write_text(json.dumps({
        "export_policy": "diagnostic_read_only",
        "production_safe": False,
        "summary": {
            "exported_affix_records": 2,
            "total_affix_records_seen": 2,
            "excluded_affix_records": 0,
            "forge_safe_records_only": True,
            "production_safe": False,
            "export_status": "pass",
        },
        "records": [
            {
                "id": "health",
                "affix_id": "health",
                "name": "Health",
                "affix_name": "Health",
                "display_name": "Health",
                "source_type": "prefix",
                "item_types": ["helm"],
                "eligible_item_types": ["helm"],
                "production_consumer": False,
                "safety": {
                    "forge_safe": True,
                    "export_policy": "diagnostic_read_only",
                    "production_safe": False,
                },
            },
            {
                "id": "fire_res",
                "affix_id": "fire_res",
                "name": "Fire Resistance",
                "affix_name": "Fire Resistance",
                "display_name": "Fire Resistance",
                "source_type": "suffix",
                "item_types": ["ring"],
                "eligible_item_types": ["ring"],
                "production_consumer": False,
                "safety": {
                    "forge_safe": True,
                    "export_policy": "diagnostic_read_only",
                    "production_safe": False,
                },
            },
        ],
    }), encoding="utf-8")
    return path


def test_catalog_disabled_returns_clean_error(client, app):
    app.config["FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED"] = False
    response = client.get("/api/affixes/catalog")
    assert response.status_code == 404
    assert response.get_json()["errors"]


def test_catalog_endpoints(client, app, tmp_path):
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="read_only",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(write_export(tmp_path)),
    )
    response = client.get("/api/affixes/catalog?limit=1&offset=0&q=health&source_type=prefix&item_type=helm")
    assert response.status_code == 200
    body = response.get_json()
    assert body["meta"]["data_source"] == "forge_safe"
    assert body["data"][0]["id"] == "health"
    assert body["data"][0]["production_consumer"] is False

    detail = client.get("/api/affixes/catalog/health")
    assert detail.status_code == 200
    assert detail.get_json()["data"]["name"] == "Health"

    summary = client.get("/api/affixes/catalog/summary")
    assert summary.status_code == 200
    assert summary.get_json()["data"]["forge_safe_count"] == 2


def test_catalog_invalid_export_503(client, app, tmp_path):
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="read_only",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(tmp_path / "missing.json"),
    )
    assert client.get("/api/affixes/catalog").status_code == 503
