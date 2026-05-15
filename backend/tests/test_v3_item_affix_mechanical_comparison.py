from app.planner_adapters.v3.item_affix_comparison import (
    ITEM_AFFIX_COMPONENT_TYPES,
    V3ItemAffixMechanicalComparison,
    build_sample_item_affix_rows,
)
from scripts.report_v3_item_affix_mechanical_comparison import (
    build_v3_item_affix_mechanical_comparison_report,
)


def test_item_affix_comparison_defaults_disabled_and_non_production():
    current_rows, candidate_rows = build_sample_item_affix_rows()
    report = V3ItemAffixMechanicalComparison().compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
    )

    assert report["mode"]["enabled"] is False
    assert report["mode"]["production_consumer"] is False
    assert report["summary"]["production_consumed"] is False
    assert report["summary"]["production_planner_output_changed"] is False
    assert report["comparison_rows"] == []


def test_item_affix_comparison_enabled_remains_isolated():
    report = _enabled_report()
    safety = report["safety_confirmations"]

    assert report["mode"]["read_only"] is True
    assert report["mode"]["production_enabled"] is False
    assert safety["production_planner_output_changed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["mechanical_calculations_performed"] is False
    assert safety["runtime_stat_aggregation_changed"] is False
    assert safety["unique_set_logic_added"] is False
    assert safety["tooltip_semantics_inferred"] is False


def test_item_affix_comparison_has_expected_supported_components():
    report = _enabled_report()

    assert set(report["run"]["component_types"]) == ITEM_AFFIX_COMPONENT_TYPES
    assert report["component_summary"]["item_base"] == 1
    assert report["component_summary"]["implicit"] == 1
    assert report["component_summary"]["affix"] >= 1


def test_item_affix_comparison_classifies_approved_and_rejected_deltas():
    report = _enabled_report()

    assert _row(report, "affix:fire-damage::affix::affix:fire-damage::fire_damage::increased")[
        "delta_category"
    ] == "accepted_explicit_dry_run_delta"
    assert _row(report, "affix:armor-delta::affix::affix:armor::armor::flat")[
        "delta_category"
    ] == "rejected_unapproved_delta"


def test_item_affix_comparison_blocks_unsupported_and_unknown_rows():
    report = _enabled_report()

    expected = {
        "affix:unsupported::affix::affix:unsupported::summon_behavior::flat": "blocked_unsupported_mechanic",
        "affix:text-only::affix::affix:text-only::display_only_note::flat": "blocked_text_only_mechanic",
        "affix:scripted::affix::affix:scripted::scripted_proc::flat": "blocked_scripted_mechanic",
        "affix:unknown-operation::affix::affix:unknown-operation::void_damage::unknown": "blocked_unknown_operation",
        "affix:unknown-stat::affix::affix:unknown-stat::unknown_stat::flat": "blocked_unresolved_stat_identity",
        "affix:audit-value::affix::affix:audit-value::minion_damage::increased": "blocked_value_normalization",
    }
    for key, category in expected.items():
        assert _row(report, key)["delta_category"] == category


def test_item_affix_comparison_requires_candidate_provenance():
    report = _enabled_report()
    row = _row(report, "affix:missing-provenance::affix::affix:missing-provenance::health::flat")

    assert row["delta_category"] == "blocked_missing_provenance"
    assert row["blocked_reasons"] == ["missing_candidate_provenance"]


def test_item_affix_comparison_sorting_and_hash_are_deterministic():
    current_rows, candidate_rows = build_sample_item_affix_rows()
    comparator = V3ItemAffixMechanicalComparison()
    first = comparator.compare(
        current_rows=list(reversed(current_rows)),
        candidate_rows=list(reversed(candidate_rows)),
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_8_item_affix_sample",
    )
    second = comparator.compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_8_item_affix_sample",
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["output_key"] for row in first["comparison_rows"]] == sorted(
        row["output_key"] for row in first["comparison_rows"]
    )


def test_item_affix_report_has_required_sections_and_limitations():
    report = build_v3_item_affix_mechanical_comparison_report()

    assert report["schema_version"] == "v3.item_affix_mechanical_comparison_report.1"
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_behavior_changed"] is False
    assert "accepted_explicit_dry_run_delta" in report["supported_comparison_categories"]
    assert "blocked_unsupported_mechanic" in report["blocked_comparison_categories"]
    assert "passive and skill identity bridge policy" in report["remaining_blockers_before_passive_skill_comparison"]


def _enabled_report():
    current_rows, candidate_rows = build_sample_item_affix_rows()
    return V3ItemAffixMechanicalComparison().compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_8_item_affix_sample",
    )


def _row(report, output_key):
    return next(row for row in report["comparison_rows"] if row["output_key"] == output_key)
