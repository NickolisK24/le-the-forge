from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.bundle_item_type_dry_run_resolver import STATUS_RESOLVED
from app.game_data.bundle_item_adapter_report import validate_output_path
from app.game_data.le_tools_fresh_sidecar_diagnostic import (
    build_fresh_sidecar_diagnostic,
    diagnose_fresh_sidecar,
    fresh_sidecar_diagnostic_to_json,
    render_fresh_sidecar_diagnostic,
)
from app.game_data.le_tools_import_context_sidecar import build_sidecar_from_fixture
from app.game_data.le_tools_import_context_sidecar_validator import load_sidecar


SAVED_SIDECAR_FIXTURE = (
    Path(__file__).parent / "fixtures" / "le_tools_import_context_sidecar_current.json"
)


def _sidecar():
    sidecar, _mapped = build_sidecar_from_fixture()
    return sidecar


def test_fresh_sidecar_diagnostic_reports_current_warning_state():
    report = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)

    assert report["status"] == "warning"
    assert report["production_safe"] is False
    assert report["errors"] == []
    assert report["summary"]["total_items"] == 12
    assert report["summary"]["resolved"] == 8
    assert report["summary"]["needs_context"] == 2
    assert report["summary"]["needs_review"] == 1
    assert report["summary"]["unresolved"] == 1
    assert report["summary"]["missing_identity"] == 3
    assert report["summary"]["ambiguous"] == 1
    assert report["summary"]["unsafe"] == 0
    assert report["shape"]["top_level_keys_match_saved"] is True
    assert report["shape"]["summary_keys_match_saved"] is True


def test_report_render_and_json_shape_are_stable():
    report = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)

    rendered = render_fresh_sidecar_diagnostic(report)
    encoded = fresh_sidecar_diagnostic_to_json(report)

    assert "# Fresh LE Tools Sidecar Diagnostic Validation Report" in rendered
    assert "production_safe: false" in rendered
    assert "## Missing / Ambiguous / Unsafe Records" in rendered
    assert '"production_safe": false' in encoded


def test_missing_required_identity_field_is_failed():
    sidecar = _sidecar()
    saved = load_sidecar(SAVED_SIDECAR_FIXTURE)
    del sidecar["items"][0]["raw"]["base_type_id"]

    report = diagnose_fresh_sidecar(sidecar, saved_sidecar=saved)

    assert report["status"] == "failed"
    assert any("raw missing keys" in error for error in report["errors"])


def test_subtype_only_identity_cannot_resolve():
    sidecar = _sidecar()
    saved = load_sidecar(SAVED_SIDECAR_FIXTURE)
    item = sidecar["items"][9]
    item["resolver"]["status"] = STATUS_RESOLVED
    item["resolver"]["bundle_item_type_id"] = "belt"
    sidecar["summary"]["needs_context"] -= 1
    sidecar["summary"]["resolved"] += 1

    report = diagnose_fresh_sidecar(sidecar, saved_sidecar=saved)

    assert report["status"] == "failed"
    assert any("subtype_only record resolved" in error for error in report["errors"])
    assert report["summary"]["unsafe"] >= 1


def test_name_only_matching_cannot_resolve():
    sidecar = _sidecar()
    saved = load_sidecar(SAVED_SIDECAR_FIXTURE)
    item = sidecar["items"][11]
    item["raw"]["name"] = "Name Only Helmet"
    item["resolver"]["status"] = STATUS_RESOLVED
    item["resolver"]["bundle_item_type_id"] = "helmet"
    sidecar["summary"]["unresolved"] -= 1
    sidecar["summary"]["resolved"] += 1

    report = diagnose_fresh_sidecar(sidecar, saved_sidecar=saved)

    assert report["status"] == "failed"
    assert any("name-only record resolved" in error for error in report["errors"])
    assert report["summary"]["unsafe"] >= 1


def test_ambiguous_records_are_counted_and_surfaced():
    report = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)

    assert report["summary"]["ambiguous"] == 1
    assert len(report["ambiguous_records"]) == 1
    assert report["ambiguous_records"][0]["raw"]["item_type"] == "spear"
    assert report["ambiguous_records"][0]["resolver_status"] == "needs_review"


def test_missing_records_are_counted_and_surfaced():
    report = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)

    assert len(report["missing_identity_records"]) == 3
    assert {record["resolver_status"] for record in report["missing_identity_records"]} == {
        "needs_context",
        "unresolved",
    }


def test_shape_mismatch_against_saved_sidecar_fails():
    sidecar = _sidecar()
    saved = load_sidecar(SAVED_SIDECAR_FIXTURE)
    del sidecar["items"][0]["context"]["requires_test_pairing"]

    report = diagnose_fresh_sidecar(sidecar, saved_sidecar=saved)

    assert report["status"] == "failed"
    assert any("context missing keys" in error for error in report["errors"])


def test_output_path_guard_refuses_production_data_directory():
    with pytest.raises(ValueError):
        validate_output_path(Path(__file__).resolve().parents[2] / "data" / "items" / "fresh-sidecar.md")
