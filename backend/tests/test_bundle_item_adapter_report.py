import json
from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import (
    READINESS_DEFERRED,
    READINESS_NEEDS_ADAPTER,
    READINESS_NEEDS_REVIEW,
    READINESS_READY,
    build_adapter_report,
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


def test_slug_only_mapping_needs_review():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")

    spear = next(record for record in report.adapter_records if record.forge_item_type == "spear")

    assert spear.readiness == READINESS_NEEDS_REVIEW
    assert spear.match_method == "exact_slug"
    assert spear.production_safe is False


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


def test_report_json_shape():
    report = build_adapter_report(_bundle_item_types(), _forge_sources(), "bundle")
    data = report.to_dict()

    assert data["bundle_item_types_count"] == 4
    assert data["adapter_record_count"] == len(report.adapter_records)
    assert "readiness_counts" in data
    assert all(record["production_safe"] is False for record in data["adapter_records"])


def test_output_path_refuses_production_data_path():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "adapter_report.md")
