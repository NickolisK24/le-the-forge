"""Audit for deterministic v4.4 boundary continuity and integrity certification."""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_continuity_integrity_hashing import (
    deterministic_boundary_continuity_integrity_hash,
    hash_boundary_continuity_integrity_certification,
    hash_certification_diagnostic_record,
    hash_certification_limitation_record,
    hash_certification_summary_record,
    hash_continuity_certification_identity,
    hash_continuity_certification_record,
    hash_integrity_certification_identity,
    hash_integrity_certification_record,
    hash_lineage_continuity_record,
    hash_phase_chain_certification_identity,
    hash_phase_evidence_reference,
    hash_provenance_continuity_record,
    hash_replay_rollback_safety_record,
)
from .v4_4_boundary_continuity_integrity_models import (
    CERTIFICATION_STATE_CERTIFIED,
    CERTIFICATION_STATE_CONTINUOUS,
    CERTIFICATION_STATE_DISCONTINUOUS,
    CERTIFICATION_STATE_INTEGRITY_BLOCKED,
    CERTIFICATION_STATE_INTEGRITY_SAFE,
    CERTIFICATION_STATE_INTEGRITY_WARNING,
    CERTIFICATION_STATE_PARTIALLY_CERTIFIED,
    CERTIFICATION_STATE_UNCERTIFIED,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_BLOCKED,
    V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_STABLE,
    BoundaryContinuityIntegrityCertification,
    default_boundary_continuity_integrity_certification,
)
from .v4_4_boundary_continuity_integrity_serialization import (
    export_boundary_continuity_integrity_certification,
    serialize_boundary_continuity_integrity_certification,
)
from .v4_4_boundary_continuity_integrity_visibility import (
    certification_diagnostic_summaries,
    certification_limitation_summaries,
    certification_summary_visibility,
    continuity_status_totals,
    count_combined_continuity_integrity_states,
    fail_visible_certification_diagnostics,
    governance_safe_certification_explainability,
    integrity_status_totals,
    lineage_continuity_visibility,
    phase_chain_certification_summaries,
    provenance_continuity_visibility,
    replay_rollback_safety_visibility,
    validate_required_continuity_integrity_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
        "runtime_activation_enabled",
        "runtime_activation_signal_enabled",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
        "readiness_approval_enabled",
    ),
    "enabled_dispatch_execution_count": (
        "dispatch_execution_enabled",
        "dispatch_enabled",
        "orchestration_dispatch_enabled",
    ),
    "enabled_routing_execution_count": (
        "routing_execution_enabled",
        "routing_enabled",
        "orchestration_routing_enabled",
    ),
    "enabled_scheduling_execution_count": (
        "scheduling_execution_enabled",
        "scheduling_enabled",
        "orchestration_scheduling_enabled",
    ),
    "enabled_recommendation_count": (
        "recommendation_enabled",
        "orchestration_recommendation_enabled",
    ),
    "enabled_decision_count": (
        "decision_enabled",
        "orchestration_decision_enabled",
    ),
    "enabled_certification_authorization_count": (
        "certification_authorization_enabled",
        "authorization_signal_enabled",
    ),
    "enabled_integrity_approval_count": (
        "integrity_approval_enabled",
        "production_readiness_inferred",
        "production_readiness_signal_enabled",
    ),
    "enabled_operational_mutation_count": (
        "operational_mutation_enabled",
        "runtime_mutation_enabled",
        "mutation_enabled",
    ),
}
PROHIBITED_BOOLEAN_FIELD_NAMES: tuple[str, ...] = tuple(
    sorted({field for fields in CAPABILITY_COUNTER_FIELD_MAP.values() for field in fields})
)


def build_v4_4_boundary_continuity_integrity() -> BoundaryContinuityIntegrityCertification:
    return default_boundary_continuity_integrity_certification()


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


