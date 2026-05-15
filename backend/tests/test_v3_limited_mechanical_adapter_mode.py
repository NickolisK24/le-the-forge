from app.planner_adapters.v3.limited_mechanical_adapter import (
    EXECUTED_CATEGORIES,
    NON_EXECUTED_CATEGORIES,
    V3LimitedMechanicalAdapter,
    build_sample_limited_adapter_inputs,
)
from scripts.report_v3_limited_mechanical_adapter_mode import build_v3_limited_mechanical_adapter_mode_report


def test_limited_adapter_defaults_disabled_and_non_production():
    report = V3LimitedMechanicalAdapter().execute(
        comparison_reports=build_sample_limited_adapter_inputs(),
        allowed_domains={"item_affix", "passive_skill"},
    )

    assert report["mode"]["enabled"] is False
    assert report["mode"]["production_consumer"] is False
    assert report["summary"]["candidate_execution_performed"] is False
    assert report["summary"]["production_consumed"] is False
    assert report["execution_rows"] == []
    assert report["candidate_aggregates"] == []


def test_limited_adapter_enabled_executes_only_accepted_dry_run_rows():
    report = _enabled_report()

    assert report["summary"]["executed_row_count"] > 0
    assert report["summary"]["rejected_row_count"] > 0
    assert report["summary"]["blocked_row_count"] > 0
    assert set(row["execution_category"] for row in report["execution_rows"] if row["status"] == "executed") <= EXECUTED_CATEGORIES
    assert all(row["gate_evidence"]["dry_run_accepted"] for row in report["execution_rows"] if row["status"] == "executed")
    assert all(row["provenance"] for row in report["execution_rows"] if row["status"] == "executed")


def test_limited_adapter_preserves_rejected_and_blocked_categories():
    report = _enabled_report()
    categories = set(report["execution_category_counts"])

    assert "rejected_unapproved_delta" in categories
    assert "blocked_unsupported_mechanic" in categories
    assert "blocked_text_only_mechanic" in categories
    assert "blocked_scripted_mechanic" in categories
    assert "blocked_unknown_operation" in categories
    assert "blocked_unresolved_stat_identity" in categories
    assert "blocked_unresolved_skill_identity" in categories
    assert "blocked_ambiguous_skill_identity" in categories
    assert "blocked_conditional_semantics" in categories
    assert "blocked_triggered_semantics" in categories
    assert categories <= EXECUTED_CATEGORIES | NON_EXECUTED_CATEGORIES


def test_limited_adapter_domain_gate_blocks_disallowed_domains():
    report = V3LimitedMechanicalAdapter().execute(
        comparison_reports=build_sample_limited_adapter_inputs(),
        enabled=True,
        allowed_domains={"item_affix"},
    )
    passive_rows = [row for row in report["execution_rows"] if row["domain"] == "passive_skill"]

    assert passive_rows
    assert all(row["execution_category"] == "blocked_domain_not_allowed" for row in passive_rows)
    assert all(row["status"] == "blocked" for row in passive_rows)
    assert all(row["gate_evidence"]["domain_allowed"] is False for row in passive_rows)


def test_limited_adapter_aggregates_only_executed_rows_with_provenance():
    report = _enabled_report()
    executed_keys = {row["output_key"] for row in report["execution_rows"] if row["status"] == "executed"}

    assert report["candidate_aggregates"]
    for aggregate in report["candidate_aggregates"]:
        assert aggregate["source_row_count"] >= 1
        assert set(aggregate["source_output_keys"]) <= executed_keys
        assert aggregate["provenance"]


def test_limited_adapter_sorting_and_hash_are_deterministic():
    comparison_reports = build_sample_limited_adapter_inputs()
    adapter = V3LimitedMechanicalAdapter()
    first = adapter.execute(
        comparison_reports=list(reversed(comparison_reports)),
        enabled=True,
        allowed_domains={"passive_skill", "item_affix"},
    )
    second = adapter.execute(
        comparison_reports=comparison_reports,
        enabled=True,
        allowed_domains={"item_affix", "passive_skill"},
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [(row["domain"], row["output_key"]) for row in first["execution_rows"]] == sorted(
        (row["domain"], row["output_key"]) for row in first["execution_rows"]
    )


def test_limited_adapter_safety_confirmations_keep_production_unchanged():
    safety = _enabled_report()["safety_confirmations"]

    assert safety["production_consumed"] is False
    assert safety["production_enabled"] is False
    assert safety["production_planner_output_changed"] is False
    assert safety["planner_remap_performed"] is False
    assert safety["live_stat_aggregation_changed"] is False
    assert safety["combat_simulation_changed"] is False
    assert safety["crafting_behavior_changed"] is False
    assert safety["optimizer_behavior_changed"] is False
    assert safety["candidate_execution_default_enabled"] is False


def test_limited_adapter_report_has_required_sections_and_blockers():
    report = build_v3_limited_mechanical_adapter_mode_report()

    assert report["schema_version"] == "v3.limited_mechanical_adapter_mode_report.1"
    assert report["metadata"]["production_consumer"] is False
    assert report["metadata"]["production_behavior_changed"] is False
    assert "executed_accepted_unchanged" in report["supported_execution_categories"]
    assert "blocked_unsupported_mechanic" in report["blocked_execution_categories"]
    assert "formal production remap gate review" in report["remaining_blockers_before_production_remap_gate_audit"]


def _enabled_report():
    return V3LimitedMechanicalAdapter().execute(
        comparison_reports=build_sample_limited_adapter_inputs(),
        enabled=True,
        allowed_domains={"item_affix", "passive_skill"},
    )
