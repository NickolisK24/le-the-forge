import json
from pathlib import Path

import pytest

from app.repositories.v2.item_repository import V2ItemBundleError, V2ItemRepository
from scripts.report_v2_item_bundles import build_v2_item_bundles, validate_v2_item_records


def test_v2_item_base_and_implicit_bundle_generation(tmp_path):
    source = tmp_path / "items.json"
    source.write_text(json.dumps(_source_items()), encoding="utf-8")

    base_bundle, implicit_bundle, validation = build_v2_item_bundles(source)

    assert base_bundle["summary"]["item_base_count"] == 1
    assert implicit_bundle["summary"]["implicit_count"] == 1
    assert validation["summary"]["error_count"] == 0
    base = base_bundle["records"]["item_bases"][0]
    implicit = implicit_bundle["records"]["implicits"][0]
    assert base["canonical_id"] == "item_base:equippable:0:1"
    assert base["implicit_ids"] == [implicit["canonical_id"]]
    assert implicit["item_base_id"] == base["canonical_id"]
    assert implicit["modifier_rows"][0]["provenance"]["source_id"] == "equippable:0:1:implicit:0"


def test_v2_item_repository_detects_duplicate_base_id():
    base_bundle, implicit_bundle = _bundles()
    base_bundle["records"]["item_bases"].append(dict(base_bundle["records"]["item_bases"][0]))

    with pytest.raises(V2ItemBundleError, match="Duplicate canonical_id"):
        V2ItemRepository("<base>", "<implicit>").load_payloads(base_bundle, implicit_bundle)


def test_v2_item_repository_requires_base_provenance():
    base_bundle, implicit_bundle = _bundles()
    base_bundle["records"]["item_bases"][0]["provenance"] = {}

    with pytest.raises(V2ItemBundleError, match="provenance.source_path"):
        V2ItemRepository("<base>", "<implicit>").load_payloads(base_bundle, implicit_bundle)


def test_v2_item_validation_requires_support_status():
    base_bundle, implicit_bundle = _bundles()
    base_bundle["records"]["item_bases"][0].pop("support_status")

    report = validate_v2_item_records(
        base_bundle["records"]["item_bases"],
        implicit_bundle["records"]["implicits"],
    )

    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2ItemBundleError, match="invalid support_status"):
        V2ItemRepository("<base>", "<implicit>").load_payloads(base_bundle, implicit_bundle)


def test_v2_item_validation_detects_missing_implicit_base_link():
    base_bundle, implicit_bundle = _bundles()
    implicit_bundle["records"]["implicits"][0]["item_base_id"] = "item_base:missing"

    report = validate_v2_item_records(
        base_bundle["records"]["item_bases"],
        implicit_bundle["records"]["implicits"],
    )

    assert report["summary"]["implicit_base_link_missing_count"] == 1
    with pytest.raises(V2ItemBundleError, match="references missing item base"):
        V2ItemRepository("<base>", "<implicit>").load_payloads(base_bundle, implicit_bundle)


def test_v2_item_repository_lookup_filter_implicit_and_debug():
    base_bundle, implicit_bundle = _bundles()
    repository = V2ItemRepository("<base>", "<implicit>").load_payloads(base_bundle, implicit_bundle)

    assert repository.count_bases() == 1
    assert repository.count_implicits() == 1
    assert repository.get_base("item_base:equippable:0:1")["display_name"] == "Iron Casque"
    assert repository.filter_bases(slot="helmet")[0]["canonical_id"] == "item_base:equippable:0:1"
    assert repository.get_implicits_for_base("item_base:equippable:0:1")[0]["canonical_id"] == "implicit:equippable:0:1:0"
    assert repository.debug_summary()["production_consumer"] is False


def test_v2_item_routes(app, tmp_path):
    base_bundle, implicit_bundle = _bundles()
    base_path = tmp_path / "v2_item_base_bundle.json"
    implicit_path = tmp_path / "v2_item_implicit_bundle.json"
    base_path.write_text(json.dumps(base_bundle), encoding="utf-8")
    implicit_path.write_text(json.dumps(implicit_bundle), encoding="utf-8")
    app.config["V2_ITEM_BASE_BUNDLE_PATH"] = str(base_path)
    app.config["V2_ITEM_IMPLICIT_BUNDLE_PATH"] = str(implicit_path)
    client = app.test_client()

    bases = client.get("/experimental/v2/items/bases?slot=helmet")
    assert bases.status_code == 200
    assert bases.get_json()["records"][0]["canonical_id"] == "item_base:equippable:0:1"

    detail = client.get("/experimental/v2/items/bases/item_base:equippable:0:1")
    assert detail.status_code == 200
    assert detail.get_json()["implicits"][0]["canonical_id"] == "implicit:equippable:0:1:0"

    implicits = client.get("/experimental/v2/items/implicits?base_id=item_base:equippable:0:1")
    assert implicits.status_code == 200
    assert implicits.get_json()["records"][0]["item_base_id"] == "item_base:equippable:0:1"

    debug = client.get("/experimental/v2/items/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_safe"] is False


