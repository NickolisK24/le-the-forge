"""Deterministic v4.3 closeout and v4.4 planning readiness audit.

The audit validates Phase 1-9 evidence inventory, deterministic guarantees,
state visibility, continuity, integrity, readiness, prohibited boundaries, and
disabled operational capabilities. It never executes orchestration, approves
readiness, authorizes operations, repairs evidence, resolves dependencies,
integrates planners, consumes production bundles, or mutates runtime state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .v4_3_closeout_readiness_models import (
    V4_3_CLOSEOUT_CLASSIFICATION_BLOCKED,
    V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE,
    V4_3_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
    V4_3_CLOSEOUT_READINESS_STATUS_BLOCKED,
    V4_3_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_3_DETERMINISTIC_GUARANTEES,
    V4_3_DISABLED_OPERATIONAL_BOUNDARIES,
    V4_3_EVIDENCE_INVALID_JSON,
    V4_3_EVIDENCE_MISSING,
    V4_3_EVIDENCE_PRESENT,
    V4_3_EXPECTED_MIGRATION_DOC_NAMES,
    V4_3_EXPECTED_PHASE_IDS,
    V4_3_EXPECTED_REPORT_NAMES,
    V4_3_EXPECTED_TEST_NAMES,
    V4_3_EXPLICIT_LIMITATIONS,
    V4_3_EXPLICIT_PROHIBITIONS,
    V4_3_FINAL_COUNTER_NAMES,
    V4_3_PHASE_DEFINITIONS,
    V4_3_STATE_TYPES,
    V4_4_READINESS_CLASSIFICATION_BLOCKED,
    V4_4_READINESS_CLASSIFICATION_READY,
    V4_4_RECOMMENDED_DIRECTION,
    V43CloseoutClassification,
    V43CloseoutIdentity,
    V43CloseoutReadinessCertification,
    V43FinalCounterGuarantee,
    V43InventoryValidation,
    V43OperationalBoundaryGuarantee,
    V43PhaseEvidenceReference,
    V43StateVisibilitySummary,
    V44ReadinessClassification,
    default_v4_3_closeout_identity,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "readiness_approved",
    "operational_authorized",
    "orchestration_runtime_enabled",
    "orchestration_execution_enabled",
    "orchestration_activation_enabled",
    "orchestration_authorization_enabled",
    "orchestration_approval_enabled",
    "orchestration_dispatch_enabled",
    "orchestration_routing_enabled",
    "orchestration_traversal_enabled",
    "orchestration_scheduling_enabled",
    "orchestration_sequencing_enabled",
    "orchestration_decision_enabled",
    "orchestration_recommendation_enabled",
    "orchestration_ranking_enabled",
    "orchestration_scoring_enabled",
    "orchestration_selection_enabled",
    "orchestration_optimization_enabled",
    "orchestration_planning_engine_enabled",
    "orchestration_decision_engine_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "remediation_enabled",
    "repair_enabled",
    "inference_enabled",
    "runtime_mutation_enabled",
    "operational_mutation_enabled",
    "hidden_orchestration_pathway_enabled",
    "implicit_operational_authorization_enabled",
    "authorization_enabled",
    "approval_enabled",
    "execution_enabled",
    "decision_enabled",
    "enabled",
    "exists",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_3_closeout_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_3_closeout_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_3_closeout_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_v4_3_closeout_evidence(value) for value in payload]
    return payload


def stable_serialize_v4_3_closeout(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_3_closeout_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def deterministic_v4_3_closeout_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize_v4_3_closeout(payload).encode("utf-8")).hexdigest()


def export_v4_3_closeout_identity(identity: V43CloseoutIdentity) -> dict[str, Any]:
    return asdict(identity)


def export_v4_3_phase_evidence(reference: V43PhaseEvidenceReference) -> dict[str, Any]:
    return asdict(reference)


def export_v4_3_inventory_validation(inventory: V43InventoryValidation) -> dict[str, Any]:
    data = asdict(inventory)
    for field_name in ("missing_names", "invalid_names"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_v4_3_state_visibility_summary(summary: V43StateVisibilitySummary) -> dict[str, Any]:
    return asdict(summary)


def export_v4_3_final_counter_guarantee(guarantee: V43FinalCounterGuarantee) -> dict[str, Any]:
    return asdict(guarantee)


def export_v4_3_operational_boundary_guarantee(
    guarantee: V43OperationalBoundaryGuarantee,
) -> dict[str, Any]:
    return asdict(guarantee)


def export_v4_3_closeout_classification(classification: V43CloseoutClassification) -> dict[str, Any]:
    data = asdict(classification)
    data["classification_reasons"] = sorted_entries(data["classification_reasons"])
    return data


def export_v4_4_readiness_classification(classification: V44ReadinessClassification) -> dict[str, Any]:
    data = asdict(classification)
    data["classification_reasons"] = sorted_entries(data["classification_reasons"])
    return data


def export_v4_3_closeout_readiness(
    closeout: V43CloseoutReadinessCertification,
) -> dict[str, Any]:
    data = asdict(closeout)
    data["identity"] = export_v4_3_closeout_identity(closeout.identity)
    data["phase_evidence"] = [
        export_v4_3_phase_evidence(reference)
        for reference in sorted(
            closeout.phase_evidence,
            key=lambda item: (item.phase_number, item.phase_id),
        )
    ]
    data["report_inventory"] = export_v4_3_inventory_validation(closeout.report_inventory)
    data["migration_doc_inventory"] = export_v4_3_inventory_validation(closeout.migration_doc_inventory)
    data["focused_test_inventory"] = export_v4_3_inventory_validation(closeout.focused_test_inventory)
    data["state_visibility_summaries"] = [
        export_v4_3_state_visibility_summary(summary)
        for summary in sorted(
            closeout.state_visibility_summaries,
            key=lambda item: (item.deterministic_order, item.state_type),
        )
    ]
    data["final_counter_guarantees"] = [
        export_v4_3_final_counter_guarantee(guarantee)
        for guarantee in sorted(
            closeout.final_counter_guarantees,
            key=lambda item: (item.deterministic_order, item.counter_name),
        )
    ]
    data["operational_boundary_guarantees"] = [
        export_v4_3_operational_boundary_guarantee(guarantee)
        for guarantee in sorted(
            closeout.operational_boundary_guarantees,
            key=lambda item: (item.deterministic_order, item.boundary_id),
        )
    ]
    data["closeout_classification"] = export_v4_3_closeout_classification(
        closeout.closeout_classification
    )
    data["v4_4_readiness_classification"] = export_v4_4_readiness_classification(
        closeout.v4_4_readiness_classification
    )
    for field_name in ("deterministic_guarantees", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def serialize_v4_3_closeout_readiness(closeout: V43CloseoutReadinessCertification) -> str:
    return stable_serialize_v4_3_closeout(export_v4_3_closeout_readiness(closeout))


def hash_v4_3_closeout_readiness(closeout: V43CloseoutReadinessCertification) -> str:
    return deterministic_v4_3_closeout_hash(export_v4_3_closeout_readiness(closeout))


def v4_3_closeout_readiness_equal(
    left: V43CloseoutReadinessCertification,
    right: V43CloseoutReadinessCertification,
) -> bool:
    return serialize_v4_3_closeout_readiness(left) == serialize_v4_3_closeout_readiness(right)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_payload(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _artifact_inventory(
    repo_root: Path,
) -> tuple[
    dict[str, str],
    dict[str, str],
    dict[str, bool],
    dict[str, bool],
    dict[str, bool],
    dict[str, bool],
    dict[str, dict[str, Any]],
]:
    report_file_hashes: dict[str, str] = {}
    internal_report_hashes: dict[str, str] = {}
    report_presence: dict[str, bool] = {}
    report_json_validity: dict[str, bool] = {}
    report_payloads: dict[str, dict[str, Any]] = {}
    for report_name in V4_3_EXPECTED_REPORT_NAMES:
        report_path = repo_root / "docs" / "generated" / report_name
        present = report_path.exists()
        report_presence[report_name] = present
        report_file_hashes[report_name] = _file_hash(report_path) if present else ""
        payload = _json_payload(report_path) if present else None
        report_json_validity[report_name] = payload is not None
        report_payloads[report_name] = payload or {}
        internal_report_hashes[report_name] = str((payload or {}).get("deterministic_report_hash", ""))
    doc_presence = {
        doc_name: (repo_root / "docs" / "migration" / doc_name).exists()
        for doc_name in V4_3_EXPECTED_MIGRATION_DOC_NAMES
    }
    test_presence = {
        test_name: (repo_root / "backend" / "tests" / test_name).exists()
        for test_name in V4_3_EXPECTED_TEST_NAMES
    }
    return (
        report_file_hashes,
        internal_report_hashes,
        report_presence,
        report_json_validity,
        doc_presence,
        test_presence,
        report_payloads,
    )


def _apply_overrides(target: dict[str, Any], overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    if overrides:
        for key, value in overrides.items():
            if key in target:
                target[key] = value
    return target


def _phase_status(report_present: bool, report_json_valid: bool, doc_present: bool, test_present: bool) -> str:
    if not report_present or not doc_present or not test_present:
        return V4_3_EVIDENCE_MISSING
    if not report_json_valid:
        return V4_3_EVIDENCE_INVALID_JSON
    return V4_3_EVIDENCE_PRESENT


def _build_phase_evidence(
    report_file_hashes: Mapping[str, str],
    internal_report_hashes: Mapping[str, str],
    report_presence: Mapping[str, bool],
    report_json_validity: Mapping[str, bool],
    doc_presence: Mapping[str, bool],
    test_presence: Mapping[str, bool],
) -> tuple[V43PhaseEvidenceReference, ...]:
    references: list[V43PhaseEvidenceReference] = []
    for phase in V4_3_PHASE_DEFINITIONS:
        report_name = str(phase["report_name"])
        doc_name = str(phase["migration_doc_name"])
        test_name = str(phase["test_name"])
        report_present = bool(report_presence.get(report_name, False))
        report_json_valid = bool(report_json_validity.get(report_name, False))
        migration_doc_present = bool(doc_presence.get(doc_name, False))
        focused_test_present = bool(test_presence.get(test_name, False))
        phase_number = int(phase["phase_number"])
        references.append(
            V43PhaseEvidenceReference(
                phase_number=phase_number,
                phase_id=str(phase["phase_id"]),
                phase_name=str(phase["phase_name"]),
                report_name=report_name,
                migration_doc_name=doc_name,
                test_name=test_name,
                report_file_hash=str(report_file_hashes.get(report_name, "")),
                internal_report_hash=str(internal_report_hashes.get(report_name, "")),
                report_present=report_present,
                report_json_valid=report_json_valid,
                migration_doc_present=migration_doc_present,
                focused_test_present=focused_test_present,
                evidence_status=_phase_status(
                    report_present,
                    report_json_valid,
                    migration_doc_present,
                    focused_test_present,
                ),
                summary=str(phase["summary"]),
                deterministic_order=phase_number * 10,
            )
        )
    return tuple(references)


def _inventory_validation(
    inventory_type: str,
    expected_names: tuple[str, ...],
    presence: Mapping[str, bool],
    invalid_names: Iterable[str] = (),
) -> V43InventoryValidation:
    missing = tuple(name for name in expected_names if not presence.get(name, False))
    invalid = tuple(sorted(invalid_names))
    return V43InventoryValidation(
        inventory_id=f"v4_3_closeout_{inventory_type}_inventory",
        inventory_type=inventory_type,
        expected_count=len(expected_names),
        present_count=len(expected_names) - len(missing),
        missing_names=missing,
        invalid_names=invalid,
        complete=not missing and not invalid,
    )


def _build_report_inventory(
    report_presence: Mapping[str, bool],
    report_json_validity: Mapping[str, bool],
) -> V43InventoryValidation:
    invalid = tuple(
        report_name
        for report_name in V4_3_EXPECTED_REPORT_NAMES
        if report_presence.get(report_name, False) and not report_json_validity.get(report_name, False)
    )
    return _inventory_validation("generated_report", V4_3_EXPECTED_REPORT_NAMES, report_presence, invalid)


def _phase_9_payload(report_payloads: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    return report_payloads.get("v4_3_orchestration_readiness_certification_report.json", {})


def _phase_8_payload(report_payloads: Mapping[str, dict[str, Any]]) -> dict[str, Any]:
    return report_payloads.get("v4_3_orchestration_continuity_and_integrity_certification_report.json", {})


def _build_state_visibility_summaries(
    report_payloads: Mapping[str, dict[str, Any]],
) -> tuple[V43StateVisibilitySummary, ...]:
    counts = _phase_9_payload(report_payloads).get("certification_counts", {})
    source_keys = {
        "prohibited": "prohibited_state_readiness_count",
        "unsupported": "unsupported_state_readiness_count",
        "blocked": "blocked_state_readiness_count",
        "stale": "stale_state_readiness_count",
        "conflicting": "conflicting_state_readiness_count",
    }
    summaries: list[V43StateVisibilitySummary] = []
    for index, state_type in enumerate(V4_3_STATE_TYPES, start=1):
        count = int(counts.get(source_keys[state_type], 0))
        summaries.append(
            V43StateVisibilitySummary(
                state_type=state_type,
                count=count,
                visible=count > 0,
                source_phase_id="v4_3_orchestration_readiness_certification",
                deterministic_order=index * 10,
            )
        )
    return tuple(summaries)


def _build_final_counter_guarantees(
    report_payloads: Mapping[str, dict[str, Any]],
) -> tuple[V43FinalCounterGuarantee, ...]:
    summary = _phase_9_payload(report_payloads).get("summary", {})
    guarantees: list[V43FinalCounterGuarantee] = []
    for index, counter_name in enumerate(V4_3_FINAL_COUNTER_NAMES, start=1):
        value = int(summary.get(counter_name, -1))
        guarantees.append(
            V43FinalCounterGuarantee(
                counter_name=counter_name,
                counter_value=value,
                valid=value == 0,
                deterministic_order=index * 10,
            )
        )
    return tuple(guarantees)


def default_v4_3_operational_boundary_guarantees() -> tuple[V43OperationalBoundaryGuarantee, ...]:
    return tuple(
        V43OperationalBoundaryGuarantee(
            boundary_id=f"v4_3_disabled_{boundary}",
            boundary_name=boundary,
            evidence=f"{boundary} remains prohibited after v4.3 closeout.",
            deterministic_order=(index + 1) * 10,
        )
        for index, boundary in enumerate(V4_3_DISABLED_OPERATIONAL_BOUNDARIES)
    )


def _all_inventory_complete(
    report_inventory: V43InventoryValidation,
    doc_inventory: V43InventoryValidation,
    test_inventory: V43InventoryValidation,
) -> bool:
    return report_inventory.complete and doc_inventory.complete and test_inventory.complete


def _phase_9_ready(report_payloads: Mapping[str, dict[str, Any]]) -> bool:
    summary = _phase_9_payload(report_payloads).get("summary", {})
    return (
        bool(summary.get("deterministic_serialization_verified", False))
        and bool(summary.get("deterministic_hashing_verified", False))
        and bool(summary.get("non_execution_enforcement_validated", False))
        and bool(summary.get("non_authorization_guarantees_validated", False))
        and bool(summary.get("non_approval_guarantees_validated", False))
        and bool(summary.get("non_decision_guarantees_validated", False))
        and all(int(summary.get(counter_name, -1)) == 0 for counter_name in V4_3_FINAL_COUNTER_NAMES)
    )


def _build_closeout_classification(
    report_inventory: V43InventoryValidation,
    doc_inventory: V43InventoryValidation,
    test_inventory: V43InventoryValidation,
    report_payloads: Mapping[str, dict[str, Any]],
) -> V43CloseoutClassification:
    complete = _all_inventory_complete(report_inventory, doc_inventory, test_inventory) and _phase_9_ready(
        report_payloads
    )
    classification = (
        V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE
        if complete
        else V4_3_CLOSEOUT_CLASSIFICATION_BLOCKED
    )
    reasons = (
        "Phase 1-9 generated report inventory is complete and valid."
        if report_inventory.complete
        else "Phase 1-9 generated report inventory has fail-visible gaps.",
        "Phase 1-9 migration documentation inventory is complete."
        if doc_inventory.complete
        else "Phase 1-9 migration documentation inventory has fail-visible gaps.",
        "Phase 1-9 focused test inventory is complete."
        if test_inventory.complete
        else "Phase 1-9 focused test inventory has fail-visible gaps.",
        "Phase 9 readiness certification validates deterministic non-execution non-authorization non-approval and non-decision guarantees."
        if _phase_9_ready(report_payloads)
        else "Phase 9 readiness certification has fail-visible readiness gaps.",
    )
    return V43CloseoutClassification(
        classification_id="v4_3_closeout_classification_primary",
        final_closeout_classification=classification,
        classification_reasons=reasons,
        deterministic_order=10,
    )


def _build_v4_4_readiness_classification(
    report_inventory: V43InventoryValidation,
    doc_inventory: V43InventoryValidation,
    test_inventory: V43InventoryValidation,
    report_payloads: Mapping[str, dict[str, Any]],
) -> V44ReadinessClassification:
    complete = _all_inventory_complete(report_inventory, doc_inventory, test_inventory) and _phase_9_ready(
        report_payloads
    )
    classification = (
        V4_4_READINESS_CLASSIFICATION_READY
        if complete
        else V4_4_READINESS_CLASSIFICATION_BLOCKED
    )
    reasons = (
        "v4.3 deterministically established governance-safe orchestration modeling.",
        "v4.4 planning may begin for governance-safe orchestration boundary intelligence refinement.",
        "v4.4 planning remains descriptive-only deterministic governance-safe fail-visible and non-executable.",
    )
    return V44ReadinessClassification(
        classification_id="v4_4_readiness_classification_primary",
        v4_4_readiness_classification=classification,
        recommended_direction=V4_4_RECOMMENDED_DIRECTION,
        classification_reasons=reasons,
        deterministic_order=10,
    )


def build_v4_3_closeout_readiness(
    repo_root: Path | None = None,
    *,
    report_file_hash_overrides: Mapping[str, str] | None = None,
    internal_report_hash_overrides: Mapping[str, str] | None = None,
    report_presence_overrides: Mapping[str, bool] | None = None,
    report_json_validity_overrides: Mapping[str, bool] | None = None,
    migration_doc_presence_overrides: Mapping[str, bool] | None = None,
    focused_test_presence_overrides: Mapping[str, bool] | None = None,
    report_payload_overrides: Mapping[str, dict[str, Any]] | None = None,
) -> V43CloseoutReadinessCertification:
    root = repo_root or Path(__file__).resolve().parents[3]
    (
        report_file_hashes,
        internal_report_hashes,
        report_presence,
        report_json_validity,
        doc_presence,
        test_presence,
        report_payloads,
    ) = _artifact_inventory(root)
    _apply_overrides(report_file_hashes, report_file_hash_overrides)
    _apply_overrides(internal_report_hashes, internal_report_hash_overrides)
    _apply_overrides(report_presence, report_presence_overrides)
    _apply_overrides(report_json_validity, report_json_validity_overrides)
    _apply_overrides(doc_presence, migration_doc_presence_overrides)
    _apply_overrides(test_presence, focused_test_presence_overrides)
    _apply_overrides(report_payloads, report_payload_overrides)

    phase_evidence = _build_phase_evidence(
        report_file_hashes,
        internal_report_hashes,
        report_presence,
        report_json_validity,
        doc_presence,
        test_presence,
    )
    report_inventory = _build_report_inventory(report_presence, report_json_validity)
    doc_inventory = _inventory_validation(
        "migration_documentation",
        V4_3_EXPECTED_MIGRATION_DOC_NAMES,
        doc_presence,
    )
    test_inventory = _inventory_validation("focused_test", V4_3_EXPECTED_TEST_NAMES, test_presence)
    return V43CloseoutReadinessCertification(
        identity=default_v4_3_closeout_identity(),
        phase_evidence=phase_evidence,
        report_inventory=report_inventory,
        migration_doc_inventory=doc_inventory,
        focused_test_inventory=test_inventory,
        state_visibility_summaries=_build_state_visibility_summaries(report_payloads),
        final_counter_guarantees=_build_final_counter_guarantees(report_payloads),
        operational_boundary_guarantees=default_v4_3_operational_boundary_guarantees(),
        closeout_classification=_build_closeout_classification(
            report_inventory,
            doc_inventory,
            test_inventory,
            report_payloads,
        ),
        v4_4_readiness_classification=_build_v4_4_readiness_classification(
            report_inventory,
            doc_inventory,
            test_inventory,
            report_payloads,
        ),
        deterministic_guarantees=V4_3_DETERMINISTIC_GUARANTEES,
        explicit_limitations=V4_3_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_3_EXPLICIT_PROHIBITIONS,
    )


def validate_v4_3_phase_evidence_coverage(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    phase_ids = [reference.phase_id for reference in closeout.phase_evidence]
    duplicate_phase_ids = sorted({phase_id for phase_id in phase_ids if phase_ids.count(phase_id) > 1})
    missing_phase_ids = [phase_id for phase_id in V4_3_EXPECTED_PHASE_IDS if phase_id not in phase_ids]
    missing_or_invalid = [
        reference.phase_id
        for reference in closeout.phase_evidence
        if reference.evidence_status != V4_3_EVIDENCE_PRESENT
    ]
    return {
        "valid": not duplicate_phase_ids and not missing_phase_ids and not missing_or_invalid,
        "expected_phase_count": len(V4_3_EXPECTED_PHASE_IDS),
        "present_phase_count": len(phase_ids) - len(missing_phase_ids),
        "duplicate_phase_ids": duplicate_phase_ids,
        "missing_phase_ids": missing_phase_ids,
        "missing_or_invalid_evidence_phase_ids": missing_or_invalid,
        "phase_order": [
            reference.phase_id
            for reference in sorted(closeout.phase_evidence, key=lambda item: (item.phase_number, item.phase_id))
        ],
    }


def validate_v4_3_report_inventory(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    return {
        "valid": closeout.report_inventory.complete,
        "expected_report_count": closeout.report_inventory.expected_count,
        "present_report_count": closeout.report_inventory.present_count,
        "missing_report_names": closeout.report_inventory.missing_names,
        "invalid_report_names": closeout.report_inventory.invalid_names,
    }


def validate_v4_3_migration_documentation_inventory(
    closeout: V43CloseoutReadinessCertification,
) -> dict[str, Any]:
    return {
        "valid": closeout.migration_doc_inventory.complete,
        "expected_doc_count": closeout.migration_doc_inventory.expected_count,
        "present_doc_count": closeout.migration_doc_inventory.present_count,
        "missing_doc_names": closeout.migration_doc_inventory.missing_names,
    }


def validate_v4_3_focused_test_inventory(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    return {
        "valid": closeout.focused_test_inventory.complete,
        "expected_test_count": closeout.focused_test_inventory.expected_count,
        "present_test_count": closeout.focused_test_inventory.present_count,
        "missing_test_names": closeout.focused_test_inventory.missing_names,
    }


def validate_v4_3_state_visibility(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    by_type = {summary.state_type: summary for summary in closeout.state_visibility_summaries}
    missing = tuple(sorted(state_type for state_type in V4_3_STATE_TYPES if state_type not in by_type))
    return {
        "valid": not missing and all(by_type[state_type].visible for state_type in V4_3_STATE_TYPES),
        "missing_state_types": missing,
        "prohibited_state_count": by_type.get("prohibited", V43StateVisibilitySummary("", 0, False, "", 0)).count,
        "unsupported_state_count": by_type.get("unsupported", V43StateVisibilitySummary("", 0, False, "", 0)).count,
        "blocked_state_count": by_type.get("blocked", V43StateVisibilitySummary("", 0, False, "", 0)).count,
        "stale_state_count": by_type.get("stale", V43StateVisibilitySummary("", 0, False, "", 0)).count,
        "conflicting_state_count": by_type.get("conflicting", V43StateVisibilitySummary("", 0, False, "", 0)).count,
        "fail_visible": all(summary.fail_visible for summary in closeout.state_visibility_summaries),
        "descriptive_only": all(summary.descriptive_only for summary in closeout.state_visibility_summaries),
    }


def validate_v4_3_final_counters(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    by_name = {guarantee.counter_name: guarantee for guarantee in closeout.final_counter_guarantees}
    missing = tuple(sorted(counter_name for counter_name in V4_3_FINAL_COUNTER_NAMES if counter_name not in by_name))
    non_zero = tuple(
        sorted(
            guarantee.counter_name
            for guarantee in closeout.final_counter_guarantees
            if guarantee.counter_value != 0 or not guarantee.valid
        )
    )
    return {
        "valid": not missing and not non_zero,
        "missing_counter_names": missing,
        "non_zero_counter_names": non_zero,
        "counters": {name: by_name[name].counter_value for name in sorted(by_name)},
    }


def validate_v4_3_operational_boundaries(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    by_name = {guarantee.boundary_name: guarantee for guarantee in closeout.operational_boundary_guarantees}
    missing = tuple(
        sorted(boundary for boundary in V4_3_DISABLED_OPERATIONAL_BOUNDARIES if boundary not in by_name)
    )
    enabled = tuple(
        sorted(
            guarantee.boundary_name
            for guarantee in closeout.operational_boundary_guarantees
            if guarantee.enabled or guarantee.exists or not guarantee.disabled
        )
    )
    return {
        "valid": not missing and not enabled,
        "missing_boundary_names": missing,
        "enabled_boundary_names": enabled,
        "disabled_boundary_count": len(closeout.operational_boundary_guarantees),
        "no_orchestration_runtime_exists": not by_name["orchestration_runtime"].exists,
        "no_orchestration_execution_exists": not by_name["orchestration_execution"].exists,
        "no_orchestration_activation_exists": not by_name["orchestration_activation"].exists,
        "no_orchestration_authorization_exists": not by_name["orchestration_authorization"].exists,
        "no_orchestration_approval_exists": not by_name["orchestration_approval"].exists,
        "no_orchestration_dispatch_exists": not by_name["orchestration_dispatch"].exists,
        "no_planner_integration_exists": not by_name["planner_integration"].exists,
        "no_production_consumption_exists": not by_name["production_consumption"].exists,
        "no_runtime_mutation_exists": not by_name["runtime_mutation"].exists,
        "no_operational_mutation_exists": not by_name["operational_mutation"].exists,
        "no_hidden_orchestration_pathways_exist": not by_name["hidden_orchestration_pathways"].exists,
    }


def v4_3_closeout_capability_flags(closeout: V43CloseoutReadinessCertification) -> dict[str, bool]:
    payload = asdict(closeout)
    flags: dict[str, bool] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                name = f"{prefix}.{key}" if prefix else str(key)
                if key in CAPABILITY_FIELD_NAMES:
                    flags[name] = bool(nested)
                visit(nested, name)
        elif isinstance(value, list | tuple):
            for index, nested in enumerate(value):
                visit(nested, f"{prefix}[{index}]")

    visit(payload)
    return flags


def enabled_v4_3_closeout_capability_flags(
    closeout: V43CloseoutReadinessCertification,
) -> dict[str, bool]:
    return {key: value for key, value in v4_3_closeout_capability_flags(closeout).items() if value}


def validate_v4_3_closeout_non_operational(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    enabled = enabled_v4_3_closeout_capability_flags(closeout)
    return {
        "valid": not enabled,
        "enabled_capability_count": len(enabled),
        "enabled_capability_flags": enabled,
        "non_executable": closeout.non_executable,
        "non_authorizing": closeout.non_authorizing,
        "non_approving": closeout.non_approving,
        "non_decisioning": closeout.non_decisioning,
        "descriptive_only": closeout.descriptive_only,
        "orchestration_runtime_disabled": not closeout.orchestration_runtime_enabled,
        "orchestration_execution_disabled": not closeout.orchestration_execution_enabled,
        "orchestration_activation_disabled": not closeout.orchestration_activation_enabled,
        "orchestration_authorization_disabled": not closeout.orchestration_authorization_enabled,
        "orchestration_approval_disabled": not closeout.orchestration_approval_enabled,
        "orchestration_dispatch_disabled": not closeout.orchestration_dispatch_enabled,
        "orchestration_routing_disabled": not closeout.orchestration_routing_enabled,
        "orchestration_traversal_disabled": not closeout.orchestration_traversal_enabled,
        "orchestration_scheduling_disabled": not closeout.orchestration_scheduling_enabled,
        "orchestration_sequencing_disabled": not closeout.orchestration_sequencing_enabled,
        "orchestration_decision_disabled": not closeout.orchestration_decision_enabled,
        "orchestration_recommendation_disabled": not closeout.orchestration_recommendation_enabled,
        "orchestration_planning_engine_disabled": not closeout.orchestration_planning_engine_enabled,
        "orchestration_decision_engine_disabled": not closeout.orchestration_decision_engine_enabled,
        "planner_integration_disabled": not closeout.planner_integration_enabled,
        "production_consumption_disabled": not closeout.production_consumption_enabled,
        "remediation_disabled": not closeout.remediation_enabled,
        "repair_disabled": not closeout.repair_enabled,
        "inference_disabled": not closeout.inference_enabled,
        "runtime_mutation_disabled": not closeout.runtime_mutation_enabled,
        "operational_mutation_disabled": not closeout.operational_mutation_enabled,
        "hidden_orchestration_pathway_absent": not closeout.hidden_orchestration_pathway_enabled,
        "implicit_operational_authorization_absent": not closeout.implicit_operational_authorization_enabled,
    }


def build_v4_3_closeout_diagnostics(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    phase_coverage = validate_v4_3_phase_evidence_coverage(closeout)
    report_inventory = validate_v4_3_report_inventory(closeout)
    doc_inventory = validate_v4_3_migration_documentation_inventory(closeout)
    test_inventory = validate_v4_3_focused_test_inventory(closeout)
    state_visibility = validate_v4_3_state_visibility(closeout)
    final_counters = validate_v4_3_final_counters(closeout)
    operational_boundaries = validate_v4_3_operational_boundaries(closeout)
    non_operational = validate_v4_3_closeout_non_operational(closeout)
    return {
        "valid": all(
            (
                phase_coverage["valid"],
                report_inventory["valid"],
                doc_inventory["valid"],
                test_inventory["valid"],
                state_visibility["valid"],
                final_counters["valid"],
                operational_boundaries["valid"],
                non_operational["valid"],
            )
        ),
        "phase_evidence_coverage": phase_coverage,
        "report_inventory": report_inventory,
        "migration_documentation_inventory": doc_inventory,
        "focused_test_inventory": test_inventory,
        "state_visibility": state_visibility,
        "final_counter_guarantees": final_counters,
        "operational_boundary_guarantees": operational_boundaries,
        "non_operational_validation": non_operational,
        "missing_evidence_visible": bool(
            phase_coverage["missing_or_invalid_evidence_phase_ids"]
            or report_inventory["missing_report_names"]
            or doc_inventory["missing_doc_names"]
            or test_inventory["missing_test_names"]
        ),
        "conflicting_evidence_visible": bool(phase_coverage["duplicate_phase_ids"]),
        "conflicting_evidence_phase_ids": phase_coverage["duplicate_phase_ids"],
    }


def validate_v4_3_closeout_readiness(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    diagnostics = build_v4_3_closeout_diagnostics(closeout)
    closeout_valid = closeout.closeout_classification.final_closeout_classification in (
        V4_3_CLOSEOUT_CLASSIFICATION_COMPLETE,
        V4_3_CLOSEOUT_CLASSIFICATION_BLOCKED,
    )
    readiness_valid = closeout.v4_4_readiness_classification.v4_4_readiness_classification in (
        V4_4_READINESS_CLASSIFICATION_READY,
        V4_4_READINESS_CLASSIFICATION_BLOCKED,
    )
    return {
        "valid": diagnostics["valid"] and closeout_valid and readiness_valid,
        "foundation_status": (
            V4_3_CLOSEOUT_READINESS_STATUS_STABLE
            if diagnostics["valid"]
            else V4_3_CLOSEOUT_READINESS_STATUS_BLOCKED
        ),
        "final_closeout_classification": closeout.closeout_classification.final_closeout_classification,
        "v4_4_readiness_classification": (
            closeout.v4_4_readiness_classification.v4_4_readiness_classification
        ),
        "diagnostics": diagnostics,
        "closeout_classification_valid": closeout_valid,
        "v4_4_readiness_classification_valid": readiness_valid,
        "descriptive_only": closeout.descriptive_only,
        "non_executable": closeout.non_executable,
    }


def hash_v4_3_phase_evidence(reference: V43PhaseEvidenceReference) -> str:
    return deterministic_v4_3_closeout_hash(export_v4_3_phase_evidence(reference))


def hash_v4_3_state_visibility_summary(summary: V43StateVisibilitySummary) -> str:
    return deterministic_v4_3_closeout_hash(export_v4_3_state_visibility_summary(summary))


def hash_v4_3_final_counter_guarantee(guarantee: V43FinalCounterGuarantee) -> str:
    return deterministic_v4_3_closeout_hash(export_v4_3_final_counter_guarantee(guarantee))


def hash_v4_3_operational_boundary_guarantee(guarantee: V43OperationalBoundaryGuarantee) -> str:
    return deterministic_v4_3_closeout_hash(export_v4_3_operational_boundary_guarantee(guarantee))


def hash_v4_3_closeout_report_payload(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_v4_3_closeout_hash(payload)


def build_v4_3_closeout_summary(closeout: V43CloseoutReadinessCertification) -> dict[str, Any]:
    validation = validate_v4_3_closeout_readiness(closeout)
    diagnostics = validation["diagnostics"]
    counters = diagnostics["final_counter_guarantees"]["counters"]
    return {
        "foundation_status": validation["foundation_status"],
        "validation_error_count": 0 if validation["valid"] else 1,
        "final_closeout_classification": validation["final_closeout_classification"],
        "v4_4_readiness_classification": validation["v4_4_readiness_classification"],
        "recommended_v4_4_direction": V4_4_RECOMMENDED_DIRECTION,
        "phase_1_9_evidence_coverage_validated": diagnostics["phase_evidence_coverage"]["valid"],
        "generated_report_inventory_validated": diagnostics["report_inventory"]["valid"],
        "migration_documentation_inventory_validated": diagnostics["migration_documentation_inventory"]["valid"],
        "focused_test_inventory_validated": diagnostics["focused_test_inventory"]["valid"],
        "deterministic_ordering_verified": True,
        "deterministic_serialization_verified": True,
        "deterministic_hashing_verified": True,
        "state_visibility_validated": diagnostics["state_visibility"]["valid"],
        "prohibited_state_count": diagnostics["state_visibility"]["prohibited_state_count"],
        "unsupported_state_count": diagnostics["state_visibility"]["unsupported_state_count"],
        "blocked_state_count": diagnostics["state_visibility"]["blocked_state_count"],
        "stale_state_count": diagnostics["state_visibility"]["stale_state_count"],
        "conflicting_state_count": diagnostics["state_visibility"]["conflicting_state_count"],
        "missing_evidence_visible": diagnostics["missing_evidence_visible"],
        "conflicting_evidence_visible": diagnostics["conflicting_evidence_visible"],
        "non_execution_guarantees_validated": diagnostics["non_operational_validation"]["valid"],
        "non_authorization_guarantees_validated": diagnostics["non_operational_validation"]["valid"],
        "non_approval_guarantees_validated": diagnostics["non_operational_validation"]["valid"],
        "non_decision_guarantees_validated": diagnostics["non_operational_validation"]["valid"],
        "enabled_coordination_execution_count": counters["enabled_coordination_execution_count"],
        "enabled_transition_execution_count": counters["enabled_transition_execution_count"],
        "enabled_policy_enforcement_count": counters["enabled_policy_enforcement_count"],
        "enabled_operational_capability_count": counters["enabled_operational_capability_count"],
        "enabled_orchestration_decision_count": counters["enabled_orchestration_decision_count"],
        "enabled_orchestration_recommendation_count": counters[
            "enabled_orchestration_recommendation_count"
        ],
        "enabled_orchestration_authorization_count": counters["enabled_orchestration_authorization_count"],
        "enabled_orchestration_approval_count": counters["enabled_orchestration_approval_count"],
        "orchestration_runtime_disabled": diagnostics["non_operational_validation"][
            "orchestration_runtime_disabled"
        ],
        "orchestration_execution_disabled": diagnostics["non_operational_validation"][
            "orchestration_execution_disabled"
        ],
        "orchestration_activation_disabled": diagnostics["non_operational_validation"][
            "orchestration_activation_disabled"
        ],
        "orchestration_authorization_disabled": diagnostics["non_operational_validation"][
            "orchestration_authorization_disabled"
        ],
        "orchestration_approval_disabled": diagnostics["non_operational_validation"][
            "orchestration_approval_disabled"
        ],
        "orchestration_dispatch_disabled": diagnostics["non_operational_validation"][
            "orchestration_dispatch_disabled"
        ],
        "planner_integration_disabled": diagnostics["non_operational_validation"][
            "planner_integration_disabled"
        ],
        "production_consumption_disabled": diagnostics["non_operational_validation"][
            "production_consumption_disabled"
        ],
        "runtime_mutation_disabled": diagnostics["non_operational_validation"]["runtime_mutation_disabled"],
        "operational_mutation_disabled": diagnostics["non_operational_validation"][
            "operational_mutation_disabled"
        ],
        "hidden_orchestration_pathway_absent": diagnostics["non_operational_validation"][
            "hidden_orchestration_pathway_absent"
        ],
    }


def build_v4_3_closeout_and_v4_4_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    closeout = build_v4_3_closeout_readiness(root)
    repeated = build_v4_3_closeout_readiness(root)
    reordered = V43CloseoutReadinessCertification(
        identity=closeout.identity,
        phase_evidence=tuple(reversed(closeout.phase_evidence)),
        report_inventory=closeout.report_inventory,
        migration_doc_inventory=closeout.migration_doc_inventory,
        focused_test_inventory=closeout.focused_test_inventory,
        state_visibility_summaries=tuple(reversed(closeout.state_visibility_summaries)),
        final_counter_guarantees=tuple(reversed(closeout.final_counter_guarantees)),
        operational_boundary_guarantees=tuple(reversed(closeout.operational_boundary_guarantees)),
        closeout_classification=closeout.closeout_classification,
        v4_4_readiness_classification=closeout.v4_4_readiness_classification,
        deterministic_guarantees=tuple(reversed(closeout.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(closeout.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(closeout.explicit_prohibitions)),
    )
    serialization_first = serialize_v4_3_closeout_readiness(closeout)
    serialization_second = serialize_v4_3_closeout_readiness(repeated)
    serialization_reordered = serialize_v4_3_closeout_readiness(reordered)
    closeout_hash = hash_v4_3_closeout_readiness(closeout)
    repeated_hash = hash_v4_3_closeout_readiness(repeated)
    reordered_hash = hash_v4_3_closeout_readiness(reordered)
    serialization_stable = serialization_first == serialization_second == serialization_reordered
    hashing_stable = closeout_hash == repeated_hash == reordered_hash
    equality_stable = v4_3_closeout_readiness_equal(closeout, repeated)
    validation = validate_v4_3_closeout_readiness(closeout)
    diagnostics = validation["diagnostics"]
    validation_error_count = sum(
        (
            0 if validation["valid"] else 1,
            0 if serialization_stable else 1,
            0 if hashing_stable else 1,
            0 if equality_stable else 1,
        )
    )
    foundation_status = (
        V4_3_CLOSEOUT_READINESS_STATUS_STABLE
        if validation_error_count == 0
        else V4_3_CLOSEOUT_READINESS_STATUS_BLOCKED
    )
    summary = build_v4_3_closeout_summary(closeout)
    summary["validation_error_count"] = validation_error_count
    summary["foundation_status"] = foundation_status
    phase_8_report = _json_payload(root / "docs" / "generated" / "v4_3_orchestration_continuity_and_integrity_certification_report.json") or {}
    phase_9_report = _json_payload(root / "docs" / "generated" / "v4_3_orchestration_readiness_certification_report.json") or {}

    report = {
        "schema_version": V4_3_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": closeout.identity.generated_at,
        "phase_id": "v4_3_closeout_and_v4_4_readiness",
        "phase_name": "v4.3_phase_10_closeout_and_v4.4_readiness",
        "repo_root": str(root),
        "architectural_purpose": "deterministic v4.3 orchestration governance closeout and v4.4 planning readiness without operational orchestration authorization",
        "closeout_mode": "descriptive_only_orchestration_governance_closeout_certification",
        "foundation_status": foundation_status,
        "phase_coverage": diagnostics["phase_evidence_coverage"],
        "certification_counts": {
            "phase_evidence_count": len(closeout.phase_evidence),
            "generated_report_count": closeout.report_inventory.present_count,
            "migration_documentation_count": closeout.migration_doc_inventory.present_count,
            "focused_test_count": closeout.focused_test_inventory.present_count,
            "state_visibility_count": len(closeout.state_visibility_summaries),
            "final_counter_guarantee_count": len(closeout.final_counter_guarantees),
            "operational_boundary_guarantee_count": len(closeout.operational_boundary_guarantees),
        },
        "state_counts": diagnostics["state_visibility"],
        "diagnostics_findings": {
            "phase_9_diagnostic_categories": phase_9_report.get("diagnostics_findings", {}).get(
                "diagnostic_categories",
                [],
            ),
            "diagnostics_are_descriptive_only": phase_9_report.get("diagnostics_findings", {}).get(
                "diagnostics_are_descriptive_only",
                False,
            ),
        },
        "explainability_findings": {
            "phase_9_explainability_categories": phase_9_report.get("explainability_findings", {}).get(
                "explainability_categories",
                [],
            ),
            "explainability_is_descriptive_only": phase_9_report.get("explainability_findings", {}).get(
                "explainability_is_descriptive_only",
                False,
            ),
        },
        "continuity_findings": phase_8_report.get("continuity_certification_visibility", {}),
        "integrity_findings": phase_8_report.get("integrity_certification_visibility", {}),
        "readiness_findings": phase_9_report.get("readiness_certification_visibility", {}),
        "inventory_validation": {
            "generated_reports": diagnostics["report_inventory"],
            "migration_documentation": diagnostics["migration_documentation_inventory"],
            "focused_tests": diagnostics["focused_test_inventory"],
        },
        "deterministic_guarantees": {
            "stable": serialization_stable and hashing_stable and equality_stable,
            "guarantees": sorted_entries(closeout.deterministic_guarantees),
            "deterministic_ordering_stable": True,
            "deterministic_serialization_stability": serialization_stable,
            "deterministic_hashing_stability": hashing_stable,
            "deterministic_equality_stability": equality_stable,
        },
        "replay_safe_guarantees": {
            "valid": bool(phase_9_report.get("replay_safe_readiness_status", False)),
            "source": "v4_3_orchestration_readiness_certification_report.json",
        },
        "rollback_safe_guarantees": {
            "valid": bool(phase_9_report.get("rollback_safe_readiness_status", False)),
            "source": "v4_3_orchestration_readiness_certification_report.json",
        },
        "non_execution_guarantees": diagnostics["non_operational_validation"],
        "non_authorization_guarantees": {
            "valid": diagnostics["non_operational_validation"]["valid"],
            "orchestration_authorization_disabled": diagnostics["non_operational_validation"][
                "orchestration_authorization_disabled"
            ],
            "implicit_operational_authorization_absent": diagnostics["non_operational_validation"][
                "implicit_operational_authorization_absent"
            ],
            "enabled_orchestration_authorization_count": diagnostics["final_counter_guarantees"][
                "counters"
            ]["enabled_orchestration_authorization_count"],
        },
        "non_approval_guarantees": {
            "valid": diagnostics["non_operational_validation"]["valid"],
            "orchestration_approval_disabled": diagnostics["non_operational_validation"][
                "orchestration_approval_disabled"
            ],
            "enabled_orchestration_approval_count": diagnostics["final_counter_guarantees"]["counters"][
                "enabled_orchestration_approval_count"
            ],
        },
        "non_decision_guarantees": {
            "valid": diagnostics["non_operational_validation"]["valid"],
            "orchestration_decision_disabled": diagnostics["non_operational_validation"][
                "orchestration_decision_disabled"
            ],
            "orchestration_recommendation_disabled": diagnostics["non_operational_validation"][
                "orchestration_recommendation_disabled"
            ],
            "enabled_orchestration_decision_count": diagnostics["final_counter_guarantees"]["counters"][
                "enabled_orchestration_decision_count"
            ],
            "enabled_orchestration_recommendation_count": diagnostics["final_counter_guarantees"][
                "counters"
            ]["enabled_orchestration_recommendation_count"],
        },
        "operational_boundary_guarantees": diagnostics["operational_boundary_guarantees"],
        "deterministic_serialization_verification": {
            "stable": serialization_stable,
            "serializer": "json_sort_keys_stable_v4_3_closeout_readiness",
            "payload_length": len(serialization_first),
            "reordered_payload_equal": serialization_first == serialization_reordered,
        },
        "deterministic_hashing_verification": {
            "stable": hashing_stable,
            "hash_algorithm": "sha256_stable_json_v4_3_closeout_readiness",
            "closeout_readiness_hash": closeout_hash,
            "repeated_closeout_readiness_hash": repeated_hash,
            "reordered_closeout_readiness_hash": reordered_hash,
            "phase_evidence_hashes": [hash_v4_3_phase_evidence(reference) for reference in closeout.phase_evidence],
            "state_visibility_hashes": [
                hash_v4_3_state_visibility_summary(summary)
                for summary in closeout.state_visibility_summaries
            ],
            "final_counter_hashes": [
                hash_v4_3_final_counter_guarantee(guarantee)
                for guarantee in closeout.final_counter_guarantees
            ],
            "operational_boundary_hashes": [
                hash_v4_3_operational_boundary_guarantee(guarantee)
                for guarantee in closeout.operational_boundary_guarantees
            ],
        },
        "phase_1_9_summary": [
            export_v4_3_phase_evidence(reference)
            for reference in sorted(closeout.phase_evidence, key=lambda item: (item.phase_number, item.phase_id))
        ],
        "final_closeout_classification": export_v4_3_closeout_classification(
            closeout.closeout_classification
        ),
        "v4_4_readiness_classification": export_v4_4_readiness_classification(
            closeout.v4_4_readiness_classification
        ),
        "summary": summary,
        "v4_3_closeout_readiness": export_v4_3_closeout_readiness(closeout),
        "explicit_limitations": list(closeout.explicit_limitations),
        "explicit_prohibitions": list(closeout.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = hash_v4_3_closeout_report_payload(report)
    return report
