import json
from pathlib import Path

import pytest

from app.repositories.v2.idol_repository import V2IdolBundleError, V2IdolRepository
from scripts.report_v2_idol_bundles import build_v2_idol_bundles, validate_v2_idol_records


def test_v2_idol_and_affix_bundle_generation(tmp_path):
    source_items, affix_bundle = _write_sources(tmp_path)

    idol_bundle, idol_affix_bundle, validation = build_v2_idol_bundles(source_items, affix_bundle)

    assert idol_bundle["summary"]["idol_count"] == 1
    assert idol_affix_bundle["summary"]["idol_affix_count"] == 1
    assert validation["summary"]["error_count"] == 0
    idol = idol_bundle["records"]["idols"][0]
    affix = idol_affix_bundle["records"]["idol_affixes"][0]
    assert idol["canonical_id"] == "idol:25:0"
    assert idol["dimensions"] == {"width": 1, "height": 1}
    assert affix["canonical_id"] == "idol_affix:105"
    assert affix["affix_domain"] == "idol"
    assert not affix["canonical_id"].startswith("affix:equipment:")
    assert affix["stable_calculable"] is False


def test_v2_idol_repository_detects_duplicate_idol_id(tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    idol_bundle["records"]["idols"].append(dict(idol_bundle["records"]["idols"][0]))

    with pytest.raises(V2IdolBundleError, match="Duplicate canonical_id"):
        V2IdolRepository("<idol>", "<affix>").load_payloads(idol_bundle, idol_affix_bundle)


def test_v2_idol_repository_detects_duplicate_idol_affix_id(tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    idol_affix_bundle["records"]["idol_affixes"].append(dict(idol_affix_bundle["records"]["idol_affixes"][0]))

    report = validate_v2_idol_records(idol_bundle["records"]["idols"], idol_affix_bundle["records"]["idol_affixes"])

    assert report["summary"]["duplicate_idol_affix_id_count"] == 1
    with pytest.raises(V2IdolBundleError, match="Duplicate canonical_id"):
        V2IdolRepository("<idol>", "<affix>").load_payloads(idol_bundle, idol_affix_bundle)


def test_v2_idol_validation_requires_provenance_and_support_status(tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    idol_bundle["records"]["idols"][0]["provenance"] = {}
    idol_affix_bundle["records"]["idol_affixes"][0].pop("support_status")

    report = validate_v2_idol_records(idol_bundle["records"]["idols"], idol_affix_bundle["records"]["idol_affixes"])

    assert report["summary"]["missing_provenance_count"] == 1
    assert report["summary"]["missing_support_status_count"] == 1
    with pytest.raises(V2IdolBundleError, match="provenance.source_path"):
        V2IdolRepository("<idol>", "<affix>").load_payloads(idol_bundle, idol_affix_bundle)


def test_v2_idol_validation_rejects_equipment_affix_mix(tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    affix = idol_affix_bundle["records"]["idol_affixes"][0]
    affix["canonical_id"] = "affix:equipment:105"

    report = validate_v2_idol_records(idol_bundle["records"]["idols"], idol_affix_bundle["records"]["idol_affixes"])

    assert report["summary"]["idol_affix_mixed_with_equipment_count"] == 1
    with pytest.raises(V2IdolBundleError, match="mixes idol and equipment"):
        V2IdolRepository("<idol>", "<affix>").load_payloads(idol_bundle, idol_affix_bundle)


def test_v2_idol_repository_lookup_filter_and_debug(tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    repository = V2IdolRepository("<idol>", "<affix>").load_payloads(idol_bundle, idol_affix_bundle)

    assert repository.count_idols() == 1
    assert repository.count_affixes() == 1
    assert repository.get_idol("idol:25:0")["display_name"] == "Small Eterran Idol"
    assert repository.get_affix("idol_affix:105")["display_name"] == "Idol Health"
    assert repository.filter_idols(shape="idol_1x1_eterra")[0]["canonical_id"] == "idol:25:0"
    assert repository.filter_affixes(idol_type="IDOL_1x1_ETERRA")[0]["canonical_id"] == "idol_affix:105"
    assert repository.debug_summary()["production_consumer"] is False


def test_v2_idol_routes(app, tmp_path):
    idol_bundle, idol_affix_bundle, _validation = _bundles(tmp_path)
    idol_path = tmp_path / "v2_idol_bundle.json"
    affix_path = tmp_path / "v2_idol_affix_bundle.json"
    idol_path.write_text(json.dumps(idol_bundle), encoding="utf-8")
    affix_path.write_text(json.dumps(idol_affix_bundle), encoding="utf-8")
    app.config["V2_IDOL_BUNDLE_PATH"] = str(idol_path)
    app.config["V2_IDOL_AFFIX_BUNDLE_PATH"] = str(affix_path)
    client = app.test_client()

    idols = client.get("/experimental/v2/idols?shape=idol_1x1_eterra")
    assert idols.status_code == 200
    assert idols.get_json()["records"][0]["canonical_id"] == "idol:25:0"

    idol_detail = client.get("/experimental/v2/idols/idol:25:0")
    assert idol_detail.status_code == 200
    assert idol_detail.get_json()["record"]["display_name"] == "Small Eterran Idol"

    affixes = client.get("/experimental/v2/idols/affixes?idol_type=IDOL_1x1_ETERRA")
    assert affixes.status_code == 200
    assert affixes.get_json()["records"][0]["canonical_id"] == "idol_affix:105"

    affix_detail = client.get("/experimental/v2/idols/affixes/idol_affix:105")
    assert affix_detail.status_code == 200
    assert affix_detail.get_json()["record"]["affix_domain"] == "idol"

    debug = client.get("/experimental/v2/idols/debug")
    assert debug.status_code == 200
    assert debug.get_json()["debug_summary"]["production_safe"] is False


def test_v2_idol_bundle_is_not_referenced_by_production_modules():
    root = Path(__file__).resolve().parents[2]
    allowed = {
        root / "backend" / "app" / "routes" / "experimental.py",
        root / "backend" / "app" / "repositories" / "v2" / "idol_repository.py",
        root / "backend" / "app" / "repositories" / "v2" / "__init__.py",
        root / "backend" / "scripts" / "report_v2_idol_bundles.py",
        Path(__file__).resolve(),
    }
    needles = ("v2_idol_bundle.json", "v2_idol_affix_bundle.json", "V2IdolRepository")
    offenders: list[str] = []
    for path in (root / "backend" / "app").rglob("*.py"):
        if path in allowed or "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if any(needle in text for needle in needles):
            offenders.append(str(path.relative_to(root)))

    assert offenders == []


def _write_sources(tmp_path: Path) -> tuple[Path, Path]:
    source_items = tmp_path / "items.json"
    affix_bundle = tmp_path / "v2_affix_bundle.json"
    source_items.write_text(json.dumps(_source_items()), encoding="utf-8")
    affix_bundle.write_text(json.dumps(_affix_bundle()), encoding="utf-8")
    return source_items, affix_bundle


def _bundles(tmp_path: Path) -> tuple[dict, dict, dict]:
    return build_v2_idol_bundles(*_write_sources(tmp_path))


def _source_items() -> dict:
    return {
        "_meta": {"game_build": {"installPath": "D:\\LastEpochTools\\game_files\\current\\1.4.6_22986002"}},
        "equippable": [
            {
                "baseTypeID": 25,
                "type": "IDOL_1x1_ETERRA",
                "name": "Small Idol",
                "displayName": "Small Idol",
                "subTypes": [
                    {
                        "subTypeID": 0,
                        "name": "Small Eterran Idol",
                        "displayName": "Small Eterran Idol",
                        "levelRequirement": 0,
                        "classRequirement": "Any",
                        "subClassRequirement": "Any",
                        "implicits": [],
                    }
                ],
            }
        ],
    }


def _affix_bundle() -> dict:
    return {
        "records": {
            "affixes": [
                {
                    "canonical_id": "affix:equipment:105",
                    "display_name": "Idol Health",
                    "source_affix_id": 105,
                    "source_id": "equipment:105",
                    "source_file": "affixes.json",
                    "support_status": "partial",
                    "trust_level": "generated_from_game_data",
                    "provenance": {"source_path": "affixes.json", "source_id": "equipment:105"},
                    "affix_domain": "idol",
                    "prefix_suffix": "suffix",
                    "slot_restrictions": ["IDOL_1x1_ETERRA"],
                    "item_type_restrictions": ["IDOL_1x1_ETERRA"],
                    "class_restrictions": [],
                    "mastery_restrictions": [],
                    "tier_ranges": [{"tier": 1, "min_value": 1.0, "max_value": 2.0, "polarity": "positive"}],
                    "modifier_references": [{"modifier_id": "equipment:105", "property": "Health", "property_path": "ADDED.Health.None"}],
                    "stable_calculable": False,
                    "warnings": [],
                }
            ]
        }
    }
