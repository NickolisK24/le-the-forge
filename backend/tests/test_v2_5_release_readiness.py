from scripts.report_v2_5_release_readiness import (
    ALLOWED_CLASSIFICATIONS,
    build_v2_5_release_readiness_report,
)


def test_v2_5_release_readiness_report_has_required_top_level_keys():
    report = build_v2_5_release_readiness_report()

    assert report["schema_version"] == "v2_5.release_readiness.1"
    for key in (
        "readiness_decision",
        "feature_completion",
        "frontend_trust_ux_surface_coverage",
        "key_route_coverage",
        "support_trust_badge_coverage",
        "provenance_warning_coverage",
        "limitation_copy_coverage",
        "manual_qa_checklist",
        "remaining_items",
        "safety_confirmations",
    ):
        assert key in report


def test_v2_5_release_readiness_decision_is_ready_with_existing_evidence():
    report = build_v2_5_release_readiness_report()

    assert report["readiness_decision"]["v2_5_trust_ux_ready"] is True
    assert report["feature_completion"]["completed_surface_count"] == report["feature_completion"]["expected_surface_count"]
    assert all(item["exists"] for item in report["required_v2_5_docs"])
    assert all(item["registered"] for item in report["key_route_coverage"])


def test_v2_5_release_readiness_keeps_production_and_v3_ready_false():
    report = build_v2_5_release_readiness_report()

    assert report["readiness_decision"]["production_planner_ready"] is False
    assert report["readiness_decision"]["v3_mechanical_ready"] is False
    assert report["readiness_decision"]["recommended_next_track"] == "v3_mechanical_intelligence_planning"


def test_v2_5_release_readiness_classifications_are_strict():
    report = build_v2_5_release_readiness_report()

    classifications = {item["classification"] for item in report["remaining_items"]}
    assert classifications.issubset(ALLOWED_CLASSIFICATIONS)


def test_v2_5_release_readiness_has_required_route_inventory():
    report = build_v2_5_release_readiness_report()

    routes = {item["route"] for item in report["key_route_coverage"]}
    assert "/trusted-data" in routes
    assert "/trusted-data/support" in routes
    assert "/trusted-data/pre-v3-readiness" in routes
    assert "/debug/v2" in routes
    assert "/debug/v2-stats-modifiers" in routes
    assert "/debug/forge-safe-affixes" in routes
    assert "/debug/v2-affixes" in routes


def test_v2_5_release_readiness_has_required_feature_checklist():
    report = build_v2_5_release_readiness_report()

    surface_ids = {item["id"] for item in report["feature_completion"]["surfaces"]}
    assert "shared_trust_support_badges" in surface_ids
    assert "provenance_warning_panels" in surface_ids
    assert "user_facing_limitation_copy" in surface_ids
    assert "stats_modifiers_debug_page" in surface_ids
    assert "trusted_data_explanation_page" in surface_ids
    assert "planner_adapter_status_panel" in surface_ids
    assert "support_matrix" in surface_ids
    assert "pre_v3_readiness_dashboard" in surface_ids


def test_v2_5_release_readiness_has_manual_qa_checklist():
    report = build_v2_5_release_readiness_report()

    qa_ids = {item["id"] for item in report["manual_qa_checklist"]}
    assert "trusted_data_loads" in qa_ids
    assert "support_matrix_loads" in qa_ids
    assert "pre_v3_readiness_loads" in qa_ids
    assert "stats_modifiers_loads" in qa_ids
    assert "affixes_actual_route_loads" in qa_ids
    assert "affix_alias_works" in qa_ids
    assert "no_production_math_claims" in qa_ids


def test_v2_5_release_readiness_preserves_safety_state():
    report = build_v2_5_release_readiness_report()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_planner_remap_performed"] is False
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"
    assert safety["experimental_mode_enabled_by_default"] is False
