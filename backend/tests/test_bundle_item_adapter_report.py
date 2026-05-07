import json
import os
from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import (
    READINESS_DEFERRED,
    READINESS_NEEDS_ADAPTER,
    READINESS_NEEDS_REVIEW,
    READINESS_READY,
    assert_report_safety_invariants,
    build_adapter_report,
    generate_adapter_report,
    validate_output_path,
)


def _bundle_item_types():
    return [
        {"id": "helm", "base_type_id": 0, "name": "Helm", "category": "armor"},
        {"id": "body_armor", "base_type_id": 1, "name": "Body Armor", "category": "armor"},
        {"id": "blessing", "base_type_id": 34, "name": "Blessing", "category": "non_equipment"},
        {"id": "spear", "base_type_id": 14, "name": "Spear", "category": "weapon"},
    ]


def _forge_sources():
    return {
        "data_item_types": [
            {"id": "helm", "name": "Helm", "slot": "head"},
            {"id": "spear", "name": "Spear", "slot": "weapon"},
        ],
        "base_type_id_to_item_type_id": {
            0: "helm",
            1: "chest",
        },
        "item_type_ids": ["helm", "chest", "spear"],
        "item_type_to_slot": {"helm": "head", "chest": "body", "spear": "weapon"},
        "game_type_to_item_type_id": {},
        "subtype_id_to_item_type_id": {},
    }


def test_base_type_id_backed_mapping_readiness():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    helm = next(record for record in report.adapter_records if record.forge_item_type == "helm")
    chest = next(record for record in report.adapter_records if record.forge_item_type == "chest")

    assert helm.readiness == READINESS_READY
    assert helm.match_method == "base_type_id"
    assert helm.production_safe is False
    assert chest.readiness == READINESS_NEEDS_ADAPTER
    assert chest.bundle_item_type_id == "body_armor"


def test_base_type_id_backed_mapping_is_preferred_over_slug():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    helm = next(record for record in report.adapter_records if record.forge_item_type == "helm")

    assert helm.bundle_item_type_id == "helm"
    assert helm.match_method == "base_type_id"
    assert helm.readiness == READINESS_READY


def test_slug_only_mapping_needs_review():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    spear = next(record for record in report.adapter_records if record.forge_item_type == "spear")

    assert spear.readiness == READINESS_NEEDS_REVIEW
    assert spear.match_method == "exact_slug"
    assert spear.production_safe is False


def test_normalized_name_mapping_is_advisory():
    sources = _forge_sources()
    sources["data_item_types"] = [
        *sources["data_item_types"],
        {"id": "body", "name": "Body Armor", "slot": "body"},
    ]
    sources["item_type_ids"] = [*sources["item_type_ids"], "body"]

    report = build_adapter_report(_bundle_item_types(), sources, "bundle")

    body = next(record for record in report.adapter_records if record.forge_item_type == "body")

    assert body.bundle_item_type_id == "body_armor"
    assert body.match_method == "normalized_name"
    assert body.readiness == READINESS_NEEDS_REVIEW
    assert body.production_safe is False


def test_subtype_id_only_source_is_not_used_for_records():
    sources = _forge_sources()
    sources["subtype_id_to_item_type_id"] = {0: "helm"}

    report = build_adapter_report(_bundle_item_types(), sources, "bundle")

    assert report.subtype_identity_risk
    assert all(record.match_method != "subtype_id" for record in report.adapter_records)


def test_unmapped_non_equipment_bundle_type_is_deferred():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    blessing = next(record for record in report.adapter_records if record.bundle_item_type_id == "blessing")

    assert blessing.readiness == READINESS_DEFERRED
    assert blessing.production_safe is False


def test_forge_types_with_no_bundle_mapping_are_reported():
    sources = _forge_sources()
    sources["item_type_ids"] = [*sources["item_type_ids"], "wand"]

    report = build_adapter_report(_bundle_item_types(), sources, "bundle")

    assert "wand" in report.unmapped_forge_types
    wand = next(record for record in report.adapter_records if record.forge_item_type == "wand")
    assert wand.bundle_item_type_id is None
    assert wand.readiness == "Not comparable"


def test_report_json_shape():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")
    data = report.to_dict()

    assert data["bundle_item_types_count"] == 4
    assert data["adapter_record_count"] == len(report.adapter_records)
    assert "adapter_records" in data
    assert "readiness_counts" in data
    assert "readiness_summary" in data
    assert "match_method_counts" in data
    assert "match_method_summary" in data
    assert "unmapped_forge_types" in data
    assert "unmapped_bundle_item_types" in data
    assert "safety_warnings" in data
    assert all(record["production_safe"] is False for record in data["adapter_records"])


def test_readiness_and_match_method_counts_are_produced():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    assert report.readiness_counts[READINESS_READY] == 1
    assert report.readiness_counts[READINESS_NEEDS_ADAPTER] == 1
    assert report.readiness_counts[READINESS_NEEDS_REVIEW] == 1
    assert report.readiness_counts[READINESS_DEFERRED] == 1
    assert report.match_method_counts["base_type_id"] == 2
    assert report.match_method_counts["exact_slug"] == 1


def test_safety_invariants_pass_for_fixture_report():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    errors, warnings = assert_report_safety_invariants(report)

    assert errors == []
    assert warnings == ["No unmapped Forge item types were reported."]


def test_output_path_refuses_production_data_path():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "adapter_report.md")


@pytest.mark.skipif(
    not os.environ.get("FORGE_DATA_BUNDLE_DIR"),
    reason="Local bundle snapshot guard requires FORGE_DATA_BUNDLE_DIR.",
)
def test_local_bundle_snapshot_counts_when_opted_in():
    report = generate_adapter_report(os.environ["FORGE_DATA_BUNDLE_DIR"])

    assert report.readiness_counts == {
        "Deferred": 8,
        "Needs adapter": 15,
        "Needs review": 8,
        "Not comparable": 1,
        "Ready candidate": 19,
    }
    assert all(record.production_safe is False for record in report.adapter_records)
