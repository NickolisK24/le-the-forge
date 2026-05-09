import json
import shutil
import uuid
from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.controlled_modifier_resolver_comparison import (
    build_controlled_modifier_resolver_comparison,
    compare_controlled_modifier_resolver_outputs,
    controlled_modifier_resolver_comparison_to_json,
    render_controlled_modifier_resolver_comparison,
)
from app.game_data.controlled_modifier_resolver_prototype import (
    controlled_modifier_resolver_report_to_json,
    resolve_modifier_diagnostics,
)
from tests.test_controlled_affix_resolver_prototype import _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_controlled_modifier_resolver_comparison"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_matching_saved_and_fresh_output_compares_with_warning_status(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    saved_path = scratch_dir / "saved_modifier_resolver.json"
    saved_path.write_text(controlled_modifier_resolver_report_to_json(saved), encoding="utf-8")

    report = build_controlled_modifier_resolver_comparison(
        saved_report_path=saved_path,
        diagnostics_dir=diagnostics_dir,
    )

    assert report["production_safe"] is False
    assert report["diagnostic_only"] is True
    assert report["comparison_status"] == "warning"
    assert report["saved_resolver_output_status"] == "warning"
    assert report["fresh_resolver_output_status"] == "warning"
    assert report["count_deltas"]["total_modifier_references"] == {"saved": 12, "fresh": 12, "delta": 0}
    assert report["count_deltas"]["resolved_modifier_objects"] == {"saved": 9, "fresh": 9, "delta": 0}
    assert report["count_deltas"]["unresolved_modifier_objects"] == {"saved": 1, "fresh": 1, "delta": 0}
    assert report["count_deltas"]["malformed_modifier_objects"] == {"saved": 1, "fresh": 1, "delta": 0}
    assert report["count_deltas"]["unsupported_modifier_objects"] == {"saved": 1, "fresh": 1, "delta": 0}
    assert all(delta["delta"] == 0 for delta in report["warning_category_delta"].values())
    assert report["provenance_coverage_agreement"]["agrees"] is True
    assert report["production_safe_agreement"]["agrees"] is True
    assert report["diagnostic_only_agreement"]["agrees"] is True
    assert report["affix_910_duplicate_evidence_agreement"]["agrees"] is True
    assert report["deterministic_output_agreement"] is True

    markdown = render_controlled_modifier_resolver_comparison(report)
    encoded = controlled_modifier_resolver_comparison_to_json(report)
    assert "# Controlled Modifier Resolver Prototype Comparison Report" in markdown
    assert "production_safe: false" in markdown
    assert '"production_safe": false' in encoded


def test_count_drift_is_reported_as_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["summary"]["total_modifier_references"] += 1

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert report["count_deltas"]["total_modifier_references"]["delta"] == 1
    assert "Saved/fresh modifier resolver count deltas are present." in report["warnings"]


def test_unresolved_malformed_unsupported_drift_is_reported_as_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["summary"]["unresolved_modifier_objects"] += 1
    fresh["summary"]["malformed_modifier_objects"] += 1
    fresh["summary"]["unsupported_modifier_objects"] += 1

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert report["count_deltas"]["unresolved_modifier_objects"]["delta"] == 1
    assert report["count_deltas"]["malformed_modifier_objects"]["delta"] == 1
    assert report["count_deltas"]["unsupported_modifier_objects"]["delta"] == 1


def test_warning_metadata_drift_is_reported_as_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["warning_category_summary"][0]["count"] += 1

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert any(delta["delta"] == 1 for delta in report["warning_category_delta"].values())
    assert "Saved/fresh warning category deltas are present." in report["warnings"]


def test_missing_saved_report_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)

    with pytest.raises(FileNotFoundError):
        build_controlled_modifier_resolver_comparison(
            saved_report_path=scratch_dir / "missing.json",
            diagnostics_dir=diagnostics_dir,
        )


def test_missing_fresh_report_artifact_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    saved_path = scratch_dir / "saved_modifier_resolver.json"
    saved_path.write_text(controlled_modifier_resolver_report_to_json(saved), encoding="utf-8")
    (diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"]).unlink()

    with pytest.raises(FileNotFoundError):
        build_controlled_modifier_resolver_comparison(
            saved_report_path=saved_path,
            diagnostics_dir=diagnostics_dir,
        )


def test_production_safe_true_violation_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    saved["production_safe"] = True

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert "Saved modifier resolver output does not have production_safe=false." in report["errors"]


def test_diagnostic_only_false_violation_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["diagnostic_only"] = False

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert "Fresh modifier resolver output does not have diagnostic_only=true." in report["errors"]


def test_deterministic_output_mismatch_is_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["notes"] = fresh["notes"] + ["new non-safety note"]

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert report["deterministic_output_agreement"] is False
    assert "Saved/fresh modifier resolver JSON output is not byte-for-byte deterministic." in report["warnings"]


def test_affix_910_duplicate_evidence_drift_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["affix_910_duplicate_evidence"]["duplicate_positions"] = [0]

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert report["affix_910_duplicate_evidence_agreement"]["agrees"] is False


def test_missing_provenance_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["modifier_objects"][0]["source_provenance_path"] = None

    report = compare_controlled_modifier_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert "Saved/fresh provenance coverage does not agree or has missing provenance." in report["errors"]


def test_json_shape_has_stable_top_level_keys(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_modifier_diagnostics(diagnostics_dir)
    report = compare_controlled_modifier_resolver_outputs(saved, deepcopy(saved))
    parsed = json.loads(controlled_modifier_resolver_comparison_to_json(report))

    assert {
        "diagnostic",
        "diagnostic_only",
        "production_safe",
        "comparison_status",
        "count_deltas",
        "errors",
        "warnings",
    }.issubset(parsed)


def _write_diagnostics_dir(scratch_dir: Path) -> Path:
    diagnostics_dir = scratch_dir / "diagnostics"
    diagnostics_dir.mkdir(parents=True, exist_ok=False)
    return _write_diagnostics(diagnostics_dir)
