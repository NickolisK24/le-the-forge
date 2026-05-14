import sys

from app.planner_adapters.v2.diagnostics import build_planner_adapter_diagnostics
from scripts.report_v2_planner_adapter_diagnostics import build_v2_planner_adapter_diagnostics_report


def test_v2_planner_adapter_diagnostics_has_required_sections():
    report = build_planner_adapter_diagnostics()

    assert report["schema_version"] == "v2.planner_adapter_diagnostics.1"
    assert "summary" in report
    assert "domains" in report
    assert "display_only_candidates" in report
    assert "blocked_mechanical_data" in report
    assert "future_remap_phase_status" in report
    assert "safety_confirmations" in report


def test_v2_planner_adapter_diagnostics_reports_zero_planner_calculable_records():
    report = build_planner_adapter_diagnostics()

    assert report["summary"]["adapter_visible_record_count"] == 19398
    assert report["summary"]["planner_calculable_record_count"] == 0
    assert report["summary"]["stable_calculable_count"] == 0
    assert report["planner_calculable_data"]["status"] == "none_available"


def test_v2_planner_adapter_diagnostics_preserves_safety_state():
    report = build_planner_adapter_diagnostics()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["planner_output_changed"] is False
    assert safety["crafting_behavior_changed"] is False
    assert safety["simulation_behavior_changed"] is False
    assert safety["stat_aggregation_behavior_changed"] is False
    assert safety["value_normalization_promoted"] is False
    assert safety["skill_identity_bridge_added"] is False
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v2_planner_adapter_diagnostics_exposes_blocked_reasons():
    report = build_planner_adapter_diagnostics()

    assert report["blocked_reason_counts"]["not_stable_calculable"] == 19398
    assert report["blocked_reason_counts"]["unstable_support_status"] == 19398
    assert report["blocked_reason_counts"]["unknown_value_scale"] == 13150
    assert report["top_blocked_reasons"][0]["reason"] in {
        "not_stable_calculable",
        "unstable_support_status",
    }


def test_v2_planner_adapter_diagnostics_distinguishes_display_only_from_calculable():
    report = build_planner_adapter_diagnostics()

    assert report["display_only_candidates"]
    assert all(candidate["mode"] == "display_only_candidate" for candidate in report["display_only_candidates"])
    assert all(candidate["planner_calculable"] is False for candidate in report["display_only_candidates"])
    assert report["blocked_mechanical_data"]
    assert all(item["mode"] == "blocked_mechanical_data" for item in report["blocked_mechanical_data"])


def test_v2_planner_adapter_diagnostics_does_not_import_production_runtime_modules():
    forbidden = {
        "app.engines.stat_engine",
        "app.engines.craft_engine",
        "app.engines.combat_simulator",
        "app.services.craft_service",
        "app.services.simulation_service",
    }
    before = {name for name in forbidden if name in sys.modules}

    build_planner_adapter_diagnostics()

    after = {name for name in forbidden if name in sys.modules}
    assert after == before


def test_v2_planner_adapter_diagnostics_report_builder_preserves_metadata():
    report = build_v2_planner_adapter_diagnostics_report()

    assert report["metadata"]["diagnostic_only"] is True
    assert report["metadata"]["optional_route_added"] is False
    assert report["metadata"]["planner_remap_performed"] is False
    assert report["summary"]["value_normalization_status"] == "audit_only"
