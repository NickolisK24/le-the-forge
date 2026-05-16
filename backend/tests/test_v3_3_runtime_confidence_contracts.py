import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import (
    CONFIDENCE_LABELS,
    NON_UPGRADEABLE_CONFIDENCE_LABELS,
    build_runtime_confidence_manifest,
    default_runtime_confidence_contracts,
    serialize_runtime_confidence_manifest,
)
from app.runtime_intelligence.confidence_hashing import (
    hash_confidence_manifest,
    validate_confidence_replay_stability,
)
from app.runtime_intelligence.confidence_registry import (
    detect_duplicate_confidence_contracts,
    export_confidence_registry,
    validate_confidence_registry,
)
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from scripts.report_v3_3_runtime_confidence_contracts import build_v3_3_runtime_confidence_contracts_report


def _deps():
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    provenance = default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)
    reasoning = default_runtime_reasoning_chain_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
    )
    explanations = default_runtime_explanation_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
    )
    return classifications, evidence, provenance, reasoning, explanations


def test_deterministic_ordering_stability():
    classifications, evidence, provenance, reasoning, explanations = _deps()
    rows = list(reversed(default_runtime_confidence_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
    )))
    manifest = build_runtime_confidence_manifest(
        rows,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
    )
    assert [row["confidence_label"] for row in manifest["confidence_contracts"]] == list(CONFIDENCE_LABELS)
    assert [row["deterministic_rank"] for row in manifest["confidence_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["confidence_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_confidence_manifest()
    second = build_runtime_confidence_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_confidence_manifest(first) == hash_confidence_manifest(second)


def test_duplicate_confidence_contract_rejection():
    rows = default_runtime_confidence_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_confidence_registry(duplicate)
    detection = detect_duplicate_confidence_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_confidence_contracts_detected" in validation["validation_errors"]
    assert rows[0]["confidence_type_id"] in detection["duplicate_confidence_type_ids"]
    assert rows[0]["confidence_label"] in detection["duplicate_confidence_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_confidence_manifest()
    replay = validate_confidence_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_confidence_serialization_stability():
    manifest = build_runtime_confidence_manifest()
    first = serialize_runtime_confidence_manifest(manifest)
    second = serialize_runtime_confidence_manifest(json.loads(first))
    assert first == second


def test_confidence_floor_ceiling_validation():
    validation = export_confidence_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["floor_ceiling_violation_count"] == 0


def test_invalid_floor_ceiling_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "confidence_floor": 101, "confidence_ceiling": 90}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "confidence_floor_ceiling_invalid" in validation["validation_errors"]
    assert validation["floor_ceiling_violation_count"] == 1


def test_non_upgradeable_confidence_state_validation():
    rows = default_runtime_confidence_contracts()
    for index, row in enumerate(rows):
        if row["confidence_label"] == NON_UPGRADEABLE_CONFIDENCE_LABELS[0]:
            rows[index] = {**row, "can_upgrade_without_revalidation": True}
            break
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "non_upgradeable_confidence_state_marked_upgradeable" in validation["validation_errors"]
    assert validation["non_upgradeable_violation_count"] == 1


def test_explicit_confidence_visibility():
    validation = export_confidence_registry()["registry_validation"]
    assert validation["unsupported_confidence_visible"] is True
    assert validation["blocked_confidence_visible"] is True
    assert validation["authorization_prohibited_confidence_visible"] is True
    assert validation["drift_present_confidence_visible"] is True
    assert validation["conflict_present_confidence_visible"] is True
    assert validation["provenance_incomplete_confidence_visible"] is True
    assert validation["blocker_visible_confidence_visible"] is True
    assert validation["risk_visible_confidence_visible"] is True
    assert validation["limitation_visible_confidence_visible"] is True


def test_confidence_to_classification_compatibility():
    registry = export_confidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_confidence_to_evidence_compatibility():
    registry = export_confidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_evidence_reference_count"] == 0


def test_confidence_to_provenance_compatibility():
    registry = export_confidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_provenance_reference_count"] == 0


def test_confidence_to_reasoning_compatibility():
    registry = export_confidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_reasoning_stage_reference_count"] == 0


def test_confidence_to_explanation_compatibility():
    registry = export_confidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_explanation_reference_count"] == 0


def test_invalid_classification_reference_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_invalid_evidence_reference_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "allowed_evidence_type_ids": ["missing_evidence_type_id"]}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_evidence_references" in validation["validation_errors"]
    assert validation["invalid_evidence_reference_count"] == 1


def test_invalid_provenance_reference_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "allowed_provenance_type_ids": ["missing_provenance_type_id"]}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_provenance_references" in validation["validation_errors"]
    assert validation["invalid_provenance_reference_count"] == 1


def test_invalid_reasoning_stage_reference_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "allowed_reasoning_stage_ids": ["missing_reasoning_stage_id"]}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_reasoning_stage_references" in validation["validation_errors"]
    assert validation["invalid_reasoning_stage_reference_count"] == 1


def test_invalid_explanation_reference_rejection():
    rows = default_runtime_confidence_contracts()
    rows[0] = {**rows[0], "allowed_explanation_type_ids": ["missing_explanation_type_id"]}
    validation = validate_confidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_explanation_references" in validation["validation_errors"]
    assert validation["invalid_explanation_reference_count"] == 1


def test_repeat_run_stability():
    first = export_confidence_registry()
    second = export_confidence_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_confidence_manifest()
    assert manifest["runtime_confidence_planning_only"] is True
    assert manifest["live_confidence_scoring_enabled"] is False
    assert manifest["probabilistic_inference_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["confidence_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_confidence_contracts_report()
    second = build_v3_3_runtime_confidence_contracts_report()
    assert first["summary"]["total_confidence_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["floor_ceiling_violation_count"] == 0
    assert first["summary"]["non_upgradeable_violation_count"] == 0
    assert first["summary"]["unsupported_confidence_count"] == 1
    assert first["summary"]["blocked_confidence_count"] == 1
    assert first["summary"]["authorization_prohibited_confidence_count"] == 1
    assert first["summary"]["conflict_present_confidence_count"] == 1
    assert first["summary"]["drift_present_confidence_count"] == 1
    assert first["summary"]["provenance_incomplete_confidence_count"] == 1
    assert first["summary"]["production_authorized_confidence_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["summary"]["invalid_evidence_reference_count"] == 0
    assert first["summary"]["invalid_provenance_reference_count"] == 0
    assert first["summary"]["invalid_reasoning_stage_reference_count"] == 0
    assert first["summary"]["invalid_explanation_reference_count"] == 0
    assert first["confidence_manifest"]["deterministic_hash"] == second["confidence_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["probabilistic_inference_enabled"] is False
