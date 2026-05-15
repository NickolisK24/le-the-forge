from scripts.report_v3_closeout_readiness import build_v3_closeout_readiness_report


def test_v3_closeout_concludes_infrastructure_complete_without_remap():
    report = build_v3_closeout_readiness_report()

    assert report["schema_version"] == "v3.closeout_readiness_report.1"
    assert report["final_v3_conclusion"] == "V3_INFRASTRUCTURE_COMPLETE_PRODUCTION_REMAP_NOT_READY"
    assert report["v3_success_definition"] == "mechanical intelligence infrastructure phase, not production remap phase"
    assert report["production_remap_allowed"] is False
    assert report["production_remap_enabled"] is False
    assert report["metadata"]["closeout_only"] is True
    assert report["metadata"]["production_behavior_changed"] is False
    assert report["metadata"]["production_remap_performed"] is False


def test_v3_closeout_lists_required_achievements():
    report = build_v3_closeout_readiness_report()
    areas = {item["area"] for item in report["v3_achievements"]}

    assert "trusted_data_foundation" in areas
    assert "dry_run_comparison" in areas
    assert "item_affix_comparison" in areas
    assert "passive_skill_comparison" in areas
    assert "limited_candidate_execution" in areas
    assert "production_remap_gate_audit" in areas


def test_v3_closeout_preserves_production_safety_confirmations():
    report = build_v3_closeout_readiness_report()
    safety = report["production_safety_guarantees"]
    confirmations = report["closeout_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_enabled"] is False
    assert safety["production_planner_output_changed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["live_stat_aggregation_changed"] is False
    assert confirmations["production_planner_math_unchanged"] is True
    assert confirmations["runtime_planner_behavior_changed"] is False
    assert confirmations["production_stat_aggregation_added"] is False


def test_v3_closeout_keeps_blocked_mechanic_protections_visible():
    report = build_v3_closeout_readiness_report()
    guarantees = report["blocked_mechanic_guarantees"]
    confirmations = report["closeout_confirmations"]

    assert guarantees["passed"] is True
    assert guarantees["promoted_to_execution"] == []
    assert confirmations["unsupported_mechanics_remain_blocked"] is True
    assert confirmations["scripted_mechanics_remain_blocked"] is True
    assert confirmations["text_only_mechanics_remain_blocked"] is True
    assert confirmations["ambiguous_identities_remain_blocked"] is True


def test_v3_closeout_carries_deterministic_and_rollback_guarantees():
    report = build_v3_closeout_readiness_report()

    assert report["deterministic_guarantees"]["passed"] is True
    assert report["rollback_debug_guarantees"]["passed"] is True
    assert report["deterministic_guarantees"]["sample_hash"] == report["deterministic_guarantees"]["repeated_hash"]
    assert "execution_rows" in report["rollback_debug_guarantees"]["debug_visibility"]


def test_v3_closeout_marks_no_domain_stable_for_production_remap():
    report = build_v3_closeout_readiness_report()

    assert report["remap_gate_audit_summary"]["final_recommendation"] == "PRODUCTION_REMAP_NOT_READY"
    assert report["remap_gate_audit_summary"]["stable_calculable_domain_count"] == 0
    assert all(finding["stable_calculable_for_production_remap"] is False for finding in report["stable_calculable_findings"])


def test_v3_closeout_defines_v3_1_readiness_and_future_roadmap():
    report = build_v3_closeout_readiness_report()
    plan = report["v3_1_readiness_plan"]
    roadmap = {item["phase"]: item for item in report["future_roadmap"]}

    assert plan["phase_name"] == "v3.1 Mechanical Parity Hardening"
    assert "golden baseline expansion" in plan["workstreams"]
    assert "approved normalization promotion strategy" in plan["workstreams"]
    assert "policy-driven production promotion requirements" in plan["workstreams"]
    assert "v3.1" in roadmap
    assert "v3.5" in roadmap
    assert "v4" in roadmap
    assert "Mechanical Parity Hardening" == roadmap["v3.1"]["name"]


def test_v3_closeout_explains_why_production_remap_is_blocked():
    report = build_v3_closeout_readiness_report()
    blockers = set(report["why_production_remap_is_blocked"])

    assert "no domain is stable-calculable for production remap" in blockers
    assert "golden baseline evidence is not sufficient for production promotion" in blockers
    assert "stat and skill identity gaps remain blocked" in blockers
    assert "unsupported, text-only, and scripted mechanics remain excluded" in blockers
