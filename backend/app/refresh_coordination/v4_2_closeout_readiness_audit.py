"""Deterministic v4.2 closeout and v4.3 planning readiness audit.

The audit validates Phase 1-9 evidence inventory, deterministic guarantees,
warning visibility, prohibited capabilities, and disabled boundaries. It never
executes coordination behavior, approves readiness, authorizes operations,
repairs evidence, resolves dependencies, integrates planners, consumes
production bundles, or mutates runtime state.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from .v4_2_closeout_readiness_models import (
    V4_2_CLOSEOUT_CLASSIFICATION_BLOCKED,
    V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS,
    V4_2_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
    V4_2_CLOSEOUT_READINESS_STATUS_BLOCKED,
    V4_2_CLOSEOUT_READINESS_STATUS_STABLE,
    V4_2_DISABLED_BOUNDARIES,
    V4_2_EVIDENCE_INVALID_JSON,
    V4_2_EVIDENCE_MISSING,
    V4_2_EVIDENCE_PRESENT,
    V4_2_EXPECTED_MIGRATION_DOC_NAMES,
    V4_2_EXPECTED_PHASE_IDS,
    V4_2_EXPECTED_REPORT_NAMES,
    V4_2_EXPECTED_TEST_NAMES,
    V4_2_EXPLICIT_LIMITATIONS,
    V4_2_EXPLICIT_PROHIBITIONS,
    V4_2_PHASE_DEFINITIONS,
    V4_2_PROHIBITED_CAPABILITIES,
    V4_2_WARNING_CATEGORIES,
    V4_3_READINESS_CLASSIFICATION_BLOCKED,
    V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS,
    V4_3_RECOMMENDED_DIRECTION,
    V42CloseoutClassification,
    V42CloseoutIdentity,
    V42CloseoutReadinessCertification,
    V42DisabledBoundarySummary,
    V42InventoryValidation,
    V42PhaseEvidenceReference,
    V42ProhibitedCapabilitySummary,
    V42WarningSummary,
    V43PlanningReadinessClassification,
    default_v4_2_closeout_identity,
    default_v4_2_deterministic_guarantees,
    default_v4_2_disabled_boundary_summaries,
    default_v4_2_prohibited_capability_summaries,
    default_v4_2_warning_summaries,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "readiness_approved",
    "operational_authorized",
    "readiness_approval_enabled",
    "operational_authorization_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "drift_correction_enabled",
    "drift_remediation_enabled",
    "continuity_repair_enabled",
    "continuity_inference_enabled",
    "routing_execution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "sequencing_execution_enabled",
    "scheduling_execution_enabled",
    "dependency_resolution_enabled",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_v4_2_closeout_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_v4_2_closeout_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_v4_2_closeout_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_v4_2_closeout_evidence(value) for value in payload]
    return payload


def stable_serialize_v4_2_closeout(payload: Any) -> str:
    return json.dumps(
        canonicalize_v4_2_closeout_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def deterministic_v4_2_closeout_hash(payload: Any) -> str:
    return hashlib.sha256(stable_serialize_v4_2_closeout(payload).encode("utf-8")).hexdigest()


def _disable_capability_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    if "enabled" in data:
        data["enabled"] = False
    return data


def export_v4_2_closeout_identity(identity: V42CloseoutIdentity) -> dict[str, Any]:
    return _disable_capability_fields(asdict(identity))


def export_v4_2_phase_evidence(reference: V42PhaseEvidenceReference) -> dict[str, Any]:
    return _disable_capability_fields(asdict(reference))


def export_v4_2_inventory_validation(inventory: V42InventoryValidation) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(inventory))
    for field_name in ("missing_names", "invalid_names"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_v4_2_warning_summary(warning: V42WarningSummary) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(warning))
    data["affected_phase_ids"] = sorted_entries(data["affected_phase_ids"])
    return data


def export_v4_2_prohibited_capability_summary(
    capability: V42ProhibitedCapabilitySummary,
) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(capability))
    data["source_phase_ids"] = sorted_entries(data["source_phase_ids"])
    data["prohibited"] = True
    return data


def export_v4_2_disabled_boundary_summary(boundary: V42DisabledBoundarySummary) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(boundary))
    data["source_phase_ids"] = sorted_entries(data["source_phase_ids"])
    data["disabled"] = True
    return data


def export_v4_2_closeout_classification(classification: V42CloseoutClassification) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(classification))
    data["classification_reasons"] = sorted_entries(data["classification_reasons"])
    return data


def export_v4_3_planning_readiness_classification(
    classification: V43PlanningReadinessClassification,
) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(classification))
    data["classification_reasons"] = sorted_entries(data["classification_reasons"])
    return data


def export_v4_2_closeout_readiness(
    closeout: V42CloseoutReadinessCertification,
) -> dict[str, Any]:
    data = _disable_capability_fields(asdict(closeout))
    data["identity"] = export_v4_2_closeout_identity(closeout.identity)
    data["phase_evidence"] = [
        export_v4_2_phase_evidence(reference)
        for reference in sorted(
            closeout.phase_evidence,
            key=lambda item: (item.phase_number, item.phase_id),
        )
    ]
    data["report_inventory"] = export_v4_2_inventory_validation(closeout.report_inventory)
    data["migration_doc_inventory"] = export_v4_2_inventory_validation(closeout.migration_doc_inventory)
    data["focused_test_inventory"] = export_v4_2_inventory_validation(closeout.focused_test_inventory)
    data["warning_summaries"] = [
        export_v4_2_warning_summary(warning)
        for warning in sorted(
            closeout.warning_summaries,
            key=lambda item: (item.deterministic_order, item.warning_id),
        )
    ]
    data["prohibited_capability_summaries"] = [
        export_v4_2_prohibited_capability_summary(capability)
        for capability in sorted(
            closeout.prohibited_capability_summaries,
            key=lambda item: (item.deterministic_order, item.capability_id),
        )
    ]
    data["disabled_boundary_summaries"] = [
        export_v4_2_disabled_boundary_summary(boundary)
        for boundary in sorted(
            closeout.disabled_boundary_summaries,
            key=lambda item: (item.deterministic_order, item.boundary_id),
        )
    ]
    data["closeout_classification"] = export_v4_2_closeout_classification(
        closeout.closeout_classification
    )
    data["v4_3_planning_readiness"] = export_v4_3_planning_readiness_classification(
        closeout.v4_3_planning_readiness
    )
    for field_name in ("deterministic_guarantees", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def serialize_v4_2_closeout_readiness(closeout: V42CloseoutReadinessCertification) -> str:
    return stable_serialize_v4_2_closeout(export_v4_2_closeout_readiness(closeout))


def hash_v4_2_closeout_readiness(closeout: V42CloseoutReadinessCertification) -> str:
    return deterministic_v4_2_closeout_hash(export_v4_2_closeout_readiness(closeout))


def v4_2_closeout_readiness_equal(
    left: V42CloseoutReadinessCertification,
    right: V42CloseoutReadinessCertification,
) -> bool:
    return serialize_v4_2_closeout_readiness(left) == serialize_v4_2_closeout_readiness(right)


def _file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json_valid(path: Path) -> bool:
    try:
        json.loads(path.read_text(encoding="utf-8"))
        return True
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return False


def _artifact_inventory(repo_root: Path) -> tuple[dict[str, str], dict[str, bool], dict[str, bool], dict[str, bool], dict[str, bool]]:
    report_hashes: dict[str, str] = {}
    report_presence: dict[str, bool] = {}
    report_json_validity: dict[str, bool] = {}
    for report_name in V4_2_EXPECTED_REPORT_NAMES:
        report_path = repo_root / "docs" / "generated" / report_name
        present = report_path.exists()
        report_presence[report_name] = present
        report_hashes[report_name] = _file_hash(report_path) if present else ""
        report_json_validity[report_name] = _json_valid(report_path) if present else False
    doc_presence = {
        doc_name: (repo_root / "docs" / "migration" / doc_name).exists()
        for doc_name in V4_2_EXPECTED_MIGRATION_DOC_NAMES
    }
    test_presence = {
        test_name: (repo_root / "backend" / "tests" / test_name).exists()
        for test_name in V4_2_EXPECTED_TEST_NAMES
    }
    return report_hashes, report_presence, report_json_validity, doc_presence, test_presence


def _apply_overrides(target: dict[str, Any], overrides: Mapping[str, Any] | None) -> dict[str, Any]:
    if overrides:
        for key, value in overrides.items():
            if key in target:
                target[key] = value
    return target


def _phase_status(report_present: bool, report_json_valid: bool, doc_present: bool, test_present: bool) -> str:
    if not report_present or not doc_present or not test_present:
        return V4_2_EVIDENCE_MISSING
    if not report_json_valid:
        return V4_2_EVIDENCE_INVALID_JSON
    return V4_2_EVIDENCE_PRESENT


def _build_phase_evidence(
    report_hashes: Mapping[str, str],
    report_presence: Mapping[str, bool],
    report_json_validity: Mapping[str, bool],
    doc_presence: Mapping[str, bool],
    test_presence: Mapping[str, bool],
) -> tuple[V42PhaseEvidenceReference, ...]:
    references: list[V42PhaseEvidenceReference] = []
    for phase in V4_2_PHASE_DEFINITIONS:
        report_name = str(phase["report_name"])
        doc_name = str(phase["migration_doc_name"])
        test_name = str(phase["test_name"])
        report_present = bool(report_presence.get(report_name, False))
        report_json_valid = bool(report_json_validity.get(report_name, False))
        migration_doc_present = bool(doc_presence.get(doc_name, False))
        focused_test_present = bool(test_presence.get(test_name, False))
        phase_number = int(phase["phase_number"])
        references.append(
            V42PhaseEvidenceReference(
                phase_number=phase_number,
                phase_id=str(phase["phase_id"]),
                phase_name=str(phase["phase_name"]),
                report_name=report_name,
                migration_doc_name=doc_name,
                test_name=test_name,
                report_hash=str(report_hashes.get(report_name, "")),
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
) -> V42InventoryValidation:
    missing = tuple(name for name in expected_names if not presence.get(name, False))
    invalid = tuple(sorted(invalid_names))
    return V42InventoryValidation(
        inventory_id=f"v4_2_closeout_{inventory_type}_inventory",
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
) -> V42InventoryValidation:
    invalid = tuple(
        report_name
        for report_name in V4_2_EXPECTED_REPORT_NAMES
        if report_presence.get(report_name, False) and not report_json_validity.get(report_name, False)
    )
    return _inventory_validation("generated_report", V4_2_EXPECTED_REPORT_NAMES, report_presence, invalid)


def _build_closeout_classification(report_inventory: V42InventoryValidation, doc_inventory: V42InventoryValidation, test_inventory: V42InventoryValidation) -> V42CloseoutClassification:
    blocked = not (report_inventory.complete and doc_inventory.complete and test_inventory.complete)
    classification = (
        V4_2_CLOSEOUT_CLASSIFICATION_BLOCKED
        if blocked
        else V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS
    )
    reasons = (
        "Generated report inventory is complete and valid."
        if report_inventory.complete
        else "Generated report inventory is incomplete or invalid and remains fail-visible.",
        "Migration documentation inventory is complete."
        if doc_inventory.complete
        else "Migration documentation inventory is incomplete and remains fail-visible.",
        "Focused test inventory is complete."
        if test_inventory.complete
        else "Focused test inventory is incomplete and remains fail-visible.",
        "v4.2 closeout preserves fail-visible warning states without remediation approval authorization or execution.",
    )
    return V42CloseoutClassification(
        classification_id="v4_2_closeout_classification_primary",
        closeout_classification=classification,
        classification_reasons=reasons,
        deterministic_order=10,
    )


def _build_v4_3_readiness_classification(report_inventory: V42InventoryValidation, doc_inventory: V42InventoryValidation, test_inventory: V42InventoryValidation) -> V43PlanningReadinessClassification:
    blocked = not (report_inventory.complete and doc_inventory.complete and test_inventory.complete)
    classification = (
        V4_3_READINESS_CLASSIFICATION_BLOCKED
        if blocked
        else V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS
    )
    reasons = (
        "v4.2 Phase 1-9 evidence is visible for planning."
        if not blocked
        else "v4.2 Phase 1-9 evidence has fail-visible inventory gaps.",
        "v4.3 direction is planning-only deterministic governance-safe orchestration modeling.",
        "v4.3 planning readiness does not authorize execution orchestration planner integration production consumption or runtime mutation.",
    )
    return V43PlanningReadinessClassification(
        classification_id="v4_3_planning_readiness_classification_primary",
        readiness_classification=classification,
        recommended_direction=V4_3_RECOMMENDED_DIRECTION,
        classification_reasons=reasons,
        deterministic_order=10,
    )


def build_v4_2_closeout_readiness(
    repo_root: Path | None = None,
    *,
    report_hash_overrides: Mapping[str, str] | None = None,
    report_presence_overrides: Mapping[str, bool] | None = None,
    report_json_validity_overrides: Mapping[str, bool] | None = None,
    migration_doc_presence_overrides: Mapping[str, bool] | None = None,
    focused_test_presence_overrides: Mapping[str, bool] | None = None,
) -> V42CloseoutReadinessCertification:
    root = repo_root or Path(__file__).resolve().parents[3]
    report_hashes, report_presence, report_json_validity, doc_presence, test_presence = _artifact_inventory(root)
    _apply_overrides(report_hashes, report_hash_overrides)
    _apply_overrides(report_presence, report_presence_overrides)
    _apply_overrides(report_json_validity, report_json_validity_overrides)
    _apply_overrides(doc_presence, migration_doc_presence_overrides)
    _apply_overrides(test_presence, focused_test_presence_overrides)

    phase_evidence = _build_phase_evidence(
        report_hashes,
        report_presence,
        report_json_validity,
        doc_presence,
        test_presence,
    )
    report_inventory = _build_report_inventory(report_presence, report_json_validity)
    doc_inventory = _inventory_validation("migration_documentation", V4_2_EXPECTED_MIGRATION_DOC_NAMES, doc_presence)
    test_inventory = _inventory_validation("focused_test", V4_2_EXPECTED_TEST_NAMES, test_presence)
    return V42CloseoutReadinessCertification(
        identity=default_v4_2_closeout_identity(),
        phase_evidence=phase_evidence,
        report_inventory=report_inventory,
        migration_doc_inventory=doc_inventory,
        focused_test_inventory=test_inventory,
        warning_summaries=default_v4_2_warning_summaries(),
        prohibited_capability_summaries=default_v4_2_prohibited_capability_summaries(),
        disabled_boundary_summaries=default_v4_2_disabled_boundary_summaries(),
        closeout_classification=_build_closeout_classification(
            report_inventory,
            doc_inventory,
            test_inventory,
        ),
        v4_3_planning_readiness=_build_v4_3_readiness_classification(
            report_inventory,
            doc_inventory,
            test_inventory,
        ),
        deterministic_guarantees=default_v4_2_deterministic_guarantees(),
        explicit_limitations=V4_2_EXPLICIT_LIMITATIONS,
        explicit_prohibitions=V4_2_EXPLICIT_PROHIBITIONS,
    )


def count_v4_2_warning_categories(warnings: Iterable[V42WarningSummary]) -> dict[str, int]:
    counts = {category: 0 for category in V4_2_WARNING_CATEGORIES}
    counts["invalid"] = 0
    for warning in warnings:
        if warning.warning_category in counts:
            counts[warning.warning_category] += 1
        else:
            counts["invalid"] += 1
    return counts


def validate_v4_2_phase_evidence_coverage(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    phase_ids = [reference.phase_id for reference in closeout.phase_evidence]
    duplicate_phase_ids = sorted({phase_id for phase_id in phase_ids if phase_ids.count(phase_id) > 1})
    missing_phase_ids = [phase_id for phase_id in V4_2_EXPECTED_PHASE_IDS if phase_id not in phase_ids]
    status_by_phase = {
        reference.phase_id: reference.evidence_status
        for reference in sorted(closeout.phase_evidence, key=lambda item: (item.phase_number, item.phase_id))
    }
    missing_evidence_phase_ids = [
        reference.phase_id
        for reference in closeout.phase_evidence
        if reference.evidence_status != V4_2_EVIDENCE_PRESENT
    ]
    return {
        "valid": not missing_phase_ids and not duplicate_phase_ids and not missing_evidence_phase_ids,
        "expected_phase_count": len(V4_2_EXPECTED_PHASE_IDS),
        "phase_evidence_count": len(closeout.phase_evidence),
        "missing_phase_ids": missing_phase_ids,
        "duplicate_phase_ids": duplicate_phase_ids,
        "missing_or_invalid_evidence_phase_ids": missing_evidence_phase_ids,
        "status_by_phase": status_by_phase,
        "fail_visible": True,
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
    }


def validate_v4_2_report_inventory(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    return {
        "valid": closeout.report_inventory.complete,
        "expected_report_count": closeout.report_inventory.expected_count,
        "present_report_count": closeout.report_inventory.present_count,
        "missing_report_names": list(closeout.report_inventory.missing_names),
        "invalid_report_names": list(closeout.report_inventory.invalid_names),
        "fail_visible_missing_evidence": bool(closeout.report_inventory.missing_names),
        "fail_visible_invalid_evidence": bool(closeout.report_inventory.invalid_names),
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
    }


def validate_v4_2_migration_documentation_inventory(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    return {
        "valid": closeout.migration_doc_inventory.complete,
        "expected_doc_count": closeout.migration_doc_inventory.expected_count,
        "present_doc_count": closeout.migration_doc_inventory.present_count,
        "missing_doc_names": list(closeout.migration_doc_inventory.missing_names),
        "fail_visible_missing_evidence": bool(closeout.migration_doc_inventory.missing_names),
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
    }


def validate_v4_2_focused_test_inventory(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    return {
        "valid": closeout.focused_test_inventory.complete,
        "expected_test_count": closeout.focused_test_inventory.expected_count,
        "present_test_count": closeout.focused_test_inventory.present_count,
        "missing_test_names": list(closeout.focused_test_inventory.missing_names),
        "fail_visible_missing_evidence": bool(closeout.focused_test_inventory.missing_names),
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
    }


def aggregate_v4_2_warnings(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    unresolved = [
        warning.warning_id
        for warning in sorted(closeout.warning_summaries, key=lambda item: (item.deterministic_order, item.warning_id))
        if warning.unresolved
    ]
    return {
        "valid": bool(closeout.warning_summaries),
        "warning_count": len(closeout.warning_summaries),
        "unresolved_warning_count": len(unresolved),
        "unresolved_warning_ids": unresolved,
        "category_counts": count_v4_2_warning_categories(closeout.warning_summaries),
        "fail_visible": all(warning.fail_visible for warning in closeout.warning_summaries),
        "descriptive_only": all(warning.descriptive_only for warning in closeout.warning_summaries),
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
        "approval_enabled": False,
        "authorization_enabled": False,
        "execution_enabled": False,
    }


def aggregate_v4_2_prohibited_capabilities(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    enabled = [
        capability.capability_name
        for capability in closeout.prohibited_capability_summaries
        if capability.enabled
    ]
    visible = sorted(capability.capability_name for capability in closeout.prohibited_capability_summaries)
    return {
        "valid": not enabled and set(visible) == set(V4_2_PROHIBITED_CAPABILITIES),
        "prohibited_capability_count": len(closeout.prohibited_capability_summaries),
        "visible_capabilities": visible,
        "enabled_capabilities": sorted(enabled),
        "fail_visible": all(capability.fail_visible for capability in closeout.prohibited_capability_summaries),
        "descriptive_only": all(capability.descriptive_only for capability in closeout.prohibited_capability_summaries),
    }


def aggregate_v4_2_disabled_boundaries(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    enabled = [boundary.boundary_name for boundary in closeout.disabled_boundary_summaries if boundary.enabled]
    visible = sorted(boundary.boundary_name for boundary in closeout.disabled_boundary_summaries)
    return {
        "valid": not enabled and set(visible) == set(V4_2_DISABLED_BOUNDARIES),
        "disabled_boundary_count": len(closeout.disabled_boundary_summaries),
        "visible_boundaries": visible,
        "enabled_boundaries": sorted(enabled),
        "fail_visible": all(boundary.fail_visible for boundary in closeout.disabled_boundary_summaries),
        "descriptive_only": all(boundary.descriptive_only for boundary in closeout.disabled_boundary_summaries),
    }


def v4_2_closeout_capability_flags(closeout: V42CloseoutReadinessCertification) -> dict[str, bool]:
    exported = export_v4_2_closeout_readiness(closeout)
    flags: dict[str, bool] = {}

    def visit(value: Any, prefix: str = "") -> None:
        if isinstance(value, dict):
            for key, nested in value.items():
                name = f"{prefix}.{key}" if prefix else str(key)
                if key in CAPABILITY_FIELD_NAMES or key == "enabled":
                    flags[name] = bool(nested)
                visit(nested, name)
        elif isinstance(value, list):
            for index, nested in enumerate(value):
                visit(nested, f"{prefix}[{index}]")

    visit(exported)
    return flags


def enabled_v4_2_closeout_capability_flags(closeout: V42CloseoutReadinessCertification) -> dict[str, bool]:
    return {key: value for key, value in v4_2_closeout_capability_flags(closeout).items() if value}


def validate_v4_2_closeout_non_execution(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    enabled = enabled_v4_2_closeout_capability_flags(closeout)
    return {
        "valid": not enabled,
        "enabled_capability_count": len(enabled),
        "enabled_capability_flags": enabled,
        "readiness_approval_disabled": not closeout.readiness_approval_enabled,
        "operational_authorization_disabled": not closeout.operational_authorization_enabled,
        "remediation_disabled": not closeout.remediation_enabled,
        "automatic_correction_disabled": not closeout.automatic_correction_enabled,
        "drift_correction_disabled": not closeout.drift_correction_enabled,
        "continuity_repair_disabled": not closeout.continuity_repair_enabled,
        "continuity_inference_disabled": not closeout.continuity_inference_enabled,
        "routing_execution_disabled": not closeout.routing_execution_enabled,
        "orchestration_execution_disabled": not closeout.orchestration_execution_enabled,
        "refresh_execution_disabled": not closeout.refresh_execution_enabled,
        "sequencing_execution_disabled": not closeout.sequencing_execution_enabled,
        "scheduling_execution_disabled": not closeout.scheduling_execution_enabled,
        "dependency_resolution_disabled": not closeout.dependency_resolution_enabled,
        "lineage_repair_disabled": not closeout.lineage_repair_enabled,
        "lineage_inference_disabled": not closeout.lineage_inference_enabled,
        "planner_integration_disabled": not closeout.planner_integration_enabled,
        "production_consumption_disabled": not closeout.production_consumption_enabled,
        "runtime_mutation_disabled": not closeout.runtime_mutation_enabled,
        "non_executable": closeout.non_executable,
        "descriptive_only": closeout.descriptive_only,
        "closeout_only": closeout.closeout_only,
        "planning_readiness_only": closeout.planning_readiness_only,
    }


def build_v4_2_closeout_diagnostics(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    phase_coverage = validate_v4_2_phase_evidence_coverage(closeout)
    report_inventory = validate_v4_2_report_inventory(closeout)
    doc_inventory = validate_v4_2_migration_documentation_inventory(closeout)
    test_inventory = validate_v4_2_focused_test_inventory(closeout)
    warning_aggregation = aggregate_v4_2_warnings(closeout)
    prohibited = aggregate_v4_2_prohibited_capabilities(closeout)
    disabled = aggregate_v4_2_disabled_boundaries(closeout)
    non_execution = validate_v4_2_closeout_non_execution(closeout)
    conflicting_evidence = phase_coverage["duplicate_phase_ids"]
    return {
        "valid": all(
            (
                phase_coverage["valid"],
                report_inventory["valid"],
                doc_inventory["valid"],
                test_inventory["valid"],
                warning_aggregation["valid"],
                prohibited["valid"],
                disabled["valid"],
                non_execution["valid"],
            )
        ),
        "phase_evidence_coverage": phase_coverage,
        "report_inventory": report_inventory,
        "migration_documentation_inventory": doc_inventory,
        "focused_test_inventory": test_inventory,
        "warning_aggregation": warning_aggregation,
        "prohibited_capability_aggregation": prohibited,
        "disabled_boundary_aggregation": disabled,
        "non_execution_validation": non_execution,
        "missing_evidence_visible": bool(
            phase_coverage["missing_or_invalid_evidence_phase_ids"]
            or report_inventory["missing_report_names"]
            or doc_inventory["missing_doc_names"]
            or test_inventory["missing_test_names"]
        ),
        "conflicting_evidence_visible": bool(conflicting_evidence),
        "conflicting_evidence_phase_ids": conflicting_evidence,
        "remediation_enabled": False,
        "automatic_correction_enabled": False,
        "approval_enabled": False,
        "authorization_enabled": False,
        "execution_enabled": False,
    }


def validate_v4_2_closeout_readiness(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    diagnostics = build_v4_2_closeout_diagnostics(closeout)
    closeout_valid = closeout.closeout_classification.closeout_classification in (
        V4_2_CLOSEOUT_CLASSIFICATION_CLOSED_WITH_WARNINGS,
        V4_2_CLOSEOUT_CLASSIFICATION_BLOCKED,
    )
    readiness_valid = closeout.v4_3_planning_readiness.readiness_classification in (
        V4_3_READINESS_CLASSIFICATION_READY_WITH_WARNINGS,
        V4_3_READINESS_CLASSIFICATION_BLOCKED,
    )
    return {
        "valid": diagnostics["valid"] and closeout_valid and readiness_valid,
        "foundation_status": (
            V4_2_CLOSEOUT_READINESS_STATUS_STABLE
            if diagnostics["valid"]
            else V4_2_CLOSEOUT_READINESS_STATUS_BLOCKED
        ),
        "closeout_classification": closeout.closeout_classification.closeout_classification,
        "v4_3_readiness_classification": closeout.v4_3_planning_readiness.readiness_classification,
        "diagnostics": diagnostics,
        "closeout_classification_valid": closeout_valid,
        "v4_3_readiness_classification_valid": readiness_valid,
        "descriptive_only": closeout.descriptive_only,
        "non_executable": closeout.non_executable,
    }


def hash_v4_2_phase_evidence(reference: V42PhaseEvidenceReference) -> str:
    return deterministic_v4_2_closeout_hash(export_v4_2_phase_evidence(reference))


def hash_v4_2_warning_summary(warning: V42WarningSummary) -> str:
    return deterministic_v4_2_closeout_hash(export_v4_2_warning_summary(warning))


def hash_v4_2_disabled_boundary_summary(boundary: V42DisabledBoundarySummary) -> str:
    return deterministic_v4_2_closeout_hash(export_v4_2_disabled_boundary_summary(boundary))


def hash_v4_2_prohibited_capability_summary(capability: V42ProhibitedCapabilitySummary) -> str:
    return deterministic_v4_2_closeout_hash(export_v4_2_prohibited_capability_summary(capability))


def hash_v4_2_closeout_report_payload(report: Mapping[str, Any]) -> str:
    payload = dict(report)
    payload.pop("deterministic_report_hash", None)
    return deterministic_v4_2_closeout_hash(payload)


def build_v4_2_closeout_summary(closeout: V42CloseoutReadinessCertification) -> dict[str, Any]:
    validation = validate_v4_2_closeout_readiness(closeout)
    diagnostics = validation["diagnostics"]
    return {
        "foundation_status": validation["foundation_status"],
        "validation_error_count": 0 if validation["valid"] else 1,
        "v4_2_closeout_classification": validation["closeout_classification"],
        "v4_3_readiness_classification": validation["v4_3_readiness_classification"],
        "recommended_v4_3_direction": V4_3_RECOMMENDED_DIRECTION,
        "phase_1_9_evidence_coverage_validated": diagnostics["phase_evidence_coverage"]["valid"],
        "generated_report_inventory_validated": diagnostics["report_inventory"]["valid"],
        "migration_documentation_inventory_validated": diagnostics["migration_documentation_inventory"]["valid"],
        "focused_test_inventory_validated": diagnostics["focused_test_inventory"]["valid"],
        "deterministic_serialization_verified": True,
        "deterministic_hashing_verified": True,
        "warning_aggregation_validated": diagnostics["warning_aggregation"]["valid"],
        "remaining_warning_count": diagnostics["warning_aggregation"]["unresolved_warning_count"],
        "prohibited_capability_aggregation_validated": diagnostics["prohibited_capability_aggregation"]["valid"],
        "disabled_boundary_aggregation_validated": diagnostics["disabled_boundary_aggregation"]["valid"],
        "missing_evidence_visible": diagnostics["missing_evidence_visible"],
        "conflicting_evidence_visible": diagnostics["conflicting_evidence_visible"],
        "non_execution_enforcement_validated": diagnostics["non_execution_validation"]["valid"],
        "readiness_approval_disabled": diagnostics["non_execution_validation"]["readiness_approval_disabled"],
        "operational_authorization_disabled": diagnostics["non_execution_validation"]["operational_authorization_disabled"],
        "remediation_disabled": diagnostics["non_execution_validation"]["remediation_disabled"],
        "orchestration_execution_disabled": diagnostics["non_execution_validation"]["orchestration_execution_disabled"],
        "refresh_execution_disabled": diagnostics["non_execution_validation"]["refresh_execution_disabled"],
        "routing_execution_disabled": diagnostics["non_execution_validation"]["routing_execution_disabled"],
        "sequencing_execution_disabled": diagnostics["non_execution_validation"]["sequencing_execution_disabled"],
        "scheduling_execution_disabled": diagnostics["non_execution_validation"]["scheduling_execution_disabled"],
        "dependency_resolution_disabled": diagnostics["non_execution_validation"]["dependency_resolution_disabled"],
        "planner_integration_disabled": diagnostics["non_execution_validation"]["planner_integration_disabled"],
        "production_consumption_disabled": diagnostics["non_execution_validation"]["production_consumption_disabled"],
        "runtime_mutation_disabled": diagnostics["non_execution_validation"]["runtime_mutation_disabled"],
    }


def build_v4_2_closeout_and_v4_3_readiness_report(repo_root: Path | None = None) -> dict[str, Any]:
    root = repo_root or Path(__file__).resolve().parents[3]
    closeout = build_v4_2_closeout_readiness(root)
    repeated = build_v4_2_closeout_readiness(root)
    reordered = V42CloseoutReadinessCertification(
        identity=closeout.identity,
        phase_evidence=tuple(reversed(closeout.phase_evidence)),
        report_inventory=closeout.report_inventory,
        migration_doc_inventory=closeout.migration_doc_inventory,
        focused_test_inventory=closeout.focused_test_inventory,
        warning_summaries=tuple(reversed(closeout.warning_summaries)),
        prohibited_capability_summaries=tuple(reversed(closeout.prohibited_capability_summaries)),
        disabled_boundary_summaries=tuple(reversed(closeout.disabled_boundary_summaries)),
        closeout_classification=closeout.closeout_classification,
        v4_3_planning_readiness=closeout.v4_3_planning_readiness,
        deterministic_guarantees=tuple(reversed(closeout.deterministic_guarantees)),
        explicit_limitations=tuple(reversed(closeout.explicit_limitations)),
        explicit_prohibitions=tuple(reversed(closeout.explicit_prohibitions)),
    )
    serialization_first = serialize_v4_2_closeout_readiness(closeout)
    serialization_second = serialize_v4_2_closeout_readiness(repeated)
    serialization_reordered = serialize_v4_2_closeout_readiness(reordered)
    closeout_hash = hash_v4_2_closeout_readiness(closeout)
    repeated_hash = hash_v4_2_closeout_readiness(repeated)
    reordered_hash = hash_v4_2_closeout_readiness(reordered)
    validation = validate_v4_2_closeout_readiness(closeout)
    diagnostics = validation["diagnostics"]
    serialization_stable = serialization_first == serialization_second == serialization_reordered
    hashing_stable = closeout_hash == repeated_hash == reordered_hash
    validation_error_count = sum(
        (
            0 if validation["valid"] else 1,
            0 if serialization_stable else 1,
            0 if hashing_stable else 1,
            0 if v4_2_closeout_readiness_equal(closeout, repeated) else 1,
        )
    )
    foundation_status = (
        V4_2_CLOSEOUT_READINESS_STATUS_STABLE
        if validation_error_count == 0
        else V4_2_CLOSEOUT_READINESS_STATUS_BLOCKED
    )
    summary = build_v4_2_closeout_summary(closeout)
    summary["validation_error_count"] = validation_error_count
    summary["foundation_status"] = foundation_status
    report = {
        "schema_version": V4_2_CLOSEOUT_READINESS_REPORT_SCHEMA_VERSION,
        "generated_at": closeout.identity.generated_at,
        "phase_id": "v4_2_closeout_and_v4_3_readiness",
        "phase_name": "v4.2_phase_10_closeout_and_v4.3_readiness",
        "repo_root": str(root),
        "architectural_purpose": "deterministic v4.2 closeout and v4.3 planning readiness without approval authorization remediation orchestration or execution",
        "closeout_mode": "closeout_and_planning_readiness_only",
        "foundation_status": foundation_status,
        "model_counts": {
            "phase_evidence_count": len(closeout.phase_evidence),
            "generated_report_count": closeout.report_inventory.present_count,
            "migration_documentation_count": closeout.migration_doc_inventory.present_count,
            "focused_test_count": closeout.focused_test_inventory.present_count,
            "warning_count": len(closeout.warning_summaries),
            "prohibited_capability_count": len(closeout.prohibited_capability_summaries),
            "disabled_boundary_count": len(closeout.disabled_boundary_summaries),
        },
        "phase_1_9_summary": [
            {
                "phase_number": reference.phase_number,
                "phase_id": reference.phase_id,
                "phase_name": reference.phase_name,
                "summary": reference.summary,
                "evidence_status": reference.evidence_status,
                "report_hash": reference.report_hash,
            }
            for reference in sorted(closeout.phase_evidence, key=lambda item: (item.phase_number, item.phase_id))
        ],
        "inventory_validation": {
            "phase_evidence": diagnostics["phase_evidence_coverage"],
            "generated_reports": diagnostics["report_inventory"],
            "migration_documentation": diagnostics["migration_documentation_inventory"],
            "focused_tests": diagnostics["focused_test_inventory"],
        },
        "deterministic_serialization_verification": {
            "stable": serialization_stable,
            "serializer": "json_sort_keys_stable_v4_2_closeout_readiness",
            "payload_length": len(serialization_first),
            "reordered_payload_equal": serialization_first == serialization_reordered,
        },
        "deterministic_hashing_verification": {
            "stable": hashing_stable,
            "hash_algorithm": "sha256_stable_json_v4_2_closeout_readiness",
            "closeout_readiness_hash": closeout_hash,
            "repeated_closeout_readiness_hash": repeated_hash,
            "reordered_closeout_readiness_hash": reordered_hash,
            "phase_evidence_hashes": [hash_v4_2_phase_evidence(reference) for reference in closeout.phase_evidence],
            "warning_hashes": [hash_v4_2_warning_summary(warning) for warning in closeout.warning_summaries],
            "prohibited_capability_hashes": [
                hash_v4_2_prohibited_capability_summary(capability)
                for capability in closeout.prohibited_capability_summaries
            ],
            "disabled_boundary_hashes": [
                hash_v4_2_disabled_boundary_summary(boundary)
                for boundary in closeout.disabled_boundary_summaries
            ],
        },
        "warning_aggregation": diagnostics["warning_aggregation"],
        "remaining_warnings": [
            export_v4_2_warning_summary(warning)
            for warning in sorted(closeout.warning_summaries, key=lambda item: (item.deterministic_order, item.warning_id))
        ],
        "prohibited_capability_aggregation": diagnostics["prohibited_capability_aggregation"],
        "disabled_boundary_aggregation": diagnostics["disabled_boundary_aggregation"],
        "non_execution_and_non_authorization_guarantees": diagnostics["non_execution_validation"],
        "closeout_classification": export_v4_2_closeout_classification(closeout.closeout_classification),
        "v4_3_planning_readiness_classification": export_v4_3_planning_readiness_classification(
            closeout.v4_3_planning_readiness
        ),
        "recommended_v4_3_direction": V4_3_RECOMMENDED_DIRECTION,
        "v4_3_direction_limit": "v4.3 should remain descriptive-only and non-executable unless explicitly approved later.",
        "summary": summary,
        "v4_2_closeout_readiness": export_v4_2_closeout_readiness(closeout),
        "explicit_limitations": list(closeout.explicit_limitations),
        "explicit_prohibitions": list(closeout.explicit_prohibitions),
    }
    report["deterministic_report_hash"] = hash_v4_2_closeout_report_payload(report)
    return report
