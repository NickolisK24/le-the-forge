from app.planner_adapters.v3.passive_skill_comparison import (
    PASSIVE_SKILL_COMPONENT_TYPES,
    V3PassiveSkillMechanicalComparison,
    build_sample_passive_skill_rows,
)
from scripts.report_v3_passive_skill_mechanical_comparison import (
    build_v3_passive_skill_mechanical_comparison_report,
)


def test_passive_skill_comparison_defaults_disabled_and_non_production():
    current_rows, candidate_rows = build_sample_passive_skill_rows()
    report = V3PassiveSkillMechanicalComparison().compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
    )

    assert report["mode"]["enabled"] is False
    assert report["mode"]["production_consumer"] is False
    assert report["summary"]["production_consumed"] is False
    assert report["summary"]["production_planner_output_changed"] is False
    assert report["comparison_rows"] == []


def test_passive_skill_comparison_enabled_remains_isolated():
    report = _enabled_report()
    safety = report["safety_confirmations"]

    assert report["mode"]["read_only"] is True
    assert report["mode"]["production_enabled"] is False
    assert safety["production_planner_output_changed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["mechanical_calculations_performed"] is False
    assert safety["skill_identity_bridge_added"] is False
    assert safety["conditional_semantics_implemented"] is False
    assert safety["triggered_semantics_implemented"] is False
    assert safety["runtime_stat_aggregation_changed"] is False


def test_passive_skill_comparison_has_expected_components():
    report = _enabled_report()

    assert set(report["run"]["component_types"]) == PASSIVE_SKILL_COMPONENT_TYPES
    assert report["component_summary"]["passive_node"] >= 1
    assert report["component_summary"]["skill_node"] >= 1
    assert report["component_summary"]["skill_modifier"] >= 1


def test_passive_skill_comparison_classifies_approved_and_rejected_deltas():
    report = _enabled_report()

    assert _row(report, "sentinel:passive:delta::passive_node::passive:delta::none::armor::flat")[
        "delta_category"
    ] == "accepted_explicit_dry_run_delta"
    assert _row(report, "skill:rejected-delta::skill_node::skill:rejected-delta::fireball::fire_damage::increased")[
        "delta_category"
    ] == "rejected_unapproved_delta"


def test_passive_skill_identity_and_semantics_gaps_are_blocked():
    report = _enabled_report()
    expected = {
        "skill:unresolved::skill_node::skill:unresolved::unknown::fire_damage::increased": "blocked_unresolved_skill_identity",
        "skill:ambiguous::skill_node::skill:ambiguous::ambiguous::cold_damage::increased": "blocked_ambiguous_skill_identity",
        "skill:conditional::skill_node::skill:conditional::fireball::fire_damage::more": "blocked_conditional_semantics",
        "skill:triggered::skill_modifier::skill:triggered::fireball::ignite_chance::chance": "blocked_triggered_semantics",
        "skill:unknown-operation::skill_node::skill:unknown-operation::fireball::void_damage::unknown": "blocked_unknown_operation",
        "skill:unknown-stat::skill_node::skill:unknown-stat::fireball::unknown_stat::flat": "blocked_unresolved_stat_identity",
    }

    for key, category in expected.items():
        assert _row(report, key)["delta_category"] == category


def test_passive_skill_support_and_value_gaps_are_blocked():
    report = _enabled_report()
    expected = {
        "skill:audit-value::skill_node::skill:audit-value::fireball::minion_damage::increased": "blocked_value_normalization",
        "skill:unsupported::skill_node::skill:unsupported::fireball::summon_behavior::flat": "blocked_unsupported_mechanic",
        "skill:text-only::skill_node::skill:text-only::fireball::display_note::flat": "blocked_text_only_mechanic",
        "skill:scripted::skill_modifier::skill:scripted::fireball::scripted_proc::flat": "blocked_scripted_mechanic",
    }

    for key, category in expected.items():
        assert _row(report, key)["delta_category"] == category


def test_passive_skill_comparison_requires_candidate_provenance():
    report = _enabled_report()
    row = _row(report, "skill:missing-provenance::skill_node::skill:missing-provenance::fireball::health::flat")

    assert row["delta_category"] == "blocked_missing_provenance"
    assert row["blocked_reasons"] == ["missing_candidate_provenance"]


def test_passive_skill_comparison_sorting_and_hash_are_deterministic():
    current_rows, candidate_rows = build_sample_passive_skill_rows()
    comparator = V3PassiveSkillMechanicalComparison()
    first = comparator.compare(
        current_rows=list(reversed(current_rows)),
        candidate_rows=list(reversed(candidate_rows)),
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_9_passive_skill_sample",
    )
    second = comparator.compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_9_passive_skill_sample",
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["output_key"] for row in first["comparison_rows"]] == sorted(
        row["output_key"] for row in first["comparison_rows"]
    )


def test_passive_skill_report_has_required_sections_and_blockers():
    report = build_v3_passive_skill_mechanical_comparison_report()

    assert report["schema_version"] == "v3.passive_skill_mechanical_comparison_report.1"
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_behavior_changed"] is False
    assert "blocked_unresolved_skill_identity" in report["blocked_comparison_categories"]
    assert "blocked_conditional_semantics" in report["blocked_comparison_categories"]
    assert "approved passive and skill identity bridge policy" in report[
        "remaining_blockers_before_limited_opt_in_mechanical_adapter_mode"
    ]


def _enabled_report():
    current_rows, candidate_rows = build_sample_passive_skill_rows()
    return V3PassiveSkillMechanicalComparison().compare(
        current_rows=current_rows,
        candidate_rows=candidate_rows,
        enabled=True,
        baseline_snapshot_id="baseline:v3_phase_9_passive_skill_sample",
    )


def _row(report, output_key):
    return next(row for row in report["comparison_rows"] if row["output_key"] == output_key)