def test_v2_item_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "item_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "app" / "repositories" / "v2" / "paths.py",
        root / "backend" / "app" / "repositories" / "v2" / "registry.py",
        root / "backend" / "scripts" / "report_v2_item_bundles.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_item_base_bundle.json", "v2_item_implicit_bundle.json", "V2ItemRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _source_items() -> dict:
    return {
        "_meta": {"game_build": {"installPath": "D:\\LastEpochTools\\game_files\\current\\1.4.6_22986002"}},
        "equippable": [
            {
                "name": "Helmets",
                "displayName": "Helmet",
                "baseTypeID": 0,
                "maximumAffixes": 4,
                "maxSockets": 0,
                "affixEffectModifier": 0.0,
                "gridSize": [2, 2],
                "type": "HELMET",
                "subTypes": [
                    {
                        "name": "Iron Helmet",
                        "displayName": "Iron Casque",
                        "subTypeID": 1,
                        "levelRequirement": 10,
                        "cannotDrop": False,
                        "isLegacySubType": False,
                        "classRequirement": "Any",
                        "subClassRequirement": "Any",
                        "attackRate": 1.0,
                        "addedWeaponRange": 0.0,
                        "IMSetTier": 8,
                        "implicits": [
                            {
                                "property": "Armour",
                                "modifierType": "ADDED",
                                "value": 40.0,
                                "maxValue": 40.0,
                                "tags": ["None"],
                            }
                        ],
                    }
                ],
            },
            {"baseTypeID": 25, "type": "IDOL_1X1_ETERRA", "subTypes": [{"subTypeID": 0}]},
        ],
    }


def _bundles() -> tuple[dict, dict]:
    base = {
        "schema_version": "v2.item_base_bundle.1",
        "summary": {"item_base_count": 1, "validation_error_count": 0},
        "records": {
            "item_bases": [
                {
                    "canonical_id": "item_base:equippable:0:1",
                    "display_name": "Iron Casque",
                    "source_id": "equippable:0:1",
                    "source_file": "items.json",
                    "support_status": "partial",
                    "trust_level": "generated_from_game_data",
                    "provenance": {
                        "source_path": "items.json",
                        "source_type": "item_base",
                        "source_id": "equippable:0:1",
                        "extraction_method": "test_fixture",
                        "schema_version": "v2.item.1",
                    },
                    "item_category": "equipment",
                    "item_type": "helmet",
                    "subtype": "Iron Helmet",
                    "equipment_slot": "helmet",
                    "slot": "helmet",
                    "classification": "armor",
                    "class_restrictions": [],
                    "mastery_restrictions": [],
                    "requirements": {"level": 10, "attributes": {}},
                    "implicit_ids": ["implicit:equippable:0:1:0"],
                    "base_stats": {},
                    "stable_calculable": False,
                    "warnings": [],
                    "raw_reference": {},
                    "normalized_fields": {},
                    "consumer_safe_fields": {},
                }
            ]
        },
    }
    implicit = {
        "schema_version": "v2.item_implicit_bundle.1",
        "summary": {"implicit_count": 1, "validation_error_count": 0},
        "records": {
            "implicits": [
                {
                    "canonical_id": "implicit:equippable:0:1:0",
                    "display_name": "ADDED Armour",
                    "source_id": "equippable:0:1:implicit:0",
                    "source_file": "items.json",
                    "support_status": "partial",
                    "trust_level": "generated_from_game_data",
                    "provenance": {
                        "source_path": "items.json",
                        "source_type": "item_implicit",
                        "source_id": "equippable:0:1:implicit:0",
                        "extraction_method": "test_fixture",
                        "schema_version": "v2.item.1",
                    },
                    "item_base_id": "item_base:equippable:0:1",
                    "item_type": "helmet",
                    "modifier_references": [
                        {"modifier_id": "item_implicit:equippable:0:1:0", "property": "Armour"}
                    ],
                    "modifier_rows": [
                        {
                            "modifier_id": "item_implicit:equippable:0:1:0",
                            "property": "Armour",
                            "support_status": "partial",
                            "trust_level": "generated_from_game_data",
                            "stable_calculable": False,
                            "provenance": {
                                "source_path": "items.json",
                                "source_type": "item_implicit",
                                "source_id": "equippable:0:1:implicit:0",
                                "extraction_method": "test_fixture",
                                "schema_version": "v2.item.1",
                            },
                        }
                    ],
                    "stable_calculable": False,
                    "warnings": [],
                    "raw_reference": {},
                    "normalized_fields": {},
                    "consumer_safe_fields": {},
                }
            ]
        },
    }
    return base, implicit
