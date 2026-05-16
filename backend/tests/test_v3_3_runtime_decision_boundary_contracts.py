import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.decision_boundary_contracts import (
    BOUNDARY_LABELS,
    build_runtime_decision_boundary_manifest,
    default_runtime_decision_boundary_contracts,
    serialize_runtime_decision_boundary_manifest,
)
from app.runtime_intelligence.decision_boundary_hashing import (
    hash_decision_boundary_manifest,
    validate_decision_boundary_replay_stability,
)
from app.runtime_intelligence.decision_boundary_registry import (
    detect_duplicate_decision_boundary_contracts,
    export_decision_boundary_registry,
    validate_decision_boundary_registry,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import default_runtime_evidence_synthesis_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from scripts.report_v3_3_runtime_decision_boundary_contracts import build_v3_3_runtime_decision_boundary_contracts_report


def _deps():
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance)
    explanations = default_runtime_explanation_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning)
    confidence = default_runtime_confidence_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations)
    synthesis = default_runtime_evidence_synthesis_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence)
    return classifications, evidence, provenance, reasoning, explanations, confidence, synthesis


def test_deterministic_ordering_stability():
    classifications, evidence, provenance, reasoning, explanations, confidence, synthesis = _deps()
    rows = list(reversed(default_runtime_decision_boundary_contracts(classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence, synthesis_contracts=synthesis)))
    manifest = build_runtime_decision_boundary_manifest(rows, classifications=classifications, evidence_contracts=evidence, provenance_contracts=provenance, reasoning_stage_contracts=reasoning, explanation_contracts=explanations, confidence_contracts=confidence, synthesis_contracts=synthesis)
    assert [row["boundary_label"] for row in manifest["boundary_contracts"]] == list(BOUNDARY_LABELS)
    assert [row["deterministic_rank"] for row in manifest["boundary_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["boundary_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_decision_boundary_manifest()
    second = build_runtime_decision_boundary_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_decision_boundary_manifest(first) == hash_decision_boundary_manifest(second)


def test_duplicate_decision_boundary_contract_rejection():
    rows = default_runtime_decision_boundary_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_decision_boundary_registry(duplicate)
    detection = detect_duplicate_decision_boundary_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_decision_boundary_contracts_detected" in validation["validation_errors"]
    assert rows[0]["boundary_type_id"] in detection["duplicate_boundary_type_ids"]
    assert rows[0]["boundary_label"] in detection["duplicate_boundary_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_decision_boundary_manifest()
    replay = validate_decision_boundary_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_decision_boundary_serialization_stability():
    manifest = build_runtime_decision_boundary_manifest()
    first = serialize_runtime_decision_boundary_manifest(manifest)
    second = serialize_runtime_decision_boundary_manifest(json.loads(first))
    assert first == second


def test_boundary_action_validation():
    validation = export_decision_boundary_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_boundary_action_count"] == 0


def test_invalid_boundary_action_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "boundary_action": "silent_pass"}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_boundary_actions" in validation["validation_errors"]
    assert validation["invalid_boundary_action_count"] == 1


def test_required_boundary_behavior_validation():
    validation = export_decision_boundary_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["behavior_rule_violation_count"] == 0


def test_required_boundary_behavior_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "blocks_downstream_reasoning": False}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "boundary_behavior_rule_invalid" in validation["validation_errors"]
    assert validation["behavior_rule_violation_count"] == 1


def test_specific_boundary_behaviors_are_visible():
    rows = {row["boundary_label"]: row for row in default_runtime_decision_boundary_contracts()}
    assert rows["unsupported_hard_stop"]["blocks_downstream_reasoning"] is True
    assert rows["unsupported_hard_stop"]["preserves_unsupported"] is True
    assert rows["authorization_prohibited_hard_stop"]["blocks_production_authorization"] is True
    assert rows["production_routing_hard_stop"]["blocks_production_authorization"] is True
    assert rows["default_manifest_consumption_hard_stop"]["blocks_production_authorization"] is True
    assert rows["confidence_ceiling_stop"]["blocks_downstream_reasoning"] is True
    assert rows["replay_mismatch_stop"]["requires_replay_validation"] is True
    assert rows["replay_mismatch_stop"]["blocks_downstream_reasoning"] is True
    assert rows["drift_detected_escalation"]["preserves_drift"] is True
    assert rows["conflict_detected_escalation"]["preserves_conflicts"] is True
    assert rows["provenance_incomplete_escalation"]["requires_manual_review"] is True
    assert rows["blocker_detected_stop"]["preserves_blockers"] is True
    assert rows["recommendation_prohibited_boundary"]["blocks_recommendation_logic"] is True
    assert rows["manual_review_required_boundary"]["requires_manual_review"] is True


def test_visibility_summary_flags():
    validation = export_decision_boundary_registry()["registry_validation"]
    assert validation["hard_stop_boundary_visible"] is True
    assert validation["escalation_boundary_visible"] is True
    assert validation["manual_review_boundary_visible"] is True
    assert validation["recommendation_prohibited_boundary_visible"] is True
    assert validation["production_prohibited_boundary_visible"] is True
    assert validation["replay_mismatch_boundary_visible"] is True
    assert validation["confidence_ceiling_boundary_visible"] is True


def test_boundary_cross_contract_compatibility():
    registry = export_decision_boundary_registry()
    validation = registry["registry_validation"]
    assert validation["valid"] is True
    assert validation["invalid_classification_reference_count"] == 0
    assert validation["invalid_evidence_reference_count"] == 0
    assert validation["invalid_provenance_reference_count"] == 0
    assert validation["invalid_reasoning_stage_reference_count"] == 0
    assert validation["invalid_explanation_reference_count"] == 0
    assert validation["invalid_confidence_reference_count"] == 0
    assert validation["invalid_synthesis_reference_count"] == 0


def test_invalid_classification_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]


