import json

from app.planner_adapters.v3_1.persisted_fixture_sets import V31PersistedFixtureSets
from app.planner_adapters.v3_1.review_policy_evaluation import V31ReviewPolicyEvaluation
from scripts.report_v3_1_review_policy_evaluation import (
    build_v3_1_review_policy_evaluation_report,
    write_report,
)


def test_policy_evaluation_is_deterministic():
    fixture_sets = _fixture_set_envelope([_fixture_set("approved", "approved_candidate")])
    first = V31ReviewPolicyEvaluation().evaluate(persisted_fixture_sets=fixture_sets)
    second = V31ReviewPolicyEvaluation().evaluate(persisted_fixture_sets=fixture_sets)

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["summary"]["deterministic"] is True


def test_policy_outcomes_classify_correctly():
    result = V31ReviewPolicyEvaluation().evaluate(
        persisted_fixture_sets=_fixture_set_envelope(
            [
                _fixture_set("approved", "approved_candidate"),
                _fixture_set("review", "review_ready"),
                _fixture_set("blocked", "blocked"),
                _fixture_set("unsupported", "unsupported"),
                _fixture_set("insufficient", "insufficient_data"),
                _fixture_set("unknown", "unexpected"),
            ]
        )
    )
    observed = {row["set_key"]: row["policy_outcome"] for row in result["evaluations"]}

    assert observed["approved"] == "passes_policy"
    assert observed["review"] == "requires_review"
    assert observed["blocked"] == "blocked"
    assert observed["unsupported"] == "unsupported"
    assert observed["insufficient"] == "insufficient_data"
    assert observed["unknown"] == "not_evaluated"


def test_unsupported_and_blocked_states_remain_visible():
    result = V31ReviewPolicyEvaluation().evaluate(
        persisted_fixture_sets=_fixture_set_envelope(
            [_fixture_set("blocked", "blocked"), _fixture_set("unsupported", "unsupported")]
        )
    )
    observed = {row["set_key"]: row for row in result["evaluations"]}

    assert observed["blocked"]["policy_outcome"] == "blocked"
    assert observed["blocked"]["blocked"] is True
    assert observed["unsupported"]["policy_outcome"] == "unsupported"
    assert observed["unsupported"]["unsupported"] is True


def test_aggregate_counts_are_correct():
    result = V31ReviewPolicyEvaluation().evaluate(
        persisted_fixture_sets=_fixture_set_envelope(
            [
                _fixture_set("approved", "approved_candidate"),
                _fixture_set("review", "review_ready"),
                _fixture_set("blocked", "blocked"),
                _fixture_set("unsupported", "unsupported"),
                _fixture_set("insufficient", "insufficient_data"),
                _fixture_set("unknown", "unexpected"),
            ]
        )
    )

    assert result["summary"]["total_evaluations"] == 6
    assert result["summary"]["policy_pass_count"] == 1
    assert result["summary"]["requires_review_count"] == 1
    assert result["summary"]["blocked_count"] == 1
    assert result["summary"]["unsupported_count"] == 1
    assert result["summary"]["insufficient_data_count"] == 1
    assert result["summary"]["not_evaluated_count"] == 1
    assert result["summary"]["production_affected_count"] == 0


def test_production_output_affected_remains_false():
    result = V31ReviewPolicyEvaluation().evaluate(
        persisted_fixture_sets=_fixture_set_envelope([_fixture_set("approved", "approved_candidate")])
    )

    assert result["summary"]["production_output_affected"] is False
    assert result["summary"]["production_affected_count"] == 0
    assert result["safety_confirmations"]["policy_authorizes_production_routing"] is False
    assert all(row["production_output_affected"] is False for row in result["evaluations"])


def test_prior_phase_compatibility_remains_intact():
    fixture_sets = V31PersistedFixtureSets().build(
        baseline_fixture_workflows={
            "schema_version": "v3_1.baseline_fixture_workflows.1",
            "deterministic_hash": "workflow-hash",
            "fixtures": [
                {
                    "fixture_id": "fixture_a",
                    "approval_state": "approved_candidate",
                    "unsupported": False,
                    "blocked": False,
                    "production_output_affected": False,
                }
            ],
        }
    )
    result = V31ReviewPolicyEvaluation().evaluate(persisted_fixture_sets=fixture_sets)

    assert result["run"]["source_fixture_set_hash"] == fixture_sets["deterministic_hash"]
    assert result["evaluations"][0]["policy_outcome"] == "passes_policy"


def test_report_generation_is_deterministic(tmp_path):
    first = build_v3_1_review_policy_evaluation_report()
    second = build_v3_1_review_policy_evaluation_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["review_policy_evaluation"]["deterministic_hash"] == second["review_policy_evaluation"]["deterministic_hash"]
    assert first["summary"] == second["summary"]

    output = tmp_path / "policy.json"
    write_report(first, output)
    loaded = json.loads(output.read_text(encoding="utf-8"))
    assert loaded["schema_version"] == "v3_1.review_policy_evaluation_report.1"
    assert loaded["production_default_routing_authorized"] is False


def _fixture_set_envelope(fixture_sets):
    return {
        "schema_version": "v3_1.persisted_fixture_sets.1",
        "deterministic_hash": "fixture-set-hash",
        "fixture_sets": fixture_sets,
    }


def _fixture_set(key, lifecycle_state):
    return {
        "fixture_set_id": f"set_{key}",
        "set_key": key,
        "lifecycle_state": lifecycle_state,
        "unsupported": lifecycle_state == "unsupported",
        "blocked": lifecycle_state == "blocked",
        "production_output_affected": False,
    }
