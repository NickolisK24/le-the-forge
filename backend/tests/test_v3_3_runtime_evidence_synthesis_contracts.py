import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.confidence_contracts import default_runtime_confidence_contracts
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.evidence_synthesis_contracts import (
    SYNTHESIS_LABELS,
    build_runtime_evidence_synthesis_manifest,
    default_runtime_evidence_synthesis_contracts,
    serialize_runtime_evidence_synthesis_manifest,
)
from app.runtime_intelligence.evidence_synthesis_hashing import (
    hash_evidence_synthesis_manifest,
    validate_evidence_synthesis_replay_stability,
)
from app.runtime_intelligence.evidence_synthesis_registry import (
    detect_duplicate_evidence_synthesis_contracts,
    export_evidence_synthesis_registry,
    validate_evidence_synthesis_registry,
)
from app.runtime_intelligence.explanation_contracts import default_runtime_explanation_contracts
from app.runtime_intelligence.provenance_contracts import default_runtime_provenance_contracts
from app.runtime_intelligence.reasoning_chain_contracts import default_runtime_reasoning_chain_contracts
from scripts.report_v3_3_runtime_evidence_synthesis_contracts import build_v3_3_runtime_evidence_synthesis_contracts_report


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
    confidence = default_runtime_confidence_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
    )
    return classifications, evidence, provenance, reasoning, explanations, confidence


