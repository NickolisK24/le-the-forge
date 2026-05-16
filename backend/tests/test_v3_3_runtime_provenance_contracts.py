import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import default_runtime_evidence_contracts
from app.runtime_intelligence.provenance_contracts import (
    PROVENANCE_LABELS,
    build_runtime_provenance_manifest,
    default_runtime_provenance_contracts,
    serialize_runtime_provenance_manifest,
)
from app.runtime_intelligence.provenance_hashing import (
    hash_provenance_manifest,
    validate_provenance_replay_stability,
)
from app.runtime_intelligence.provenance_registry import (
    detect_duplicate_provenance_contracts,
    export_provenance_registry,
    validate_provenance_registry,
)
from scripts.report_v3_3_runtime_provenance_contracts import build_v3_3_runtime_provenance_contracts_report


def test_deterministic_ordering_stability():
    classifications = default_runtime_intelligence_classifications()
    evidence = default_runtime_evidence_contracts(classifications)
    rows = list(reversed(default_runtime_provenance_contracts(classifications=classifications, evidence_contracts=evidence)))
    manifest = build_runtime_provenance_manifest(rows, classifications=classifications, evidence_contracts=evidence)
    assert [row["provenance_label"] for row in manifest["provenance_contracts"]] == list(PROVENANCE_LABELS)
    assert [row["deterministic_rank"] for row in manifest["provenance_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["provenance_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_provenance_manifest()
    second = build_runtime_provenance_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_provenance_manifest(first) == hash_provenance_manifest(second)


def test_duplicate_provenance_contract_rejection():
    rows = default_runtime_provenance_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_provenance_registry(duplicate)
    detection = detect_duplicate_provenance_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_provenance_contracts_detected" in validation["validation_errors"]
    assert rows[0]["provenance_type_id"] in detection["duplicate_provenance_type_ids"]
    assert rows[0]["provenance_label"] in detection["duplicate_provenance_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_provenance_manifest()
    replay = validate_provenance_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_provenance_serialization_stability():
    manifest = build_runtime_provenance_manifest()
    first = serialize_runtime_provenance_manifest(manifest)
    second = serialize_runtime_provenance_manifest(json.loads(first))
    assert first == second


def test_unsupported_provenance_visibility():
    validation = validate_provenance_registry(default_runtime_provenance_contracts())
    assert validation["unsupported_provenance_visible"] is True
    unsupported = [row for row in default_runtime_provenance_contracts() if row["provenance_label"] == "unsupported_source"][0]
    assert unsupported["drift_visible"] is True
    assert unsupported["production_authorized"] is False


def test_authorization_gate_provenance_visibility():
    validation = validate_provenance_registry(default_runtime_provenance_contracts())
    assert validation["authorization_gate_provenance_visible"] is True
    authorization = [row for row in default_runtime_provenance_contracts() if row["provenance_label"] == "authorization_gate_source"][0]
    assert authorization["production_authorized"] is False


def test_source_required_validation():
    registry = export_provenance_registry()
    assert registry["registry_validation"]["source_required_by_all_contracts"] is True
    assert all(row["source_required"] for row in registry["provenance_contracts"])


def test_hash_required_validation():
    registry = export_provenance_registry()
    assert registry["registry_validation"]["hash_required_by_all_contracts"] is True
    assert all(row["hash_required"] for row in registry["provenance_contracts"])


def test_provenance_to_evidence_compatibility():
    registry = export_provenance_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_evidence_reference_count"] == 0


def test_provenance_to_classification_compatibility():
    registry = export_provenance_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_invalid_evidence_reference_rejection():
    rows = default_runtime_provenance_contracts()
    rows[0] = {**rows[0], "allowed_evidence_type_ids": ["missing_evidence_type_id"]}
    validation = validate_provenance_registry(rows)
    assert validation["valid"] is False
    assert "invalid_evidence_references" in validation["validation_errors"]
    assert validation["invalid_evidence_reference_count"] == 1


def test_invalid_classification_reference_rejection():
    rows = default_runtime_provenance_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_provenance_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_repeat_run_stability():
    first = export_provenance_registry()
    second = export_provenance_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_provenance_manifest()
    assert manifest["runtime_provenance_planning_only"] is True
    assert manifest["runtime_evidence_synthesis_enabled"] is False
    assert manifest["runtime_reasoning_decisions_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["provenance_contracts"])
    assert all(row["default_runtime_manifest_consumption_enabled"] is False for row in manifest["provenance_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_provenance_contracts_report()
    second = build_v3_3_runtime_provenance_contracts_report()
    assert first["summary"]["total_provenance_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["unsupported_provenance_contract_count"] == 1
    assert first["summary"]["authorization_gate_provenance_contract_count"] == 1
    assert first["summary"]["production_authorized_provenance_contract_count"] == 0
    assert first["summary"]["invalid_evidence_reference_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["provenance_manifest"]["deterministic_hash"] == second["provenance_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
