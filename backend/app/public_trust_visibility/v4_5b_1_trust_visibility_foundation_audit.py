"""Audit for deterministic v4.5B.1 public trust visibility foundations.

The audit validates descriptive public trust visibility only. It does not
authorize, approve, execute, dispatch, route, traverse, schedule, sequence,
decide, recommend, rank, remediate, repair, mitigate, correct, integrate
planners, consume production paths, or mutate runtime or operational state.
"""

from __future__ import annotations

import json
from dataclasses import is_dataclass, replace
from pathlib import Path
from typing import Any, Iterable

from .v4_5b_1_trust_visibility_foundation_hashing import (
    deterministic_v4_5b_1_trust_visibility_foundation_hash,
    hash_governance_transparency_visibility,
    hash_public_explainability_visibility,
    hash_public_integrity_visibility,
    hash_public_trust_diagnostic_record,
    hash_public_trust_evidence_visibility,
    hash_trust_summary_record,
    hash_trust_visibility_identity,
    hash_trust_visibility_record,
    hash_unsupported_public_trust_visibility,
    hash_unsupported_state_visibility,
    hash_v4_5b_1_trust_visibility_foundation,
)
from .v4_5b_1_trust_visibility_foundation_models import (
    GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES,
    PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES,
    PUBLIC_INTEGRITY_VISIBILITY_TYPES,
    PUBLIC_TRUST_DIAGNOSTIC_TYPES,
    PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES,
    PUBLIC_TRUST_VISIBILITY_NON_AUTHORITY_STATEMENT,
    PUBLIC_TRUST_VISIBILITY_STATEMENT,
    TRUST_SUMMARY_TYPES,
    UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES,
    UNSUPPORTED_STATE_VISIBILITY_TYPES,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_DISABLED_COUNTER_NAMES,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_GENERATED_AT,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_PHASE_ID,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_PURPOSE,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_SCHEMA_VERSION,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_BLOCKED,
    V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_STABLE,
    TrustVisibilityFoundationIntelligence,
    default_v4_5b_1_trust_visibility_foundation,
)
from .v4_5b_1_trust_visibility_foundation_serialization import (
    export_v4_5b_1_trust_visibility_foundation,
    serialize_v4_5b_1_trust_visibility_foundation,
)
from .v4_5b_1_trust_visibility_foundation_visibility import (
    descriptive_only_public_trust_summary,
    diagnostics_summary,
    evidence_visibility_summary,
    explainability_summary,
    governance_transparency_summary,
    integrity_summary,
    trust_summary_visibility,
    trust_visibility_summary,
    unsupported_public_trust_summary,
    unsupported_state_summary,
    validate_required_trust_visibility_foundation,
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
    "enabled_trust_authorization_count": (
        "trust_authorization_enabled",
        "trust_authority_enabled",
        "authorization_enabled",
    ),
    "enabled_trust_approval_count": (
        "trust_approval_enabled",
        "approval_enabled",
        "operational_approval_enabled",
    ),
    "enabled_trust_ranking_count": (
        "trust_ranking_enabled",
        "ranking_enabled",
        "scoring_enabled",
    ),
    "enabled_trust_recommendation_count": (
        "trust_recommendation_enabled",
        "recommendation_enabled",
    ),
    "enabled_remediation_count": ("remediation_enabled",),
    "enabled_repair_count": ("repair_enabled",),
    "enabled_mitigation_count": ("mitigation_enabled",),
    "enabled_auto_correction_count": (
        "auto_correction_enabled",
        "automated_correction_enabled",
    ),
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
        "operational_semantics_enabled",
        "operational_enabled",
    ),
}

PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_5b_1_trust_visibility_foundation() -> (
    TrustVisibilityFoundationIntelligence
):
    return default_v4_5b_1_trust_visibility_foundation()


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


