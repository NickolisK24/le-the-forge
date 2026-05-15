from app.planner_adapters.v3_1.admission_aware_manifest_candidates import build_admission_aware_manifest_candidates
from scripts.report_v3_1_admission_aware_manifest_candidates import build_v3_1_admission_aware_manifest_candidates_report


def test_ready_for_approval_review_becomes_candidate_ready():
    result = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([_readiness_record("set_a", "ready_for_approval_review")]),
        approval_manifest_candidates=_original([_candidate("set_a", "excluded_not_ready")]),
    )

    row = result["manifest_candidates"][0]
    assert row["candidate_status"] == "candidate_ready"
    assert row["original_candidate_status"] == "excluded_not_ready"
    assert row["candidate_refresh_status"] == "promoted_to_candidate_ready_for_review"


def test_blocked_readiness_remains_excluded():
    result = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([_readiness_record("set_a", "blocked_policy_failure", ["policy_blocked"])]),
        approval_manifest_candidates=_original([_candidate("set_a", "excluded_not_ready")]),
    )

    row = result["manifest_candidates"][0]
    assert row["candidate_status"] == "excluded_not_ready"
    assert result["exclusion_reason_counts"]["policy_blocked"] == 1


def test_missing_admission_aware_readiness_blocks():
    result = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([]),
        approval_manifest_candidates=_original([_candidate("set_a", "excluded_not_ready")]),
    )

    row = result["manifest_candidates"][0]
    assert row["candidate_status"] == "excluded_missing_admission_readiness"
    assert row["reason_codes"] == ["missing_admission_aware_readiness_record"]


def test_invalid_readiness_state_blocks():
    result = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([_readiness_record("set_a", "unexpected_state")]),
        approval_manifest_candidates=_original([]),
    )

    row = result["manifest_candidates"][0]
    assert row["candidate_status"] == "excluded_invalid_readiness_state"
    assert row["reason_codes"] == ["invalid_admission_aware_readiness_state_unexpected_state"]


def test_deterministic_ordering():
    first = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([
            _readiness_record("set_b", "ready_for_approval_review"),
            _readiness_record("set_a", "ready_for_approval_review"),
        ]),
        approval_manifest_candidates=_original([_candidate("set_b", "excluded_not_ready"), _candidate("set_a", "excluded_not_ready")]),
    )
    second = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([
            _readiness_record("set_a", "ready_for_approval_review"),
            _readiness_record("set_b", "ready_for_approval_review"),
        ]),
        approval_manifest_candidates=_original([_candidate("set_a", "excluded_not_ready"), _candidate("set_b", "excluded_not_ready")]),
    )

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["manifest_candidates"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_admission_aware_manifest_candidates_report()
    second = build_v3_1_admission_aware_manifest_candidates_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["admission_aware_manifest_candidates"]["deterministic_hash"] == second["admission_aware_manifest_candidates"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_admission_aware_manifest_candidates(
        admission_aware_readiness_gate=_readiness([_readiness_record("set_a", "ready_for_approval_review")]),
        approval_manifest_candidates=_original([_candidate("set_a", "excluded_not_ready")]),
    )
    row = result["manifest_candidates"][0]

    assert result["safety_confirmations"]["candidate_ready_is_production_approval"] is False
    assert result["safety_confirmations"]["admission_aware_candidates_authorize_production_routing"] is False
    assert row["authorization_status"]["candidate_authorizes_production_routing"] is False
    assert row["authorization_status"]["candidate_is_production_approved"] is False
    assert row["non_production_authoritative"] is True


def _readiness(records):
    return {
        "schema_version": "v3_1.admission_aware_readiness_gate.1",
        "deterministic_hash": "readiness-hash",
        "admission_aware_readiness_records": records,
    }


def _readiness_record(set_id, status, blockers=None):
    return {
        "admission_aware_readiness_id": f"readiness_{set_id}",
        "fixture_set_id": set_id,
        "set_key": set_id,
        "final_admission_aware_readiness_status": status,
        "admission_aware_readiness_status": status,
        "admission_aware_policy_status": "policy_satisfied_for_review",
        "readiness_reclassification": "policy_blocker_cleared_by_admission_aware_policy",
        "remaining_blockers": blockers or [],
        "associated_fixture_ids": [f"fixture_{set_id}"],
        "original_readiness_status": "blocked_policy_failure",
        "original_block_reason_codes": ["policy_unsupported"],
        "production_output_affected": False,
    }


def _original(records):
    return {
        "schema_version": "v3_1.approval_manifest_candidates.1",
        "deterministic_hash": "candidate-hash",
        "manifest_candidates": records,
    }


def _candidate(set_id, status):
    return {
        "manifest_candidate_id": f"candidate_{set_id}",
        "fixture_set_id": set_id,
        "candidate_status": status,
        "source_summary": {"set_key": set_id},
        "policy_summary": {"policy_outcome": "unsupported"},
        "readiness_summary": {"readiness_classification": "blocked_policy_failure"},
        "reason_codes": ["policy_unsupported"],
        "production_output_affected": False,
    }
