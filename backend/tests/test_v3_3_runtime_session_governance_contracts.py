import json

from app.runtime_intelligence.session_governance_contracts import (
    SESSION_LABELS,
    build_runtime_session_governance_manifest,
    default_runtime_session_governance_contracts,
    serialize_runtime_session_governance_manifest,
)
from app.runtime_intelligence.session_governance_hashing import (
    hash_session_governance_manifest,
    validate_session_governance_replay_stability,
)
from app.runtime_intelligence.session_governance_registry import (
    detect_duplicate_session_governance_contracts,
    export_session_governance_registry,
    validate_session_governance_registry,
)
from scripts.report_v3_3_runtime_session_governance_contracts import build_v3_3_runtime_session_governance_contracts_report


def test_deterministic_ordering_stability():
    rows = list(reversed(default_runtime_session_governance_contracts()))
    manifest = build_runtime_session_governance_manifest(rows)
    assert [row["session_label"] for row in manifest["session_contracts"]] == list(SESSION_LABELS)
    assert [row["deterministic_rank"] for row in manifest["session_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["session_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_session_governance_manifest()
    second = build_runtime_session_governance_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_session_governance_manifest(first) == hash_session_governance_manifest(second)


def test_duplicate_session_governance_contract_rejection():
    rows = default_runtime_session_governance_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_session_governance_registry(duplicate)
    detection = detect_duplicate_session_governance_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_session_governance_contracts_detected" in validation["validation_errors"]
    assert rows[0]["session_contract_id"] in detection["duplicate_session_contract_ids"]


def test_deterministic_replay_validation():
    replay = validate_session_governance_replay_stability(build_runtime_session_governance_manifest())
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_session_governance_serialization_stability():
    manifest = build_runtime_session_governance_manifest()
    first = serialize_runtime_session_governance_manifest(manifest)
    second = serialize_runtime_session_governance_manifest(json.loads(first))
    assert first == second


def test_required_previous_session_and_rank_validation():
    validation = export_session_governance_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_previous_session_reference_count"] == 0
    assert validation["previous_session_rank_violation_count"] == 0


def test_invalid_previous_session_reference_rejection():
    rows = default_runtime_session_governance_contracts()
    rows[1] = {**rows[1], "required_previous_session_contract_ids": ["missing_session_id"]}
    validation = validate_session_governance_registry(rows)
    assert validation["valid"] is False
    assert "invalid_previous_session_references" in validation["validation_errors"]


def test_previous_session_rank_violation_rejection():
    rows = default_runtime_session_governance_contracts()
    rows[0] = {**rows[0], "required_previous_session_contract_ids": [rows[-1]["session_contract_id"]]}
    validation = validate_session_governance_registry(rows)
    assert validation["valid"] is False
    assert "previous_session_rank_ordering_invalid" in validation["validation_errors"]


def test_required_session_behavior_validation():
    validation = export_session_governance_registry()["registry_validation"]
    assert validation["behavior_rule_violation_count"] == 0


def test_session_identity_requirement_rejection():
    rows = default_runtime_session_governance_contracts()
    rows[0] = {**rows[0], "requires_session_id": False}
    validation = validate_session_governance_registry(rows)
    assert validation["valid"] is False
    assert "session_behavior_rule_invalid" in validation["validation_errors"]


def test_input_manifest_hash_requirement_rejection():
    rows = default_runtime_session_governance_contracts()
    rows[1] = {**rows[1], "requires_input_manifest_hash": False}
    validation = validate_session_governance_registry(rows)
    assert validation["valid"] is False


def test_lineage_replay_drift_rollback_and_invalidation_visibility():
    rows = {row["session_label"]: row for row in default_runtime_session_governance_contracts()}
    assert rows["session_lineage_record"]["requires_lineage_hash"] is True
    assert rows["session_replay_scope"]["requires_replay_scope"] is True
    assert rows["session_drift_scope"]["requires_drift_scope"] is True
    assert rows["session_rollback_rule"]["requires_rollback_path"] is True
    assert rows["session_rollback_rule"]["rollback_visible"] is True
    assert rows["session_invalidation_rule"]["requires_invalidation_rule"] is True
    assert rows["session_invalidation_rule"]["blocks_invalidated_session_reuse"] is True
    assert rows["session_invalidation_rule"]["invalidation_visible"] is True


def test_isolation_and_authorization_behaviors():
    rows = {row["session_label"]: row for row in default_runtime_session_governance_contracts()}
    assert rows["session_isolation_boundary"]["isolates_session_state"] is True
    assert rows["session_isolation_boundary"]["blocks_cross_session_mutation"] is True
    assert rows["session_authorization_boundary"]["blocks_production_authorization"] is True
    assert rows["session_audit_summary"]["replay_mismatch_visible"] is True
    assert rows["session_audit_summary"]["drift_visible"] is True
    assert rows["session_audit_summary"]["boundary_visible"] is True


def test_session_cross_contract_compatibility():
    validation = export_session_governance_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_classification_reference_count"] == 0
    assert validation["invalid_evidence_reference_count"] == 0
    assert validation["invalid_provenance_reference_count"] == 0
    assert validation["invalid_reasoning_stage_reference_count"] == 0
    assert validation["invalid_explanation_reference_count"] == 0
    assert validation["invalid_confidence_reference_count"] == 0
    assert validation["invalid_synthesis_reference_count"] == 0
    assert validation["invalid_boundary_reference_count"] == 0
    assert validation["invalid_replay_reference_count"] == 0
    assert validation["invalid_drift_reference_count"] == 0


def _assert_invalid_ref(field: str, error: str, count: str):
    rows = default_runtime_session_governance_contracts()
    rows[0] = {**rows[0], field: ["missing_ref"]}
    validation = validate_session_governance_registry(rows)
    assert validation["valid"] is False
    assert error in validation["validation_errors"]
    assert validation[count] == 1


def test_invalid_classification_reference_rejection():
    _assert_invalid_ref("allowed_classification_ids", "invalid_classification_references", "invalid_classification_reference_count")


def test_invalid_evidence_reference_rejection():
    _assert_invalid_ref("allowed_evidence_type_ids", "invalid_evidence_references", "invalid_evidence_reference_count")


def test_invalid_provenance_reference_rejection():
    _assert_invalid_ref("allowed_provenance_type_ids", "invalid_provenance_references", "invalid_provenance_reference_count")


def test_invalid_reasoning_stage_reference_rejection():
    _assert_invalid_ref("allowed_reasoning_stage_ids", "invalid_reasoning_stage_references", "invalid_reasoning_stage_reference_count")


def test_invalid_explanation_reference_rejection():
    _assert_invalid_ref("allowed_explanation_type_ids", "invalid_explanation_references", "invalid_explanation_reference_count")


def test_invalid_confidence_reference_rejection():
    _assert_invalid_ref("allowed_confidence_type_ids", "invalid_confidence_references", "invalid_confidence_reference_count")


def test_invalid_synthesis_reference_rejection():
    _assert_invalid_ref("allowed_synthesis_type_ids", "invalid_synthesis_references", "invalid_synthesis_reference_count")


def test_invalid_boundary_reference_rejection():
    _assert_invalid_ref("allowed_boundary_type_ids", "invalid_boundary_references", "invalid_boundary_reference_count")


def test_invalid_replay_reference_rejection():
    _assert_invalid_ref("allowed_replay_type_ids", "invalid_replay_references", "invalid_replay_reference_count")


def test_invalid_drift_reference_rejection():
    _assert_invalid_ref("allowed_drift_type_ids", "invalid_drift_references", "invalid_drift_reference_count")


def test_repeat_run_stability():
    first = export_session_governance_registry()
    second = export_session_governance_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_session_governance_manifest()
    assert manifest["runtime_session_governance_planning_only"] is True
    assert manifest["live_session_execution_enabled"] is False
    assert manifest["live_drift_detection_enabled"] is False
    assert manifest["live_replay_execution_enabled"] is False
    assert manifest["live_synthesis_execution_enabled"] is False
    assert manifest["live_decision_routing_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["session_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_session_governance_contracts_report()
    second = build_v3_3_runtime_session_governance_contracts_report()
    assert first["summary"]["total_session_governance_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["invalid_previous_session_reference_count"] == 0
    assert first["summary"]["previous_session_rank_violation_count"] == 0
    assert first["summary"]["behavior_rule_violation_count"] == 0
    assert first["summary"]["production_authorized_session_governance_count"] == 0
    assert first["session_governance_manifest"]["deterministic_hash"] == second["session_governance_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["live_session_execution_enabled"] is False
