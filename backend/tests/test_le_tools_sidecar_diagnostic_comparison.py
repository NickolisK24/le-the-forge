from copy import deepcopy
from pathlib import Path

from app.game_data.le_tools_fresh_sidecar_diagnostic import diagnose_fresh_sidecar
from app.game_data.le_tools_fresh_sidecar_diagnostic import build_fresh_sidecar_diagnostic
from app.game_data.le_tools_import_context_sidecar import build_sidecar_from_fixture
from app.game_data.le_tools_import_context_sidecar_validator import load_sidecar
from app.game_data.le_tools_sidecar_diagnostic_comparison import (
    build_sidecar_diagnostic_comparison,
    compare_sidecar_diagnostics,
    render_sidecar_diagnostic_comparison,
    sidecar_diagnostic_comparison_to_json,
)
from app.game_data.le_tools_sidecar_diagnostic_consumer import consume_sidecar_diagnostic


SAVED_SIDECAR_FIXTURE = (
    Path(__file__).parent / "fixtures" / "le_tools_import_context_sidecar_current.json"
)


def _fresh_report_from_sidecar(sidecar):
    saved = load_sidecar(SAVED_SIDECAR_FIXTURE)
    return diagnose_fresh_sidecar(sidecar, saved_sidecar=saved)


def test_current_saved_and_fresh_diagnostics_compare_with_warning_gate():
    report = build_sidecar_diagnostic_comparison(sidecar_path=SAVED_SIDECAR_FIXTURE)

    assert report["production_safe"] is False
    assert report["migration_gate_status"] == "warning"
    assert report["saved_sidecar_status"] == "warning"
    assert report["fresh_sidecar_status"] == "warning"
    assert all(report["shape_agreement"].values())
    assert report["count_deltas"]["total_items"] == {"saved": 12, "fresh": 12, "delta": 0}
    assert report["count_deltas"]["resolved"] == {"saved": 8, "fresh": 8, "delta": 0}
    assert report["count_deltas"]["unsafe"] == {"saved": 0, "fresh": 0, "delta": 0}


def test_json_and_markdown_outputs_include_gate_and_production_safe_false():
    report = build_sidecar_diagnostic_comparison(sidecar_path=SAVED_SIDECAR_FIXTURE)

    markdown = render_sidecar_diagnostic_comparison(report)
    encoded = sidecar_diagnostic_comparison_to_json(report)

    assert "# LE Tools Sidecar Diagnostic Comparison Report" in markdown
    assert "migration_gate_status: warning" in markdown
    assert "production_safe: false" in markdown
    assert '"production_safe": false' in encoded
    assert '"migration_gate_status": "warning"' in encoded


def test_count_drift_is_reported_as_warning():
    saved = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)
    fresh = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)
    fresh = deepcopy(fresh)
    fresh["summary"]["total_items"] -= 1
    fresh["summary"]["unresolved"] -= 1

    report = compare_sidecar_diagnostics(saved, fresh)

    assert report["migration_gate_status"] == "warning"
    assert report["count_deltas"]["total_items"]["delta"] == -1
    assert report["count_deltas"]["unresolved"]["delta"] == -1
    assert "Investigate count drift between saved and fresh diagnostics." in report["recommendations"]


def test_warning_drift_is_reported_without_claiming_pass():
    saved = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)
    fresh = build_fresh_sidecar_diagnostic(saved_sidecar_path=SAVED_SIDECAR_FIXTURE)
    fresh = deepcopy(fresh)
    fresh["warnings"] = fresh["warnings"] + ["new warning from fresh diagnostic"]

    report = compare_sidecar_diagnostics(saved, fresh)

    assert report["migration_gate_status"] == "warning"
    assert "new warning from fresh diagnostic" in report["warning_delta"]["added_in_fresh"]


def test_unsafe_identity_findings_block_gate():
    saved = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)
    sidecar, _mapped = build_sidecar_from_fixture()
    item = sidecar["items"][9]
    item["resolver"]["status"] = "resolved"
    item["resolver"]["bundle_item_type_id"] = "belt"
    sidecar["summary"]["needs_context"] -= 1
    sidecar["summary"]["resolved"] += 1
    fresh = _fresh_report_from_sidecar(sidecar)

    report = compare_sidecar_diagnostics(saved, fresh)

    assert report["migration_gate_status"] == "blocked"
    assert report["fresh"]["counts"]["unsafe"] >= 1
    assert any("unsafe" in error for error in report["fresh"]["errors"])


def test_shape_mismatch_blocks_gate():
    saved = consume_sidecar_diagnostic(SAVED_SIDECAR_FIXTURE)
    sidecar, _mapped = build_sidecar_from_fixture()
    del sidecar["items"][0]["context"]["requires_test_pairing"]
    fresh = _fresh_report_from_sidecar(sidecar)

    report = compare_sidecar_diagnostics(saved, fresh)

    assert report["migration_gate_status"] == "blocked"
    assert report["shape_agreement"]["fresh_item_sections_present"] is True
    assert any("context missing keys" in error for error in report["fresh"]["errors"])
