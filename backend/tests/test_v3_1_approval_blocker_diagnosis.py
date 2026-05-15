from app.planner_adapters.v3_1.approval_blocker_diagnosis import build_approval_blocker_diagnosis
from scripts.report_v3_1_approval_blocker_diagnosis import build_v3_1_approval_blocker_diagnosis_report


def test_each_blocker_classification_is_visible():
    result = build_approval_blocker_diagnosis(
        reviewed_fixture_inputs=_reviewed_inputs(),
        persisted_fixture_sets=_fixture_sets(),
        review_policy_evaluation=_policy(),
        fixture_set_readiness_gate=_readiness(),
        approval_manifest_candidates=_candidates(),
        approval_manifest_serialization=_serialization(),
    )

    counts = result["blocker_type_counts"]
    assert counts["missing_reviewed_inputs"] == 1
    assert counts["malformed_or_duplicate_inputs"] == 1
    assert counts["unsupported_fixture_source"] >= 1
    assert counts["insufficient_fixture_set_coverage"] >= 1
    assert counts["policy_not_satisfied"] == 1
    assert counts["readiness_gate_blocked"] == 1
    assert counts["no_candidate_ready_records"] == 1
    assert counts["no_serialized_manifests"] == 1


def test_unknown_blocker_when_no_inputs_produce_explicit_record():
    result = build_approval_blocker_diagnosis(
        approval_manifest_candidates={"summary": {"candidate_ready_count": 1}},
        approval_manifest_serialization={"summary": {"serialized_manifest_count": 1}},
    )

    assert result["blocker_type_counts"]["unknown_blocker"] == 1
    assert result["blocker_records"][0]["severity"] == "info"


def test_deterministic_ordering():
    first = build_approval_blocker_diagnosis(
        reviewed_fixture_inputs=_reviewed_inputs(),
        persisted_fixture_sets=_fixture_sets(),
        review_policy_evaluation=_policy(),
        fixture_set_readiness_gate=_readiness(),
        approval_manifest_candidates=_candidates(),
        approval_manifest_serialization=_serialization(),
    )
    second = build_approval_blocker_diagnosis(
        approval_manifest_serialization=_serialization(),
        approval_manifest_candidates=_candidates(),
        fixture_set_readiness_gate=_readiness(),
        review_policy_evaluation=_policy(),
        persisted_fixture_sets=_fixture_sets(),
        reviewed_fixture_inputs=_reviewed_inputs(),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["blocker_id"] for row in first["blocker_records"]] == [row["blocker_id"] for row in second["blocker_records"]]


def test_zero_serialized_manifests_are_diagnosed():
    result = build_approval_blocker_diagnosis(
        approval_manifest_candidates={"summary": {"candidate_ready_count": 0}},
        approval_manifest_serialization={"summary": {"serialized_manifest_count": 0}},
    )

    assert result["blocker_type_counts"]["no_candidate_ready_records"] == 1
    assert result["blocker_type_counts"]["no_serialized_manifests"] == 1
    assert result["summary"]["blocking_count"] == 2


def test_stable_report_generation():
    first = build_v3_1_approval_blocker_diagnosis_report()
    second = build_v3_1_approval_blocker_diagnosis_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["approval_blocker_diagnosis"]["deterministic_hash"] == second["approval_blocker_diagnosis"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_approval_blocker_diagnosis(
        approval_manifest_candidates={"summary": {"candidate_ready_count": 0}},
        approval_manifest_serialization={"summary": {"serialized_manifest_count": 0}},
    )

    assert result["safety_confirmations"]["diagnosis_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["diagnosis_promotes_fixture_sets"] is False
    assert result["summary"]["production_output_affected"] is False
    assert all(row["diagnosis_authorizes_production_routing"] is False for row in result["blocker_records"])


def test_compatibility_with_phase_5_through_9_governance_outputs():
    report = build_v3_1_approval_blocker_diagnosis_report()
    diagnosis = report["approval_blocker_diagnosis"]

    assert diagnosis["run"]["reviewed_fixture_input_hash"]
    assert diagnosis["run"]["persisted_fixture_set_hash"]
    assert diagnosis["run"]["review_policy_evaluation_hash"]
    assert diagnosis["run"]["readiness_gate_hash"]
    assert diagnosis["run"]["approval_manifest_candidate_hash"]
    assert diagnosis["run"]["approval_manifest_serialization_hash"]
    assert diagnosis["blocker_type_counts"]["no_serialized_manifests"] == 1


def _reviewed_inputs():
    return {
        "deterministic_hash": "reviewed-hash",
        "summary": {
            "missing_source_count": 1,
            "malformed_count": 1,
            "duplicate_count": 1,
        },
        "normalized_fixture_inputs": [
            {"normalized_fixture_id": "fixture_unsupported", "status": "unsupported"},
        ],
    }


def _fixture_sets():
    return {
        "deterministic_hash": "sets-hash",
        "summary": {"total_fixture_sets": 2},
        "fixture_sets": [
            {
                "fixture_set_id": "set_insufficient",
                "lifecycle_state": "insufficient_data",
                "missing_fixture_ids": ["fixture_missing"],
            },
            {
                "fixture_set_id": "set_unsupported",
                "lifecycle_state": "unsupported",
                "unsupported": True,
            },
        ],
    }


def _policy():
    return {
        "deterministic_hash": "policy-hash",
        "evaluations": [
            {
                "fixture_set_id": "set_unsupported",
                "policy_outcome": "unsupported",
            }
        ],
    }


def _readiness():
    return {
        "deterministic_hash": "readiness-hash",
        "readiness_records": [
            {
                "fixture_set_id": "set_unsupported",
                "readiness_classification": "blocked_policy_failure",
                "block_reason_codes": ["policy_unsupported"],
            }
        ],
    }


def _candidates():
    return {
        "deterministic_hash": "candidate-hash",
        "summary": {"candidate_ready_count": 0},
        "manifest_candidates": [
            {"fixture_set_id": "set_unsupported", "candidate_status": "excluded_not_ready"},
        ],
    }


def _serialization():
    return {
        "deterministic_hash": "serialization-hash",
        "summary": {"serialized_manifest_count": 0},
        "serialized_manifests": [],
    }
