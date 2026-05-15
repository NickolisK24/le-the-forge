from app.planner_adapters.v3.mechanical_dry_run import (
    DELTA_CATEGORIES,
    V3ExperimentalMechanicalDryRun,
    build_sample_v3_dry_run_inputs,
)
from scripts.report_v3_experimental_dry_run_mode import build_v3_experimental_dry_run_mode_report


def test_v3_dry_run_defaults_disabled_and_non_production():
    current, candidate = build_sample_v3_dry_run_inputs()
    envelope = V3ExperimentalMechanicalDryRun().compare(
        current_output=current,
        candidate_output=candidate,
    )

    assert envelope["mode"]["enabled"] is False
    assert envelope["mode"]["active"] is False
    assert envelope["mode"]["production_consumer"] is False
    assert envelope["summary"]["production_consumed"] is False
    assert envelope["summary"]["production_planner_output_changed"] is False
    assert envelope["comparison_rows"] == []


def test_v3_dry_run_enabled_is_read_only_and_isolated():
    envelope = _enabled_sample()
    safety = envelope["safety_confirmations"]

    assert envelope["mode"]["read_only"] is True
    assert envelope["mode"]["production_consumer"] is False
    assert envelope["mode"]["production_enabled"] is False
    assert safety["production_planner_output_changed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["mechanical_calculations_performed"] is False
    assert safety["candidate_inputs_only"] is True
    assert safety["production_planner_imported"] is False


def test_v3_dry_run_delta_categories_are_strict_and_visible():
    envelope = _enabled_sample()
    categories = {row["delta_category"] for row in envelope["comparison_rows"]}

    assert categories.issubset(DELTA_CATEGORIES)
    assert "accepted_unchanged" in categories
    assert "accepted_explicit_dry_run_delta" in categories
    assert "rejected_unapproved_delta" in categories
    assert "blocked_unsupported_mechanic" in categories
    assert "blocked_text_only_mechanic" in categories
    assert "blocked_scripted_mechanic" in categories
    assert "blocked_unknown_operation" in categories
    assert "blocked_unresolved_stat_identity" in categories
    assert "blocked_value_normalization" in categories


def test_v3_dry_run_requires_provenance_for_candidate_rows():
    envelope = _enabled_sample()
    row = _row(envelope, "missing.provenance")

    assert row["status"] == "blocked"
    assert row["delta_category"] == "blocked_missing_provenance"
    assert row["blocked_reasons"] == ["missing_candidate_provenance"]


def test_v3_dry_run_keeps_missing_snapshots_blocked():
    envelope = _enabled_sample()

    assert _row(envelope, "candidate.added")["delta_category"] == "blocked_missing_current"
    assert _row(envelope, "candidate.missing")["delta_category"] == "blocked_missing_candidate"


def test_v3_dry_run_is_deterministic_for_same_inputs():
    current, candidate = build_sample_v3_dry_run_inputs()
    comparator = V3ExperimentalMechanicalDryRun()

    first = comparator.compare(
        current_output=current,
        candidate_output=candidate,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_7_foundation",
    )
    second = comparator.compare(
        current_output=current,
        candidate_output=candidate,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_7_foundation",
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["comparison_rows"] == second["comparison_rows"]
    assert first["delta_category_counts"] == second["delta_category_counts"]


def test_v3_dry_run_report_has_required_sections_and_blockers():
    report = build_v3_experimental_dry_run_mode_report()

    assert report["schema_version"] == "v3.experimental_dry_run_mode_report.1"
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_behavior_changed"] is False
    assert report["safety_confirmations"]["production_planner_output_changed"] is False
    assert "approved value normalization contracts" in report["remaining_blockers_before_mechanical_remap"]
    assert "candidate adapter implementation behind this comparison boundary" in report["remaining_blockers_before_mechanical_remap"]


def _enabled_sample():
    current, candidate = build_sample_v3_dry_run_inputs()
    return V3ExperimentalMechanicalDryRun().compare(
        current_output=current,
        candidate_output=candidate,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_7_foundation",
    )


def _row(envelope, output_key):
    return next(row for row in envelope["comparison_rows"] if row["output_key"] == output_key)
