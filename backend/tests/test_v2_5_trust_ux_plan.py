from scripts.report_v2_5_trust_ux_plan import UX_CLASSIFICATIONS, build_v2_5_trust_ux_plan


def test_v2_5_trust_ux_plan_has_required_top_level_keys():
    report = build_v2_5_trust_ux_plan()

    assert report["schema_version"] == "v2_5.trust_ux_plan.1"
    for key in (
        "summary",
        "ux_items",
        "classification_counts",
        "v2_5_implementation_sequence",
        "user_facing_concepts",
        "developer_only_concepts",
        "frontend_gaps",
        "backend_report_data_available_for_ux",
        "safety_confirmations",
    ):
        assert key in report


def test_v2_5_trust_ux_classifications_are_strict():
    report = build_v2_5_trust_ux_plan()

    classifications = {item["classification"] for item in report["ux_items"]}
    assert classifications.issubset(UX_CLASSIFICATIONS)
    assert report["allowed_classifications"] == sorted(UX_CLASSIFICATIONS)


def test_v2_5_sequence_is_ordered_and_non_empty():
    report = build_v2_5_trust_ux_plan()
    sequence = report["v2_5_implementation_sequence"]

    assert sequence
    assert [step["order"] for step in sequence] == sorted(step["order"] for step in sequence)
    assert sequence[0]["id"] == "shared_trust_support_badges"


def test_v2_5_plan_preserves_release_readiness_decisions():
    report = build_v2_5_trust_ux_plan()
    safety = report["safety_confirmations"]

    assert safety["v2_infrastructure_ready"] is True
    assert safety["production_planner_ready"] is False
    assert safety["mechanical_remap_ready"] is False
    assert safety["production_consumed"] is False


def test_v2_5_plan_preserves_mechanical_blockers():
    report = build_v2_5_trust_ux_plan()
    safety = report["safety_confirmations"]

    assert safety["stable_calculable_count"] == 0
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"
    assert safety["value_normalization_promoted"] is False
    assert safety["skill_identity_bridge_added"] is False


def test_v2_5_plan_has_user_facing_and_developer_only_boundaries():
    report = build_v2_5_trust_ux_plan()

    assert report["user_facing_concepts"]
    assert report["developer_only_concepts"]
    assert any(item["id"] == "raw_debug_payloads" for item in report["developer_only_concepts"])
    assert "raw API envelopes" in report["debug_only_boundaries"]


def test_v2_5_plan_inventories_existing_frontend_surfaces():
    report = build_v2_5_trust_ux_plan()

    assert report["frontend_inventory"]
    assert all(item["exists"] for item in report["frontend_inventory"])
    assert any(item["id"] == "v2_envelope_helpers" for item in report["frontend_inventory"])


def test_v2_5_plan_identifies_frontend_gaps_without_implementation():
    report = build_v2_5_trust_ux_plan()

    gap_ids = {gap["id"] for gap in report["frontend_gaps"]}
    assert "shared_user_facing_badges_missing" in gap_ids
    assert "trusted_data_explanation_page_missing" in gap_ids
    assert report["metadata"]["frontend_behavior_changed"] is False
    assert report["metadata"]["backend_behavior_changed"] is False
