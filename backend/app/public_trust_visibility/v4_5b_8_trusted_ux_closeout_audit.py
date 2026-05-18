"""Audit for deterministic v4.5B.8 trusted UX closeout."""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_8_trusted_ux_closeout_hashing import (
    deterministic_v4_5b_8_trusted_ux_closeout_hash,
    hash_frontend_readiness_visibility_record,
    hash_generated_report_coverage_record,
    hash_inherited_prohibition_certification_record,
    hash_migration_document_coverage_record,
    hash_phase_coverage_record,
    hash_public_trust_continuity_record,
    hash_trusted_ux_closeout_diagnostic_record,
    hash_trusted_ux_closeout_identity,
    hash_trusted_ux_closeout_record,
    hash_trusted_ux_readiness_record,
    hash_unsupported_state_certification_record,
    hash_unsupported_trusted_ux_operational_state_visibility,
    hash_v4_5b_8_trusted_ux_closeout,
)
from .v4_5b_8_trusted_ux_closeout_models import (
    CLOSEOUT_DIAGNOSTIC_TYPES,
    FRONTEND_READINESS_TYPES,
    FRONTEND_READINESS_VISIBILITY_TYPES,
    INHERITED_PROHIBITION_CERTIFICATION_TYPES,
    MIGRATION_DOCUMENT_COVERAGE_TYPES,
    PHASE_ARTIFACTS,
    PUBLIC_TRUST_CONTINUITY_TYPES,
    REPORT_COVERAGE_TYPES,
    TRUSTED_UX_CLOSEOUT_TYPES,
    TRUSTED_UX_READINESS_NON_AUTHORITY_STATEMENT,
    TRUSTED_UX_READINESS_STATEMENT,
    UNSUPPORTED_STATE_CERTIFICATION_TYPES,
    UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_GENERATED_AT,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_PHASE_ID,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_PURPOSE,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_REPORT_SCHEMA_VERSION,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_BLOCKED,
    V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_STABLE,
    V4_5B_8_TRUSTED_UX_DISABLED_COUNTER_NAMES,
    TrustedUxCloseoutCertification,
    default_v4_5b_8_trusted_ux_closeout,
)
from .v4_5b_8_trusted_ux_closeout_serialization import (
    export_v4_5b_8_trusted_ux_closeout,
    serialize_v4_5b_8_trusted_ux_closeout,
)
from .v4_5b_8_trusted_ux_closeout_visibility import (
    descriptive_only_trusted_ux_summary,
    frontend_readiness_visibility_summary,
    inherited_prohibition_summary,
    migration_document_summary,
    phase_coverage_summary,
    public_trust_continuity_summary,
    readiness_classification_summary,
    report_coverage_summary,
    trusted_ux_closeout_diagnostic_summary,
    trusted_ux_closeout_summary,
    trusted_ux_readiness_summary,
    unsupported_operational_state_summary,
    unsupported_state_summary,
    validate_required_trusted_ux_closeout_visibility,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enablement_enabled",
        "execution_safety_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
    ),
    "enabled_orchestration_dispatch_count": (
        "orchestration_dispatch_enabled",
        "dispatch_enabled",
    ),
    "enabled_orchestration_routing_count": (
        "orchestration_routing_enabled",
        "routing_enabled",
    ),
    "enabled_orchestration_traversal_count": (
        "orchestration_traversal_enabled",
        "traversal_enabled",
    ),
    "enabled_orchestration_scheduling_count": (
        "orchestration_scheduling_enabled",
        "scheduling_enabled",
    ),
    "enabled_orchestration_sequencing_count": (
        "orchestration_sequencing_enabled",
        "sequencing_enabled",
    ),
    "enabled_orchestration_decision_count": (
        "orchestration_decision_enabled",
        "decision_enabled",
    ),
    "enabled_orchestration_recommendation_count": (
        "orchestration_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_frontend_launch_authorization_count": (
        "frontend_launch_authorization_enabled",
        "frontend_launch_enabled",
    ),
    "enabled_production_enablement_count": ("production_enablement_enabled",),
    "enabled_ui_authorization_count": ("ui_authorization_enabled",),
    "enabled_ui_approval_count": ("ui_approval_enabled",),
    "enabled_scoring_count": (
        "scoring_enabled",
        "trust_scoring_enabled",
        "evidence_scoring_enabled",
        "coverage_scoring_enabled",
        "confidence_scoring_enabled",
    ),
    "enabled_ranking_count": ("ranking_enabled",),
    "enabled_recommendation_count": ("recommendation_enabled",),
    "enabled_triage_count": ("triage_enabled",),
    "enabled_remediation_count": ("remediation_enabled",),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
    "enabled_planner_integration_count": ("planner_integration_enabled",),
    "enabled_production_consumption_count": ("production_consumption_enabled",),
    "enabled_runtime_mutation_count": (
        "runtime_mutation_enabled",
        "runtime_enablement_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "operational_behavior_enabled",
        "operational_enabled",
        "operational_readiness_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5b_8_trusted_ux_closeout() -> TrustedUxCloseoutCertification:
    return default_v4_5b_8_trusted_ux_closeout()


def _iter_dataclass_objects(value: Any) -> Iterable[Any]:
    if is_dataclass(value) and not isinstance(value, type):
        yield value
        for item in value.__dict__.values():
            yield from _iter_dataclass_objects(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_dataclass_objects(item)
    elif isinstance(value, tuple | list | set):
        for item in value:
            yield from _iter_dataclass_objects(item)


def _relative_path_exists(reference: str) -> bool:
    return (REPO_ROOT / reference).exists()


def _report_hash_matches(reference: str, expected_hash: str) -> bool:
    path = REPO_ROOT / reference
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return payload.get("deterministic_report_hash") == expected_hash


def _record_id(item: object) -> str:
    return str(
        getattr(item, "closeout_record_id", None)
        or getattr(item, "readiness_record_id", None)
        or getattr(item, "phase_coverage_id", None)
        or getattr(item, "report_coverage_id", None)
        or getattr(item, "migration_document_coverage_id", None)
        or getattr(item, "continuity_record_id", None)
        or getattr(item, "unsupported_state_record_id", None)
        or getattr(item, "inherited_prohibition_record_id", None)
        or getattr(item, "frontend_readiness_id", None)
        or getattr(item, "diagnostic_id", None)
        or getattr(item, "state_id", None)
        or getattr(item, "trusted_ux_closeout_id", item.__class__.__name__)
    )


def enabled_trusted_ux_capability_flags(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(certification):
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(_record_id(item), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def trusted_ux_capability_counter_values(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(certification))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def trusted_ux_closeout_equal(
    left: TrustedUxCloseoutCertification,
    right: TrustedUxCloseoutCertification,
) -> bool:
    return serialize_v4_5b_8_trusted_ux_closeout(
        left
    ) == serialize_v4_5b_8_trusted_ux_closeout(right)


def validate_trusted_ux_closeout_ordering_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    reordered = replace(
        certification,
        closeout_records=tuple(reversed(certification.closeout_records)),
        readiness_records=tuple(reversed(certification.readiness_records)),
        phase_coverage_records=tuple(reversed(certification.phase_coverage_records)),
        report_coverage_records=tuple(reversed(certification.report_coverage_records)),
        migration_document_coverage_records=tuple(
            reversed(certification.migration_document_coverage_records)
        ),
        public_trust_continuity_records=tuple(
            reversed(certification.public_trust_continuity_records)
        ),
        unsupported_state_records=tuple(
            reversed(certification.unsupported_state_records)
        ),
        inherited_prohibition_records=tuple(
            reversed(certification.inherited_prohibition_records)
        ),
        frontend_readiness_records=tuple(
            reversed(certification.frontend_readiness_records)
        ),
        closeout_diagnostic_records=tuple(
            reversed(certification.closeout_diagnostic_records)
        ),
        unsupported_operational_state_visibility=tuple(
            reversed(certification.unsupported_operational_state_visibility)
        ),
        deterministic_guarantees=tuple(reversed(certification.deterministic_guarantees)),
        inherited_prohibitions=tuple(reversed(certification.inherited_prohibitions)),
        inherited_constraints=tuple(reversed(certification.inherited_constraints)),
        explicit_limitations=tuple(reversed(certification.explicit_limitations)),
    )
    serialization_stable = serialize_v4_5b_8_trusted_ux_closeout(
        certification
    ) == serialize_v4_5b_8_trusted_ux_closeout(reordered)
    hashing_stable = hash_v4_5b_8_trusted_ux_closeout(
        certification
    ) == hash_v4_5b_8_trusted_ux_closeout(reordered)
    return {
        "valid": serialization_stable and hashing_stable,
        "serialization_stable": serialization_stable,
        "hashing_stable": hashing_stable,
    }


def validate_trusted_ux_closeout_identity_integrity(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    identity = certification.identity
    required_fields = (
        "trusted_ux_closeout_id",
        "trusted_ux_readiness_id",
        "phase_chain_id",
        "public_trust_visibility_reference_id",
        "support_status_reference_id",
        "explainability_surface_reference_id",
        "provenance_lineage_reference_id",
        "evidence_panel_reference_id",
        "coverage_confidence_reference_id",
        "public_diagnostics_reference_id",
        "continuity_reference_id",
        "lineage_reference_id",
        "provenance_reference_id",
    )
    missing_fields = [field for field in required_fields if not getattr(identity, field)]
    phase_valid = identity.phase_id == V4_5B_8_TRUSTED_UX_CLOSEOUT_PHASE_ID
    generated_at_valid = identity.generated_at == V4_5B_8_TRUSTED_UX_CLOSEOUT_GENERATED_AT
    return {
        "valid": (
            not missing_fields
            and phase_valid
            and generated_at_valid
            and bool(identity.schema_version)
        ),
        "missing_fields": missing_fields,
        "phase_valid": phase_valid,
        "generated_at_valid": generated_at_valid,
    }


def _validate_required_types(
    records: Iterable[Any],
    *,
    type_field: str,
    expected_types: tuple[str, ...],
    prohibited_fields: tuple[str, ...],
    require_fail_visible: bool = False,
) -> dict[str, Any]:
    records_tuple = tuple(records)
    observed = {str(getattr(record, type_field)) for record in records_tuple}
    missing_types = sorted(set(expected_types) - observed)
    non_descriptive_records = sorted(
        _record_id(record)
        for record in records_tuple
        if not bool(getattr(record, "descriptive_only", True))
    )
    non_fail_visible_records = sorted(
        _record_id(record)
        for record in records_tuple
        if require_fail_visible and not bool(getattr(record, "fail_visible", True))
    )
    prohibited_enabled_records = {
        _record_id(record): sorted(
            field
            for field in prohibited_fields
            if bool(getattr(record, field, False))
        )
        for record in records_tuple
        if any(bool(getattr(record, field, False)) for field in prohibited_fields)
    }
    return {
        "valid": (
            not missing_types
            and not non_descriptive_records
            and not non_fail_visible_records
            and not prohibited_enabled_records
        ),
        "missing_types": missing_types,
        "non_descriptive_records": non_descriptive_records,
        "non_fail_visible_records": non_fail_visible_records,
        "prohibited_enabled_records": prohibited_enabled_records,
    }


def validate_closeout_record_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return _validate_required_types(
        certification.closeout_records,
        type_field="closeout_type",
        expected_types=TRUSTED_UX_CLOSEOUT_TYPES,
        prohibited_fields=(
            "frontend_launch_authorization_enabled",
            "production_enablement_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
    )


def validate_readiness_record_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    validation = _validate_required_types(
        certification.readiness_records,
        type_field="readiness_type",
        expected_types=FRONTEND_READINESS_TYPES,
        prohibited_fields=(
            "frontend_launch_enabled",
            "production_enablement_enabled",
            "planner_integration_enabled",
            "runtime_enablement_enabled",
            "authorization_enabled",
            "approval_enabled",
        ),
    )
    missing_classifications = sorted(
        record.readiness_record_id
        for record in certification.readiness_records
        if not record.readiness_classification.endswith("_descriptive_only_ready")
    )
    return {
        **validation,
        "valid": validation["valid"] and not missing_classifications,
        "missing_classifications": missing_classifications,
    }


def validate_phase_coverage_certification_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    expected_labels = tuple(item[0] for item in PHASE_ARTIFACTS)
    validation = _validate_required_types(
        certification.phase_coverage_records,
        type_field="phase_label",
        expected_types=expected_labels,
        prohibited_fields=("frontend_launch_authorization_enabled", "approval_enabled"),
    )
    missing_reports = sorted(
        record.generated_report_reference
        for record in certification.phase_coverage_records
        if not _relative_path_exists(record.generated_report_reference)
    )
    hash_mismatches = sorted(
        record.generated_report_reference
        for record in certification.phase_coverage_records
        if not _report_hash_matches(
            record.generated_report_reference,
            record.generated_report_hash,
        )
    )
    missing_migration_docs = sorted(
        record.migration_document_reference
        for record in certification.phase_coverage_records
        if not _relative_path_exists(record.migration_document_reference)
    )
    return {
        **validation,
        "valid": (
            validation["valid"]
            and not missing_reports
            and not hash_mismatches
            and not missing_migration_docs
        ),
        "missing_reports": missing_reports,
        "hash_mismatches": hash_mismatches,
        "missing_migration_docs": missing_migration_docs,
    }


def validate_report_coverage_certification_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    validation = _validate_required_types(
        certification.report_coverage_records,
        type_field="report_coverage_type",
        expected_types=REPORT_COVERAGE_TYPES,
        prohibited_fields=("runtime_authority_enabled",),
    )
    missing_reports: list[str] = []
    hash_mismatches: list[str] = []
    for record in certification.report_coverage_records:
        for reference, expected_hash in zip(
            record.report_references,
            record.expected_report_hashes,
            strict=True,
        ):
            if not _relative_path_exists(reference):
                missing_reports.append(reference)
            elif not _report_hash_matches(reference, expected_hash):
                hash_mismatches.append(reference)
    return {
        **validation,
        "valid": validation["valid"] and not missing_reports and not hash_mismatches,
        "missing_reports": sorted(set(missing_reports)),
        "hash_mismatches": sorted(set(hash_mismatches)),
    }


def validate_migration_document_coverage_certification_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    validation = _validate_required_types(
        certification.migration_document_coverage_records,
        type_field="migration_document_coverage_type",
        expected_types=MIGRATION_DOCUMENT_COVERAGE_TYPES,
        prohibited_fields=("production_enablement_enabled",),
    )
    missing_docs: list[str] = []
    for record in certification.migration_document_coverage_records:
        for reference in record.migration_document_references:
            if not _relative_path_exists(reference):
                missing_docs.append(reference)
    return {
        **validation,
        "valid": validation["valid"] and not missing_docs,
        "missing_migration_documents": sorted(set(missing_docs)),
    }


def validate_public_trust_continuity_certification(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return _validate_required_types(
        certification.public_trust_continuity_records,
        type_field="continuity_type",
        expected_types=PUBLIC_TRUST_CONTINUITY_TYPES,
        prohibited_fields=("restoration_enabled", "repair_enabled"),
    )


def validate_unsupported_state_preservation_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return _validate_required_types(
        certification.unsupported_state_records,
        type_field="unsupported_state_type",
        expected_types=UNSUPPORTED_STATE_CERTIFICATION_TYPES,
        prohibited_fields=("suppression_enabled", "operational_fallback_enabled"),
        require_fail_visible=True,
    )


def validate_inherited_prohibition_preservation_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return _validate_required_types(
        certification.inherited_prohibition_records,
        type_field="inherited_prohibition_type",
        expected_types=INHERITED_PROHIBITION_CERTIFICATION_TYPES,
        prohibited_fields=("authorization_enabled", "approval_enabled"),
    )


def validate_frontend_readiness_visibility_stability(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    return _validate_required_types(
        certification.frontend_readiness_records,
        type_field="frontend_readiness_type",
        expected_types=FRONTEND_READINESS_VISIBILITY_TYPES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "frontend_launch_enabled",
            "production_enablement_enabled",
            "planner_integration_enabled",
        ),
    )


def validate_lineage_and_provenance_preservation(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    lineage_continuity_preserved = bool(certification.identity.lineage_reference_id)
    provenance_continuity_preserved = bool(certification.identity.provenance_reference_id)
    continuity_reference_preserved = bool(certification.identity.continuity_reference_id)
    return {
        "valid": (
            lineage_continuity_preserved
            and provenance_continuity_preserved
            and continuity_reference_preserved
        ),
        "lineage_continuity_preserved": lineage_continuity_preserved,
        "provenance_continuity_preserved": provenance_continuity_preserved,
        "continuity_reference_preserved": continuity_reference_preserved,
    }


def validate_trusted_ux_closeout_serialization_and_hashing(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    serialization_one = serialize_v4_5b_8_trusted_ux_closeout(certification)
    serialization_two = serialize_v4_5b_8_trusted_ux_closeout(
        build_v4_5b_8_trusted_ux_closeout()
    )
    hash_one = hash_v4_5b_8_trusted_ux_closeout(certification)
    hash_two = hash_v4_5b_8_trusted_ux_closeout(build_v4_5b_8_trusted_ux_closeout())
    ordering = validate_trusted_ux_closeout_ordering_stability(certification)
    return {
        "valid": (
            serialization_one == serialization_two
            and hash_one == hash_two
            and ordering["valid"]
        ),
        "serialization_stable": serialization_one == serialization_two,
        "hashing_stable": hash_one == hash_two,
        "ordering_stable": ordering["valid"],
        "serialized_length": len(serialization_one),
        "deterministic_hash": hash_one,
    }


def validate_fail_visible_trusted_ux_closeout_diagnostics(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    diagnostics = _validate_required_types(
        certification.closeout_diagnostic_records,
        type_field="diagnostic_type",
        expected_types=CLOSEOUT_DIAGNOSTIC_TYPES,
        prohibited_fields=(
            "silent_fallback_enabled",
            "authorization_enabled",
            "approval_enabled",
            "remediation_enabled",
            "repair_enabled",
            "mitigation_enabled",
            "auto_correction_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "triage_enabled",
        ),
        require_fail_visible=True,
    )
    unsupported = _validate_required_types(
        certification.unsupported_operational_state_visibility,
        type_field="unsupported_state",
        expected_types=UNSUPPORTED_TRUSTED_UX_OPERATIONAL_STATES,
        prohibited_fields=(
            "authorization_enabled",
            "approval_enabled",
            "operational_enabled",
            "remediation_enabled",
            "repair_enabled",
            "mitigation_enabled",
            "automated_correction_enabled",
            "ranking_enabled",
            "recommendation_enabled",
            "scoring_enabled",
            "triage_enabled",
            "production_enablement_enabled",
            "frontend_launch_enabled",
            "suppression_enabled",
        ),
        require_fail_visible=True,
    )
    missing_explicit_reasons = sorted(
        record.state_id
        for record in certification.unsupported_operational_state_visibility
        if not record.explicit_reason
    )
    return {
        "valid": diagnostics["valid"] and unsupported["valid"] and not missing_explicit_reasons,
        "diagnostic_visibility": diagnostics,
        "unsupported_operational_visibility": unsupported,
        "missing_explicit_reasons": missing_explicit_reasons,
    }


def validate_descriptive_only_trusted_ux_guarantees(
    certification: TrustedUxCloseoutCertification,
) -> dict[str, Any]:
    counters = trusted_ux_capability_counter_values(certification)
    enabled_flags = enabled_trusted_ux_capability_flags(certification)
    required_boundary_booleans = {
        "descriptive_only": certification.descriptive_only,
        "publicly_transparent": certification.publicly_transparent,
        "non_operational": certification.non_operational,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_executing": certification.non_executing,
        "non_remediating": certification.non_remediating,
        "non_runtime_mutating": certification.non_runtime_mutating,
        "non_ranking": certification.non_ranking,
        "non_recommending": certification.non_recommending,
        "non_scoring": certification.non_scoring,
        "non_triaging": certification.non_triaging,
    }
    all_required_true = all(required_boundary_booleans.values())
    all_counters_zero = all(
        counters.get(counter_name, 1) == 0
        for counter_name in V4_5B_8_TRUSTED_UX_DISABLED_COUNTER_NAMES
    )
    statements_valid = (
        certification.trusted_ux_readiness_statement
        == TRUSTED_UX_READINESS_STATEMENT
        and certification.trusted_ux_readiness_non_authority_statement
        == TRUSTED_UX_READINESS_NON_AUTHORITY_STATEMENT
    )
    return {
        "valid": all_required_true
        and all_counters_zero
        and not enabled_flags
        and statements_valid,
        "required_boundary_booleans": required_boundary_booleans,
        "counters": counters,
        "enabled_flags": enabled_flags,
        "statements_valid": statements_valid,
        "publicly_transparent": certification.publicly_transparent,
        "trusted_ux_readiness_statement": (
            certification.trusted_ux_readiness_statement
        ),
        "trusted_ux_readiness_non_authority_statement": (
            certification.trusted_ux_readiness_non_authority_statement
        ),
        "inherited_prohibition_count": len(certification.inherited_prohibitions),
        "inherited_constraint_count": len(certification.inherited_constraints),
        "explicit_limitation_count": len(certification.explicit_limitations),
    }


def validate_v4_5b_8_trusted_ux_closeout(
    certification: TrustedUxCloseoutCertification | None = None,
) -> dict[str, Any]:
    if certification is None:
        certification = build_v4_5b_8_trusted_ux_closeout()
    validations = {
        "identity_integrity": validate_trusted_ux_closeout_identity_integrity(
            certification
        ),
        "required_visibility": validate_required_trusted_ux_closeout_visibility(
            certification
        ),
        "closeout_records": validate_closeout_record_stability(certification),
        "readiness_records": validate_readiness_record_stability(certification),
        "phase_coverage": validate_phase_coverage_certification_stability(
            certification
        ),
        "report_coverage": validate_report_coverage_certification_stability(
            certification
        ),
        "migration_document_coverage": (
            validate_migration_document_coverage_certification_stability(
                certification
            )
        ),
        "public_trust_continuity": validate_public_trust_continuity_certification(
            certification
        ),
        "unsupported_state_preservation": (
            validate_unsupported_state_preservation_stability(certification)
        ),
        "inherited_prohibition_preservation": (
            validate_inherited_prohibition_preservation_stability(certification)
        ),
        "frontend_readiness_visibility": (
            validate_frontend_readiness_visibility_stability(certification)
        ),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            certification
        ),
        "serialization_and_hashing": (
            validate_trusted_ux_closeout_serialization_and_hashing(certification)
        ),
        "fail_visible_closeout_diagnostics": (
            validate_fail_visible_trusted_ux_closeout_diagnostics(certification)
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_trusted_ux_guarantees(certification)
        ),
    }
    errors = sorted(name for name, result in validations.items() if not result["valid"])
    return {
        "valid": not errors,
        "foundation_status": (
            V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_STABLE
            if not errors
            else V4_5B_8_TRUSTED_UX_CLOSEOUT_STATUS_BLOCKED
        ),
        "validation_error_count": len(errors),
        "validation_errors": errors,
        "validations": validations,
    }


def build_v4_5b_8_trusted_ux_closeout_report() -> dict[str, Any]:
    certification = build_v4_5b_8_trusted_ux_closeout()
    validation = validate_v4_5b_8_trusted_ux_closeout(certification)
    exported = export_v4_5b_8_trusted_ux_closeout(certification)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_and_hashing"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_closeout_diagnostics"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "trusted_ux_closeout_identity_hash": hash_trusted_ux_closeout_identity(
            certification.identity
        ),
        "trusted_ux_closeout_hash": hash_v4_5b_8_trusted_ux_closeout(
            certification
        ),
        "closeout_hashes": {
            record.closeout_record_id: hash_trusted_ux_closeout_record(record)
            for record in sorted(
                certification.closeout_records,
                key=lambda item: (item.deterministic_order, item.closeout_record_id),
            )
        },
        "readiness_hashes": {
            record.readiness_record_id: hash_trusted_ux_readiness_record(record)
            for record in sorted(
                certification.readiness_records,
                key=lambda item: (item.deterministic_order, item.readiness_record_id),
            )
        },
        "phase_coverage_hashes": {
            record.phase_coverage_id: hash_phase_coverage_record(record)
            for record in sorted(
                certification.phase_coverage_records,
                key=lambda item: (item.deterministic_order, item.phase_coverage_id),
            )
        },
        "report_coverage_hashes": {
            record.report_coverage_id: hash_generated_report_coverage_record(record)
            for record in sorted(
                certification.report_coverage_records,
                key=lambda item: (item.deterministic_order, item.report_coverage_id),
            )
        },
        "migration_document_coverage_hashes": {
            record.migration_document_coverage_id: (
                hash_migration_document_coverage_record(record)
            )
            for record in sorted(
                certification.migration_document_coverage_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.migration_document_coverage_id,
                ),
            )
        },
        "public_trust_continuity_hashes": {
            record.continuity_record_id: hash_public_trust_continuity_record(record)
            for record in sorted(
                certification.public_trust_continuity_records,
                key=lambda item: (item.deterministic_order, item.continuity_record_id),
            )
        },
        "unsupported_state_hashes": {
            record.unsupported_state_record_id: (
                hash_unsupported_state_certification_record(record)
            )
            for record in sorted(
                certification.unsupported_state_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_state_record_id,
                ),
            )
        },
        "inherited_prohibition_hashes": {
            record.inherited_prohibition_record_id: (
                hash_inherited_prohibition_certification_record(record)
            )
            for record in sorted(
                certification.inherited_prohibition_records,
                key=lambda item: (
                    item.deterministic_order,
                    item.inherited_prohibition_record_id,
                ),
            )
        },
        "frontend_readiness_hashes": {
            record.frontend_readiness_id: (
                hash_frontend_readiness_visibility_record(record)
            )
            for record in sorted(
                certification.frontend_readiness_records,
                key=lambda item: (item.deterministic_order, item.frontend_readiness_id),
            )
        },
        "closeout_diagnostic_hashes": {
            record.diagnostic_id: hash_trusted_ux_closeout_diagnostic_record(record)
            for record in sorted(
                certification.closeout_diagnostic_records,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_operational_hashes": {
            record.state_id: (
                hash_unsupported_trusted_ux_operational_state_visibility(record)
            )
            for record in sorted(
                certification.unsupported_operational_state_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    readiness_classifications = readiness_classification_summary(
        certification.readiness_records
    )
    summary = {
        "closeout_record_count": len(certification.closeout_records),
        "readiness_record_count": len(certification.readiness_records),
        "phase_coverage_record_count": len(certification.phase_coverage_records),
        "report_coverage_record_count": len(certification.report_coverage_records),
        "migration_document_coverage_record_count": len(
            certification.migration_document_coverage_records
        ),
        "public_trust_continuity_record_count": len(
            certification.public_trust_continuity_records
        ),
        "unsupported_state_record_count": len(certification.unsupported_state_records),
        "inherited_prohibition_record_count": len(
            certification.inherited_prohibition_records
        ),
        "frontend_readiness_record_count": len(
            certification.frontend_readiness_records
        ),
        "closeout_diagnostic_record_count": len(
            certification.closeout_diagnostic_records
        ),
        "unsupported_operational_state_count": len(
            certification.unsupported_operational_state_visibility
        ),
        "closeout_counts": required_visibility["closeout_counts"],
        "readiness_counts": required_visibility["readiness_counts"],
        "phase_counts": required_visibility["phase_counts"],
        "report_counts": required_visibility["report_counts"],
        "migration_counts": required_visibility["migration_counts"],
        "continuity_counts": required_visibility["continuity_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "inherited_counts": required_visibility["inherited_counts"],
        "frontend_counts": required_visibility["frontend_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_closeout_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_closeout_hashing_verified": serialization_hashing[
            "hashing_stable"
        ],
        "phase_coverage_stable": validation["validations"]["phase_coverage"]["valid"],
        "report_coverage_stable": validation["validations"]["report_coverage"][
            "valid"
        ],
        "migration_document_coverage_stable": validation["validations"][
            "migration_document_coverage"
        ]["valid"],
        "public_trust_continuity_preserved": validation["validations"][
            "public_trust_continuity"
        ]["valid"],
        "unsupported_state_preservation_stable": validation["validations"][
            "unsupported_state_preservation"
        ]["valid"],
        "inherited_prohibition_preservation_stable": validation["validations"][
            "inherited_prohibition_preservation"
        ]["valid"],
        "frontend_readiness_visibility_stable": validation["validations"][
            "frontend_readiness_visibility"
        ]["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "continuity_reference_preserved": lineage_provenance[
            "continuity_reference_preserved"
        ],
        "fail_visible_closeout_diagnostics_preserved": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "trusted_ux_readiness_statement": descriptive_only[
            "trusted_ux_readiness_statement"
        ],
        "trusted_ux_readiness_non_authority_statement": descriptive_only[
            "trusted_ux_readiness_non_authority_statement"
        ],
        "inherited_prohibition_count": descriptive_only[
            "inherited_prohibition_count"
        ],
        "inherited_constraint_count": descriptive_only["inherited_constraint_count"],
        "explicit_limitation_count": descriptive_only["explicit_limitation_count"],
        "validation_error_count": validation["validation_error_count"],
        "readiness_classifications": readiness_classifications,
        "repository_remains": [
            "NON-operational",
            "NON-authorizing",
            "NON-approving",
            "NON-executing",
            "NON-remediating",
            "NON-runtime-mutating",
            "NON-ranking",
            "NON-recommending",
            "NON-scoring",
            "NON-triaging",
        ],
    }
    summary.update(counters)
    report = {
        "phase_id": V4_5B_8_TRUSTED_UX_CLOSEOUT_PHASE_ID,
        "schema_version": V4_5B_8_TRUSTED_UX_CLOSEOUT_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_8_TRUSTED_UX_CLOSEOUT_GENERATED_AT,
        "purpose": V4_5B_8_TRUSTED_UX_CLOSEOUT_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "readiness_classifications": readiness_classifications,
        "visibility": {
            "closeout": trusted_ux_closeout_summary(certification.closeout_records),
            "readiness": trusted_ux_readiness_summary(certification.readiness_records),
            "phase_coverage": phase_coverage_summary(
                certification.phase_coverage_records
            ),
            "report_coverage": report_coverage_summary(
                certification.report_coverage_records
            ),
            "migration_documents": migration_document_summary(
                certification.migration_document_coverage_records
            ),
            "public_trust_continuity": public_trust_continuity_summary(
                certification.public_trust_continuity_records
            ),
            "unsupported_states": unsupported_state_summary(
                certification.unsupported_state_records
            ),
            "inherited_prohibitions": inherited_prohibition_summary(
                certification.inherited_prohibition_records
            ),
            "frontend_readiness": frontend_readiness_visibility_summary(
                certification.frontend_readiness_records
            ),
            "closeout_diagnostics": trusted_ux_closeout_diagnostic_summary(
                certification.closeout_diagnostic_records
            ),
            "unsupported_operational_states": unsupported_operational_state_summary(
                certification.unsupported_operational_state_visibility
            ),
            "descriptive_only": descriptive_only_trusted_ux_summary(certification),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_certification": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_8_trusted_ux_closeout_hash(report)
    )
    return report


def contaminate_v4_5b_8_trusted_ux_closeout_for_non_operational_validation(
    certification: TrustedUxCloseoutCertification | None = None,
) -> TrustedUxCloseoutCertification:
    if certification is None:
        certification = build_v4_5b_8_trusted_ux_closeout()
    return replace(
        certification,
        runtime_execution_enabled=True,
        frontend_launch_authorization_enabled=True,
        production_enablement_enabled=True,
        ui_authorization_enabled=True,
        ui_approval_enabled=True,
        scoring_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        triage_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
