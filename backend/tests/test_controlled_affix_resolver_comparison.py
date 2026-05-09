import json
import shutil
import uuid
from copy import deepcopy
from pathlib import Path

import pytest

from app.game_data.affix_diagnostic_consumer import PHASE_ARTIFACTS
from app.game_data.controlled_affix_resolver_comparison import (
    build_controlled_affix_resolver_comparison,
    compare_controlled_affix_resolver_outputs,
    controlled_affix_resolver_comparison_to_json,
    render_controlled_affix_resolver_comparison,
)
from app.game_data.controlled_affix_resolver_prototype import (
    controlled_affix_resolver_report_to_json,
    resolve_affix_diagnostics,
)
from tests.test_controlled_affix_resolver_prototype import _write_diagnostics


@pytest.fixture
def scratch_dir():
    root = Path(__file__).parent / "_tmp_controlled_affix_resolver_comparison"
    path = root / uuid.uuid4().hex
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def test_matching_saved_and_fresh_output_compares_with_warning_status(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    saved_path = scratch_dir / "saved_resolver.json"
    saved_path.write_text(controlled_affix_resolver_report_to_json(saved), encoding="utf-8")

    report = build_controlled_affix_resolver_comparison(
        saved_report_path=saved_path,
        diagnostics_dir=diagnostics_dir,
    )

    assert report["production_safe"] is False
    assert report["comparison_status"] == "warning"
    assert report["saved_resolver_status"] == "warning"
    assert report["fresh_resolver_status"] == "warning"
    assert report["count_deltas"]["total_normalized_affixes"] == {"saved": 6, "fresh": 6, "delta": 0}
    assert report["count_deltas"]["equipment_affixes"] == {"saved": 4, "fresh": 4, "delta": 0}
    assert report["count_deltas"]["idol_affixes"] == {"saved": 2, "fresh": 2, "delta": 0}
    assert report["count_deltas"]["total_embedded_tiers"] == {"saved": 12, "fresh": 12, "delta": 0}
    assert all(delta["agrees"] for delta in report["phase_status_delta"].values())
    assert all(delta["delta"] == 0 for delta in report["warning_category_delta"].values())
    assert report["affix_910_duplicate_evidence_agreement"]["agrees"] is True
    assert report["production_safe_agreement"]["agrees"] is True
    assert report["non_production_inspection_allowed_agreement"]["agrees"] is True
    assert report["deterministic_output_agreement"] is True

    markdown = render_controlled_affix_resolver_comparison(report)
    encoded = controlled_affix_resolver_comparison_to_json(report)
    assert "# Controlled Affix Resolver Prototype Comparison Report" in markdown
    assert "production_safe: false" in markdown
    assert '"production_safe": false' in encoded


def test_count_drift_is_reported_as_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["summary"]["total_normalized_affixes"] += 1

    report = compare_controlled_affix_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert report["count_deltas"]["total_normalized_affixes"]["delta"] == 1
    assert "Saved/fresh resolver count deltas are present." in report["warnings"]


def test_missing_saved_report_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)

    with pytest.raises(FileNotFoundError):
        build_controlled_affix_resolver_comparison(
            saved_report_path=scratch_dir / "missing.json",
            diagnostics_dir=diagnostics_dir,
        )


def test_missing_fresh_report_artifact_fails(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    saved_path = scratch_dir / "saved_resolver.json"
    saved_path.write_text(controlled_affix_resolver_report_to_json(saved), encoding="utf-8")
    (diagnostics_dir / PHASE_ARTIFACTS["phase_1_source_shape"]).unlink()

    with pytest.raises(FileNotFoundError):
        build_controlled_affix_resolver_comparison(
            saved_report_path=saved_path,
            diagnostics_dir=diagnostics_dir,
        )


def test_production_safe_true_violation_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    saved["production_safe"] = True

    report = compare_controlled_affix_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert "Saved resolver output does not have production_safe=false." in report["errors"]


def test_affix_910_duplicate_evidence_drift_is_error(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["affix_910_duplicate_evidence"]["duplicate_positions"] = [0]

    report = compare_controlled_affix_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "error"
    assert report["affix_910_duplicate_evidence_agreement"]["agrees"] is False
    assert "Affix 910 duplicate evidence does not agree or is missing." in report["errors"]


def test_deterministic_output_mismatch_is_warning(scratch_dir):
    diagnostics_dir = _write_diagnostics_dir(scratch_dir)
    saved = resolve_affix_diagnostics(diagnostics_dir)
    fresh = deepcopy(saved)
    fresh["notes"] = fresh["notes"] + ["new non-safety note"]

    report = compare_controlled_affix_resolver_outputs(saved, fresh)

    assert report["comparison_status"] == "warning"
    assert report["deterministic_output_agreement"] is False
    assert "Saved/fresh resolver JSON output is not byte-for-byte deterministic." in report["warnings"]


def _write_diagnostics_dir(scratch_dir: Path) -> Path:
    diagnostics_dir = scratch_dir / "diagnostics"
    diagnostics_dir.mkdir(parents=True, exist_ok=False)
    return _write_diagnostics(diagnostics_dir)