def test_invalid_evidence_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_evidence_type_ids": ["missing_evidence_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_evidence_references" in validation["validation_errors"]


def test_invalid_provenance_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_provenance_type_ids": ["missing_provenance_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_provenance_references" in validation["validation_errors"]


def test_invalid_reasoning_stage_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_reasoning_stage_ids": ["missing_reasoning_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_reasoning_stage_references" in validation["validation_errors"]


def test_invalid_explanation_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_explanation_type_ids": ["missing_explanation_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_explanation_references" in validation["validation_errors"]


def test_invalid_confidence_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_confidence_type_ids": ["missing_confidence_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_confidence_references" in validation["validation_errors"]


def test_invalid_synthesis_reference_rejection():
    rows = default_runtime_decision_boundary_contracts()
    rows[0] = {**rows[0], "allowed_synthesis_type_ids": ["missing_synthesis_id"]}
    validation = validate_decision_boundary_registry(rows)
    assert validation["valid"] is False
    assert "invalid_synthesis_references" in validation["validation_errors"]


def test_repeat_run_stability():
    first = export_decision_boundary_registry()
    second = export_decision_boundary_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_decision_boundary_manifest()
    assert manifest["runtime_decision_boundaries_planning_only"] is True
    assert manifest["live_decision_routing_enabled"] is False
    assert manifest["live_synthesis_execution_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["boundary_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_decision_boundary_contracts_report()
    second = build_v3_3_runtime_decision_boundary_contracts_report()
    assert first["summary"]["total_decision_boundary_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["invalid_boundary_action_count"] == 0
    assert first["summary"]["behavior_rule_violation_count"] == 0
    assert first["summary"]["production_authorized_boundary_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["summary"]["invalid_evidence_reference_count"] == 0
    assert first["summary"]["invalid_provenance_reference_count"] == 0
    assert first["summary"]["invalid_reasoning_stage_reference_count"] == 0
    assert first["summary"]["invalid_explanation_reference_count"] == 0
    assert first["summary"]["invalid_confidence_reference_count"] == 0
    assert first["summary"]["invalid_synthesis_reference_count"] == 0
    assert first["decision_boundary_manifest"]["deterministic_hash"] == second["decision_boundary_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["live_decision_routing_enabled"] is False
