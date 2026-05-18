"""Deterministic audit for v4.4 boundary intelligence foundations.

The audit certifies descriptive boundary intelligence evidence only. It never
executes orchestration, authorizes operations, approves readiness, dispatches,
routes, traverses, schedules, sequences, recommends, decides, integrates
planners, consumes production bundles, remediates, repairs, infers hidden
semantics, or mutates runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_intelligence_foundations_hashing import (
    deterministic_boundary_intelligence_hash,
    hash_boundary_continuity_metadata,
    hash_boundary_diagnostic_record,
    hash_boundary_explainability_record,
    hash_boundary_governance_visibility_summary,
    hash_boundary_intelligence_foundations,
    hash_boundary_intelligence_identity,
    hash_boundary_intelligence_record,
    hash_boundary_lineage_metadata,
    hash_boundary_provenance_metadata,
)
from .v4_4_boundary_intelligence_foundations_models import (
    BOUNDARY_INTELLIGENCE_STATES,
    BOUNDARY_STATE_BLOCKED,
    BOUNDARY_STATE_CONFLICTING,
    BOUNDARY_STATE_PROHIBITED,
    BOUNDARY_STATE_STALE,
    BOUNDARY_STATE_SUPPORTED,
    BOUNDARY_STATE_UNSUPPORTED,
    FAIL_VISIBLE_BOUNDARY_STATES,
    V4_4_BOUNDARY_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_INTELLIGENCE_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_INTELLIGENCE_STATUS_BLOCKED,
    V4_4_BOUNDARY_INTELLIGENCE_STATUS_STABLE,
    BoundaryIntelligenceFoundations,
    default_boundary_intelligence_foundations,
)
from .v4_4_boundary_intelligence_foundations_serialization import (
    export_boundary_intelligence_foundations,
    serialize_boundary_intelligence_foundations,
)
from .v4_4_boundary_intelligence_foundations_visibility import (
    aggregate_boundary_diagnostics,
    aggregate_explainability_visibility,
    aggregate_fail_visible_findings,
    count_boundary_classification_states,
    count_boundary_visibility_states,
    fail_visible_summary,
    governance_safe_boundary_summaries,
    validate_governance_visibility_summaries,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
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
        "orchestration_dispatch_enabled",
        "dispatch_enabled",
    ),
    "enabled_routing_execution_count": (
        "routing_execution_enabled",
        "orchestration_routing_enabled",
        "routing_enabled",
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


def build_v4_4_boundary_intelligence_foundations() -> BoundaryIntelligenceFoundations:
    return default_boundary_intelligence_foundations()


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


def enabled_boundary_capability_flags(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(foundations):
        item_id = (
            getattr(item, "boundary_id", None)
            or getattr(item, "classification_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "integrity_id", None)
            or getattr(item, "summary_id", None)
            or getattr(item, "finding_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "boundary_intelligence_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def boundary_capability_counter_values(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, int]:
    objects = tuple(_iter_dataclass_objects(foundations))
    counters: dict[str, int] = {}
    for counter_name, field_names in CAPABILITY_COUNTER_FIELD_MAP.items():
        counters[counter_name] = sum(
            1
            for item in objects
            for field_name in field_names
            if bool(getattr(item, field_name, False))
        )
    return counters


def boundary_intelligence_foundations_equal(
    left: BoundaryIntelligenceFoundations,
    right: BoundaryIntelligenceFoundations,
) -> bool:
    return serialize_boundary_intelligence_foundations(left) == serialize_boundary_intelligence_foundations(right)


def validate_boundary_ordering_stability(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    order_groups = {
        "classifications": tuple(item.deterministic_order for item in foundations.classifications),
        "boundary_records": tuple(item.deterministic_order for item in foundations.boundary_records),
        "scope_visibility": tuple(item.deterministic_order for item in foundations.scope_visibility),
        "segmentation_visibility": tuple(
            item.deterministic_order for item in foundations.segmentation_visibility
        ),
        "diagnostics": tuple(item.deterministic_order for item in foundations.diagnostics),
        "explainability": tuple(item.deterministic_order for item in foundations.explainability),
        "integrity_visibility": tuple(
            item.deterministic_order for item in foundations.integrity_visibility
        ),
        "governance_visibility_summaries": tuple(
            item.deterministic_order for item in foundations.governance_visibility_summaries
        ),
        "fail_visible_findings": tuple(
            item.deterministic_order for item in foundations.fail_visible_findings
        ),
    }
    unordered_groups = [
        name for name, orders in order_groups.items() if tuple(sorted(orders)) != orders
    ]
    duplicate_groups = [
        name for name, orders in order_groups.items() if len(set(orders)) != len(orders)
    ]
    return {
        "valid": not unordered_groups and not duplicate_groups,
        "unordered_groups": unordered_groups,
        "duplicate_order_groups": duplicate_groups,
        "order_groups": {name: list(orders) for name, orders in order_groups.items()},
    }


def validate_boundary_serialization_and_hashing(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_intelligence_foundations()
    serialized = serialize_boundary_intelligence_foundations(foundations)
    rebuilt_serialized = serialize_boundary_intelligence_foundations(rebuilt)
    foundation_hash = hash_boundary_intelligence_foundations(foundations)
    rebuilt_hash = hash_boundary_intelligence_foundations(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and foundation_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": foundation_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "foundation_hash": foundation_hash,
        "rebuilt_foundation_hash": rebuilt_hash,
    }


def validate_boundary_state_visibility(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    record_counts = count_boundary_visibility_states(foundations.boundary_records)
    classification_counts = count_boundary_classification_states(foundations)
    governance_validation = validate_governance_visibility_summaries(
        foundations.governance_visibility_summaries,
        foundations.boundary_records,
    )
    finding_aggregation = aggregate_fail_visible_findings(foundations.fail_visible_findings)
    required_state_gaps = [
        state
        for state in BOUNDARY_INTELLIGENCE_STATES
        if record_counts[state] <= 0 or classification_counts[state] <= 0
    ]
    fail_visible_gaps = [
        state
        for state in FAIL_VISIBLE_BOUNDARY_STATES
        if finding_aggregation["state_counts"][state] <= 0
    ]
    return {
        "valid": (
            not required_state_gaps
            and not fail_visible_gaps
            and governance_validation["valid"]
            and finding_aggregation["fail_visible"]
            and finding_aggregation["hidden_inference_used_count"] == 0
        ),
        "record_counts": record_counts,
        "classification_counts": classification_counts,
        "required_state_gaps": required_state_gaps,
        "fail_visible_state_gaps": fail_visible_gaps,
        "governance_validation": governance_validation,
        "fail_visible_findings": finding_aggregation,
        "prohibited_visibility_count": finding_aggregation["state_counts"][BOUNDARY_STATE_PROHIBITED],
        "unsupported_visibility_count": finding_aggregation["state_counts"][BOUNDARY_STATE_UNSUPPORTED],
        "blocked_visibility_count": finding_aggregation["state_counts"][BOUNDARY_STATE_BLOCKED],
        "stale_visibility_count": finding_aggregation["state_counts"][BOUNDARY_STATE_STALE],
        "conflicting_visibility_count": finding_aggregation["state_counts"][BOUNDARY_STATE_CONFLICTING],
    }


def validate_boundary_replay_rollback_evidence(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    continuity = foundations.continuity_metadata
    deterministic_ids = set(continuity.deterministic_evidence_ids)
    replay_ids = set(continuity.replay_evidence_ids)
    rollback_ids = set(continuity.rollback_evidence_ids)
    boundary_ids = {record.boundary_id for record in foundations.boundary_records}
    return {
        "valid": (
            continuity.replay_safe
            and continuity.rollback_safe
            and deterministic_ids == boundary_ids
            and replay_ids == boundary_ids
            and rollback_ids == boundary_ids
        ),
        "deterministic_evidence_count": len(deterministic_ids),
        "replay_safe_evidence_count": len(replay_ids),
        "rollback_safe_evidence_count": len(rollback_ids),
        "missing_replay_evidence_ids": sorted(boundary_ids - replay_ids),
        "missing_rollback_evidence_ids": sorted(boundary_ids - rollback_ids),
        "replay_safe": continuity.replay_safe,
        "rollback_safe": continuity.rollback_safe,
    }


def validate_boundary_continuity_metadata(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    continuity = foundations.continuity_metadata
    provenance = foundations.provenance_metadata
    lineage = foundations.lineage_metadata
    return {
        "valid": (
            continuity.provenance_continuity_preserved
            and continuity.lineage_continuity_preserved
            and provenance.provenance_continuity_preserved
            and lineage.lineage_continuity_preserved
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
        ),
        "provenance_continuity_preserved": provenance.provenance_continuity_preserved,
        "lineage_continuity_preserved": lineage.lineage_continuity_preserved,
        "continuity_provenance_preserved": continuity.provenance_continuity_preserved,
        "continuity_lineage_preserved": continuity.lineage_continuity_preserved,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
    }


def validate_boundary_non_operational(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    counters = boundary_capability_counter_values(foundations)
    enabled_flags = enabled_boundary_capability_flags(foundations)
    root_disabled = {
        "descriptive_only": foundations.descriptive_only,
        "non_operational": foundations.non_operational,
        "non_executing": foundations.non_executing,
        "non_authorizing": foundations.non_authorizing,
        "non_approving": foundations.non_approving,
        "non_dispatching": foundations.non_dispatching,
        "non_routing": foundations.non_routing,
        "non_mutating": foundations.non_mutating,
        "planner_integration_disabled": not foundations.planner_integration_enabled,
        "production_consumption_disabled": not foundations.production_consumption_enabled,
        "runtime_mutation_disabled": not foundations.runtime_mutation_enabled,
        "operational_mutation_disabled": not foundations.operational_mutation_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_diagnostics_and_explainability(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    diagnostics = aggregate_boundary_diagnostics(foundations.diagnostics)
    explainability = aggregate_explainability_visibility(foundations.explainability)
    return {
        "valid": (
            diagnostics["descriptive_only"]
            and diagnostics["auto_remediation_enabled_count"] == 0
            and diagnostics["repair_enabled_count"] == 0
            and explainability["explainability_first"]
            and explainability["descriptive_only"]
            and explainability["recommendation_enabled_count"] == 0
            and explainability["decision_enabled_count"] == 0
        ),
        "diagnostics": diagnostics,
        "explainability": explainability,
    }


def validate_boundary_intelligence_foundations(
    foundations: BoundaryIntelligenceFoundations,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_boundary_ordering_stability(foundations),
        "serialization_hashing": validate_boundary_serialization_and_hashing(foundations),
        "state_visibility": validate_boundary_state_visibility(foundations),
        "replay_rollback": validate_boundary_replay_rollback_evidence(foundations),
        "continuity": validate_boundary_continuity_metadata(foundations),
        "non_operational": validate_boundary_non_operational(foundations),
        "diagnostics_explainability": validate_boundary_diagnostics_and_explainability(foundations),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_intelligence_foundations_report() -> dict[str, Any]:
    foundations = build_v4_4_boundary_intelligence_foundations()
    exported = export_boundary_intelligence_foundations(foundations)
    validation = validate_boundary_intelligence_foundations(foundations)
    state_validation = validation["validations"]["state_visibility"]
    non_operational = validation["validations"]["non_operational"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    replay_rollback = validation["validations"]["replay_rollback"]
    continuity = validation["validations"]["continuity"]
    diagnostics_explainability = validation["validations"]["diagnostics_explainability"]
    state_counts = state_validation["record_counts"]
    fail_visible = fail_visible_summary(foundations)
    deterministic_hash_evidence = {
        "identity_hash": hash_boundary_intelligence_identity(foundations.identity),
        "foundation_hash": hash_boundary_intelligence_foundations(foundations),
        "continuity_metadata_hash": hash_boundary_continuity_metadata(foundations.continuity_metadata),
        "provenance_metadata_hash": hash_boundary_provenance_metadata(foundations.provenance_metadata),
        "lineage_metadata_hash": hash_boundary_lineage_metadata(foundations.lineage_metadata),
        "record_hashes": {
            record.boundary_id: hash_boundary_intelligence_record(record)
            for record in sorted(
                foundations.boundary_records,
                key=lambda item: (item.deterministic_order, item.boundary_id),
            )
        },
        "diagnostic_hashes": {
            diagnostic.diagnostic_id: hash_boundary_diagnostic_record(diagnostic)
            for diagnostic in sorted(
                foundations.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "explainability_hashes": {
            explanation.explainability_id: hash_boundary_explainability_record(explanation)
            for explanation in sorted(
                foundations.explainability,
                key=lambda item: (item.deterministic_order, item.explainability_id),
            )
        },
        "governance_visibility_summary_hashes": {
            summary.summary_id: hash_boundary_governance_visibility_summary(summary)
            for summary in sorted(
                foundations.governance_visibility_summaries,
                key=lambda item: (item.deterministic_order, item.summary_id),
            )
        },
    }
    deterministic_serialization_evidence = {
        "serialization_stable": serialization_hashing["serialization_stable"],
        "hashing_stable": serialization_hashing["hashing_stable"],
        "serialization_length": serialization_hashing["serialization_length"],
        "foundation_hash": serialization_hashing["foundation_hash"],
    }
    summary = {
        "boundary_intelligence_record_count": len(foundations.boundary_records),
        "boundary_intelligence_classification_count": len(foundations.classifications),
        "visibility_classification_counts": state_validation["classification_counts"],
        "supported_visibility_count": state_counts[BOUNDARY_STATE_SUPPORTED],
        "unsupported_visibility_count": state_counts[BOUNDARY_STATE_UNSUPPORTED],
        "prohibited_visibility_count": state_counts[BOUNDARY_STATE_PROHIBITED],
        "blocked_visibility_count": state_counts[BOUNDARY_STATE_BLOCKED],
        "stale_visibility_count": state_counts[BOUNDARY_STATE_STALE],
        "conflicting_visibility_count": state_counts[BOUNDARY_STATE_CONFLICTING],
        "fail_visible_finding_count": fail_visible["fail_visible_finding_count"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "deterministic_serialization_verified": serialization_hashing["serialization_stable"],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "provenance_continuity_verified": continuity["provenance_continuity_preserved"],
        "lineage_continuity_verified": continuity["lineage_continuity_preserved"],
        "governance_safe_certification_verified": validation["valid"],
        "non_operational_certification_verified": non_operational["valid"],
        "descriptive_only_enforced": foundations.descriptive_only,
        "diagnostics_visibility_verified": diagnostics_explainability["diagnostics"]["descriptive_only"],
        "explainability_visibility_verified": diagnostics_explainability["explainability"]["explainability_first"],
        "validation_error_count": validation["validation_error_count"],
        "remaining_warning_count": 0,
        "remaining_blocker_count": 0,
        **non_operational["counters"],
        "planner_integration_enabled": foundations.planner_integration_enabled,
        "production_consumption_enabled": foundations.production_consumption_enabled,
        "runtime_mutation_enabled": foundations.runtime_mutation_enabled,
        "operational_mutation_enabled": foundations.operational_mutation_enabled,
    }
    report: dict[str, Any] = {
        "report_schema_version": V4_4_BOUNDARY_INTELLIGENCE_REPORT_SCHEMA_VERSION,
        "phase_id": foundations.identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_INTELLIGENCE_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_INTELLIGENCE_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_intelligence_foundations": exported,
        "governance_visibility": {
            "summaries": governance_safe_boundary_summaries(foundations),
            "state_visibility_validation": state_validation,
        },
        "diagnostics_visibility": diagnostics_explainability["diagnostics"],
        "explainability_visibility": diagnostics_explainability["explainability"],
        "fail_visible_visibility": fail_visible,
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": deterministic_serialization_evidence,
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "provenance_continuity_evidence": {
            "provenance_metadata": exported["provenance_metadata"],
            "provenance_continuity_verified": continuity["provenance_continuity_preserved"],
            "hidden_source_inference_used": continuity["hidden_source_inference_used"],
        },
        "lineage_continuity_evidence": {
            "lineage_metadata": exported["lineage_metadata"],
            "lineage_continuity_verified": continuity["lineage_continuity_preserved"],
            "ambiguous_lineage_inferred": continuity["ambiguous_lineage_inferred"],
        },
        "governance_safe_certification_evidence": {
            "valid": validation["valid"],
            "descriptive_only": foundations.descriptive_only,
            "non_operational": foundations.non_operational,
            "explicit_limitations": sorted(foundations.explicit_limitations),
            "explicit_prohibitions": sorted(foundations.explicit_prohibitions),
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_boundary_intelligence_hash(report)
    return report


def contaminate_foundations_for_non_operational_validation(
    foundations: BoundaryIntelligenceFoundations,
) -> BoundaryIntelligenceFoundations:
    first_record = replace(foundations.boundary_records[0], runtime_execution_enabled=True)
    return replace(
        foundations,
        boundary_records=(first_record,) + foundations.boundary_records[1:],
        orchestration_authorization_enabled=True,
        orchestration_approval_enabled=True,
        dispatch_execution_enabled=True,
        routing_execution_enabled=True,
        operational_mutation_enabled=True,
    )
