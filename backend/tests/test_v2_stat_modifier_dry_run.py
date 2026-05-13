from app.planner_adapters.v2.stat_modifier_dry_run import (
    COMPARISON_CATEGORIES,
    V2StatModifierDryRunComparison,
)
from scripts.report_v2_stat_modifier_dry_run import build_v2_stat_modifier_dry_run_report


def test_v2_stat_modifier_dry_run_report_has_required_top_level_keys():
    report = build_v2_stat_modifier_dry_run_report()

    assert report["schema_version"] == "v2.stat_modifier_dry_run.1"
    for key in (
        "summary",
        "operation_distribution",
        "value_scale_distribution",
        "blocked_reason_counts",
        "comparison_category_summary",
        "stat_identity_findings",
        "modifier_identity_coverage",
        "current_planner_expectation_gaps",
        "golden_baseline_requirements",
        "safety_confirmations",
    ):
        assert key in report


def test_v2_stat_modifier_dry_run_counts_remain_non_calculating():
    summary = V2StatModifierDryRunComparison().summarize_dry_run(sample_limit=2)

    assert summary["summary"]["stat_registry_count"] == 2070
    assert summary["summary"]["modifier_row_count"] == 19398
    assert summary["summary"]["adapter_visible_modifier_count"] == 19398
    assert summary["summary"]["planner_calculable_modifier_count"] == 0
    assert summary["summary"]["stable_calculable_modifier_count"] == 0
    assert summary["summary"]["blocked_modifier_count"] == 19398
    assert summary["summary"]["production_consumed"] is False


def test_v2_stat_modifier_dry_run_keeps_value_normalization_audit_only():
    report = build_v2_stat_modifier_dry_run_report()

    assert report["summary"]["value_normalization_status"] == "audit_only"
    assert report["safety_confirmations"]["value_normalization_promoted"] is False
    assert report["summary"]["source_unit_value_scale_count"] == 6248
    assert report["summary"]["unknown_value_scale_count"] == 13150
    assert report["value_scale_distribution"]["source_units"] == 6248
    assert report["value_scale_distribution"]["unknown"] == 13150


def test_v2_stat_modifier_dry_run_exposes_blocked_reasons():
    report = build_v2_stat_modifier_dry_run_report()

    assert report["blocked_reason_counts"]["source_units_value_scale"] == 6248
    assert report["blocked_reason_counts"]["unknown_value_scale"] == 13150
    assert report["blocked_reason_counts"]["unknown_operation"] == 11606
    assert report["blocked_reason_counts"]["not_stable_calculable"] == 19398
    assert report["blocked_reason_counts"]["unstable_support_status"] == 19398


def test_v2_stat_modifier_dry_run_comparison_categories_are_allowed():
    report = build_v2_stat_modifier_dry_run_report()

    assert set(report["comparison_category_summary"]).issubset(COMPARISON_CATEGORIES)
    assert report["comparison_category_summary"]["blocked_by_value_normalization"] == 19398


def test_v2_stat_modifier_dry_run_unknown_operation_stays_blocked():
    report = build_v2_stat_modifier_dry_run_report()

    assert report["operation_distribution"]["unknown"] == 11606
    assert report["blocked_reason_counts"]["unknown_operation"] == 11606


def test_v2_stat_modifier_dry_run_preserves_identity_and_production_safety():
    report = build_v2_stat_modifier_dry_run_report()

    assert report["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert report["safety_confirmations"]["skill_identity_bridge_added"] is False
    assert report["safety_confirmations"]["production_consumed"] is False
    assert report["safety_confirmations"]["planner_output_changed"] is False
    assert report["safety_confirmations"]["stat_aggregation_behavior_changed"] is False
    assert report["safety_confirmations"]["crafting_behavior_changed"] is False