def enabled_boundary_continuity_integrity_capability_flags(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(certification):
        item_id = (
            getattr(item, "continuity_certification_id", None)
            or getattr(item, "integrity_certification_id", None)
            or getattr(item, "phase_chain_id", None)
            or getattr(item, "evidence_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "integrity_id", None)
            or getattr(item, "limitation_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "safety_id", None)
            or getattr(item, "summary_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def boundary_continuity_integrity_capability_counter_values(
    certification: BoundaryContinuityIntegrityCertification,
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


def boundary_continuity_integrity_equal(
    left: BoundaryContinuityIntegrityCertification,
    right: BoundaryContinuityIntegrityCertification,
) -> bool:
    return serialize_boundary_continuity_integrity_certification(
        left
    ) == serialize_boundary_continuity_integrity_certification(right)


def validate_continuity_integrity_ordering_stability(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    order_groups = {
        "phase_evidence_references": tuple(
            item.deterministic_order for item in certification.phase_evidence_references
        ),
        "continuity_records": tuple(
            item.deterministic_order for item in certification.continuity_records
        ),
        "integrity_records": tuple(
            item.deterministic_order for item in certification.integrity_records
        ),
        "limitation_records": tuple(
            item.deterministic_order for item in certification.limitation_records
        ),
        "diagnostic_records": tuple(
            item.deterministic_order for item in certification.diagnostic_records
        ),
        "certification_summaries": tuple(
            item.deterministic_order for item in certification.certification_summaries
        ),
    }
    unordered_groups = [name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders]
    duplicate_groups = [name for name, orders in order_groups.items() if len(set(orders)) != len(orders)]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_continuity_integrity_serialization_and_hashing(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_continuity_integrity()
    serialized = serialize_boundary_continuity_integrity_certification(certification)
    rebuilt_serialized = serialize_boundary_continuity_integrity_certification(rebuilt)
    certification_hash = hash_boundary_continuity_integrity_certification(certification)
    rebuilt_hash = hash_boundary_continuity_integrity_certification(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and certification_hash == rebuilt_hash,
        "continuity_serialization_stable": serialized == rebuilt_serialized,
        "integrity_serialization_stable": serialized == rebuilt_serialized,
        "continuity_hashing_stable": certification_hash == rebuilt_hash,
        "integrity_hashing_stable": certification_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "certification_hash": certification_hash,
        "rebuilt_certification_hash": rebuilt_hash,
    }


def validate_continuity_integrity_visibility(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    required = validate_required_continuity_integrity_visibility(certification)
    phase = phase_chain_certification_summaries(certification)
    continuity = continuity_status_totals(certification)
    integrity = integrity_status_totals(certification)
    limitations = certification_limitation_summaries(certification)
    diagnostics = certification_diagnostic_summaries(certification)
    summaries = certification_summary_visibility(certification)
    explanation = governance_safe_certification_explainability(certification)
    return {
        "valid": (
            required["valid"]
            and phase["phase_evidence_reference_count"] == 6
            and phase["production_consumption_enabled_count"] == 0
            and not phase["runtime_activation_enabled"]
            and continuity["runtime_activation_enabled_count"] == 0
            and continuity["recommendation_enabled_count"] == 0
            and continuity["decision_enabled_count"] == 0
            and integrity["certification_authorization_enabled_count"] == 0
            and integrity["integrity_approval_enabled_count"] == 0
            and integrity["production_readiness_inferred_count"] == 0
            and integrity["planner_integration_enabled_count"] == 0
            and limitations["automatic_remediation_enabled_count"] == 0
            and limitations["automatic_repair_enabled_count"] == 0
            and diagnostics["authorization_enabled_count"] == 0
            and diagnostics["approval_enabled_count"] == 0
            and diagnostics["recommendation_enabled_count"] == 0
            and diagnostics["decision_enabled_count"] == 0
            and diagnostics["automatic_remediation_enabled_count"] == 0
            and diagnostics["automatic_repair_enabled_count"] == 0
            and summaries["authorization_signal_enabled_count"] == 0
            and summaries["production_readiness_signal_enabled_count"] == 0
            and summaries["runtime_activation_signal_enabled_count"] == 0
            and explanation["descriptive_only"]
            and explanation["non_operational"]
            and explanation["runtime_readiness_inference_disabled"]
        ),
        "combined_counts": count_combined_continuity_integrity_states(certification),
        "missing_states": required["missing_states"],
        "missing_fail_visible_states": required["missing_fail_visible_states"],
        "phase_chain": phase,
        "continuity": continuity,
        "integrity": integrity,
        "limitations": limitations,
        "diagnostics": diagnostics,
        "summaries": summaries,
        "explainability": explanation,
    }


def validate_continuity_integrity_replay_rollback_evidence(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    evidence = certification.replay_rollback_record
    expected = set(evidence.phase_evidence_ids)
    replay = set(evidence.replay_evidence_ids)
    rollback = set(evidence.rollback_evidence_ids)
    return {
        "valid": evidence.replay_safe and evidence.rollback_safe and replay == expected and rollback == expected,
        "expected_evidence_count": len(expected),
        "replay_safe_evidence_count": len(replay),
        "rollback_safe_evidence_count": len(rollback),
        "missing_replay_evidence_ids": sorted(expected - replay),
        "missing_rollback_evidence_ids": sorted(expected - rollback),
        "replay_safe": evidence.replay_safe,
        "rollback_safe": evidence.rollback_safe,
    }


def validate_continuity_integrity_provenance_lineage(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    provenance = certification.provenance_record
    lineage = certification.lineage_record
    return {
        "valid": (
            provenance.provenance_continuity_preserved
            and lineage.lineage_continuity_preserved
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
            and not provenance.production_consumption_enabled
            and not lineage.operational_mutation_enabled
        ),
        "provenance_continuity_preserved": provenance.provenance_continuity_preserved,
        "lineage_continuity_preserved": lineage.lineage_continuity_preserved,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
        "production_consumption_enabled": provenance.production_consumption_enabled,
        "operational_mutation_enabled": lineage.operational_mutation_enabled,
    }


def validate_boundary_continuity_integrity_non_operational(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    counters = boundary_continuity_integrity_capability_counter_values(certification)
    enabled_flags = enabled_boundary_continuity_integrity_capability_flags(certification)
    root_disabled = {
        "descriptive_only": certification.descriptive_only,
        "non_operational": certification.non_operational,
        "non_authoritative": certification.non_authoritative,
        "non_authorizing": certification.non_authorizing,
        "non_approving": certification.non_approving,
        "non_recommending": certification.non_recommending,
        "non_deciding": certification.non_deciding,
        "non_remediating": certification.non_remediating,
        "non_mutating": certification.non_mutating,
        "runtime_readiness_inference_disabled": certification.runtime_readiness_inference_disabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": not certification.production_consumption_enabled,
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "operational_mutation_disabled": not certification.operational_mutation_enabled,
        "traversal_execution_disabled": not certification.traversal_execution_enabled,
        "sequencing_execution_disabled": not certification.sequencing_execution_enabled,
        "ranking_disabled": not certification.ranking_enabled,
        "scoring_disabled": not certification.scoring_enabled,
        "selection_disabled": not certification.selection_enabled,
        "optimization_disabled": not certification.optimization_enabled,
        "automatic_remediation_disabled": not certification.automatic_remediation_enabled,
        "automatic_repair_disabled": not certification.automatic_repair_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_continuity_integrity(
    certification: BoundaryContinuityIntegrityCertification,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_continuity_integrity_ordering_stability(certification),
        "serialization_hashing": validate_continuity_integrity_serialization_and_hashing(
            certification
        ),
        "visibility": validate_continuity_integrity_visibility(certification),
        "replay_rollback": validate_continuity_integrity_replay_rollback_evidence(
            certification
        ),
        "provenance_lineage": validate_continuity_integrity_provenance_lineage(
            certification
        ),
        "non_operational": validate_boundary_continuity_integrity_non_operational(
            certification
        ),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_continuity_integrity_report() -> dict[str, Any]:
    certification = build_v4_4_boundary_continuity_integrity()
    exported = export_boundary_continuity_integrity_certification(certification)
    validation = validate_boundary_continuity_integrity(certification)
    visibility = validation["validations"]["visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    non_operational = validation["validations"]["non_operational"]
    combined_counts = visibility["combined_counts"]
    continuity = visibility["continuity"]
    integrity = visibility["integrity"]
    limitations = visibility["limitations"]
    diagnostics = visibility["diagnostics"]
    summaries = visibility["summaries"]
    deterministic_hash_evidence = {
        "continuity_identity_hash": hash_continuity_certification_identity(
            certification.continuity_identity
        ),
        "integrity_identity_hash": hash_integrity_certification_identity(
            certification.integrity_identity
        ),
        "phase_chain_hash": hash_phase_chain_certification_identity(
            certification.phase_chain_identity
        ),
        "certification_hash": hash_boundary_continuity_integrity_certification(
            certification
        ),
        "provenance_hash": hash_provenance_continuity_record(certification.provenance_record),
        "lineage_hash": hash_lineage_continuity_record(certification.lineage_record),
        "replay_rollback_hash": hash_replay_rollback_safety_record(
            certification.replay_rollback_record
        ),
        "phase_evidence_hashes": {
            record.evidence_id: hash_phase_evidence_reference(record)
            for record in sorted(
                certification.phase_evidence_references,
                key=lambda item: item.deterministic_order,
            )
        },
        "continuity_hashes": {
            record.continuity_id: hash_continuity_certification_record(record)
            for record in sorted(
                certification.continuity_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "integrity_hashes": {
            record.integrity_id: hash_integrity_certification_record(record)
            for record in sorted(
                certification.integrity_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "limitation_hashes": {
            record.limitation_id: hash_certification_limitation_record(record)
            for record in sorted(
                certification.limitation_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "diagnostic_hashes": {
            record.diagnostic_id: hash_certification_diagnostic_record(record)
            for record in sorted(
                certification.diagnostic_records,
                key=lambda item: item.deterministic_order,
            )
        },
        "summary_hashes": {
            record.summary_id: hash_certification_summary_record(record)
            for record in sorted(
                certification.certification_summaries,
                key=lambda item: item.deterministic_order,
            )
        },
    }
    summary = {
        "phase_evidence_reference_count": len(certification.phase_evidence_references),
        "continuity_certification_record_count": len(certification.continuity_records),
        "integrity_certification_record_count": len(certification.integrity_records),
        "certification_summary_count": len(certification.certification_summaries),
        "certified_count": combined_counts[CERTIFICATION_STATE_CERTIFIED],
        "partially_certified_count": combined_counts[CERTIFICATION_STATE_PARTIALLY_CERTIFIED],
        "uncertified_count": combined_counts[CERTIFICATION_STATE_UNCERTIFIED],
        "continuous_count": combined_counts[CERTIFICATION_STATE_CONTINUOUS],
        "discontinuous_count": combined_counts[CERTIFICATION_STATE_DISCONTINUOUS],
        "integrity_safe_count": combined_counts[CERTIFICATION_STATE_INTEGRITY_SAFE],
        "integrity_warning_count": combined_counts[CERTIFICATION_STATE_INTEGRITY_WARNING],
        "integrity_blocked_count": combined_counts[CERTIFICATION_STATE_INTEGRITY_BLOCKED],
        "replay_safe_count": combined_counts["replay_safe"],
        "rollback_safe_count": combined_counts["rollback_safe"],
        "provenance_safe_count": combined_counts["provenance_safe"],
        "lineage_safe_count": combined_counts["lineage_safe"],
        "limitation_count": limitations["limitation_count"],
        "fail_visible_limitation_count": limitations["fail_visible_limitation_count"],
        "diagnostic_record_count": diagnostics["diagnostic_record_count"],
        "fail_visible_diagnostic_count": diagnostics["fail_visible_diagnostic_count"],
        "combined_state_counts": combined_counts,
        "continuity_state_counts": continuity["continuity_state_counts"],
        "integrity_state_counts": integrity["integrity_state_counts"],
        "diagnostic_severity_totals": diagnostics["severity_counts"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "continuity_serialization_verified": (
            serialization_hashing["continuity_serialization_stable"]
        ),
        "integrity_serialization_verified": (
            serialization_hashing["integrity_serialization_stable"]
        ),
        "continuity_hashing_verified": serialization_hashing["continuity_hashing_stable"],
        "integrity_hashing_verified": serialization_hashing["integrity_hashing_stable"],
        "phase_evidence_reference_stability_verified": (
            visibility["phase_chain"]["phase_evidence_reference_count"] == 6
        ),
        "certification_limitation_visibility_preserved": (
            limitations["fail_visible_limitation_count"] == limitations["limitation_count"]
        ),
        "fail_visible_diagnostic_preserved": diagnostics["fail_visible_diagnostic_count"] > 0,
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "provenance_continuity_verified": (
            provenance_lineage["provenance_continuity_preserved"]
        ),
        "lineage_continuity_verified": provenance_lineage["lineage_continuity_preserved"],
        "governance_safe_certification_verified": validation["valid"],
        "non_operational_certification_verified": non_operational["valid"],
        "authorization_behavior_enabled": False,
        "approval_behavior_enabled": False,
        "recommendation_behavior_enabled": False,
        "decision_behavior_enabled": False,
        "runtime_readiness_inferred": False,
        "validation_error_count": validation["validation_error_count"],
        "remaining_warning_count": 0,
        "remaining_blocker_count": 0,
        **non_operational["counters"],
        "planner_integration_enabled": certification.planner_integration_enabled,
        "production_consumption_enabled": certification.production_consumption_enabled,
        "runtime_mutation_enabled": certification.runtime_mutation_enabled,
        "operational_mutation_enabled": certification.operational_mutation_enabled,
    }
    report: dict[str, Any] = {
        "report_schema_version": V4_4_BOUNDARY_CONTINUITY_INTEGRITY_REPORT_SCHEMA_VERSION,
        "phase_id": certification.continuity_identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_CONTINUITY_INTEGRITY_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_continuity_integrity_certification": exported,
        "phase_chain_certification_visibility": visibility["phase_chain"],
        "continuity_certification_visibility": continuity,
        "integrity_certification_visibility": integrity,
        "certification_limitation_visibility": limitations,
        "certification_diagnostic_visibility": diagnostics,
        "certification_summary_visibility": summaries,
        "fail_visible_certification_diagnostics": fail_visible_certification_diagnostics(
            certification
        ),
        "provenance_continuity_evidence": provenance_continuity_visibility(certification),
        "lineage_continuity_evidence": lineage_continuity_visibility(certification),
        "replay_safe_evidence": replay_rollback_safety_visibility(certification),
        "rollback_safe_evidence": replay_rollback_safety_visibility(certification),
        "governance_safe_certification_explainability": visibility["explainability"],
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": {
            "continuity_serialization_stable": (
                serialization_hashing["continuity_serialization_stable"]
            ),
            "integrity_serialization_stable": (
                serialization_hashing["integrity_serialization_stable"]
            ),
            "continuity_hashing_stable": (
                serialization_hashing["continuity_hashing_stable"]
            ),
            "integrity_hashing_stable": serialization_hashing["integrity_hashing_stable"],
            "serialization_length": serialization_hashing["serialization_length"],
            "certification_hash": serialization_hashing["certification_hash"],
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_boundary_continuity_integrity_hash(
        report
    )
    return report


def contaminate_boundary_continuity_integrity_for_non_operational_validation(
    certification: BoundaryContinuityIntegrityCertification,
) -> BoundaryContinuityIntegrityCertification:
    contaminated_continuity = replace(
        certification.continuity_records[0],
        runtime_activation_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
    )
    contaminated_integrity = replace(
        certification.integrity_records[0],
        certification_authorization_enabled=True,
        integrity_approval_enabled=True,
        production_readiness_inferred=True,
    )
    contaminated_summary = replace(
        certification.certification_summaries[0],
        authorization_signal_enabled=True,
        production_readiness_signal_enabled=True,
        runtime_activation_signal_enabled=True,
    )
    return replace(
        certification,
        continuity_records=(contaminated_continuity,) + certification.continuity_records[1:],
        integrity_records=(contaminated_integrity,) + certification.integrity_records[1:],
        certification_summaries=(contaminated_summary,) + certification.certification_summaries[1:],
        runtime_execution_enabled=True,
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
        scheduling_execution_enabled=True,
        recommendation_enabled=True,
        decision_enabled=True,
        certification_authorization_enabled=True,
        integrity_approval_enabled=True,
        operational_mutation_enabled=True,
    )
