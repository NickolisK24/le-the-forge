import json

from app.runtime_intelligence.classification_contracts import default_runtime_intelligence_classifications
from app.runtime_intelligence.evidence_contracts import (
    EVIDENCE_LABELS,
    build_runtime_evidence_manifest,
    default_runtime_evidence_contracts,
    serialize_runtime_evidence_manifest,
)
from app.runtime_intelligence.evidence_hashing import hash_evidence_manifest, validate_evidence_replay_stability
from app.runtime_intelligence.evidence_registry import (
    detect_duplicate_evidence_contracts,
    export_evidence_registry,
    validate_evidence_registry,
)
from scripts.report_v3_3_runtime_evidence_contracts import build_v3_3_runtime_evidence_contracts_report


def test_deterministic_ordering_stability():
    classifications = default_runtime_intelligence_classifications()
    rows = list(reversed(default_runtime_evidence_contracts(classifications)))
    manifest = build_runtime_evidence_manifest(rows, classifications=classifications)
    assert [row["evidence_label"] for row in manifest["evidence_contracts"]] == list(EVIDENCE_LABELS)
    assert [row["deterministic_rank"] for row in manifest["evidence_contracts"]] == sorted(row["deterministic_rank"] for row in manifest["evidence_contracts"])


def test_stable_hash_repeatability():
    first = build_runtime_evidence_manifest()
    second = build_runtime_evidence_manifest()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert hash_evidence_manifest(first) == hash_evidence_manifest(second)


def test_duplicate_evidence_contract_rejection():
    rows = default_runtime_evidence_contracts()
    duplicate = rows + [rows[0]]
    validation = validate_evidence_registry(duplicate)
    detection = detect_duplicate_evidence_contracts(duplicate)
    assert validation["valid"] is False
    assert "duplicate_evidence_contracts_detected" in validation["validation_errors"]
    assert rows[0]["evidence_type_id"] in detection["duplicate_evidence_type_ids"]
    assert rows[0]["evidence_label"] in detection["duplicate_evidence_labels"]


def test_deterministic_replay_validation():
    manifest = build_runtime_evidence_manifest()
    replay = validate_evidence_replay_stability(manifest)
    assert replay["replay_stable"] is True
    assert replay["first_hash"] == replay["second_hash"]


def test_evidence_serialization_stability():
    manifest = build_runtime_evidence_manifest()
    first = serialize_runtime_evidence_manifest(manifest)
    second = serialize_runtime_evidence_manifest(json.loads(first))
    assert first == second


def test_unsupported_evidence_visibility():
    validation = validate_evidence_registry(default_runtime_evidence_contracts())
    assert validation["unsupported_evidence_visible"] is True
    unsupported = [row for row in default_runtime_evidence_contracts() if row["evidence_label"] == "unsupported_signal"][0]
    assert unsupported["drift_visible"] is True
    assert unsupported["production_authorized"] is False


def test_provenance_required_validation():
    manifest = build_runtime_evidence_manifest()
    assert all(row["provenance_required"] for row in manifest["evidence_contracts"])
    assert export_evidence_registry()["registry_validation"]["provenance_required_by_all_contracts"] is True


def test_source_required_validation():
    manifest = build_runtime_evidence_manifest()
    assert all(row["source_required"] for row in manifest["evidence_contracts"])
    assert export_evidence_registry()["registry_validation"]["source_required_by_all_contracts"] is True


def test_authorization_prohibited_validation():
    validation = validate_evidence_registry(default_runtime_evidence_contracts())
    assert validation["authorization_prohibited_evidence_visible"] is True
    assert validation["production_authorized_evidence_contracts"] == []
    authorization = [row for row in default_runtime_evidence_contracts() if row["evidence_label"] == "authorization_signal"][0]
    assert authorization["production_authorized"] is False


def test_evidence_to_classification_compatibility():
    registry = export_evidence_registry()
    assert registry["registry_validation"]["valid"] is True
    assert registry["registry_validation"]["invalid_classification_reference_count"] == 0


def test_invalid_classification_reference_rejection():
    rows = default_runtime_evidence_contracts()
    rows[0] = {**rows[0], "allowed_classification_ids": ["missing_classification_id"]}
    validation = validate_evidence_registry(rows)
    assert validation["valid"] is False
    assert "invalid_classification_references" in validation["validation_errors"]
    assert validation["invalid_classification_reference_count"] == 1


def test_repeat_run_stability():
    first = export_evidence_registry()
    second = export_evidence_registry()
    assert first["deterministic_hash"] == second["deterministic_hash"]
    assert first["registry_validation"]["valid"] is True


def test_production_non_consumption_guard_compatibility():
    manifest = build_runtime_evidence_manifest()
    assert manifest["runtime_evidence_planning_only"] is True
    assert manifest["runtime_evidence_synthesis_enabled"] is False
    assert manifest["runtime_reasoning_decisions_enabled"] is False
    assert manifest["runtime_manifest_consumption_enabled"] is False
    assert manifest["production_runtime_routing_authorized"] is False
    assert manifest["production_authoritative_manifest_treatment"] is False
    assert all(row["production_authorized"] is False for row in manifest["evidence_contracts"])
    assert all(row["default_runtime_manifest_consumption_enabled"] is False for row in manifest["evidence_contracts"])


def test_report_generation_is_stable_and_complete():
    first = build_v3_3_runtime_evidence_contracts_report()
    second = build_v3_3_runtime_evidence_contracts_report()
    assert first["summary"]["total_evidence_contract_count"] == 12
    assert first["summary"]["stable_hash_valid"] is True
    assert first["summary"]["duplicate_detection_passed"] is True
    assert first["summary"]["unsupported_evidence_contract_count"] == 1
    assert first["summary"]["authorization_prohibited_evidence_contract_count"] == 1
    assert first["summary"]["production_authorized_evidence_contract_count"] == 0
    assert first["summary"]["invalid_classification_reference_count"] == 0
    assert first["evidence_manifest"]["deterministic_hash"] == second["evidence_manifest"]["deterministic_hash"]
    assert first["safety_confirmations"]["production_runtime_routing_prohibited"] is True
    assert first["safety_confirmations"]["default_runtime_manifest_consumption_disabled"] is True
    assert first["safety_confirmations"]["production_authoritative_manifest_treatment_prohibited"] is True
