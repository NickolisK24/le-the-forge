import json
from pathlib import Path

import pytest

from app.repositories.v2.unique_set_repository import V2UniqueSetBundleError, V2UniqueSetRepository
from scripts.report_v2_unique_set_bundles import (
    build_v2_unique_set_bundles,
    unsupported_special_behavior_report,
    validate_v2_unique_set_records,
)


def test_v2_unique_and_set_bundle_generation(tmp_path):
    source_uniques, source_set_bonuses, item_bases = _write_sources(tmp_path)

    unique_bundle, set_bundle, validation, unsupported = build_v2_unique_set_bundles(
        source_uniques,
        source_set_bonuses,
        item_bases,
    )

    assert unique_bundle["summary"]["unique_count"] == 2
    assert set_bundle["summary"]["set_group_count"] == 1
    assert set_bundle["summary"]["set_item_count"] == 1
    assert set_bundle["summary"]["set_bonus_count"] == 2
    assert validation["summary"]["error_count"] == 0
    assert unsupported["summary"]["classification_counts"] == {"partial_modifier": 1, "text_only_effect": 2}
    unique = unique_bundle["records"]["uniques"][0]
    assert unique["canonical_id"] == "unique:1"
    assert unique["base_item_id"] == "item_base:equippable:0:1"
    assert unique["modifier_rows"][0]["support_status"] == "partial"
    assert unique["stable_calculable"] is False


