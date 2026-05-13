from scripts.report_v2_release_readiness import (
    REQUIRED_PREVIOUS_REPORTS,
    WORK_CLASSIFICATIONS,
    build_v2_release_readiness_report,
)


def test_v2_release_readiness_report_has_required_top_level_keys():
    report = build_v2_release_readiness_report()

    assert report["schema_version"] == "v2.release_readiness.1"
    for key in (
        "readiness_decision",
        "readiness_evidence",
        "infrastructure_completeness",
        "trusted_data_coverage",
        "production_blockers",
        "classified_remaining_work",
        "required_previous_reports",
        "safety_confirmations",
    ):
        assert key in report


def test_v2_release_readiness_decision_uses_existing_evidence():
    report = build_v2_release_readiness_report()

    evidence = report["readiness_evidence"]
    assert evidence["all_required_reports_present"] is True
    assert evidence["validation_status"] == "pass"
    assert evidence["repository_loaded_domain_count"] == evidence["repository_domain_count"] == 10
    assert evidence["missing_artifact_count"] == 0
    assert evidence["invalid_repository_count"] == 0
    assert report["readiness_decision"]["v2_infrastructure_ready"] is True


def test_v2_release_readiness_keeps_production_and_mechanical_ready_false():
    report = build_v2_release_readiness_report()

    assert report["readiness_decision"]["production_planner_ready"] is False
    assert report["readiness_decision"]["mechanical_remap_ready"] is False
    assert report["readiness_decision"]["recommended_next_track"] == "v2_5_trust_ux_layer"


def test_v2_release_readiness_classifications_are_strict():
    report = build_v2_release_readiness_report()

    classifications = {item["classification"] for item in report["classified_remaining_work"]}
    classifications.update(item["classification"] for item in report["production_blockers"])
    assert classifications.issubset(WORK_CLASSIFICATIONS)


def test_v2_release_readiness_includes_required_production_blockers():
    report = build_v2_release_readiness_report()

    blocker_ids = {item["id"] for item in report["production_blockers"]}
    assert "stable_calculable_zero" in blocker_ids
    assert "value_normalization_audit_only" in blocker_ids
    assert "source_units_unresolved" in blocker_ids
    assert "unknown_value_scales_unresolved" in blocker_ids
    assert "unknown_operations_unresolved" in blocker_ids
    assert "skill_identity_gaps_unbridged" in blocker_ids
    assert "mechanical_baselines_missing" in blocker_ids


def test_v2_release_readiness_experimental_mode_remains_disabled_by_default():
    report = build_v2_release_readiness_report()

    assert report["readiness_evidence"]["experimental_mode_default_enabled"] is False
    assert report["safety_confirmations"]["experimental_mode_enabled_by_default"] is False


def test_v2_release_readiness_preserves_safety_state():
    report = build_v2_release_readiness_report()

    safety = report["safety_confirmations"]
    assert safety["production_consumed"] is False
    assert safety["production_planner_remap_performed"] is False
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v2_release_readiness_references_required_previous_reports():
    report = build_v2_release_readiness_report()

    report_names = {item["report"] for item in report["required_previous_reports"]}
    assert report_names == set(REQUIRED_PREVIOUS_REPORTS)
    assert all(item["exists"] for item in report["required_previous_reports"])
