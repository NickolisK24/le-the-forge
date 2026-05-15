import json

from app.planner_adapters.v3_1.dual_run_comparison import V31DualRunComparison
from app.planner_adapters.v3_1.planner_snapshot_baselines import (
    V31PlannerSnapshotBaselines,
)
from scripts.report_v3_1_planner_snapshot_baselines import (
    build_v3_1_planner_snapshot_baselines_report,
    write_report,
)


def test_snapshot_generation_is_deterministic():
    dual_run = _dual_run([_comparison("affix", "equivalent")])

    first = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)
    second = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_stable_snapshot_ids_remain_stable():
    dual_run = _dual_run([_comparison("affix", "equivalent")])

    first = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)
    second = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)

    assert first["snapshots"][0]["snapshot_id"] == second["snapshots"][0]["snapshot_id"]
    assert first["snapshots"][0]["snapshot_id"].startswith("v3_1_snapshot_")


def test_baseline_classifications_are_deterministic():
    baselines = V31PlannerSnapshotBaselines().build(
        dual_run_comparison=_dual_run(
            [
                _comparison("affix", "equivalent"),
                _comparison("item_base", "divergent"),
                _comparison("legacy_only", "legacy_only"),
                _comparison("shadow_only", "trusted_only"),
            ]
        )
    )
    observed = {snapshot["stable_key"]: snapshot["baseline_readiness"] for snapshot in baselines["snapshots"]}

    assert observed["affix"] == "baseline_candidate"
    assert observed["item_base"] == "comparison_ready"
    assert observed["legacy_only"] == "legacy_only"
    assert observed["shadow_only"] == "shadow_only"


def test_unsupported_states_remain_visible():
    snapshot = _single_snapshot("passive_skill", "unsupported")

    assert snapshot["baseline_readiness"] == "unsupported"
    assert snapshot["unsupported"] is True
    assert snapshot["comparison_eligible"] is False
    assert "unsupported_state_visible" in snapshot["reason_codes"]


def test_blocked_states_remain_visible():
    snapshot = _single_snapshot("affix", "blocked", reason="blocked_for_test")

    assert snapshot["baseline_readiness"] == "blocked"
    assert snapshot["blocked"] is True
    assert snapshot["unsupported_or_blocked_reason"] == "blocked_for_test"
    assert snapshot["comparison_eligible"] is False


def test_insufficient_data_states_remain_visible():
    unavailable = _single_snapshot("affix", "unavailable")
    not_evaluated = _single_snapshot("item_base", "not_evaluated")

    assert unavailable["baseline_readiness"] == "insufficient_data"
    assert not_evaluated["baseline_readiness"] == "insufficient_data"
    assert unavailable["comparison_eligible"] is False
    assert not_evaluated["comparison_eligible"] is False


def test_aggregate_counts_are_correct():
    baselines = V31PlannerSnapshotBaselines().build(
        dual_run_comparison=_dual_run(
            [
                _comparison("baseline", "equivalent"),
                _comparison("comparison", "divergent"),
                _comparison("unsupported", "unsupported"),
                _comparison("blocked", "blocked"),
                _comparison("unavailable", "unavailable"),
                _comparison("legacy_only", "legacy_only"),
                _comparison("shadow_only", "trusted_only"),
            ]
        )
    )

    assert baselines["summary"]["total_snapshots"] == 7
    assert baselines["summary"]["baseline_candidate_count"] == 1
    assert baselines["summary"]["comparison_ready_count"] == 1
    assert baselines["summary"]["unsupported_count"] == 1
    assert baselines["summary"]["blocked_count"] == 1
    assert baselines["summary"]["insufficient_data_count"] == 1
    assert baselines["summary"]["legacy_only_count"] == 1
    assert baselines["summary"]["shadow_only_count"] == 1
    assert baselines["summary"]["production_affected_count"] == 0


def test_production_output_affected_remains_false():
    baselines = V31PlannerSnapshotBaselines().build(
        dual_run_comparison=_dual_run([_comparison("affix", "equivalent")])
    )

    assert baselines["summary"]["production_output_affected"] is False
    assert baselines["summary"]["production_affected_count"] == 0
    assert baselines["safety_confirmations"]["legacy_planner_ownership_preserved"] is True
    assert all(snapshot["production_output_affected"] is False for snapshot in baselines["snapshots"])


def test_phase_2_compatibility_is_preserved():
    dual_run = V31DualRunComparison().compare(
        legacy_summaries=[
            {"comparison_id": "affix", "legacy_status": "available", "comparable_value": 2},
        ],
        trusted_shadow_metadata={
            "gate": {"enabled": True, "mode": "shadow", "shadow_only": True},
            "trusted_repository_rows": [
                {
                    "domain": "affix",
                    "repository_name": "trusted_affix",
                    "routing_status": "trusted_repository_shadowed",
                    "trusted_entity_count": 2,
                    "blocked_reasons": [],
                    "production_output_affected": False,
                }
            ],
        },
    )
    baselines = V31PlannerSnapshotBaselines().build(dual_run_comparison=dual_run)

    assert baselines["run"]["source_dual_run_hash"] == dual_run["deterministic_hash"]
    assert baselines["snapshots"][0]["dual_run_comparison_state"]["drift_classification"] == "equivalent"
    assert baselines["snapshots"][0]["baseline_readiness"] == "baseline_candidate"


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_planner_snapshot_baselines_report()
    second = build_v3_1_planner_snapshot_baselines_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["planner_snapshot_baselines"]["deterministic_hash"] == second["planner_snapshot_baselines"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "snapshot_baselines.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.planner_snapshot_baselines_report.1"
    assert loaded["production_default_routing_authorized"] is False
    assert loaded["metadata"]["observational_only"] is True


def _single_snapshot(stable_key, drift, reason=None):
    baselines = V31PlannerSnapshotBaselines().build(
        dual_run_comparison=_dual_run([_comparison(stable_key, drift, reason=reason)])
    )
    return baselines["snapshots"][0]


def _dual_run(rows):
    return {
        "schema_version": "v3_1.dual_run_comparison.1",
        "deterministic_hash": "fixture-dual-run-hash",
        "trusted_shadow_gate": {
            "enabled": True,
            "mode": "shadow",
            "shadow_only": True,
            "production_truth_source": "legacy",
            "production_output_affected": False,
        },
        "comparison_results": rows,
    }


def _comparison(stable_key, drift, reason=None):
    return {
        "comparison_id": stable_key,
        "stable_key": stable_key,
        "legacy_status": "available",
        "trusted_shadow_status": "available",
        "drift_classification": drift,
        "production_output_affected": False,
        "trusted_shadow_gate": {"enabled": True, "mode": "shadow", "shadow_only": True},
        "unsupported_or_blocked_reason": reason,
        "reason_codes": [f"{drift}_fixture"],
        "legacy_hash": f"legacy:{stable_key}",
        "trusted_hash": f"trusted:{stable_key}",
    }
