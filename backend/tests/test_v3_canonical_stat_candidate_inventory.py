from scripts.report_v3_canonical_stat_candidate_inventory import (
    ALLOWED_CANDIDATE_STATUSES,
    CANDIDATE_ENTRY_FIELDS,
    build_v3_canonical_stat_candidate_inventory_report,
)


def test_v3_candidate_inventory_report_generation_succeeds():
    report = build_v3_canonical_stat_candidate_inventory_report()

    assert report["schema_version"] == "v3.canonical_stat_candidate_inventory.1"
    assert report["summary"]["total_stat_registry_entries"] == 2070
    assert report["summary"]["total_modifier_rows"] == 19398


def test_v3_candidate_inventory_has_required_top_level_keys():
    report = build_v3_canonical_stat_candidate_inventory_report()

    for key in (
        "summary",
        "candidate_entry_fields",
        "allowed_candidate_statuses",
        "candidate_status_distribution",
        "identity_state_distribution",
        "conservative_ranking_criteria",
        "candidate_inventory_entries",
        "recommended_pilot_candidates",
        "explicitly_excluded_candidates",
        "dependency_summaries",
        "evidence_gaps",
        "production_remap_blockers",
        "safety_confirmations",
        "recommended_next_phase",
    ):
        assert key in report


def test_v3_candidate_inventory_entries_include_required_fields():
    report = build_v3_canonical_stat_candidate_inventory_report()

    assert report["candidate_inventory_entries"]
    for entry in report["candidate_inventory_entries"]:
        assert set(CANDIDATE_ENTRY_FIELDS).issubset(set(entry))


def test_v3_candidate_inventory_statuses_are_allowed():
    report = build_v3_canonical_stat_candidate_inventory_report()

    statuses = {entry["candidate_status"] for entry in report["candidate_inventory_entries"]}
    statuses.update(report["candidate_status_distribution"])
    assert statuses.issubset(ALLOWED_CANDIDATE_STATUSES)


def test_v3_candidate_inventory_never_allows_promotion():
    report = build_v3_canonical_stat_candidate_inventory_report()

    assert all(entry["promotion_allowed"] is False for entry in report["candidate_inventory_entries"])
    assert all(entry["promotion_allowed"] is False for entry in report["recommended_pilot_candidates"])
    assert all(entry["promotion_allowed"] is False for entry in report["explicitly_excluded_candidates"])


def test_v3_candidate_inventory_preserves_no_planner_or_stable_promotion():
    report = build_v3_canonical_stat_candidate_inventory_report()
    safety = report["safety_confirmations"]

    assert safety["planner_calculable_promoted"] is False
    assert safety["stable_calculable_promoted"] is False
    assert safety["planner_calculable_count"] == 0
    assert safety["stable_calculable_count"] == 0


def test_v3_candidate_inventory_preserves_non_consumption_and_audit_only_status():
    report = build_v3_canonical_stat_candidate_inventory_report()
    safety = report["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_planner_changed"] is False
    assert safety["values_normalized"] is False
    assert safety["value_normalization_status"] == "audit_only"
    assert safety["skill_identity_bridge_status"] == "unbridged"


def test_v3_candidate_inventory_keeps_ambiguous_mappings_blocked():
    report = build_v3_canonical_stat_candidate_inventory_report()

    assert report["summary"]["ambiguous_mapping_stat_count"] == 253
    assert report["summary"]["ambiguous_mapping_modifier_count"] == 7064
    assert report["candidate_status_distribution"]["candidate_blocked_by_ambiguity"] > 0
    assert report["safety_confirmations"]["ambiguous_mappings_blocked"] is True


def test_v3_candidate_inventory_recommended_next_phase_exists():
    report = build_v3_canonical_stat_candidate_inventory_report()

    assert report["recommended_next_phase"] == "v3_skill_identity_bridge_policy"
    assert report["recommended_pilot_candidates"]


def test_v3_candidate_inventory_has_safety_confirmations():
    report = build_v3_canonical_stat_candidate_inventory_report()
    safety = report["safety_confirmations"]

    for key in (
        "stat_identities_promoted",
        "canonical_candidates_promoted",
        "stat_calculations_changed",
        "values_normalized",
        "operation_semantics_implemented",
        "planner_calculable_promoted",
        "stable_calculable_promoted",
        "production_consumed",
        "unresolved_stat_identities_blocked",
        "ambiguous_mappings_blocked",
    ):
        assert key in safety
