from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_import_context_sidecar import (
    build_sidecar_from_fixture,
    validate_sidecar,
)
from app.game_data.le_tools_import_stage_context_report import load_stage_fixture
from app.routes.import_route import _map_let_build


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "le_tools_offline_buildinfo_stage_context_sample.json"


def _sidecar():
    sidecar, mapped_gear = build_sidecar_from_fixture(FIXTURE_PATH)
    return sidecar, mapped_gear


def test_sidecar_builds_from_offline_stage_fixture():
    sidecar, _mapped_gear = _sidecar()

    assert sidecar["production_safe"] is False
    assert sidecar["source"] == "le_tools_import_diagnostic"
    assert sidecar["importer"] == "lastepochtools"
    assert sidecar["build_id"] == "le_tools_offline_buildinfo_stage_context_sample"
    assert len(sidecar["items"]) == 12
    assert validate_sidecar(sidecar) == []


def test_sidecar_summary_counts_are_stable():
    sidecar, _mapped_gear = _sidecar()

    assert sidecar["summary"] == {
        "total_items": 12,
        "resolved": 8,
        "needs_context": 2,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 1,
        "raw_with_base_type_id": 9,
        "mapped_with_base_type_id": 9,
        "mapped_missing_item_type": 12,
        "requires_test_pairing": 11,
        "raw_with_subtype_only": 1,
    }


def test_sidecar_preserves_safety_flags_globally_and_per_item():
    sidecar, _mapped_gear = _sidecar()

    assert sidecar["production_safe"] is False
    assert all(item["resolver"]["production_safe"] is False for item in sidecar["items"])


def test_sidecar_detects_raw_and_mapped_context():
    sidecar, _mapped_gear = _sidecar()
    first = sidecar["items"][0]

    assert first["raw"]["item_type"] == "helm"
    assert first["raw"]["base_type_id"] == 0
    assert first["mapped"]["base_type_id"] == 0
    assert first["mapped"]["has_item_type"] is False
    assert first["context"]["has_base_type_id"] is True
    assert first["context"]["requires_test_pairing"] is True


def test_sidecar_resolver_statuses_match_expected_safe_behavior():
    sidecar, _mapped_gear = _sidecar()
    resolved = {
        (item["raw"]["item_type"], item["mapped"]["base_type_id"]): item["resolver"]["bundle_item_type_id"]
        for item in sidecar["items"]
        if item["resolver"]["status"] == "resolved"
    }

    assert resolved[("helm", 0)] == "helmet"
    assert resolved[("chest", 1)] == "body_armor"
    assert resolved[("axe", 5)] == "one_handed_axe"
    assert resolved[("axe", 12)] == "two_handed_axe"
    assert resolved[("mace", 7)] == "one_handed_maces"
    assert resolved[("sword", 16)] == "two_handed_sword"
    assert resolved[("idol_1x1", 25)] == "idol_1x1_eterra"
    assert resolved[("idol_1x1", 26)] == "idol_1x1_lagon"


def test_sidecar_blocks_missing_subtype_only_spear_and_name_only_cases():
    sidecar, _mapped_gear = _sidecar()
    by_status = {}
    for item in sidecar["items"]:
        by_status.setdefault(item["resolver"]["status"], []).append(item)

    assert {item["raw"]["item_type"] for item in by_status["needs_context"]} == {"axe", "belt"}
    assert any(item["context"]["subtype_only"] for item in by_status["needs_context"])
    assert by_status["needs_review"][0]["raw"]["item_type"] == "spear"
    assert by_status["unresolved"][0]["raw"]["item_type"] is None
    assert all(
        item["resolver"]["bundle_item_type_id"] is None
        for item in by_status["needs_context"] + by_status["needs_review"] + by_status["unresolved"]
    )


def test_sidecar_does_not_mutate_importer_mapped_output():
    fixture = load_stage_fixture(FIXTURE_PATH)
    mapped = _map_let_build(deepcopy(fixture["build_info"]))
    original = deepcopy(mapped["gear"])

    sidecar, copied_mapped = build_sidecar_from_fixture(FIXTURE_PATH)

    assert mapped["gear"] == original
    assert copied_mapped == original
    assert sidecar["summary"]["total_items"] == len(original)
    assert all("bundle_item_type_id" not in item for item in original)


def test_sidecar_validation_rejects_unsafe_mutations():
    sidecar, _mapped_gear = _sidecar()
    sidecar["production_safe"] = True

    assert "top-level production_safe must be false" in validate_sidecar(sidecar)


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "sidecar.md")
