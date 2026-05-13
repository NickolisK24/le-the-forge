from app.planner_adapters.v2.experimental_mode import INCLUDED_SUMMARIES, V2ExperimentalPlannerAdapterMode
from scripts.report_v2_experimental_planner_adapter_mode import build_v2_experimental_planner_adapter_mode_report


def test_v2_experimental_planner_adapter_mode_defaults_disabled():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode()

    assert summary["mode"]["enabled"] is False
    assert summary["mode"]["active"] is False
    assert summary["mode"]["default_enabled"] is False
    assert summary["summary"]["summaries_included"] == []
    assert summary["summaries"] == {}


def test_v2_experimental_planner_adapter_mode_disabled_does_not_expose_active_mode():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode(enabled=False)

    assert summary["mode"]["status"] == "disabled"
    assert summary["summary"]["adapter_visible_modifier_count"] == 0
    assert summary["summary"]["blocked_modifier_count"] == 0
    assert summary["safety_confirmations"]["mechanical_calculations_performed"] is False


def test_v2_experimental_planner_adapter_mode_enabled_includes_diagnostic_summaries():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode(enabled=True, sample_limit=1)

    assert summary["mode"]["enabled"] is True
    assert summary["mode"]["active"] is True
    assert summary["summary"]["summaries_included"] == list(INCLUDED_SUMMARIES)
    for name in INCLUDED_SUMMARIES:
        assert name in summary["summaries"]
    assert summary["summary"]["adapter_visible_modifier_count"] == 19398
    assert summary["summary"]["blocked_modifier_count"] == 19398


def test_v2_experimental_planner_adapter_mode_enabled_remains_non_calculating():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode(enabled=True, sample_limit=1)

    assert summary["summary"]["planner_calculable_count"] == 0
    assert summary["summary"]["stable_calculable_count"] == 0
    assert summary["safety_confirmations"]["production_consumed"] is False
    assert summary["safety_confirmations"]["production_planner_output_changed"] is False
    assert summary["safety_confirmations"]["mechanical_calculations_performed"] is False


def test_v2_experimental_planner_adapter_mode_preserves_policy_statuses():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode(enabled=True, sample_limit=1)

    assert summary["summary"]["value_normalization_status"] == "audit_only"
    assert summary["summary"]["skill_identity_bridge_status"] == "unbridged"
    assert summary["safety_confirmations"]["value_normalization_promoted"] is False
    assert summary["safety_confirmations"]["skill_identity_bridge_added"] is False


def test_v2_experimental_planner_adapter_mode_reports_baseline_readiness():
    summary = V2ExperimentalPlannerAdapterMode().summarize_mode(enabled=True, sample_limit=1)

    assert summary["baseline_readiness"]["safe_now_fixture_count"] == 7
    assert summary["baseline_readiness"]["blocked_fixture_count"] == 6
    assert summary["summary"]["safe_now_baseline_fixture_count"] == 7
    assert summary["summary"]["blocked_baseline_fixture_count"] == 6


def test_v2_experimental_planner_adapter_mode_has_no_route_by_default():
    report = build_v2_experimental_planner_adapter_mode_report()

    assert report["metadata"]["optional_route_added"] is False
    assert report["mode_enabled_behavior"]["optional_route_added"] is False
    assert report["mode_disabled_behavior"]["optional_route_added"] is False
    assert report["safety_confirmations"]["production_planner_route_added"] is False


def test_v2_experimental_planner_adapter_mode_report_has_required_sections():
    report = build_v2_experimental_planner_adapter_mode_report()

    for key in (
        "mode_enabled_behavior",
        "mode_disabled_behavior",
        "summary",
        "summaries",
        "blocked_reason_summary",
        "baseline_readiness",
        "diagnostic_context",
        "safety_confirmations",
    ):
        assert key in report
