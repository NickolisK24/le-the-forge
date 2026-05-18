"""Audit for deterministic v4.5A.8 readiness closeout.

The audit validates descriptive closeout and readiness visibility only. It does
not authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5a_8_readiness_closeout_hashing import (
    deterministic_v4_5a_8_readiness_closeout_hash,
    hash_closeout_diagnostic_record,
    hash_closeout_record,
    hash_continuity_certification,
    hash_generated_report_coverage_certification,
    hash_inherited_prohibition_preservation_certification,
    hash_migration_document_coverage_certification,
    hash_phase_coverage_certification,
    hash_readiness_certification_record,
    hash_readiness_closeout_identity,
    hash_readiness_visibility,
    hash_unsupported_readiness_visibility,
    hash_unsupported_state_preservation_certification,
    hash_v4_5a_8_readiness_closeout,
)
from .v4_5a_8_readiness_closeout_models import (
    CLOSEOUT_DIAGNOSTIC_TYPES,
    CONTINUITY_CERTIFICATION_TYPES,
    INHERITED_PROHIBITION_PRESERVATION_TYPES,
    PHASE_COVERAGE_TYPES,
    PHASE_MIGRATION_DOCUMENT_REFERENCES,
    PHASE_REPORT_REFERENCES,
    READINESS_TARGETS,
    READINESS_VISIBILITY_TYPES,
    UNSUPPORTED_READINESS_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_PRESERVATION_TYPES,
    V4_5A_8_READINESS_CLOSEOUT_DISABLED_COUNTER_NAMES,
    V4_5A_8_READINESS_CLOSEOUT_GENERATED_AT,
    V4_5A_8_READINESS_CLOSEOUT_PHASE_ID,
    V4_5A_8_READINESS_CLOSEOUT_PURPOSE,
    V4_5A_8_READINESS_CLOSEOUT_REPORT_SCHEMA_VERSION,
    V4_5A_8_READINESS_CLOSEOUT_STATUS_BLOCKED,
    V4_5A_8_READINESS_CLOSEOUT_STATUS_STABLE,
    ReadinessCloseoutIntelligence,
    default_v4_5a_8_readiness_closeout,
)
from .v4_5a_8_readiness_closeout_serialization import (
    export_v4_5a_8_readiness_closeout,
    serialize_v4_5a_8_readiness_closeout,
)
from .v4_5a_8_readiness_closeout_visibility import (
    closeout_summary_visibility,
    continuity_certification_summary_visibility,
    descriptive_only_readiness_closeout_summary,
    fail_visible_closeout_diagnostic_summaries,
    inherited_prohibition_summary_visibility,
    migration_document_summary_visibility,
    phase_coverage_summary_visibility,
    readiness_summary_visibility,
    readiness_visibility_summary,
    report_coverage_summary_visibility,
    unsupported_readiness_visibility_summaries,
    unsupported_state_summary_visibility,
    validate_required_readiness_closeout_visibility,
)


REPO_ROOT = Path(__file__).resolve().parents[3]

CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_execution_enabled",
        "planner_execution_enabled",
        "execution_enabled",
        "execution_enablement_enabled",
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
        "orchestration_response_enabled",
    ),
    "enabled_readiness_authorization_count": (
        "readiness_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_readiness_approval_count": (
        "readiness_approval_enabled",
        "approval_enabled",
    ),
    "enabled_remediation_count": ("remediation_enabled",),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
    "enabled_ranking_count": ("ranking_enabled",),
    "enabled_recommendation_count": ("recommendation_enabled",),
    "enabled_planner_integration_count": ("planner_integration_enabled",),
    "enabled_production_consumption_count": (
        "production_consumption_enabled",
        "production_enablement_enabled",
    ),
    "enabled_runtime_mutation_count": (
        "runtime_mutation_enabled",
        "runtime_enablement_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "operational_behavior_enabled",
        "operational_readiness_enabled",
        "operational_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5a_8_readiness_closeout() -> ReadinessCloseoutIntelligence:
    return default_v4_5a_8_readiness_closeout()


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


def enabled_readiness_closeout_capability_flags(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "closeout_record_id", None)
            or getattr(item, "readiness_record_id", None)
            or getattr(item, "phase_coverage_id", None)
            or getattr(item, "report_coverage_id", None)
            or getattr(item, "document_coverage_id", None)
            or getattr(item, "continuity_certification_id", None)
            or getattr(item, "unsupported_certification_id", None)
            or getattr(item, "prohibition_certification_id", None)
            or getattr(item, "readiness_visibility_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "closeout_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def readiness_closeout_capability_counter_values(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(intelligence))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def readiness_closeout_equal(
    left: ReadinessCloseoutIntelligence,
    right: ReadinessCloseoutIntelligence,
) -> bool:
    return serialize_v4_5a_8_readiness_closeout(
        left
    ) == serialize_v4_5a_8_readiness_closeout(right)


def validate_closeout_ordering_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "closeout_records": tuple(
            record.deterministic_order for record in intelligence.closeout_records
        ),
        "readiness_certifications": tuple(
            record.deterministic_order for record in intelligence.readiness_certifications
        ),
        "phase_coverage_certifications": tuple(
            record.deterministic_order
            for record in intelligence.phase_coverage_certifications
        ),
        "report_coverage_certifications": tuple(
            record.deterministic_order
            for record in intelligence.report_coverage_certifications
        ),
        "migration_document_certifications": tuple(
            record.deterministic_order
            for record in intelligence.migration_document_certifications
        ),
        "continuity_certifications": tuple(
            record.deterministic_order
            for record in intelligence.continuity_certifications
        ),
        "unsupported_state_certifications": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_certifications
        ),
        "inherited_prohibition_certifications": tuple(
            record.deterministic_order
            for record in intelligence.inherited_prohibition_certifications
        ),
        "readiness_visibility": tuple(
            record.deterministic_order for record in intelligence.readiness_visibility
        ),
        "closeout_diagnostics": tuple(
            record.deterministic_order for record in intelligence.closeout_diagnostics
        ),
        "unsupported_readiness_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_readiness_visibility
        ),
    }
    unordered_groups = [
        name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders
    ]
    duplicate_groups = [
        name for name, orders in order_groups.items() if len(set(orders)) != len(orders)
    ]
    return {
        "valid": not (unordered_groups or duplicate_groups),
        "order_groups": order_groups,
        "unordered_groups": unordered_groups,
        "duplicate_groups": duplicate_groups,
    }


def validate_closeout_identity_integrity(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    identity = intelligence.closeout_identity
    empty_fields = [
        field_name
        for field_name in (
            "closeout_id",
            "readiness_id",
            "phase_chain_id",
            "certification_chain_id",
            "evidence_chain_id",
            "continuity_reference_id",
            "lineage_reference_id",
            "provenance_reference_id",
            "generated_report_reference_id",
            "migration_document_reference_id",
            "phase_id",
            "schema_version",
            "generated_at",
            "classification",
            "source_integrity_certification_report_reference",
            "source_integrity_certification_hash_reference",
        )
        if not getattr(identity, field_name)
    ]
    source_report, source_hash = PHASE_REPORT_REFERENCES["v4_5a_7_integrity_certification"]
    mismatched_records = sorted(
        record.closeout_record_id
        for record in intelligence.closeout_records
        if (
            record.closeout_id != identity.closeout_id
            or record.readiness_id != identity.readiness_id
            or record.phase_chain_id != identity.phase_chain_id
            or record.certification_chain_id != identity.certification_chain_id
            or record.evidence_chain_id != identity.evidence_chain_id
            or record.continuity_reference_id != identity.continuity_reference_id
            or record.lineage_reference_id != identity.lineage_reference_id
            or record.provenance_reference_id != identity.provenance_reference_id
        )
    )
    return {
        "valid": not (
            empty_fields
            or mismatched_records
            or identity.source_integrity_certification_report_reference != source_report
            or identity.source_integrity_certification_hash_reference != source_hash
        ),
        "empty_identity_fields": empty_fields,
        "mismatched_records": mismatched_records,
        "closeout_record_count": len(intelligence.closeout_records),
        "source_integrity_certification_report_reference": (
            identity.source_integrity_certification_report_reference
        ),
        "source_integrity_certification_hash_reference": (
            identity.source_integrity_certification_hash_reference
        ),
    }


def validate_phase_coverage_certification_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.phase_coverage_certifications
    present = {record.phase_id for record in records}
    missing_types = sorted(set(PHASE_COVERAGE_TYPES) - present)
    bad_references = sorted(
        record.phase_coverage_id
        for record in records
        if (
            PHASE_REPORT_REFERENCES[record.phase_id]
            != (record.report_reference, record.report_hash_reference)
            or PHASE_MIGRATION_DOCUMENT_REFERENCES[record.phase_id]
            != record.migration_document_reference
        )
    )
    missing_files = sorted(
        record.phase_coverage_id
        for record in records
        if not _relative_path_exists(record.report_reference)
        or not _relative_path_exists(record.migration_document_reference)
    )
    unsafe_ids = sorted(
        record.phase_coverage_id
        for record in records
        if (
            not record.coverage_certified
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_readiness_enabled
        )
    )
    return {
        "valid": not (missing_types or bad_references or missing_files or unsafe_ids),
        "phase_coverage_count": len(records),
        "missing_phase_types": missing_types,
        "bad_references": bad_references,
        "missing_files": missing_files,
        "unsafe_phase_coverage_ids": unsafe_ids,
    }


def validate_report_coverage_certification_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.report_coverage_certifications
    missing_reports = sorted(
        record.report_coverage_id
        for record in records
        if not _relative_path_exists(record.report_reference)
    )
    mismatched_hashes = sorted(
        record.report_coverage_id
        for record in records
        if not _report_hash_matches(record.report_reference, record.report_hash_reference)
    )
    unsafe_ids = sorted(
        record.report_coverage_id
        for record in records
        if (
            not record.report_present
            or not record.report_continuity_preserved
            or not record.hashing_stability_preserved
            or not record.replay_stability_preserved
            or not record.evidence_continuity_preserved
            or not record.descriptive_only
            or record.runtime_authority_enabled
        )
    )
    return {
        "valid": not (missing_reports or mismatched_hashes or unsafe_ids),
        "report_coverage_count": len(records),
        "missing_reports": missing_reports,
        "mismatched_hashes": mismatched_hashes,
        "unsafe_report_coverage_ids": unsafe_ids,
    }


def validate_migration_documentation_certification_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.migration_document_certifications
    missing_documents = sorted(
        record.document_coverage_id
        for record in records
        if not _relative_path_exists(record.migration_document_reference)
    )
    unsafe_ids = sorted(
        record.document_coverage_id
        for record in records
        if (
            not record.document_present
            or not record.document_continuity_preserved
            or not record.coverage_integrity_preserved
            or not record.replay_visibility_preserved
            or not record.descriptive_only
            or record.operational_readiness_enabled
        )
    )
    return {
        "valid": not (missing_documents or unsafe_ids),
        "migration_document_count": len(records),
        "missing_documents": missing_documents,
        "unsafe_document_coverage_ids": unsafe_ids,
    }


def validate_continuity_certification_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.continuity_certifications
    present = {record.continuity_type for record in records}
    missing_types = sorted(set(CONTINUITY_CERTIFICATION_TYPES) - present)
    unsafe_ids = sorted(
        record.continuity_certification_id
        for record in records
        if (
            not record.continuity_certified
            or not record.descriptive_only
            or record.restoration_enabled
            or record.repair_enabled
            or record.remediation_enabled
            or not record.continuity_reference_id
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "continuity_certification_count": len(records),
        "missing_continuity_types": missing_types,
        "unsafe_continuity_certification_ids": unsafe_ids,
    }


def validate_unsupported_state_preservation_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_certifications
    present = {record.preservation_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_STATE_PRESERVATION_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_certification_id
        for record in records
        if (
            not record.preservation_certified
            or not record.descriptive_only
            or not record.fail_visible
            or record.suppression_enabled
            or record.authorization_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "unsupported_state_certification_count": len(records),
        "missing_unsupported_state_types": missing_types,
        "unsafe_unsupported_state_ids": unsafe_ids,
    }


def validate_inherited_prohibition_preservation_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    records = intelligence.inherited_prohibition_certifications
    present = {record.preservation_type for record in records}
    missing_types = sorted(set(INHERITED_PROHIBITION_PRESERVATION_TYPES) - present)
    unsafe_ids = sorted(
        record.prohibition_certification_id
        for record in records
        if (
            not record.preservation_certified
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_behavior_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "inherited_prohibition_certification_count": len(records),
        "missing_inherited_prohibition_types": missing_types,
        "unsafe_inherited_prohibition_ids": unsafe_ids,
    }


def validate_readiness_visibility_stability(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    readiness_targets = {record.readiness_target for record in intelligence.readiness_certifications}
    visibility_types = {record.readiness_visibility_type for record in intelligence.readiness_visibility}
    missing_targets = sorted(set(READINESS_TARGETS) - readiness_targets)
    missing_visibility_types = sorted(set(READINESS_VISIBILITY_TYPES) - visibility_types)
    unsafe_readiness_ids = sorted(
        record.readiness_record_id
        for record in intelligence.readiness_certifications
        if (
            not record.descriptive_only
            or not record.non_authorizing
            or not record.non_approving
            or record.authorization_enabled
            or record.approval_enabled
            or record.execution_enablement_enabled
            or record.production_enablement_enabled
            or record.runtime_enablement_enabled
        )
    )
    unsafe_visibility_ids = sorted(
        record.readiness_visibility_id
        for record in intelligence.readiness_visibility
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.execution_enablement_enabled
            or record.production_enablement_enabled
            or record.runtime_enablement_enabled
        )
    )
    return {
        "valid": not (
            missing_targets
            or missing_visibility_types
            or unsafe_readiness_ids
            or unsafe_visibility_ids
        ),
        "readiness_certification_count": len(intelligence.readiness_certifications),
        "readiness_visibility_count": len(intelligence.readiness_visibility),
        "missing_targets": missing_targets,
        "missing_visibility_types": missing_visibility_types,
        "unsafe_readiness_ids": unsafe_readiness_ids,
        "unsafe_visibility_ids": unsafe_visibility_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    identity = intelligence.closeout_identity
    missing_lineage = not bool(identity.lineage_reference_id)
    missing_provenance = not bool(identity.provenance_reference_id)
    missing_continuity = not bool(identity.continuity_reference_id)
    missing_evidence = sorted(
        str(
            getattr(item, "readiness_record_id", None)
            or getattr(item, "phase_coverage_id", None)
            or getattr(item, "report_coverage_id", None)
            or getattr(item, "document_coverage_id", None)
            or getattr(item, "continuity_certification_id", None)
            or getattr(item, "unsupported_certification_id", None)
            or getattr(item, "prohibition_certification_id", None)
            or getattr(item, "readiness_visibility_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", "")
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "evidence_reference_ids")
        and not tuple(getattr(item, "evidence_reference_ids"))
    )
    return {
        "valid": not (missing_lineage or missing_provenance or missing_continuity or missing_evidence),
        "lineage_continuity_preserved": not missing_lineage,
        "provenance_continuity_preserved": not missing_provenance,
        "continuity_reference_preserved": not missing_continuity,
        "evidence_continuity_preserved": not missing_evidence,
        "missing_evidence_reference_ids": missing_evidence,
    }


def validate_readiness_closeout_serialization_and_hashing(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5a_8_readiness_closeout(intelligence)
    second_serialization = serialize_v4_5a_8_readiness_closeout(intelligence)
    first_hash = hash_v4_5a_8_readiness_closeout(intelligence)
    second_hash = hash_v4_5a_8_readiness_closeout(intelligence)
    rebuilt_hash = hash_v4_5a_8_readiness_closeout(
        build_v4_5a_8_readiness_closeout()
    )
    return {
        "valid": (
            first_serialization == second_serialization
            and first_hash == second_hash
            and first_hash == rebuilt_hash
        ),
        "serialization_stable": first_serialization == second_serialization,
        "hashing_stable": first_hash == second_hash == rebuilt_hash,
        "readiness_closeout_hash": first_hash,
        "rebuilt_readiness_closeout_hash": rebuilt_hash,
        "serialization_length": len(first_serialization),
    }


def validate_fail_visible_closeout_diagnostics(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    diagnostics = intelligence.closeout_diagnostics
    unsupported = intelligence.unsupported_readiness_visibility
    missing_diagnostic_types = sorted(
        set(CLOSEOUT_DIAGNOSTIC_TYPES) - {record.diagnostic_type for record in diagnostics}
    )
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_READINESS_OPERATIONAL_STATES)
        - {record.unsupported_state for record in unsupported}
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in diagnostics
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.silent_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.auto_correction_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.orchestration_response_enabled
        )
    )
    unsafe_unsupported_ids = sorted(
        record.state_id
        for record in unsupported
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.operational_enabled
            or record.remediation_enabled
            or record.repair_enabled
            or record.mitigation_enabled
            or record.automated_correction_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_ids
        ),
        "closeout_diagnostic_count": len(diagnostics),
        "unsupported_readiness_state_count": len(unsupported),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_ids": unsafe_unsupported_ids,
        "fail_visible": all(record.fail_visible for record in diagnostics)
        and all(record.fail_visible for record in unsupported),
        "silent_fallback_enabled_count": sum(
            1 for record in diagnostics if record.silent_fallback_enabled
        ),
        "authorization_enabled_count": sum(
            1 for record in diagnostics if record.authorization_enabled
        )
        + sum(1 for record in unsupported if record.authorization_enabled),
        "approval_enabled_count": sum(
            1 for record in diagnostics if record.approval_enabled
        )
        + sum(1 for record in unsupported if record.approval_enabled),
        "ranking_enabled_count": sum(
            1 for record in diagnostics if record.ranking_enabled
        )
        + sum(1 for record in unsupported if record.ranking_enabled),
        "recommendation_enabled_count": sum(
            1 for record in diagnostics if record.recommendation_enabled
        )
        + sum(1 for record in unsupported if record.recommendation_enabled),
    }


def validate_descriptive_only_readiness_closeout_guarantees(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    counters = readiness_closeout_capability_counter_values(intelligence)
    enabled_flags = enabled_readiness_closeout_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "closeout_record_id", None)
            or getattr(item, "readiness_record_id", None)
            or getattr(item, "phase_coverage_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "closeout_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5A_8_READINESS_CLOSEOUT_DISABLED_COUNTER_NAMES) - set(counters)
    )
    required_repository_states = {
        "NON-operational": intelligence.non_operational,
        "NON-authorizing": intelligence.non_authorizing,
        "NON-approving": intelligence.non_approving,
        "NON-executing": intelligence.non_executing,
        "NON-remediating": intelligence.non_remediating,
        "NON-runtime-mutating": intelligence.non_runtime_mutating,
        "NON-ranking": intelligence.non_ranking,
        "NON-recommending": intelligence.non_recommending,
    }
    missing_repository_states = sorted(
        state for state, preserved in required_repository_states.items() if not preserved
    )
    return {
        "valid": not (
            any(counters.values())
            or enabled_flags
            or descriptive_failures
            or missing_disabled_counters
            or missing_repository_states
        ),
        "counters": counters,
        "enabled_flags": enabled_flags,
        "descriptive_failures": descriptive_failures,
        "missing_disabled_counters": missing_disabled_counters,
        "required_repository_states": required_repository_states,
        "missing_repository_states": missing_repository_states,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "inherited_limitation_count": len(intelligence.inherited_limitations),
        "inherited_blocker_count": len(intelligence.inherited_blockers),
        "inherited_warning_count": len(intelligence.inherited_warnings),
    }


def validate_v4_5a_8_readiness_closeout(
    intelligence: ReadinessCloseoutIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_closeout_ordering_stability(intelligence),
        "identity_integrity": validate_closeout_identity_integrity(intelligence),
        "phase_coverage": validate_phase_coverage_certification_stability(
            intelligence
        ),
        "report_coverage": validate_report_coverage_certification_stability(
            intelligence
        ),
        "migration_documentation": validate_migration_documentation_certification_stability(
            intelligence
        ),
        "continuity_certification": validate_continuity_certification_stability(
            intelligence
        ),
        "unsupported_state_preservation": validate_unsupported_state_preservation_stability(
            intelligence
        ),
        "inherited_prohibition_preservation": validate_inherited_prohibition_preservation_stability(
            intelligence
        ),
        "readiness_visibility": validate_readiness_visibility_stability(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_readiness_closeout_serialization_and_hashing(
            intelligence
        ),
        "required_visibility": validate_required_readiness_closeout_visibility(
            intelligence
        ),
        "fail_visible_closeout": validate_fail_visible_closeout_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": validate_descriptive_only_readiness_closeout_guarantees(
            intelligence
        ),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_5a_8_readiness_closeout_report() -> dict[str, Any]:
    intelligence = build_v4_5a_8_readiness_closeout()
    exported = export_v4_5a_8_readiness_closeout(intelligence)
    validation = validate_v4_5a_8_readiness_closeout(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    phase_coverage = validation["validations"]["phase_coverage"]
    report_coverage = validation["validations"]["report_coverage"]
    migration_docs = validation["validations"]["migration_documentation"]
    continuity = validation["validations"]["continuity_certification"]
    unsupported = validation["validations"]["unsupported_state_preservation"]
    prohibition = validation["validations"]["inherited_prohibition_preservation"]
    readiness = validation["validations"]["readiness_visibility"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_closeout"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "closeout_identity_hash": hash_readiness_closeout_identity(
            intelligence.closeout_identity
        ),
        "readiness_closeout_hash": hash_v4_5a_8_readiness_closeout(intelligence),
        "closeout_record_hashes": {
            record.closeout_record_id: hash_closeout_record(record)
            for record in sorted(
                intelligence.closeout_records,
                key=lambda item: (item.deterministic_order, item.closeout_record_id),
            )
        },
        "readiness_certification_hashes": {
            record.readiness_record_id: hash_readiness_certification_record(record)
            for record in sorted(
                intelligence.readiness_certifications,
                key=lambda item: (item.deterministic_order, item.readiness_record_id),
            )
        },
        "phase_coverage_hashes": {
            record.phase_coverage_id: hash_phase_coverage_certification(record)
            for record in sorted(
                intelligence.phase_coverage_certifications,
                key=lambda item: (item.deterministic_order, item.phase_coverage_id),
            )
        },
        "report_coverage_hashes": {
            record.report_coverage_id: hash_generated_report_coverage_certification(record)
            for record in sorted(
                intelligence.report_coverage_certifications,
                key=lambda item: (item.deterministic_order, item.report_coverage_id),
            )
        },
        "migration_document_hashes": {
            record.document_coverage_id: hash_migration_document_coverage_certification(
                record
            )
            for record in sorted(
                intelligence.migration_document_certifications,
                key=lambda item: (item.deterministic_order, item.document_coverage_id),
            )
        },
        "continuity_hashes": {
            record.continuity_certification_id: hash_continuity_certification(record)
            for record in sorted(
                intelligence.continuity_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.continuity_certification_id,
                ),
            )
        },
        "unsupported_state_hashes": {
            record.unsupported_certification_id: (
                hash_unsupported_state_preservation_certification(record)
            )
            for record in sorted(
                intelligence.unsupported_state_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_certification_id,
                ),
            )
        },
        "inherited_prohibition_hashes": {
            record.prohibition_certification_id: (
                hash_inherited_prohibition_preservation_certification(record)
            )
            for record in sorted(
                intelligence.inherited_prohibition_certifications,
                key=lambda item: (
                    item.deterministic_order,
                    item.prohibition_certification_id,
                ),
            )
        },
        "readiness_visibility_hashes": {
            record.readiness_visibility_id: hash_readiness_visibility(record)
            for record in sorted(
                intelligence.readiness_visibility,
                key=lambda item: (item.deterministic_order, item.readiness_visibility_id),
            )
        },
        "closeout_diagnostic_hashes": {
            record.diagnostic_id: hash_closeout_diagnostic_record(record)
            for record in sorted(
                intelligence.closeout_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_readiness_hashes": {
            record.state_id: hash_unsupported_readiness_visibility(record)
            for record in sorted(
                intelligence.unsupported_readiness_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "closeout_record_count": len(intelligence.closeout_records),
        "readiness_certification_count": len(intelligence.readiness_certifications),
        "phase_coverage_count": len(intelligence.phase_coverage_certifications),
        "report_coverage_count": len(intelligence.report_coverage_certifications),
        "migration_document_count": len(intelligence.migration_document_certifications),
        "continuity_certification_count": len(intelligence.continuity_certifications),
        "unsupported_state_certification_count": len(
            intelligence.unsupported_state_certifications
        ),
        "inherited_prohibition_certification_count": len(
            intelligence.inherited_prohibition_certifications
        ),
        "readiness_visibility_count": len(intelligence.readiness_visibility),
        "closeout_diagnostic_count": len(intelligence.closeout_diagnostics),
        "unsupported_readiness_state_count": len(
            intelligence.unsupported_readiness_visibility
        ),
        "phase_counts": required_visibility["phase_counts"],
        "report_counts": required_visibility["report_counts"],
        "document_counts": required_visibility["document_counts"],
        "continuity_counts": required_visibility["continuity_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "prohibition_counts": required_visibility["prohibition_counts"],
        "readiness_counts": required_visibility["readiness_counts"],
        "readiness_visibility_counts": required_visibility[
            "readiness_visibility_counts"
        ],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_state_counts": required_visibility["unsupported_state_counts"],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "phase_coverage_stable": phase_coverage["valid"],
        "report_coverage_stable": report_coverage["valid"],
        "migration_documentation_stable": migration_docs["valid"],
        "continuity_certification_stable": continuity["valid"],
        "unsupported_state_preservation_stable": unsupported["valid"],
        "inherited_prohibition_preservation_stable": prohibition["valid"],
        "readiness_visibility_stable": readiness["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_closeout_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "inherited_prohibition_count": descriptive_only["inherited_prohibition_count"],
        "inherited_constraint_count": descriptive_only["inherited_constraint_count"],
        "inherited_limitation_count": descriptive_only["inherited_limitation_count"],
        "inherited_blocker_count": descriptive_only["inherited_blocker_count"],
        "inherited_warning_count": descriptive_only["inherited_warning_count"],
        "validation_error_count": validation["validation_error_count"],
        "repository_remains": [
            "NON-operational",
            "NON-authorizing",
            "NON-approving",
            "NON-executing",
            "NON-remediating",
            "NON-runtime-mutating",
            "NON-ranking",
            "NON-recommending",
        ],
        "repository_state": descriptive_only["required_repository_states"],
        "readiness_classifications": {
            record.readiness_target: record.readiness_classification
            for record in intelligence.readiness_certifications
        },
        **counters,
    }
    visibility = {
        "closeout_summaries": closeout_summary_visibility(
            intelligence.closeout_records
        ),
        "readiness_summaries": readiness_summary_visibility(
            intelligence.readiness_certifications
        ),
        "phase_coverage_summaries": phase_coverage_summary_visibility(
            intelligence.phase_coverage_certifications
        ),
        "report_coverage_summaries": report_coverage_summary_visibility(
            intelligence.report_coverage_certifications
        ),
        "migration_document_summaries": migration_document_summary_visibility(
            intelligence.migration_document_certifications
        ),
        "continuity_certification_summaries": (
            continuity_certification_summary_visibility(
                intelligence.continuity_certifications
            )
        ),
        "unsupported_state_summaries": unsupported_state_summary_visibility(
            intelligence.unsupported_state_certifications
        ),
        "inherited_prohibition_summaries": (
            inherited_prohibition_summary_visibility(
                intelligence.inherited_prohibition_certifications
            )
        ),
        "readiness_visibility_summaries": readiness_visibility_summary(
            intelligence.readiness_visibility
        ),
        "fail_visible_closeout_diagnostics": (
            fail_visible_closeout_diagnostic_summaries(
                intelligence.closeout_diagnostics
            )
        ),
        "unsupported_readiness_visibility": unsupported_readiness_visibility_summaries(
            intelligence.unsupported_readiness_visibility
        ),
        "inherited_limitations": sorted(intelligence.inherited_limitations),
        "inherited_blockers": sorted(intelligence.inherited_blockers),
        "inherited_warnings": sorted(intelligence.inherited_warnings),
        "descriptive_only_summary": descriptive_only_readiness_closeout_summary(
            intelligence
        ),
    }
    report_without_hash = {
        "schema_version": V4_5A_8_READINESS_CLOSEOUT_REPORT_SCHEMA_VERSION,
        "phase_id": V4_5A_8_READINESS_CLOSEOUT_PHASE_ID,
        "generated_at": V4_5A_8_READINESS_CLOSEOUT_GENERATED_AT,
        "purpose": V4_5A_8_READINESS_CLOSEOUT_PURPOSE,
        "foundation_status": (
            V4_5A_8_READINESS_CLOSEOUT_STATUS_STABLE
            if validation["valid"]
            else V4_5A_8_READINESS_CLOSEOUT_STATUS_BLOCKED
        ),
        "summary": summary,
        "visibility": visibility,
        "validation": validation,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "readiness_closeout_intelligence": exported,
    }
    return {
        **report_without_hash,
        "deterministic_report_hash": deterministic_v4_5a_8_readiness_closeout_hash(
            report_without_hash
        ),
    }


def contaminate_v4_5a_8_readiness_closeout_for_non_operational_validation(
    intelligence: ReadinessCloseoutIntelligence,
) -> ReadinessCloseoutIntelligence:
    contaminated_readiness = replace(
        intelligence.readiness_certifications[0],
        authorization_enabled=True,
        approval_enabled=True,
        execution_enablement_enabled=True,
        production_enablement_enabled=True,
        runtime_enablement_enabled=True,
    )
    contaminated_phase = replace(
        intelligence.phase_coverage_certifications[0],
        authorization_enabled=True,
        approval_enabled=True,
        operational_readiness_enabled=True,
    )
    contaminated_diagnostic = replace(
        intelligence.closeout_diagnostics[0],
        authorization_enabled=True,
        approval_enabled=True,
        remediation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        silent_fallback_enabled=True,
    )
    contaminated_state = replace(
        intelligence.unsupported_readiness_visibility[0],
        authorization_enabled=True,
        approval_enabled=True,
        operational_enabled=True,
        remediation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
    )
    return replace(
        intelligence,
        readiness_certifications=(contaminated_readiness,)
        + intelligence.readiness_certifications[1:],
        phase_coverage_certifications=(contaminated_phase,)
        + intelligence.phase_coverage_certifications[1:],
        closeout_diagnostics=(contaminated_diagnostic,)
        + intelligence.closeout_diagnostics[1:],
        unsupported_readiness_visibility=(contaminated_state,)
        + intelligence.unsupported_readiness_visibility[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        readiness_authorization_enabled=True,
        readiness_approval_enabled=True,
        remediation_enabled=True,
        ranking_enabled=True,
        recommendation_enabled=True,
        planner_integration_enabled=True,
        production_consumption_enabled=True,
        runtime_mutation_enabled=True,
    )
