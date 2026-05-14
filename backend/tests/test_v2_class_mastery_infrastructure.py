import json
from pathlib import Path

import pytest

from app.repositories.v2.class_mastery_repository import V2ClassMasteryBundleError, V2ClassMasteryRepository
from scripts.report_v2_class_mastery_bundle import build_v2_class_mastery_bundle, validate_v2_class_mastery_records


def test_v2_class_mastery_bundle_generation(tmp_path):
    source, references = _write_sources(tmp_path)

    bundle, validation = build_v2_class_mastery_bundle(source, reference_bundle_paths=references)

    assert bundle["summary"]["class_count"] == 1
    assert bundle["summary"]["mastery_count"] == 1
    assert bundle["summary"]["mapped_restriction_label_count"] == 2
    assert validation["summary"]["error_count"] == 0
    class_record = bundle["records"]["classes"][0]
    mastery_record = bundle["records"]["masteries"][0]
    assert class_record["canonical_id"] == "class:mage"
    assert class_record["mastery_ids"] == ["mastery:mage:runemaster"]
    assert class_record["known_restriction_labels"] == ["Mage"]
    assert mastery_record["canonical_id"] == "mastery:mage:runemaster"
    assert mastery_record["class_id"] == "class:mage"
    assert mastery_record["known_restriction_labels"] == ["Runemaster"]
    assert class_record["stable_calculable"] is False


def test_v2_class_mastery_validation_detects_duplicate_ids(tmp_path):
    bundle, _validation = _bundle(tmp_path)
    classes = bundle["records"]["classes"]
    masteries = bundle["records"]["masteries"]
    classes.append(dict(classes[0]))
    masteries.append(dict(masteries[0]))

    report = validate_v2_class_mastery_records(classes, masteries)

    assert report["summary"]["duplicate_class_id_count"] == 1
    assert report["summary"]["duplicate_mastery_id_count"] == 1
    with pytest.raises(V2ClassMasteryBundleError, match="Duplicate canonical_id"):
        V2ClassMasteryRepository("<bundle>").load_payload(bundle)


def test_v2_class_mastery_validation_detects_missing_parent_and_class_link(tmp_path):
    bundle, _validation = _bundle(tmp_path)
    bundle["records"]["classes"][0]["mastery_ids"] = ["mastery:mage:missing"]
    bundle["records"]["masteries"][0]["class_id"] = "class:missing"

    report = validate_v2_class_mastery_records(bundle["records"]["classes"], bundle["records"]["masteries"])

    assert report["summary"]["class_links_missing_mastery_count"] == 1
    assert report["summary"]["mastery_parent_missing_count"] == 1
    with pytest.raises(V2ClassMasteryBundleError, match="links missing mastery"):
        V2ClassMasteryRepository("<bundle>").load_payload(bundle)


def test_v2_class_mastery_validation_requires_provenance_and_support_status(tmp_path):
    bundle, _validation = _bundle(tmp_path)
    bundle["records"]["classes"][0]["provenance"] = {}
    bundle["records"]["masteries"][0].pop("support_status")

    report = validate_v2_class_mastery_records(bundle["records"]["classes"], bundle["records"]["masteries"])

    assert report["summary"]["missing_provenance_count"] == 1
    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2ClassMasteryBundleError, match="missing provenance"):
        V2ClassMasteryRepository("<bundle>").load_payload(bundle)


def test_v2_class_mastery_validation_requires_manual_bridge_marking(tmp_path):
    bundle, _validation = _bundle(tmp_path)
    bundle["records"]["classes"][0]["manual_bridge"] = True

    report = validate_v2_class_mastery_records(bundle["records"]["classes"], bundle["records"]["masteries"])

    assert report["summary"]["manual_bridge_not_marked_count"] == 1
    with pytest.raises(V2ClassMasteryBundleError, match="manual bridge"):
        V2ClassMasteryRepository("<bundle>").load_payload(bundle)