def test_v2_unique_validation_detects_duplicate_unique_id(tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    unique_bundle["records"]["uniques"].append(dict(unique_bundle["records"]["uniques"][0]))

    with pytest.raises(V2UniqueSetBundleError, match="Duplicate canonical_id"):
        V2UniqueSetRepository("<unique>", "<set>").load_payloads(unique_bundle, set_bundle)


def test_v2_set_validation_detects_duplicate_set_item_id(tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    set_bundle["records"]["set_items"].append(dict(set_bundle["records"]["set_items"][0]))

    report = validate_v2_unique_set_records(
        unique_bundle["records"]["uniques"],
        set_bundle["records"]["sets"],
        set_bundle["records"]["set_items"],
        set_bundle["records"]["set_bonuses"],
        {"item_base:equippable:0:1"},
    )

    assert report["summary"]["duplicate_set_item_id_count"] == 1
    with pytest.raises(V2UniqueSetBundleError, match="Duplicate canonical_id"):
        V2UniqueSetRepository("<unique>", "<set>").load_payloads(unique_bundle, set_bundle)


def test_v2_unique_set_validation_requires_provenance_and_support_status(tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    unique_bundle["records"]["uniques"][0]["provenance"] = {}
    set_bundle["records"]["set_items"][0].pop("support_status")

    report = validate_v2_unique_set_records(
        unique_bundle["records"]["uniques"],
        set_bundle["records"]["sets"],
        set_bundle["records"]["set_items"],
        set_bundle["records"]["set_bonuses"],
        {"item_base:equippable:0:1"},
    )

    assert report["summary"]["missing_provenance_count"] == 1
    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2UniqueSetBundleError, match="provenance.source_path"):
        V2UniqueSetRepository("<unique>", "<set>").load_payloads(unique_bundle, set_bundle)


def test_v2_unique_set_validation_detects_base_and_set_links(tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    unique_bundle["records"]["uniques"][0]["base_item_id"] = "item_base:missing"
    set_bundle["records"]["set_items"][0]["set_group_id"] = "set:missing"
    set_bundle["records"]["set_bonuses"][0]["set_group_id"] = "set:missing"

    report = validate_v2_unique_set_records(
        unique_bundle["records"]["uniques"],
        set_bundle["records"]["sets"],
        set_bundle["records"]["set_items"],
        set_bundle["records"]["set_bonuses"],
        {"item_base:equippable:0:1"},
    )

    assert report["summary"]["missing_base_link_count"] == 1
    assert report["summary"]["set_group_link_missing_count"] == 1
    assert report["summary"]["set_bonus_group_missing_count"] == 1


def test_v2_unique_set_unsupported_report_and_repository(tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    repository = V2UniqueSetRepository("<unique>", "<set>").load_payloads(unique_bundle, set_bundle)

    assert repository.count_uniques() == 2
    assert repository.count_sets() == 1
    assert repository.get_unique("unique:1")["display_name"] == "Test Unique"
    assert repository.filter_uniques(slot="helmet")[0]["canonical_id"] == "unique:1"
    assert repository.get_set("set:7")["display_name"] == "Test Set"
    assert repository.get_set_items("set:7")[0]["canonical_id"] == "set_item:10"
    assert repository.get_set_bonuses("set:7")[0]["canonical_id"] == "set_bonus:7:0"
    assert repository.debug_summary()["production_safe"] is False

    unsupported = unsupported_special_behavior_report(
        unique_bundle["records"]["uniques"],
        set_bundle["records"]["sets"],
        set_bundle["records"]["set_items"],
        set_bundle["records"]["set_bonuses"],
    )
    assert unsupported["summary"]["unsupported_or_text_only_count"] == 3


def test_v2_unique_set_routes(app, tmp_path):
    unique_bundle, set_bundle, _validation, _unsupported = _bundles(tmp_path)
    unique_path = tmp_path / "v2_unique_bundle.json"
    set_path = tmp_path / "v2_set_bundle.json"
    unique_path.write_text(json.dumps(unique_bundle), encoding="utf-8")
    set_path.write_text(json.dumps(set_bundle), encoding="utf-8")
    app.config["V2_UNIQUE_BUNDLE_PATH"] = str(unique_path)
    app.config["V2_SET_BUNDLE_PATH"] = str(set_path)
    client = app.test_client()

    uniques = client.get("/experimental/v2/uniques?slot=helmet")
    assert uniques.status_code == 200
    assert uniques.get_json()["records"][0]["canonical_id"] == "unique:1"

    unique_detail = client.get("/experimental/v2/uniques/unique:1")
    assert unique_detail.status_code == 200
    assert unique_detail.get_json()["record"]["display_name"] == "Test Unique"

    sets = client.get("/experimental/v2/sets")
    assert sets.status_code == 200
    assert sets.get_json()["records"][0]["canonical_id"] == "set:7"

    set_detail = client.get("/experimental/v2/sets/set:7")
    assert set_detail.status_code == 200
    assert set_detail.get_json()["items"][0]["canonical_id"] == "set_item:10"
    assert set_detail.get_json()["bonuses"][0]["canonical_id"] == "set_bonus:7:0"

    debug = client.get("/experimental/v2/uniques/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_consumer"] is False


def test_v2_unique_set_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "unique_set_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "scripts" / "report_v2_unique_set_bundles.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_unique_bundle.json", "v2_set_bundle.json", "V2UniqueSetRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _write_sources(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_uniques = tmp_path / "uniques.json"
    source_set_bonuses = tmp_path / "set_bonuses.json"
    item_bases = tmp_path / "v2_item_base_bundle.json"
    source_uniques.write_text(json.dumps(_source_uniques()), encoding="utf-8")
    source_set_bonuses.write_text(json.dumps(_source_set_bonuses()), encoding="utf-8")
    item_bases.write_text(json.dumps(_item_base_bundle()), encoding="utf-8")
    return source_uniques, source_set_bonuses, item_bases


def _bundles(tmp_path: Path) -> tuple[dict, dict, dict, dict]:
    return build_v2_unique_set_bundles(*_write_sources(tmp_path))


def _source_uniques() -> dict:
    return {
        "_meta": {"game_build": {"installPath": "D:\\LastEpochTools\\game_files\\current\\1.4.6_22986002"}},
        "uniques": [
            _item_record(1, "TestUnique", "Test Unique", mods=[_mod("Armour", 5.0, 10.0)]),
            _item_record(2, "TextOnlyUnique", "Text Only Unique", mods=[], tooltip="Summons a source-defined effect."),
        ],
        "setItems": [
            _item_record(10, "TestSetItem", "Test Set Item", set_id=7, mods=[_mod("Health", 3.0, 6.0)]),
        ],
        "setBonusData": {},
    }


def _source_set_bonuses() -> dict:
    return {
        "_meta": {"game_build": {"installPath": "D:\\LastEpochTools\\game_files\\current\\1.4.6_22986002"}},
        "setBonuses": [
            {
                "setId": 7,
                "setName": "Test Set",
                "mappingConfidence": "confirmed",
                "bonuses": [
                    {"kind": "mod", "piecesRequired": 2, "mod": _mod("Damage", 0.1, None)},
                    {"kind": "description", "piecesRequired": 3, "text": "Text-only behavior"},
                ],
            }
        ],
    }


def _item_record(item_id: int, name: str, display_name: str, *, mods: list[dict], set_id: int | None = None, tooltip: str | None = None) -> dict:
    record = {
        "id": item_id,
        "name": name,
        "displayName": display_name,
        "baseType": "HELMET",
        "subTypes": [1],
        "mods": mods,
        "legendaryType": "None",
        "canDropRandomly": True,
        "rerollChance": 0.0,
        "resolvedBaseItem": {
            "baseTypeID": 0,
            "type": "HELMET",
            "displayName": "Helmet",
            "subType": {"subTypeID": 1, "name": "Iron Helmet", "displayName": "Iron Casque", "levelRequirement": 10},
        },
        "resolvedImplicitMods": [],
        "resolutionStatus": "resolved",
    }
    if set_id is not None:
        record["isSetItem"] = True
        record["setId"] = set_id
    if tooltip:
        record["tooltipDescriptions"] = [{"text": tooltip}]
    return record


def _mod(property_name: str, value: float, max_value: float | None) -> dict:
    mod = {
        "value": value,
        "property": property_name,
        "tags": ["None"],
        "extraTag": 0,
        "modifierType": "ADDED",
    }
    if max_value is not None:
        mod["maxValue"] = max_value
    return mod


def _item_base_bundle() -> dict:
    return {
        "records": {
            "item_bases": [
                {
                    "canonical_id": "item_base:equippable:0:1",
                    "raw_reference": {"baseTypeID": 0, "subTypeID": 1},
                }
            ]
        }
    }
