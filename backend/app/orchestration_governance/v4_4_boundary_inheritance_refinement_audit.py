"""Audit for deterministic v4.4 boundary inheritance refinement.

The audit validates descriptive inheritance/refinement intelligence only. It
never executes orchestration, authorizes or approves orchestration, dispatches,
routes, traverses, schedules, sequences, recommends, decides, integrates
planners, consumes production bundles, repairs, remediates, infers hidden
authority, or mutates runtime or operational state.
"""

from __future__ import annotations

from dataclasses import is_dataclass, replace
from typing import Any, Iterable

from .v4_4_boundary_inheritance_refinement_hashing import (
    deterministic_boundary_inheritance_hash,
    hash_boundary_ancestry_visibility,
    hash_boundary_inheritance_identity,
    hash_boundary_inheritance_refinement_intelligence,
    hash_continuity_propagation_metadata,
    hash_inheritance_fail_visible_finding,
    hash_inheritance_relationship,
    hash_lineage_propagation_metadata,
    hash_provenance_propagation_metadata,
    hash_refinement_diagnostic,
    hash_refinement_explainability,
    hash_refinement_lineage_continuity,
    hash_refinement_relationship,
)
from .v4_4_boundary_inheritance_refinement_models import (
    BOUNDARY_INHERITANCE_STATES,
    FAIL_VISIBLE_INHERITANCE_STATES,
    INHERITANCE_STATE_AMBIGUOUS,
    INHERITANCE_STATE_CONFLICTING,
    INHERITANCE_STATE_INHERITED,
    INHERITANCE_STATE_PROHIBITED,
    INHERITANCE_STATE_REFINED,
    INHERITANCE_STATE_STALE,
    INHERITANCE_STATE_SUPPORTED,
    INHERITANCE_STATE_UNSUPPORTED,
    V4_4_BOUNDARY_INHERITANCE_DISABLED_COUNTER_NAMES,
    V4_4_BOUNDARY_INHERITANCE_REPORT_SCHEMA_VERSION,
    V4_4_BOUNDARY_INHERITANCE_STATUS_BLOCKED,
    V4_4_BOUNDARY_INHERITANCE_STATUS_STABLE,
    BoundaryInheritanceRefinementIntelligence,
    default_boundary_inheritance_refinement_intelligence,
)
from .v4_4_boundary_inheritance_refinement_serialization import (
    export_boundary_inheritance_refinement_intelligence,
    serialize_boundary_inheritance_refinement_intelligence,
)
from .v4_4_boundary_inheritance_refinement_visibility import (
    aggregate_refinement_diagnostics,
    ancestry_depth_visibility,
    continuity_propagation_visibility,
    count_combined_relationship_states,
    count_inheritance_relationship_states,
    count_refinement_relationship_states,
    fail_visible_ambiguity_summaries,
    fail_visible_inheritance_summary,
    governance_safe_refinement_explainability,
    inheritance_chain_summaries,
    inheritance_conflict_visibility,
    lineage_propagation_visibility,
    prohibited_inheritance_visibility,
    provenance_propagation_visibility,
    refinement_ancestry_summaries,
    refinement_drift_visibility,
    unsupported_inheritance_visibility,
    validate_required_state_visibility,
)