def test_v2_class_mastery_repository_lookup_filter_and_debug(tmp_path):
    bundle, _validation = _bundle(tmp_path)
    repository = V2ClassMasteryRepository("<bundle>").load_payload(bundle)

    assert repository.count_classes() == 1
    assert repository.count_masteries() == 1
    assert repository.get_class("class:mage")["display_name"] == "Mage"
    assert repository.get_mastery("mastery:mage:runemaster")["display_name"] == "Runemaster"
    assert repository.filter_classes(query="mage")[0]["canonical_id"] == "class:mage"
    assert repository.filter_masteries(class_id="class:mage")[0]["canonical_id"] == "mastery:mage:runemaster"
    assert repository.get_masteries_by_class("class:mage")[0]["canonical_id"] == "mastery:mage:runemaster"
    assert repository.debug_summary()["production_consumer"] is False


def test_v2_class_mastery_routes(app, tmp_path):
    bundle, _validation = _bundle(tmp_path)
    path = tmp_path / "v2_class_mastery_bundle.json"
    path.write_text(json.dumps(bundle), encoding="utf-8")
    app.config["V2_CLASS_MASTERY_BUNDLE_PATH"] = str(path)
    client = app.test_client()

    classes = client.get("/experimental/v2/classes?q=mage")
    assert classes.status_code == 200
    assert classes.get_json()["records"][0]["canonical_id"] == "class:mage"

    detail = client.get("/experimental/v2/classes/class:mage")
    assert detail.status_code == 200
    assert detail.get_json()["masteries"][0]["canonical_id"] == "mastery:mage:runemaster"

    masteries = client.get("/experimental/v2/masteries?class_id=class:mage")
    assert masteries.status_code == 200
    assert masteries.get_json()["records"][0]["canonical_id"] == "mastery:mage:runemaster"

    mastery_detail = client.get("/experimental/v2/masteries/mastery:mage:runemaster")
    assert mastery_detail.status_code == 200
    assert mastery_detail.get_json()["record"]["class_id"] == "class:mage"

    debug = client.get("/experimental/v2/classes/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_safe"] is False


def test_v2_class_mastery_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "class_mastery_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "app" / "repositories" / "v2" / "paths.py",
        root / "backend" / "app" / "repositories" / "v2" / "registry.py",
        root / "backend" / "scripts" / "report_v2_class_mastery_bundle.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_class_mastery_bundle.json", "V2ClassMasteryRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _bundle(tmp_path: Path) -> tuple[dict, dict]:
    source, references = _write_sources(tmp_path)
    return build_v2_class_mastery_bundle(source, reference_bundle_paths=references)


def _write_sources(tmp_path: Path) -> tuple[Path, list[Path]]:
    source = tmp_path / "classes.json"
    reference = tmp_path / "v2_affix_bundle.json"
    source.write_text(json.dumps(_source_classes()), encoding="utf-8")
    reference.write_text(json.dumps(_reference_bundle()), encoding="utf-8")
    return source, [reference]


def _source_classes() -> dict:
    return {
        "_meta": {"game_build": {"installPath": "D:\\LastEpochTools\\game_files\\current\\1.4.6_22986002"}},
        "classes": [
            {
                "id": 1,
                "name": "Mage",
                "displayName": "Mage",
                "treeID": "mg-1",
                "stats": {"baseHealth": 100},
                "abilities": {"defaultPathIds": [101], "knownPathIds": [102], "unlockable": [{"abilityPathId": 103, "level": 2}]},
                "masteries": [
                    {"name": "Mage", "localizationKey": "Class_Mage", "masteryAbilityPathId": 0, "abilityPathIds": []},
                    {"name": "Runemaster", "localizationKey": "Mastery_Runemaster", "masteryAbilityPathId": 201, "abilityPathIds": [202]},
                ],
            }
        ],
    }


def _reference_bundle() -> dict:
    return {
        "records": {
            "affixes": [
                {
                    "canonical_id": "affix:equipment:1",
                    "class_restrictions": ["Mage"],
                    "mastery_restrictions": ["Runemaster"],
                }
            ]
        }
    }