def test_deterministic_ordering_stability():
    classifications, evidence, provenance, reasoning, explanations, confidence = _deps()
    rows = list(reversed(default_runtime_evidence_synthesis_contracts(
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
        confidence_contracts=confidence,
    )))
    manifest = build_runtime_evidence_synthesis_manifest(
        rows,
        classifications=classifications,
        evidence_contracts=evidence,
        provenance_contracts=provenance,
        reasoning_stage_contracts=reasoning,
        explanation_contracts=explanations,
        confidence_contracts=confidence,
    )
    assert [row["synthesis_label"] for row in manifest["synthesis_contracts"]] == list(SYNTHESIS_LABELS)
    assert [row["deterministic_rank"] for row in manifest["synthesis_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["synthesis_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_evidence_synthesis_manifest()
    second = build_runtime_evidence_synthesis_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_evidence_synthesis_manifest(first) == hash_evidence_synthesis_manifest(second)


def test_duplicate_synthesis_contract_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_evidence_synthesis_registry(duplicate)
    detection = detect_duplicate_evidence_synthesis_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_synthesis_contracts_detected" in validation["validation_errors"]
    assert rows[0]["synthesis_type_id"] in detection["duplicate_synthesis_type_ids"]
    assert rows[0]["synthesis_label"] in detection["duplicate_synthesis_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_evidence_synthesis_manifest()
    replay = validate_evidence_synthesis_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_synthesis_serialization_stability():
    manifest = build_runtime_evidence_synthesis_manifest()
    first = serialize_runtime_evidence_synthesis_manifest(manifest)
    second = serialize_runtime_evidence_synthesis_manifest(json.loads(first))
    assert first == second


def test_input_output_count_validation():
    validation = export_evidence_synthesis_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["input_count_violation_count"] == 0


def test_invalid_input_output_count_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "minimum_input_count": 0, "maximum_input_count": 0}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "input_output_count_invalid" in validation["validation_errors"]
    assert validation["input_count_violation_count"] == 1


def test_preservation_rule_validation():
    validation = export_evidence_synthesis_registry()["registry_validation"]
    assert validation["valid"] is True
    assert validation["preservation_rule_violation_count"] == 0


def test_preservation_rule_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    for index, row in enumerate(rows):
        if row["synthesis_label"] == "conflict_preserving_merge":
            rows[index] = {**row, "preserves_conflicts": False}
            break
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "preservation_rule_invalid" in validation["validation_errors"]
    assert validation["preservation_rule_violation_count"] == 1


def test_explicit_preservation_visibility():
    validation = export_evidence_synthesis_registry()["registry_validation"]
    assert validation["conflict_preserving_synthesis_visible"] is True
    assert validation["drift_preserving_synthesis_visible"] is True
    assert validation["unsupported_preserving_synthesis_visible"] is True
    assert validation["blocker_preserving_synthesis_visible"] is True
    assert validation["limitation_preserving_synthesis_visible"] is True
    assert validation["provenance_preserving_synthesis_visible"] is True
    assert validation["decision_boundary_preserving_synthesis_visible"] is True


def test_synthesis_to_input_evidence_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_input_evidence_reference_count"] == 0


def test_synthesis_to_output_evidence_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_output_evidence_reference_count"] == 0


def test_synthesis_to_provenance_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_provenance_reference_count"] == 0


def test_synthesis_to_classification_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_synthesis_to_confidence_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_confidence_reference_count"] == 0


def test_synthesis_to_reasoning_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_reasoning_stage_reference_count"] == 0


def test_synthesis_to_explanation_compatibility():
    registry = export_evidence_synthesis_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_explanation_reference_count"] == 0


def test_invalid_input_evidence_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_input_evidence_type_ids": ["missing_input_evidence_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_input_evidence_references" in validation["validation_errors"]
    assert validation["invalid_input_evidence_reference_count"] == 1


def test_invalid_output_evidence_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_output_evidence_type_ids": ["missing_output_evidence_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_output_evidence_references" in validation["validation_errors"]
    assert validation["invalid_output_evidence_reference_count"] == 1


def test_invalid_provenance_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_provenance_type_ids": ["missing_provenance_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_provenance_references" in validation["validation_errors"]
    assert validation["invalid_provenance_reference_count"] == 1


def test_invalid_classification_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_invalid_confidence_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_confidence_type_ids": ["missing_confidence_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_confidence_references" in validation["validation_errors"]
    assert validation["invalid_confidence_reference_count"] == 1


def test_invalid_reasoning_stage_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_reasoning_stage_ids": ["missing_reasoning_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_reasoning_stage_references" in validation["validation_errors"]
    assert validation["invalid_reasoning_stage_reference_count"] == 1


def test_invalid_explanation_reference_rejection():
    rows = default_runtime_evidence_synthesis_contracts()
    rows[0] = {**rows[0], "allowed_explanation_type_ids": ["missing_explanation_id"]}
    validation = validate_evidence_synthesis_registry(rows)
    assert validation["valid"] is False
    assert "invalid_explanation_references" in validation["validation_errors"]
    assert validation["invalid_explanation_reference_count"] == 1


def test_repeat_run_stability():
    first = export_evidence_synthesis_registry()
    second = export_evidence_synthesis_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_evidence_synthesis_manifest()
    assert manifest["runtime_evidence_synthesis_planning_only"] is True
    assert manifest["live_synthesis_execution_enabled"] is False
    assert manifest["active_runtime_reasoning_decisions_enabled"] is False
    assert manifest["recommendation_logic_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["synthesis_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_evidence_synthesis_contracts_report()
    second = build_v3_3_runtime_evidence_synthesis_contracts_report()
    assert first["summary"]["total_synthesis_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["input_count_violation_count"] == 0
    assert first["summary"]["preservation_rule_violation_count"] == 0
    assert first["summary"]["production_authorized_synthesis_count"] == 0
    assert first["summary"]["invalid_input_evidence_reference_count"] == 0
    assert first["summary"]["invalid_output_evidence_reference_count"] == 0
    assert first["summary"]["invalid_provenance_reference_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["summary"]["invalid_confidence_reference_count"] == 0
    assert first["summary"]["invalid_reasoning_stage_reference_count"] == 0
    assert first["summary"]["invalid_explanation_reference_count"] == 0
    assert first["evidence_synthesis_manifest"]["deterministic_hash"] == second["evidence_synthesis_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
    assert first["safety_confirmations"]["live_synthesis_execution_enabled"] is False