CAPABILITY_COUNTER_FIELD_MAP: dict[str, tuple[str, ...]] = {
    "enabled_runtime_execution_count": (
        "runtime_execution_enabled",
        "orchestration_runtime_behavior_enabled",
        "orchestration_execution_enabled",
        "execution_enabled",
        "execution_authority",
        "execution_capability",
    ),
    "enabled_orchestration_authorization_count": (
        "orchestration_authorization_enabled",
        "authorization_enabled",
        "authorization_capability",
    ),
    "enabled_orchestration_approval_count": (
        "orchestration_approval_enabled",
        "approval_enabled",
        "approval_capability",
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
        "routing_capability",
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


def build_v4_4_boundary_inheritance_refinement() -> BoundaryInheritanceRefinementIntelligence:
    return default_boundary_inheritance_refinement_intelligence()


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


def enabled_inheritance_capability_flags(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, list[str]]:
    enabled: dict[str, list[str]] = {}
    for item in _iter_dataclass_objects(intelligence):
        item_id = (
            getattr(item, "inheritance_id", None)
            or getattr(item, "refinement_id", None)
            or getattr(item, "ancestry_id", None)
            or getattr(item, "diagnostic_id", None)
            or getattr(item, "explainability_id", None)
            or getattr(item, "finding_id", None)
            or getattr(item, "continuity_id", None)
            or getattr(item, "provenance_id", None)
            or getattr(item, "lineage_id", None)
            or getattr(item, "inheritance_intelligence_id", item.__class__.__name__)
        )
        for field_name in PROHIBITED_BOOLEAN_FIELD_NAMES:
            if bool(getattr(item, field_name, False)):
                enabled.setdefault(str(item_id), []).append(field_name)
    return {key: sorted(values) for key, values in sorted(enabled.items())}


def inheritance_capability_counter_values(
    intelligence: BoundaryInheritanceRefinementIntelligence,
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


def boundary_inheritance_refinement_equal(
    left: BoundaryInheritanceRefinementIntelligence,
    right: BoundaryInheritanceRefinementIntelligence,
) -> bool:
    return (
        serialize_boundary_inheritance_refinement_intelligence(left)
        == serialize_boundary_inheritance_refinement_intelligence(right)
    )


def validate_inheritance_ordering_stability(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    order_groups = {
        "inheritance_relationships": tuple(
            item.deterministic_order for item in intelligence.inheritance_relationships
        ),
        "refinement_relationships": tuple(
            item.deterministic_order for item in intelligence.refinement_relationships
        ),
        "ancestry_visibility": tuple(
            item.deterministic_order for item in intelligence.ancestry_visibility
        ),
        "parent_child_refinement_visibility": tuple(
            item.deterministic_order for item in intelligence.parent_child_refinement_visibility
        ),
        "refinement_lineage_continuity": tuple(
            item.deterministic_order for item in intelligence.refinement_lineage_continuity
        ),
        "diagnostics": tuple(item.deterministic_order for item in intelligence.diagnostics),
        "explainability": tuple(item.deterministic_order for item in intelligence.explainability),
        "fail_visible_findings": tuple(
            item.deterministic_order for item in intelligence.fail_visible_findings
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


def validate_inheritance_serialization_and_hashing(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    rebuilt = build_v4_4_boundary_inheritance_refinement()
    serialized = serialize_boundary_inheritance_refinement_intelligence(intelligence)
    rebuilt_serialized = serialize_boundary_inheritance_refinement_intelligence(rebuilt)
    intelligence_hash = hash_boundary_inheritance_refinement_intelligence(intelligence)
    rebuilt_hash = hash_boundary_inheritance_refinement_intelligence(rebuilt)
    return {
        "valid": serialized == rebuilt_serialized and intelligence_hash == rebuilt_hash,
        "serialization_stable": serialized == rebuilt_serialized,
        "hashing_stable": intelligence_hash == rebuilt_hash,
        "serialization_length": len(serialized),
        "intelligence_hash": intelligence_hash,
        "rebuilt_intelligence_hash": rebuilt_hash,
    }


def validate_inheritance_state_visibility(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    state_visibility = validate_required_state_visibility(intelligence)
    inheritance_counts = count_inheritance_relationship_states(intelligence.inheritance_relationships)
    refinement_counts = count_refinement_relationship_states(intelligence.refinement_relationships)
    combined_counts = count_combined_relationship_states(intelligence)
    fail_visible = fail_visible_inheritance_summary(intelligence.fail_visible_findings)
    return {
        "valid": (
            state_visibility["valid"]
            and fail_visible["fail_visible"]
            and fail_visible["hidden_inference_used_count"] == 0
            and fail_visible["automatic_repair_enabled_count"] == 0
            and fail_visible["automatic_remediation_enabled_count"] == 0
        ),
        "inheritance_counts": inheritance_counts,
        "refinement_counts": refinement_counts,
        "combined_counts": combined_counts,
        "missing_states": state_visibility["missing_states"],
        "missing_fail_visible_states": state_visibility["missing_fail_visible_states"],
        "fail_visible_summary": fail_visible,
        "unsupported_visibility_count": combined_counts[INHERITANCE_STATE_UNSUPPORTED],
        "prohibited_visibility_count": combined_counts[INHERITANCE_STATE_PROHIBITED],
        "ambiguous_visibility_count": combined_counts[INHERITANCE_STATE_AMBIGUOUS],
        "stale_visibility_count": combined_counts[INHERITANCE_STATE_STALE],
        "conflicting_visibility_count": combined_counts[INHERITANCE_STATE_CONFLICTING],
    }


def validate_ancestry_continuity(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    ancestry = ancestry_depth_visibility(intelligence.ancestry_visibility)
    inheritance_ids = {relationship.inheritance_id for relationship in intelligence.inheritance_relationships}
    ancestry_child_ids = {item.boundary_id for item in intelligence.ancestry_visibility}
    child_ids = {relationship.child_boundary_id for relationship in intelligence.inheritance_relationships}
    return {
        "valid": (
            ancestry["descriptive_only"]
            and ancestry["non_authoritative"]
            and ancestry["operational_authority_count"] == 0
            and ancestry["max_ancestry_depth"] >= 3
            and child_ids == ancestry_child_ids
            and len(inheritance_ids) == len(intelligence.ancestry_visibility)
        ),
        "ancestry_depth_visibility": ancestry,
        "missing_ancestry_boundary_ids": sorted(child_ids - ancestry_child_ids),
    }


def validate_replay_rollback_evidence(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    continuity = intelligence.continuity_propagation_metadata
    relationship_ids = {
        relationship.inheritance_id for relationship in intelligence.inheritance_relationships
    } | {relationship.refinement_id for relationship in intelligence.refinement_relationships}
    propagated = set(continuity.propagated_relationship_ids)
    replay = set(continuity.replay_evidence_ids)
    rollback = set(continuity.rollback_evidence_ids)
    return {
        "valid": (
            continuity.replay_safe
            and continuity.rollback_safe
            and continuity.continuity_propagation_preserved
            and propagated == relationship_ids
            and replay == relationship_ids
            and rollback == relationship_ids
        ),
        "relationship_count": len(relationship_ids),
        "propagated_relationship_count": len(propagated),
        "replay_safe_evidence_count": len(replay),
        "rollback_safe_evidence_count": len(rollback),
        "missing_propagated_relationship_ids": sorted(relationship_ids - propagated),
        "missing_replay_evidence_ids": sorted(relationship_ids - replay),
        "missing_rollback_evidence_ids": sorted(relationship_ids - rollback),
        "replay_safe": continuity.replay_safe,
        "rollback_safe": continuity.rollback_safe,
    }


def validate_provenance_lineage_propagation(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    provenance = intelligence.provenance_propagation_metadata
    lineage = intelligence.lineage_propagation_metadata
    continuity = intelligence.continuity_propagation_metadata
    return {
        "valid": (
            continuity.continuity_propagation_preserved
            and provenance.provenance_continuity_preserved
            and lineage.lineage_continuity_preserved
            and not provenance.hidden_source_inference_used
            and not lineage.ambiguous_lineage_inferred
        ),
        "continuity_propagation_preserved": continuity.continuity_propagation_preserved,
        "provenance_continuity_preserved": provenance.provenance_continuity_preserved,
        "lineage_continuity_preserved": lineage.lineage_continuity_preserved,
        "hidden_source_inference_used": provenance.hidden_source_inference_used,
        "ambiguous_lineage_inferred": lineage.ambiguous_lineage_inferred,
    }


def validate_inheritance_diagnostics_and_explainability(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    diagnostics = aggregate_refinement_diagnostics(intelligence.diagnostics)
    explainability = governance_safe_refinement_explainability(intelligence.explainability)
    return {
        "valid": (
            diagnostics["descriptive_only"]
            and diagnostics["automatic_repair_enabled_count"] == 0
            and diagnostics["automatic_remediation_enabled_count"] == 0
            and explainability["explainability_first"]
            and explainability["descriptive_only"]
            and explainability["recommendation_enabled_count"] == 0
            and explainability["decision_enabled_count"] == 0
        ),
        "diagnostics": diagnostics,
        "explainability": explainability,
    }


def validate_inheritance_non_operational(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    counters = inheritance_capability_counter_values(intelligence)
    enabled_flags = enabled_inheritance_capability_flags(intelligence)
    root_disabled = {
        "descriptive_only": intelligence.descriptive_only,
        "non_operational": intelligence.non_operational,
        "non_authoritative": intelligence.non_authoritative,
        "non_executing": intelligence.non_executing,
        "non_authorizing": intelligence.non_authorizing,
        "non_approving": intelligence.non_approving,
        "non_dispatching": intelligence.non_dispatching,
        "non_routing": intelligence.non_routing,
        "non_mutating": intelligence.non_mutating,
        "planner_integration_disabled": not intelligence.planner_integration_enabled,
        "production_consumption_disabled": not intelligence.production_consumption_enabled,
        "runtime_mutation_disabled": not intelligence.runtime_mutation_enabled,
        "operational_mutation_disabled": not intelligence.operational_mutation_enabled,
    }
    return {
        "valid": all(value == 0 for value in counters.values()) and all(root_disabled.values()),
        "counters": counters,
        "enabled_flags": enabled_flags,
        **root_disabled,
    }


def validate_boundary_inheritance_refinement(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> dict[str, Any]:
    validations = {
        "ordering": validate_inheritance_ordering_stability(intelligence),
        "serialization_hashing": validate_inheritance_serialization_and_hashing(intelligence),
        "state_visibility": validate_inheritance_state_visibility(intelligence),
        "ancestry": validate_ancestry_continuity(intelligence),
        "replay_rollback": validate_replay_rollback_evidence(intelligence),
        "provenance_lineage": validate_provenance_lineage_propagation(intelligence),
        "diagnostics_explainability": validate_inheritance_diagnostics_and_explainability(
            intelligence
        ),
        "non_operational": validate_inheritance_non_operational(intelligence),
    }
    invalid = [name for name, result in validations.items() if not result["valid"]]
    return {
        "valid": not invalid,
        "invalid_validation_names": invalid,
        "validation_error_count": len(invalid),
        "validations": validations,
    }


def build_v4_4_boundary_inheritance_refinement_report() -> dict[str, Any]:
    intelligence = build_v4_4_boundary_inheritance_refinement()
    exported = export_boundary_inheritance_refinement_intelligence(intelligence)
    validation = validate_boundary_inheritance_refinement(intelligence)
    state_validation = validation["validations"]["state_visibility"]
    serialization_hashing = validation["validations"]["serialization_hashing"]
    ancestry = validation["validations"]["ancestry"]
    replay_rollback = validation["validations"]["replay_rollback"]
    provenance_lineage = validation["validations"]["provenance_lineage"]
    diagnostics_explainability = validation["validations"]["diagnostics_explainability"]
    non_operational = validation["validations"]["non_operational"]
    combined_counts = state_validation["combined_counts"]
    fail_visible = state_validation["fail_visible_summary"]
    deterministic_hash_evidence = {
        "identity_hash": hash_boundary_inheritance_identity(intelligence.identity),
        "intelligence_hash": hash_boundary_inheritance_refinement_intelligence(intelligence),
        "continuity_propagation_hash": hash_continuity_propagation_metadata(
            intelligence.continuity_propagation_metadata
        ),
        "provenance_propagation_hash": hash_provenance_propagation_metadata(
            intelligence.provenance_propagation_metadata
        ),
        "lineage_propagation_hash": hash_lineage_propagation_metadata(
            intelligence.lineage_propagation_metadata
        ),
        "inheritance_relationship_hashes": {
            relationship.inheritance_id: hash_inheritance_relationship(relationship)
            for relationship in sorted(
                intelligence.inheritance_relationships,
                key=lambda item: (item.deterministic_order, item.inheritance_id),
            )
        },
        "refinement_relationship_hashes": {
            relationship.refinement_id: hash_refinement_relationship(relationship)
            for relationship in sorted(
                intelligence.refinement_relationships,
                key=lambda item: (item.deterministic_order, item.refinement_id),
            )
        },
        "ancestry_visibility_hashes": {
            ancestry_record.ancestry_id: hash_boundary_ancestry_visibility(ancestry_record)
            for ancestry_record in sorted(
                intelligence.ancestry_visibility,
                key=lambda item: (item.deterministic_order, item.ancestry_id),
            )
        },
        "refinement_lineage_hashes": {
            continuity.lineage_id: hash_refinement_lineage_continuity(continuity)
            for continuity in sorted(
                intelligence.refinement_lineage_continuity,
                key=lambda item: (item.deterministic_order, item.lineage_id),
            )
        },
        "diagnostic_hashes": {
            diagnostic.diagnostic_id: hash_refinement_diagnostic(diagnostic)
            for diagnostic in sorted(
                intelligence.diagnostics,
                key=lambda item: (item.deterministic_order, item.diagnostic_id),
            )
        },
        "explainability_hashes": {
            explainability.explainability_id: hash_refinement_explainability(explainability)
            for explainability in sorted(
                intelligence.explainability,
                key=lambda item: (item.deterministic_order, item.explainability_id),
            )
        },
        "fail_visible_finding_hashes": {
            finding.finding_id: hash_inheritance_fail_visible_finding(finding)
            for finding in sorted(
                intelligence.fail_visible_findings,
                key=lambda item: (item.deterministic_order, item.finding_id),
            )
        },
    }
    deterministic_serialization_evidence = {
        "serialization_stable": serialization_hashing["serialization_stable"],
        "hashing_stable": serialization_hashing["hashing_stable"],
        "serialization_length": serialization_hashing["serialization_length"],
        "intelligence_hash": serialization_hashing["intelligence_hash"],
    }
    summary = {
        "inheritance_relationship_count": len(intelligence.inheritance_relationships),
        "refinement_relationship_count": len(intelligence.refinement_relationships),
        "relationship_count": len(intelligence.inheritance_relationships)
        + len(intelligence.refinement_relationships),
        "ancestry_visibility_count": len(intelligence.ancestry_visibility),
        "max_ancestry_depth": ancestry["ancestry_depth_visibility"]["max_ancestry_depth"],
        "multi_level_ancestry_count": ancestry["ancestry_depth_visibility"]["multi_level_ancestry_count"],
        "refinement_lineage_count": len(intelligence.refinement_lineage_continuity),
        "supported_visibility_count": combined_counts[INHERITANCE_STATE_SUPPORTED],
        "unsupported_visibility_count": combined_counts[INHERITANCE_STATE_UNSUPPORTED],
        "prohibited_visibility_count": combined_counts[INHERITANCE_STATE_PROHIBITED],
        "ambiguous_inheritance_count": combined_counts[INHERITANCE_STATE_AMBIGUOUS],
        "stale_refinement_count": combined_counts[INHERITANCE_STATE_STALE],
        "conflicting_refinement_count": combined_counts[INHERITANCE_STATE_CONFLICTING],
        "inherited_visibility_count": combined_counts[INHERITANCE_STATE_INHERITED],
        "refined_visibility_count": combined_counts[INHERITANCE_STATE_REFINED],
        "fail_visible_finding_count": fail_visible["finding_count"],
        "deterministic_ordering_verified": validation["validations"]["ordering"]["valid"],
        "deterministic_serialization_verified": serialization_hashing["serialization_stable"],
        "deterministic_hashing_verified": serialization_hashing["hashing_stable"],
        "replay_safe_evidence_verified": replay_rollback["replay_safe"],
        "rollback_safe_evidence_verified": replay_rollback["rollback_safe"],
        "inheritance_continuity_verified": ancestry["valid"],
        "continuity_propagation_verified": provenance_lineage["continuity_propagation_preserved"],
        "provenance_continuity_verified": provenance_lineage["provenance_continuity_preserved"],
        "lineage_continuity_verified": provenance_lineage["lineage_continuity_preserved"],
        "fail_visible_ambiguity_verified": fail_visible["state_counts"][INHERITANCE_STATE_AMBIGUOUS] > 0,
        "governance_safe_certification_verified": validation["valid"],
        "non_operational_certification_verified": non_operational["valid"],
        "descriptive_only_enforced": intelligence.descriptive_only,
        "validation_error_count": validation["validation_error_count"],
        "remaining_warning_count": 0,
        "remaining_blocker_count": 0,
        **non_operational["counters"],
        "planner_integration_enabled": intelligence.planner_integration_enabled,
        "production_consumption_enabled": intelligence.production_consumption_enabled,
        "runtime_mutation_enabled": intelligence.runtime_mutation_enabled,
        "operational_mutation_enabled": intelligence.operational_mutation_enabled,
    }
    report: dict[str, Any] = {
        "report_schema_version": V4_4_BOUNDARY_INHERITANCE_REPORT_SCHEMA_VERSION,
        "phase_id": intelligence.identity.phase_id,
        "foundation_status": (
            V4_4_BOUNDARY_INHERITANCE_STATUS_STABLE
            if validation["valid"]
            else V4_4_BOUNDARY_INHERITANCE_STATUS_BLOCKED
        ),
        "summary": summary,
        "boundary_inheritance_refinement_intelligence": exported,
        "inheritance_chain_visibility": inheritance_chain_summaries(intelligence),
        "refinement_ancestry_visibility": refinement_ancestry_summaries(intelligence),
        "ancestry_depth_visibility": ancestry["ancestry_depth_visibility"],
        "diagnostics_visibility": diagnostics_explainability["diagnostics"],
        "explainability_visibility": diagnostics_explainability["explainability"],
        "fail_visible_visibility": fail_visible,
        "inheritance_conflict_visibility": inheritance_conflict_visibility(intelligence),
        "refinement_drift_visibility": refinement_drift_visibility(intelligence),
        "fail_visible_ambiguity_visibility": fail_visible_ambiguity_summaries(intelligence),
        "prohibited_inheritance_visibility": prohibited_inheritance_visibility(intelligence),
        "unsupported_inheritance_visibility": unsupported_inheritance_visibility(intelligence),
        "continuity_propagation_visibility": continuity_propagation_visibility(intelligence),
        "provenance_propagation_visibility": provenance_propagation_visibility(intelligence),
        "lineage_propagation_visibility": lineage_propagation_visibility(intelligence),
        "deterministic_hash_evidence": deterministic_hash_evidence,
        "deterministic_serialization_evidence": deterministic_serialization_evidence,
        "replay_safe_evidence": replay_rollback,
        "rollback_safe_evidence": replay_rollback,
        "provenance_continuity_evidence": {
            "provenance_metadata": exported["provenance_propagation_metadata"],
            "provenance_continuity_verified": provenance_lineage["provenance_continuity_preserved"],
            "hidden_source_inference_used": provenance_lineage["hidden_source_inference_used"],
        },
        "lineage_continuity_evidence": {
            "lineage_metadata": exported["lineage_propagation_metadata"],
            "lineage_continuity_verified": provenance_lineage["lineage_continuity_preserved"],
            "ambiguous_lineage_inferred": provenance_lineage["ambiguous_lineage_inferred"],
        },
        "non_operational_certification_evidence": non_operational,
        "validation": validation,
        "remaining_warnings": [],
        "remaining_blockers": [],
    }
    report["deterministic_report_hash"] = deterministic_boundary_inheritance_hash(report)
    return report


def contaminate_inheritance_for_non_operational_validation(
    intelligence: BoundaryInheritanceRefinementIntelligence,
) -> BoundaryInheritanceRefinementIntelligence:
    contaminated_inheritance = replace(
        intelligence.inheritance_relationships[0],
        runtime_execution_enabled=True,
        authorization_capability=True,
    )
    contaminated_refinement = replace(
        intelligence.refinement_relationships[0],
        execution_capability=True,
        routing_execution_enabled=True,
    )
    return replace(
        intelligence,
        inheritance_relationships=(contaminated_inheritance,)
        + intelligence.inheritance_relationships[1:],
        refinement_relationships=(contaminated_refinement,)
        + intelligence.refinement_relationships[1:],
        orchestration_approval_enabled=True,
        dispatch_execution_enabled=True,
        operational_mutation_enabled=True,
    )
