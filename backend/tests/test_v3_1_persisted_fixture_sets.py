import json

from app.planner_adapters.v3_1.baseline_fixture_workflows import V31BaselineFixtureWorkflows
from app.planner_adapters.v3_1.persisted_fixture_sets import V31PersistedFixtureSets
from scripts.report_v3_1_persisted_fixture_sets import (
    build_v3_1_persisted_fixture_sets_report,
    write_report,
)


def test_fixture_set_generation_is_deterministic():
    workflows = _workflow_envelope([_fixture("a", "pending_review")])
    first = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)
    second = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_stable_ids_remain_stable():
    workflows = _workflow_envelope([_fixture("a", "pending_review")])
    first = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)
    second = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)

    assert first["fixture_sets"][0]["fixture_set_id"] == second["fixture_sets"][0]["fixture_set_id"]
    assert first["fixture_sets"][0]["fixture_set_id"].startswith("v3_1_fixture_set_")


def test_lifecycle_states_classify_correctly():
    workflows = _workflow_envelope(
        [
            _fixture("pending", "pending_review"),
            _fixture("candidate", "approved_candidate"),
            _fixture("baseline", "approved_baseline"),
            _fixture("unsupported", "unsupported"),
            _fixture("blocked", "blocked"),
            _fixture("insufficient", "insufficient_data"),
        ]
    )
    result = V31PersistedFixtureSets().build(
        baseline_fixture_workflows=workflows,
        set_definitions=[
            _set("draft", []),
            _set("review", ["pending"]),
            _set("partial", ["pending", "candidate"]),
            _set("approved", ["candidate", "baseline"]),
            _set("unsupported", ["unsupported"]),
            _set("blocked", ["blocked"]),
            _set("insufficient", ["insufficient"]),
            _set("archived", ["pending"], lifecycle_state="archived"),
        ],
    )
    observed = {row["set_key"]: row["lifecycle_state"] for row in result["fixture_sets"]}

    assert observed["draft"] == "insufficient_data"
    assert observed["review"] == "review_ready"
    assert observed["partial"] == "partially_approved"
    assert observed["approved"] == "approved_candidate"
    assert observed["unsupported"] == "unsupported"
    assert observed["blocked"] == "blocked"
    assert observed["insufficient"] == "insufficient_data"
    assert observed["archived"] == "archived"


def test_unsupported_and_blocked_states_remain_visible():
    workflows = _workflow_envelope([_fixture("unsupported", "unsupported"), _fixture("blocked", "blocked")])
    result = V31PersistedFixtureSets().build(
        baseline_fixture_workflows=workflows,
        set_definitions=[_set("unsupported", ["unsupported"]), _set("blocked", ["blocked"])],
    )
    observed = {row["set_key"]: row for row in result["fixture_sets"]}

    assert observed["unsupported"]["unsupported"] is True
    assert observed["unsupported"]["lifecycle_state"] == "unsupported"
    assert observed["blocked"]["blocked"] is True
    assert observed["blocked"]["lifecycle_state"] == "blocked"


def test_aggregate_counts_are_correct():
    workflows = _workflow_envelope(
        [
            _fixture("pending", "pending_review"),
            _fixture("candidate", "approved_candidate"),
            _fixture("baseline", "approved_baseline"),
            _fixture("unsupported", "unsupported"),
            _fixture("blocked", "blocked"),
            _fixture("insufficient", "insufficient_data"),
        ]
    )
    result = V31PersistedFixtureSets().build(
        baseline_fixture_workflows=workflows,
        set_definitions=[
            _set("draft", [], lifecycle_state="draft"),
            _set("review", ["pending"]),
            _set("partial", ["pending", "candidate"]),
            _set("approved", ["candidate", "baseline"]),
            _set("unsupported", ["unsupported"]),
            _set("blocked", ["blocked"]),
            _set("insufficient", ["insufficient"]),
        ],
    )

    assert result["summary"]["total_fixture_sets"] == 7
    assert result["summary"]["draft_count"] == 1
    assert result["summary"]["review_ready_count"] == 1
    assert result["summary"]["partially_approved_count"] == 1
    assert result["summary"]["approved_candidate_count"] == 1
    assert result["summary"]["unsupported_count"] == 1
    assert result["summary"]["blocked_count"] == 1
    assert result["summary"]["insufficient_data_count"] == 1
    assert result["summary"]["policy_pass_count"] == 1
    assert result["summary"]["requires_review_count"] == 3
    assert result["summary"]["production_affected_count"] == 0


def test_production_output_affected_remains_false():
    result = V31PersistedFixtureSets().build(baseline_fixture_workflows=_workflow_envelope([_fixture("a", "approved_candidate")]))

    assert result["summary"]["production_output_affected"] is False
    assert result["summary"]["production_affected_count"] == 0
    assert result["safety_confirmations"]["fixture_set_authorizes_production_routing"] is False
    assert all(row["production_output_affected"] is False for row in result["fixture_sets"])


def test_prior_phase_compatibility_remains_intact():
    workflows = V31BaselineFixtureWorkflows().build(
        planner_snapshot_baselines={
            "schema_version": "v3_1.planner_snapshot_baselines.1",
            "deterministic_hash": "snapshot-hash",
            "snapshots": [
                {
                    "snapshot_id": "snapshot_a",
                    "stable_key": "affix",
                    "baseline_readiness": "baseline_candidate",
                    "comparison_eligible": True,
                    "baseline_candidate": True,
                    "unsupported": False,
                    "blocked": False,
                    "production_output_affected": False,
                    "dual_run_comparison_state": {"drift_classification": "equivalent"},
                }
            ],
        }
    )
    result = V31PersistedFixtureSets().build(baseline_fixture_workflows=workflows)

    assert result["run"]["source_fixture_workflow_hash"] == workflows["deterministic_hash"]
    assert result["fixture_sets"][0]["associated_fixture_ids"] == [workflows["fixtures"][0]["fixture_id"]]


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_persisted_fixture_sets_report()
    second = build_v3_1_persisted_fixture_sets_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["persisted_fixture_sets"]["deterministic_hash"] == second["persisted_fixture_sets"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "fixture_sets.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.persisted_fixture_sets_report.1"
    assert loaded["production_default_routing_authorized"] is False


def _workflow_envelope(fixtures):
    return {
        "schema_version": "v3_1.baseline_fixture_workflows.1",
        "deterministic_hash": "workflow-hash",
        "fixtures": fixtures,
    }


def _fixture(key, state):
    return {
        "fixture_id": key,
        "approval_state": state,
        "unsupported": state == "unsupported",
        "blocked": state == "blocked",
        "production_output_affected": False,
    }


def _set(key, fixture_ids, lifecycle_state=None):
    row = {"set_key": key, "fixture_ids": fixture_ids}
    if lifecycle_state:
        row["lifecycle_state"] = lifecycle_state
    return row
