import json

from app.planner_adapters.v3_1.baseline_fixture_workflows import (
    V31BaselineFixtureWorkflows,
)
from app.planner_adapters.v3_1.planner_snapshot_baselines import (
    V31PlannerSnapshotBaselines,
)
from scripts.report_v3_1_baseline_fixture_workflows import (
    build_v3_1_baseline_fixture_workflows_report,
    write_report,
)


def test_fixture_workflow_generation_is_deterministic():
    snapshots = _snapshot_baselines([_snapshot("affix", "baseline_candidate")])

    first = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)
    second = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_stable_fixture_ids_remain_stable():
    snapshots = _snapshot_baselines([_snapshot("affix", "baseline_candidate")])

    first = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)
    second = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)

    assert first["fixtures"][0]["fixture_id"] == second["fixtures"][0]["fixture_id"]
    assert first["fixtures"][0]["fixture_id"].startswith("v3_1_fixture_")


def test_lifecycle_states_classify_correctly():
    snapshots = _snapshot_baselines(
        [
            _snapshot("pending", "baseline_candidate"),
            _snapshot("candidate", "baseline_candidate"),
            _snapshot("baseline", "baseline_candidate"),
            _snapshot("rejected", "comparison_ready"),
            _snapshot("archived", "legacy_only"),
        ]
    )
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=snapshots,
        approval_overrides={
            "candidate": {"approval_state": "approved_candidate"},
            "baseline": {"approval_state": "approved_baseline"},
            "rejected": {"approval_state": "rejected"},
            "archived": {"approval_state": "archived"},
        },
    )
    observed = {fixture["snapshot_stable_key"]: fixture["approval_state"] for fixture in workflows["fixtures"]}

    assert observed["pending"] == "pending_review"
    assert observed["candidate"] == "approved_candidate"
    assert observed["baseline"] == "approved_baseline"
    assert observed["rejected"] == "rejected"
    assert observed["archived"] == "archived"


def test_unsupported_states_remain_visible():
    fixture = _single_fixture("passive_skill", "unsupported")

    assert fixture["approval_state"] == "unsupported"
    assert fixture["unsupported"] is True
    assert "unsupported_state_visible" in fixture["reason_codes"]


def test_blocked_states_remain_visible():
    fixture = _single_fixture("affix", "blocked", reason="blocked_for_test")

    assert fixture["approval_state"] == "blocked"
    assert fixture["blocked"] is True
    assert fixture["unsupported_or_blocked_reason"] == "blocked_for_test"


def test_rejected_states_remain_visible():
    snapshots = _snapshot_baselines([_snapshot("item_base", "comparison_ready")])
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=snapshots,
        approval_overrides={"item_base": {"approval_state": "rejected", "review_notes": ["drift requires review"]}},
    )
    fixture = workflows["fixtures"][0]

    assert fixture["approval_state"] == "rejected"
    assert fixture["review_notes"] == ["drift requires review"]
    assert fixture["production_ownership_state"]["approval_authorizes_production_routing"] is False


def test_aggregate_counts_are_correct():
    snapshots = _snapshot_baselines(
        [
            _snapshot("pending", "baseline_candidate"),
            _snapshot("candidate", "baseline_candidate"),
            _snapshot("baseline", "baseline_candidate"),
            _snapshot("rejected", "comparison_ready"),
            _snapshot("unsupported", "unsupported"),
            _snapshot("blocked", "blocked"),
            _snapshot("insufficient", "insufficient_data"),
            _snapshot("archived", "legacy_only"),
        ]
    )
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=snapshots,
        approval_overrides={
            "candidate": {"approval_state": "approved_candidate"},
            "baseline": {"approval_state": "approved_baseline"},
            "rejected": {"approval_state": "rejected"},
            "archived": {"approval_state": "archived"},
        },
    )

    assert workflows["summary"]["total_fixtures"] == 8
    assert workflows["summary"]["pending_review_count"] == 1
    assert workflows["summary"]["approved_candidate_count"] == 1
    assert workflows["summary"]["approved_baseline_count"] == 1
    assert workflows["summary"]["rejected_count"] == 1
    assert workflows["summary"]["unsupported_count"] == 1
    assert workflows["summary"]["blocked_count"] == 1
    assert workflows["summary"]["insufficient_data_count"] == 1
    assert workflows["summary"]["archived_count"] == 1
    assert workflows["summary"]["production_affected_count"] == 0


def test_production_output_affected_remains_false():
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=_snapshot_baselines([_snapshot("affix", "baseline_candidate")]),
        approval_overrides={"affix": {"approval_state": "approved_baseline"}},
    )

    assert workflows["summary"]["production_output_affected"] is False
    assert workflows["summary"]["production_affected_count"] == 0
    assert workflows["safety_confirmations"]["approval_status_authorizes_production_routing"] is False
    assert all(fixture["production_output_affected"] is False for fixture in workflows["fixtures"])


def test_prior_phase_compatibility_is_preserved():
    snapshots = V31PlannerSnapshotBaselines().build(
        dual_run_comparison={
            "schema_version": "v3_1.dual_run_comparison.1",
            "deterministic_hash": "phase2-hash",
            "trusted_shadow_gate": {"enabled": True, "mode": "shadow", "shadow_only": True},
            "comparison_results": [
                {
                    "comparison_id": "affix",
                    "stable_key": "affix",
                    "legacy_status": "available",
                    "trusted_shadow_status": "available",
                    "drift_classification": "equivalent",
                    "production_output_affected": False,
                    "trusted_shadow_gate": {"enabled": True, "mode": "shadow", "shadow_only": True},
                    "unsupported_or_blocked_reason": None,
                    "reason_codes": ["comparable_value_hash_match"],
                    "legacy_hash": "legacy",
                    "trusted_hash": "trusted",
                }
            ],
        }
    )
    workflows = V31BaselineFixtureWorkflows().build(planner_snapshot_baselines=snapshots)

    assert workflows["run"]["source_snapshot_hash"] == snapshots["deterministic_hash"]
    assert workflows["fixtures"][0]["baseline_classification"] == "baseline_candidate"
    assert workflows["fixtures"][0]["approval_state"] == "pending_review"


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_baseline_fixture_workflows_report()
    second = build_v3_1_baseline_fixture_workflows_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["baseline_fixture_workflows"]["deterministic_hash"] == second["baseline_fixture_workflows"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "fixture_workflows.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.baseline_fixture_workflows_report.1"
    assert loaded["production_default_routing_authorized"] is False
    assert loaded["metadata"]["observational_only"] is True


def _single_fixture(stable_key, baseline_readiness, reason=None):
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines=_snapshot_baselines([_snapshot(stable_key, baseline_readiness, reason=reason)])
    )
    return workflows["fixtures"][0]


def _snapshot_baselines(snapshots):
    return {
        "schema_version": "v3_1.planner_snapshot_baselines.1",
        "deterministic_hash": "fixture-snapshot-hash",
        "snapshots": snapshots,
    }


def _snapshot(stable_key, baseline_readiness, reason=None):
    return {
        "snapshot_id": f"snapshot_{stable_key}",
        "stable_key": stable_key,
        "baseline_readiness": baseline_readiness,
        "comparison_eligible": baseline_readiness in {"baseline_candidate", "comparison_ready"},
        "baseline_candidate": baseline_readiness == "baseline_candidate",
        "unsupported": baseline_readiness == "unsupported",
        "blocked": baseline_readiness == "blocked",
        "unsupported_or_blocked_reason": reason,
        "production_output_affected": False,
        "dual_run_comparison_state": {
            "drift_classification": baseline_readiness,
        },
    }