def enabled_trust_visibility_capability_flags(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "trust_record_id", None)
            or getattr(item, "evidence_visibility_id", None)
            or getattr(item, "unsupported_visibility_id", None)
            or getattr(item, "transparency_visibility_id", None)
            or getattr(item, "trust_summary_record_id", None)
            or getattr(item, "explainability_visibility_id", None)
            or getattr(item, "integrity_visibility_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "trust_visibility_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def trust_visibility_capability_counter_values(
    intelligence: TrustVisibilityFoundationIntelligence,
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


def trust_visibility_foundation_equal(
    left: TrustVisibilityFoundationIntelligence,
    right: TrustVisibilityFoundationIntelligence,
) -> bool:
    return serialize_v4_5b_1_trust_visibility_foundation(
        left
    ) == serialize_v4_5b_1_trust_visibility_foundation(right)


def validate_trust_visibility_ordering_stability(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "trust_visibility_records": tuple(
            record.deterministic_order
            for record in intelligence.trust_visibility_records
        ),
        "evidence_visibility": tuple(
            record.deterministic_order for record in intelligence.evidence_visibility
        ),
        "unsupported_state_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_state_visibility
        ),
        "governance_transparency_visibility": tuple(
            record.deterministic_order
            for record in intelligence.governance_transparency_visibility
        ),
        "trust_summaries": tuple(
            record.deterministic_order for record in intelligence.trust_summaries
        ),
        "explainability_visibility": tuple(
            record.deterministic_order
            for record in intelligence.explainability_visibility
        ),
        "integrity_visibility": tuple(
            record.deterministic_order for record in intelligence.integrity_visibility
        ),
        "public_trust_diagnostics": tuple(
            record.deterministic_order
            for record in intelligence.public_trust_diagnostics
        ),
        "unsupported_public_trust_visibility": tuple(
            record.deterministic_order
            for record in intelligence.unsupported_public_trust_visibility
        ),
    }
    unordered_groups = sorted(
        key for key, values in order_groups.items() if tuple(sorted(values)) != values
    )
    return {
        "valid": not unordered_groups,
        "order_groups": {key: list(values) for key, values in order_groups.items()},
        "unordered_groups": unordered_groups,
    }


def validate_trust_visibility_identity_integrity(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    identity = intelligence.trust_identity
    required_values = {
        "trust_visibility_id": identity.trust_visibility_id,
        "trust_summary_id": identity.trust_summary_id,
        "transparency_reference_id": identity.transparency_reference_id,
        "evidence_reference_id": identity.evidence_reference_id,
        "continuity_reference_id": identity.continuity_reference_id,
        "explainability_reference_id": identity.explainability_reference_id,
        "integrity_reference_id": identity.integrity_reference_id,
        "diagnostics_reference_id": identity.diagnostics_reference_id,
        "unsupported_state_reference_id": identity.unsupported_state_reference_id,
        "lineage_reference_id": identity.lineage_reference_id,
        "provenance_reference_id": identity.provenance_reference_id,
    }
    missing_fields = sorted(key for key, value in required_values.items() if not value)
    source_report_present = _relative_path_exists(
        identity.source_readiness_closeout_report_reference
    )
    source_report_hash_matches = _report_hash_matches(
        identity.source_readiness_closeout_report_reference,
        identity.source_readiness_closeout_hash_reference,
    )
    return {
        "valid": not missing_fields
        and identity.phase_id == V4_5B_1_TRUST_VISIBILITY_FOUNDATION_PHASE_ID
        and source_report_present
        and source_report_hash_matches,
        "missing_identity_fields": missing_fields,
        "phase_id": identity.phase_id,
        "schema_version": identity.schema_version,
        "source_report_present": source_report_present,
        "source_report_hash_matches": source_report_hash_matches,
    }


def validate_public_trust_evidence_visibility(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.evidence_visibility
    present = {record.evidence_visibility_type for record in records}
    missing_types = sorted(set(PUBLIC_TRUST_EVIDENCE_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.evidence_visibility_id
        for record in records
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or not record.replay_safe
            or not record.provenance_safe
            or record.authorization_enabled
            or record.approval_enabled
            or record.scoring_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "evidence_visibility_count": len(records),
        "missing_evidence_visibility_types": missing_types,
        "unsafe_evidence_visibility_ids": unsafe_ids,
    }


def validate_unsupported_state_visibility_preservation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.unsupported_state_visibility
    present = {record.unsupported_state_type for record in records}
    missing_types = sorted(set(UNSUPPORTED_STATE_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.unsupported_visibility_id
        for record in records
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or not record.fail_visible
            or record.suppression_enabled
            or record.hidden_fallback_enabled
            or record.authorization_enabled
            or record.approval_enabled
            or record.remediation_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "unsupported_state_visibility_count": len(records),
        "missing_unsupported_state_types": missing_types,
        "unsafe_unsupported_state_ids": unsafe_ids,
    }


def validate_governance_transparency_visibility_preservation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.governance_transparency_visibility
    present = {record.transparency_type for record in records}
    missing_types = sorted(set(GOVERNANCE_TRANSPARENCY_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.transparency_visibility_id
        for record in records
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or not record.public_visibility
            or record.operational_approval_enabled
            or record.authorization_enabled
            or record.approval_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "transparency_visibility_count": len(records),
        "missing_transparency_types": missing_types,
        "unsafe_transparency_ids": unsafe_ids,
    }


def validate_trust_summary_stability(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.trust_summaries
    present = {record.summary_type for record in records}
    missing_types = sorted(set(TRUST_SUMMARY_TYPES) - present)
    unsafe_ids = sorted(
        record.trust_summary_record_id
        for record in records
        if (
            not record.descriptive_only
            or record.authorization_enabled
            or record.approval_enabled
            or record.ranking_enabled
            or record.recommendation_enabled
            or record.execution_enablement_enabled
            or record.production_enablement_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "trust_summary_count": len(records),
        "missing_summary_types": missing_types,
        "unsafe_summary_ids": unsafe_ids,
    }


def validate_public_explainability_visibility(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.explainability_visibility
    present = {record.explainability_visibility_type for record in records}
    missing_types = sorted(set(PUBLIC_EXPLAINABILITY_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.explainability_visibility_id
        for record in records
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or record.recommendation_enabled
            or record.decision_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "explainability_visibility_count": len(records),
        "missing_explainability_types": missing_types,
        "unsafe_explainability_ids": unsafe_ids,
    }


def validate_public_integrity_visibility(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    records = intelligence.integrity_visibility
    present = {record.integrity_visibility_type for record in records}
    missing_types = sorted(set(PUBLIC_INTEGRITY_VISIBILITY_TYPES) - present)
    unsafe_ids = sorted(
        record.integrity_visibility_id
        for record in records
        if (
            not record.visibility_preserved
            or not record.descriptive_only
            or record.operational_semantics_enabled
            or record.approval_enabled
            or record.authorization_enabled
        )
    )
    return {
        "valid": not (missing_types or unsafe_ids),
        "integrity_visibility_count": len(records),
        "missing_integrity_types": missing_types,
        "unsafe_integrity_ids": unsafe_ids,
    }


def validate_lineage_and_provenance_preservation(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    identity = intelligence.trust_identity
    missing_lineage = not bool(identity.lineage_reference_id)
    missing_provenance = not bool(identity.provenance_reference_id)
    missing_continuity = not bool(identity.continuity_reference_id)
    missing_evidence = sorted(
        str(
            getattr(item, "evidence_visibility_id", None)
            or getattr(item, "unsupported_visibility_id", None)
            or getattr(item, "transparency_visibility_id", None)
            or getattr(item, "trust_summary_record_id", None)
            or getattr(item, "explainability_visibility_id", None)
            or getattr(item, "integrity_visibility_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", "")
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "evidence_reference_ids")
        and not tuple(getattr(item, "evidence_reference_ids"))
    )
    return {
        "valid": not (
            missing_lineage
            or missing_provenance
            or missing_continuity
            or missing_evidence
        ),
        "lineage_continuity_preserved": not missing_lineage,
        "provenance_continuity_preserved": not missing_provenance,
        "continuity_reference_preserved": not missing_continuity,
        "evidence_continuity_preserved": not missing_evidence,
        "missing_evidence_reference_ids": missing_evidence,
    }


def validate_trust_visibility_serialization_and_hashing(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    first_serialization = serialize_v4_5b_1_trust_visibility_foundation(intelligence)
    second_serialization = serialize_v4_5b_1_trust_visibility_foundation(intelligence)
    first_hash = hash_v4_5b_1_trust_visibility_foundation(intelligence)
    second_hash = hash_v4_5b_1_trust_visibility_foundation(intelligence)
    rebuilt_hash = hash_v4_5b_1_trust_visibility_foundation(
        build_v4_5b_1_trust_visibility_foundation()
    )
    return {
        "valid": (
            first_serialization == second_serialization
            and first_hash == second_hash
            and first_hash == rebuilt_hash
        ),
        "serialization_stable": first_serialization == second_serialization,
        "hashing_stable": first_hash == second_hash == rebuilt_hash,
        "trust_visibility_hash": first_hash,
        "rebuilt_trust_visibility_hash": rebuilt_hash,
        "serialization_length": len(first_serialization),
    }


def validate_fail_visible_public_trust_diagnostics(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    diagnostics = intelligence.public_trust_diagnostics
    unsupported = intelligence.unsupported_public_trust_visibility
    missing_diagnostic_types = sorted(
        set(PUBLIC_TRUST_DIAGNOSTIC_TYPES)
        - {record.diagnostic_type for record in diagnostics}
    )
    missing_unsupported_states = sorted(
        set(UNSUPPORTED_PUBLIC_TRUST_OPERATIONAL_STATES)
        - {record.unsupported_state for record in unsupported}
    )
    unsafe_diagnostic_ids = sorted(
        record.diagnostic_id
        for record in diagnostics
        if (
            not record.fail_visible
            or not record.descriptive_only
            or record.silent_fallback_enabled
            or record.hidden_fallback_enabled
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
            or record.suppression_enabled
        )
    )
    return {
        "valid": not (
            missing_diagnostic_types
            or missing_unsupported_states
            or unsafe_diagnostic_ids
            or unsafe_unsupported_ids
        ),
        "public_trust_diagnostic_count": len(diagnostics),
        "unsupported_public_trust_state_count": len(unsupported),
        "missing_diagnostic_types": missing_diagnostic_types,
        "missing_unsupported_states": missing_unsupported_states,
        "unsafe_diagnostic_ids": unsafe_diagnostic_ids,
        "unsafe_unsupported_ids": unsafe_unsupported_ids,
        "fail_visible": all(record.fail_visible for record in diagnostics)
        and all(record.fail_visible for record in unsupported),
        "silent_fallback_enabled_count": sum(
            1 for record in diagnostics if record.silent_fallback_enabled
        ),
        "hidden_fallback_enabled_count": sum(
            1 for record in diagnostics if record.hidden_fallback_enabled
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


def validate_descriptive_only_public_trust_guarantees(
    intelligence: TrustVisibilityFoundationIntelligence,
) -> dict[str, Any]:
    counters = trust_visibility_capability_counter_values(intelligence)
    enabled_flags = enabled_trust_visibility_capability_flags(intelligence)
    descriptive_failures = sorted(
        str(
            getattr(item, "trust_record_id", None)
            or getattr(item, "evidence_visibility_id", None)
            or getattr(item, "unsupported_visibility_id", None)
            or getattr(item, "transparency_visibility_id", None)
            or getattr(item, "trust_summary_record_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "state_id", None)
            or getattr(item, "trust_visibility_id", item.__class__.__name__)
        )
        for item in _iter_dataclass_objects(intelligence)
        if hasattr(item, "descriptive_only") and not getattr(item, "descriptive_only")
    )
    missing_disabled_counters = sorted(
        set(V4_5B_1_TRUST_VISIBILITY_FOUNDATION_DISABLED_COUNTER_NAMES)
        - set(counters)
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
    statement_valid = (
        intelligence.public_trust_visibility_statement
        == PUBLIC_TRUST_VISIBILITY_STATEMENT
        and intelligence.trust_visibility_non_authority_statement
        == PUBLIC_TRUST_VISIBILITY_NON_AUTHORITY_STATEMENT
    )
    return {
        "valid": (
            not enabled_flags
            and all(value == 0 for value in counters.values())
            and not descriptive_failures
            and not missing_disabled_counters
            and all(required_repository_states.values())
            and intelligence.publicly_transparent
            and statement_valid
        ),
        "enabled_flags": enabled_flags,
        "counters": counters,
        "descriptive_failures": descriptive_failures,
        "missing_disabled_counters": missing_disabled_counters,
        "repository_remains": required_repository_states,
        "publicly_transparent": intelligence.publicly_transparent,
        "public_trust_visibility_statement": (
            intelligence.public_trust_visibility_statement
        ),
        "trust_visibility_non_authority_statement": (
            intelligence.trust_visibility_non_authority_statement
        ),
        "statement_valid": statement_valid,
        "inherited_prohibition_count": len(intelligence.inherited_prohibitions),
        "inherited_constraint_count": len(intelligence.inherited_constraints),
        "explicit_limitation_count": len(intelligence.explicit_limitations),
    }


def validate_v4_5b_1_trust_visibility_foundation(
    intelligence: TrustVisibilityFoundationIntelligence | None = None,
) -> dict[str, Any]:
    if intelligence is None:
        intelligence = build_v4_5b_1_trust_visibility_foundation()
    validations = {
        "required_visibility": validate_required_trust_visibility_foundation(
            intelligence
        ),
        "ordering_stability": validate_trust_visibility_ordering_stability(
            intelligence
        ),
        "identity_integrity": validate_trust_visibility_identity_integrity(
            intelligence
        ),
        "evidence_visibility": validate_public_trust_evidence_visibility(
            intelligence
        ),
        "unsupported_state_visibility": (
            validate_unsupported_state_visibility_preservation(intelligence)
        ),
        "governance_transparency": (
            validate_governance_transparency_visibility_preservation(intelligence)
        ),
        "trust_summary": validate_trust_summary_stability(intelligence),
        "explainability_visibility": validate_public_explainability_visibility(
            intelligence
        ),
        "integrity_visibility": validate_public_integrity_visibility(intelligence),
        "lineage_and_provenance": validate_lineage_and_provenance_preservation(
            intelligence
        ),
        "serialization_hashing": validate_trust_visibility_serialization_and_hashing(
            intelligence
        ),
        "fail_visible_public_trust": validate_fail_visible_public_trust_diagnostics(
            intelligence
        ),
        "descriptive_only_guarantees": (
            validate_descriptive_only_public_trust_guarantees(intelligence)
        ),
    }
    failed_validations = sorted(
        name for name, result in validations.items() if not result["valid"]
    )
    return {
        "valid": not failed_validations,
        "foundation_status": (
            V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_STABLE
            if not failed_validations
            else V4_5B_1_TRUST_VISIBILITY_FOUNDATION_STATUS_BLOCKED
        ),
        "validation_error_count": len(failed_validations),
        "failed_validations": failed_validations,
        "validations": validations,
    }


def build_v4_5b_1_trust_visibility_foundation_report() -> dict[str, Any]:
    intelligence = build_v4_5b_1_trust_visibility_foundation()
    exported = export_v4_5b_1_trust_visibility_foundation(intelligence)
    validation = validate_v4_5b_1_trust_visibility_foundation(intelligence)
    required_visibility = validation["validations"]["required_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    evidence = validation["validations"]["evidence_visibility"]
    unsupported = validation["validations"]["unsupported_state_visibility"]
    transparency = validation["validations"]["governance_transparency"]
    trust_summary = validation["validations"]["trust_summary"]
    explainability = validation["validations"]["explainability_visibility"]
    integrity = validation["validations"]["integrity_visibility"]
    lineage_provenance = validation["validations"]["lineage_and_provenance"]
    fail_visible = validation["validations"]["fail_visible_public_trust"]
    descriptive_only = validation["validations"]["descriptive_only_guarantees"]
    counters = descriptive_only["counters"]

    deterministic_hash_evidence = {
        "trust_identity_hash": hash_trust_visibility_identity(
            intelligence.trust_identity
        ),
        "trust_visibility_foundation_hash": hash_v4_5b_1_trust_visibility_foundation(
            intelligence
        ),
        "trust_visibility_record_hashes": {
            record.trust_record_id: hash_trust_visibility_record(record)
            for record in sorted(
                intelligence.trust_visibility_records,
                key=lambda item: (item.deterministic_order, item.trust_record_id),
            )
        },
        "evidence_visibility_hashes": {
            record.evidence_visibility_id: hash_public_trust_evidence_visibility(record)
            for record in sorted(
                intelligence.evidence_visibility,
                key=lambda item: (item.deterministic_order, item.evidence_visibility_id),
            )
        },
        "unsupported_state_visibility_hashes": {
            record.unsupported_visibility_id: hash_unsupported_state_visibility(record)
            for record in sorted(
                intelligence.unsupported_state_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.unsupported_visibility_id,
                ),
            )
        },
        "governance_transparency_hashes": {
            record.transparency_visibility_id: (
                hash_governance_transparency_visibility(record)
            )
            for record in sorted(
                intelligence.governance_transparency_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.transparency_visibility_id,
                ),
            )
        },
        "trust_summary_hashes": {
            record.trust_summary_record_id: hash_trust_summary_record(record)
            for record in sorted(
                intelligence.trust_summaries,
                key=lambda item: (item.deterministic_order, item.trust_summary_record_id),
            )
        },
        "explainability_visibility_hashes": {
            record.explainability_visibility_id: (
                hash_public_explainability_visibility(record)
            )
            for record in sorted(
                intelligence.explainability_visibility,
                key=lambda item: (
                    item.deterministic_order,
                    item.explainability_visibility_id,
                ),
            )
        },
        "integrity_visibility_hashes": {
            record.integrity_visibility_id: hash_public_integrity_visibility(record)
            for record in sorted(
                intelligence.integrity_visibility,
                key=lambda item: (item.deterministic_order, item.integrity_visibility_id),
            )
        },
        "public_trust_diagnostic_hashes": {
            record.diagnostic_id: hash_public_trust_diagnostic_record(record)
            for record in sorted(
                intelligence.public_trust_diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "unsupported_public_trust_hashes": {
            record.state_id: hash_unsupported_public_trust_visibility(record)
            for record in sorted(
                intelligence.unsupported_public_trust_visibility,
                key=lambda item: (item.deterministic_order, item.state_id),
            )
        },
    }
    summary = {
        "trust_visibility_record_count": len(intelligence.trust_visibility_records),
        "evidence_visibility_count": len(intelligence.evidence_visibility),
        "unsupported_state_visibility_count": len(
            intelligence.unsupported_state_visibility
        ),
        "governance_transparency_visibility_count": len(
            intelligence.governance_transparency_visibility
        ),
        "trust_summary_count": len(intelligence.trust_summaries),
        "explainability_visibility_count": len(intelligence.explainability_visibility),
        "integrity_visibility_count": len(intelligence.integrity_visibility),
        "public_trust_diagnostic_count": len(intelligence.public_trust_diagnostics),
        "unsupported_public_trust_state_count": len(
            intelligence.unsupported_public_trust_visibility
        ),
        "evidence_counts": required_visibility["evidence_counts"],
        "unsupported_counts": required_visibility["unsupported_counts"],
        "transparency_counts": required_visibility["transparency_counts"],
        "summary_counts": required_visibility["summary_counts"],
        "explainability_counts": required_visibility["explainability_counts"],
        "integrity_counts": required_visibility["integrity_counts"],
        "diagnostic_counts": required_visibility["diagnostic_counts"],
        "unsupported_operational_counts": required_visibility[
            "unsupported_operational_counts"
        ],
        "deterministic_serialization_verified": serialization_hashing[
            "serialization_stable"
        ],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "evidence_visibility_stable": evidence["valid"],
        "unsupported_state_visibility_preserved": unsupported["valid"],
        "governance_transparency_visibility_preserved": transparency["valid"],
        "trust_summary_stable": trust_summary["valid"],
        "explainability_visibility_stable": explainability["valid"],
        "integrity_visibility_stable": integrity["valid"],
        "lineage_continuity_preserved": lineage_provenance[
            "lineage_continuity_preserved"
        ],
        "provenance_continuity_preserved": lineage_provenance[
            "provenance_continuity_preserved"
        ],
        "evidence_continuity_preserved": lineage_provenance[
            "evidence_continuity_preserved"
        ],
        "fail_visible_public_trust_diagnostics_verified": fail_visible["valid"],
        "descriptive_only_guarantees_verified": descriptive_only["valid"],
        "publicly_transparent": descriptive_only["publicly_transparent"],
        "public_trust_visibility_statement": (
            descriptive_only["public_trust_visibility_statement"]
        ),
        "trust_visibility_non_authority_statement": (
            descriptive_only["trust_visibility_non_authority_statement"]
        ),
        "inherited_prohibition_count": descriptive_only[
            "inherited_prohibition_count"
        ],
        "inherited_constraint_count": descriptive_only["inherited_constraint_count"],
        "explicit_limitation_count": descriptive_only["explicit_limitation_count"],
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
    }
    summary.update(counters)
    report = {
        "phase_id": V4_5B_1_TRUST_VISIBILITY_FOUNDATION_PHASE_ID,
        "schema_version": V4_5B_1_TRUST_VISIBILITY_FOUNDATION_REPORT_SCHEMA_VERSION,
        "generated_at": V4_5B_1_TRUST_VISIBILITY_FOUNDATION_GENERATED_AT,
        "purpose": V4_5B_1_TRUST_VISIBILITY_FOUNDATION_PURPOSE,
        "foundation_status": validation["foundation_status"],
        "summary": summary,
        "visibility": {
            "trust_visibility": trust_visibility_summary(
                intelligence.trust_visibility_records
            ),
            "public_trust_evidence": evidence_visibility_summary(
                intelligence.evidence_visibility
            ),
            "unsupported_states": unsupported_state_summary(
                intelligence.unsupported_state_visibility
            ),
            "governance_transparency": governance_transparency_summary(
                intelligence.governance_transparency_visibility
            ),
            "trust_summaries": trust_summary_visibility(
                intelligence.trust_summaries
            ),
            "explainability": explainability_summary(
                intelligence.explainability_visibility
            ),
            "integrity": integrity_summary(intelligence.integrity_visibility),
            "diagnostics": diagnostics_summary(
                intelligence.public_trust_diagnostics
            ),
            "unsupported_public_trust": unsupported_public_trust_summary(
                intelligence.unsupported_public_trust_visibility
            ),
            "descriptive_only": descriptive_only_public_trust_summary(
                intelligence
            ),
        },
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "validation": validation,
        "exported_intelligence": exported,
    }
    report["deterministic_report_hash"] = (
        deterministic_v4_5b_1_trust_visibility_foundation_hash(report)
    )
    return report


def contaminate_v4_5b_1_trust_visibility_foundation_for_non_operational_validation(
    intelligence: TrustVisibilityFoundationIntelligence | None = None,
) -> TrustVisibilityFoundationIntelligence:
    if intelligence is None:
        intelligence = build_v4_5b_1_trust_visibility_foundation()
    return replace(
        intelligence,
        runtime_execution_enabled=True,
        trust_authorization_enabled=True,
        trust_approval_enabled=True,
        trust_ranking_enabled=True,
        trust_recommendation_enabled=True,
        remediation_enabled=True,
        planner_integration_enabled=True,
    )
