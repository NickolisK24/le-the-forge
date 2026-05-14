from pathlib import Path
from unittest.mock import patch

from app.game_data.le_tools_import_stage_context_report import (
    build_stage_context_report,
    load_stage_fixture,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "le_tools_offline_buildinfo_stage_context_sample.json"


def _report():
    return build_stage_context_report(load_stage_fixture(FIXTURE_PATH))


def test_stage_report_detects_raw_and_mapped_base_type_context_without_network():
    with patch("app.services.importers.lastepochtools_importer._requests.get") as mock_get:
        report = _report()

    mock_get.assert_not_called()
    assert report["production_safe"] is False
    assert report["total_items"] == 12
    assert report["stage_summary"]["raw_with_base_type_id"] == 9
    assert report["stage_summary"]["mapped_with_base_type_id"] == 9
    assert report["stage_summary"]["raw_missing_base_type_id"] == 3
    assert report["stage_summary"]["mapped_missing_item_type"] == 12
    assert report["stage_summary"]["needs_test_only_pairing"] == 11
    assert report["stage_summary"]["raw_with_subtype_only"] == 1


def test_stage_report_status_counts_and_safety_rules_are_stable():
    report = _report()

    assert report["resolver_status_counts"] == {
        "resolved": 8,
        "needs_context": 2,
        "needs_review": 1,
        "deferred": 0,
        "unresolved": 1,
    }
    assert all(record["production_safe"] is False for record in report["records"])


def test_stage_report_resolves_base_type_backed_records():
    report = _report()
    resolved = {
        (record["raw_item_type"], record["mapped_base_type_id"]): record["bundle_item_type_id"]
        for record in report["records"]
        if record["resolver_status"] == "resolved"
    }

    assert resolved[("helm", 0)] == "helmet"
    assert resolved[("chest", 1)] == "body_armor"
    assert resolved[("axe", 5)] == "one_handed_axe"
    assert resolved[("axe", 12)] == "two_handed_axe"
    assert resolved[("mace", 7)] == "one_handed_maces"
    assert resolved[("sword", 16)] == "two_handed_sword"
    assert resolved[("idol_1x1", 25)] == "idol_1x1_eterra"
    assert resolved[("idol_1x1", 26)] == "idol_1x1_lagon"


def test_stage_report_keeps_gap_records_blocked_or_warned():
    report = _report()
    by_status = {}
    for record in report["records"]:
        by_status.setdefault(record["resolver_status"], []).append(record)

    assert {record["raw_item_type"] for record in by_status["needs_context"]} == {"axe", "belt"}
    assert any(record["raw_has_subtype_id"] for record in by_status["needs_context"])
    assert by_status["needs_review"][0]["raw_item_type"] == "spear"
    assert by_status["unresolved"][0]["raw_item_type"] is None
    assert all(record["bundle_item_type_id"] is None for record in by_status["needs_context"] + by_status["needs_review"] + by_status["unresolved"])


def test_stage_report_documents_pairing_need_but_does_not_change_mapped_shape():
    report = _report()

    assert report["mapped_output_shape_changed"] is False
    assert report["test_only_pairing_used"] is True
    assert all(record["mapped_has_item_type"] is False for record in report["records"])
    assert any("test-only pairing" in note for record in report["records"] for note in record["notes"])
