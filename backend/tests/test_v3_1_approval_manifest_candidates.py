from app.planner_adapters.v3_1.approval_manifest_candidates import build_approval_manifest_candidates
from scripts.report_v3_1_approval_manifest_candidates import build_v3_1_approval_manifest_candidates_report


def test_ready_records_become_candidate_ready():
    result = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_a", "ready_for_approval_review", "passes_policy")]))

    candidate = result["manifest_candidates"][0]
    assert candidate["candidate_status"] == "candidate_ready"
    assert result["summary"]["candidate_ready_count"] == 1


def test_non_ready_records_are_excluded():
    result = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_a", "blocked_policy_failure", "unsupported", ["policy_unsupported"])]))

    candidate = result["manifest_candidates"][0]
    assert candidate["candidate_status"] == "excluded_not_ready"
    assert result["summary"]["excluded_count"] == 1
    assert result["exclusion_reason_counts"]["policy_unsupported"] == 1


def test_missing_readiness_is_excluded():
    row = _record("set_a", "ready_for_approval_review", "passes_policy")
    row.pop("readiness_classification")
    result = build_approval_manifest_candidates(readiness_gate=_gate([row]))

    assert result["manifest_candidates"][0]["candidate_status"] == "excluded_missing_readiness"
    assert result["exclusion_reason_counts"]["missing_readiness_classification"] == 1


def test_invalid_policy_state_is_excluded():
    result = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_a", "ready_for_approval_review", "requires_review")]))

    assert result["manifest_candidates"][0]["candidate_status"] == "excluded_invalid_policy_state"
    assert result["exclusion_reason_counts"]["invalid_policy_state_requires_review"] == 1


def test_deterministic_ordering():
    first = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_b", "ready_for_approval_review"), _record("set_a", "ready_for_approval_review")]))
    second = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_a", "ready_for_approval_review"), _record("set_b", "ready_for_approval_review")]))

    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert [row["fixture_set_id"] for row in first["manifest_candidates"]] == ["set_a", "set_b"]


def test_stable_report_generation():
    first = build_v3_1_approval_manifest_candidates_report()
    second = build_v3_1_approval_manifest_candidates_report()

    assert first["deterministic_guarantees"]["passed"] is True
    assert first["approval_manifest_candidates"]["deterministic_hash"] == second["approval_manifest_candidates"]["deterministic_hash"]
    assert first["summary"] == second["summary"]


def test_no_production_routing_enablement():
    result = build_approval_manifest_candidates(readiness_gate=_gate([_record("set_a", "ready_for_approval_review")]))
    candidate = result["manifest_candidates"][0]

    assert result["safety_confirmations"]["approval_manifest_authorizes_production_routing"] is False
    assert result["safety_confirmations"]["manifest_candidates_are_production_approved"] is False
    assert candidate["authorization_status"]["candidate_is_production_approved"] is False
    assert candidate["authorization_status"]["candidate_authorizes_production_routing"] is False


def _gate(records):
    return {
        "schema_version": "v3_1.fixture_set_readiness_gate.1",
        "deterministic_hash": "readiness-hash",
        "readiness_records": records,
    }


def _record(set_id, readiness, policy="passes_policy", reasons=None):
    return {
        "fixture_set_id": set_id,
        "set_key": set_id,
        "readiness_classification": readiness,
        "associated_fixture_ids": [f"fixture_{set_id}"],
        "input_statuses": {f"fixture_{set_id}": "reviewed"},
        "policy_outcome": policy,
        "workflow_states": {f"fixture_{set_id}": "pending_review"},
        "block_reason_codes": reasons or [],
        "production_output_affected": False,
    }
