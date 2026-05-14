import json

import pytest

from app.services.affix_catalog_service import AffixCatalogFilters, AffixCatalogService, AffixCatalogUnavailable


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


def test_service_uses_legacy_when_disabled(app):
    app.config["FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED"] = False
    svc = AffixCatalogService(app)
    registry_before = app.extensions["affix_registry"]
    result = svc.list_affixes(limit=5, offset=0)
    assert result["data_source"] == "legacy"
    assert len(result["affixes"]) <= 5
    assert app.extensions["affix_registry"] is registry_before


def test_service_uses_forge_safe_when_enabled_read_only(app, tmp_path):
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="read_only",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(write_export(tmp_path)),
    )
    svc = AffixCatalogService(app)
    result = svc.list_affixes(limit=10, offset=0)
    assert result["data_source"] == "forge_safe"
    assert result["total"] == 2
    assert svc.get_affix("health")["name"] == "Health"


def test_service_search_filter_and_pagination(app, tmp_path):
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="active",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(write_export(tmp_path)),
    )
    svc = AffixCatalogService(app)
    filtered = svc.search_affixes("res", filters=AffixCatalogFilters(source_type="suffix", item_type="ring"))
    assert filtered["total"] == 1
    assert filtered["affixes"][0]["id"] == "fire_res"
    paged = svc.list_affixes(limit=1, offset=1)
    assert paged["limit"] == 1
    assert paged["offset"] == 1
    assert len(paged["affixes"]) == 1


def test_service_invalid_export_fails_cleanly(app, tmp_path):
    broken = tmp_path / "missing.json"
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="read_only",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(broken),
    )
    with pytest.raises(AffixCatalogUnavailable):
        AffixCatalogService(app).list_affixes()


def test_service_summary_metadata(app, tmp_path):
    app.config.update(
        FORGE_SAFE_AFFIX_CONSUMPTION_ENABLED=True,
        FORGE_SAFE_AFFIX_CONSUMPTION_MODE="read_only",
        FORGE_SAFE_AFFIX_EXPORT_PATH=str(write_export(tmp_path)),
    )
    summary = AffixCatalogService(app).summary()
    assert summary["active_source"] == "forge_safe"
    assert summary["forge_safe_count"] == 2
    assert summary["production_consumer"] is False
