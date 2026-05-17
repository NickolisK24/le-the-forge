"""Aggregation diagnostics for v4.2 coordination diagnostics explainability."""

from __future__ import annotations

from typing import Any

from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import CoordinationDependencyGraph, default_coordination_dependency_graph
from .coordination_diagnostics_hashing import (
    hash_coordination_diagnostics_explainability,
    hash_cross_layer_coordination_diagnostic_record,
    hash_diagnostic_severity_visibility,
    hash_state_aggregation_visibility,
)
from .coordination_diagnostics_models import (
    DIAGNOSTIC_AGGREGATION_BLOCKED,
    DIAGNOSTIC_AGGREGATION_CONFLICTING,
    DIAGNOSTIC_AGGREGATION_MISSING,
    DIAGNOSTIC_AGGREGATION_PROHIBITED,
    DIAGNOSTIC_AGGREGATION_STALE,
    DIAGNOSTIC_AGGREGATION_UNSUPPORTED,
    DIAGNOSTIC_AGGREGATION_STATES,
    FAIL_VISIBLE_DIAGNOSTIC_AGGREGATION_STATES,
    CoordinationDiagnosticsExplainability,
    CrossLayerCoordinationDiagnosticRecord,
    default_coordination_diagnostics_explainability,
)
from .coordination_diagnostics_serialization import serialize_coordination_diagnostics_explainability
from .coordination_drift_hashing import hash_coordination_drift_certification
from .coordination_drift_models import CoordinationDriftCertification, default_coordination_drift_certification
from .coordination_explainability import build_coordination_explainability_evidence
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import hash_governance_routing_visibility
from .governance_routing_models import GovernanceRoutingVisibility, default_governance_routing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "remediation_enabled",
    "automatic_correction_enabled",
    "drift_correction_enabled",
    "drift_remediation_enabled",
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
    "hidden_correction_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_diagnostic_states(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...],
) -> dict[str, int]:
    counts = {state: 0 for state in DIAGNOSTIC_AGGREGATION_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.aggregation_state in counts:
            counts[record.aggregation_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def aggregate_coordination_diagnostic_records(
    diagnostics: CoordinationDiagnosticsExplainability,
    aggregation_state: str,
) -> tuple[str, ...]:
    return tuple(
        record.diagnostic_record_id
        for record in diagnostics.diagnostic_records
        if record.aggregation_state == aggregation_state
    )


def fail_visible_coordination_diagnostic_record_ids(
    records: tuple[CrossLayerCoordinationDiagnosticRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        record.diagnostic_record_id
        for record in records
        if record.aggregation_state in FAIL_VISIBLE_DIAGNOSTIC_AGGREGATION_STATES and record.fail_visible
    )


def coordination_diagnostics_capability_flags(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        diagnostics,
        diagnostics.identity,
        diagnostics.unsupported_state_aggregation,
        diagnostics.prohibited_state_aggregation,
        diagnostics.blocked_state_aggregation,
        diagnostics.stale_state_aggregation,
        diagnostics.missing_state_aggregation,
        diagnostics.conflicting_state_aggregation,
        diagnostics.fail_visible_explanation_summary,
        diagnostics.governance_visibility,
        *diagnostics.manifest_diagnostic_references,
        *diagnostics.dependency_graph_diagnostic_references,
        *diagnostics.lineage_diagnostic_references,
        *diagnostics.sequencing_diagnostic_references,
        *diagnostics.routing_diagnostic_references,
        *diagnostics.drift_diagnostic_references,
        *diagnostics.diagnostic_records,
        *diagnostics.severity_visibility,
        *diagnostics.explanation_records,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_diagnostics_capability_flags(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, bool]:
    return {key: value for key, value in coordination_diagnostics_capability_flags(diagnostics).items() if value}


def coordination_diagnostics_equal(
    left: CoordinationDiagnosticsExplainability,
    right: CoordinationDiagnosticsExplainability,
) -> bool:
    return serialize_coordination_diagnostics_explainability(left) == serialize_coordination_diagnostics_explainability(right)


def _corrective_enabled(item: object) -> bool:
    return any(bool(getattr(item, flag_name, False)) for flag_name in CAPABILITY_FLAG_NAMES)


def validate_coordination_diagnostic_aggregation(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, object]:
    unsupported_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_UNSUPPORTED)
    prohibited_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_PROHIBITED)
    blocked_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_BLOCKED)
    stale_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_STALE)
    missing_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_MISSING)
    conflicting_ids = aggregate_coordination_diagnostic_records(diagnostics, DIAGNOSTIC_AGGREGATION_CONFLICTING)
    unsupported_visible = set(unsupported_ids).issubset(set(diagnostics.unsupported_state_aggregation.diagnostic_record_ids))
    prohibited_visible = set(prohibited_ids).issubset(set(diagnostics.prohibited_state_aggregation.diagnostic_record_ids))
    blocked_visible = set(blocked_ids).issubset(set(diagnostics.blocked_state_aggregation.diagnostic_record_ids))
    stale_visible = set(stale_ids).issubset(set(diagnostics.stale_state_aggregation.diagnostic_record_ids))
    missing_visible = set(missing_ids).issubset(set(diagnostics.missing_state_aggregation.diagnostic_record_ids))
    conflicting_visible = set(conflicting_ids).issubset(set(diagnostics.conflicting_state_aggregation.diagnostic_record_ids))
    invalid_record_ids = tuple(
        record.diagnostic_record_id
        for record in diagnostics.diagnostic_records
        if record.aggregation_state not in DIAGNOSTIC_AGGREGATION_STATES
    )
    hidden_count = sum(1 for record in diagnostics.diagnostic_records if record.hidden)
    corrective_count = sum(
        1
        for item in (
            diagnostics.unsupported_state_aggregation,
            diagnostics.prohibited_state_aggregation,
            diagnostics.blocked_state_aggregation,
            diagnostics.stale_state_aggregation,
            diagnostics.missing_state_aggregation,
            diagnostics.conflicting_state_aggregation,
            *diagnostics.diagnostic_records,
        )
        if _corrective_enabled(item)
    )
    return {
        "valid": (
            unsupported_visible
            and prohibited_visible
            and blocked_visible
            and stale_visible
            and missing_visible
            and conflicting_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "diagnostic_state_counts": count_coordination_diagnostic_states(diagnostics.diagnostic_records),
        "fail_visible_record_ids": fail_visible_coordination_diagnostic_record_ids(diagnostics.diagnostic_records),
        "unsupported_record_ids": unsupported_ids,
        "prohibited_record_ids": prohibited_ids,
        "blocked_record_ids": blocked_ids,
        "stale_record_ids": stale_ids,
        "missing_record_ids": missing_ids,
        "conflicting_record_ids": conflicting_ids,
        "unsupported_state_visible": unsupported_visible,
        "prohibited_state_visible": prohibited_visible,
        "blocked_state_visible": blocked_visible,
        "stale_state_visible": stale_visible,
        "missing_state_visible": missing_visible,
        "conflicting_state_visible": conflicting_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
    }


def validate_diagnostic_severity_visibility(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, object]:
    record_ids = {record.diagnostic_record_id for record in diagnostics.diagnostic_records}
    severity_record_ids = tuple(
        record_id for visibility in diagnostics.severity_visibility for record_id in visibility.diagnostic_record_ids
    )
    missing_record_ids = tuple(sorted(record_ids - set(severity_record_ids)))
    corrective_count = sum(1 for visibility in diagnostics.severity_visibility if _corrective_enabled(visibility))
    return {
        "valid": len(missing_record_ids) == 0 and corrective_count == 0,
        "severity_count": len(diagnostics.severity_visibility),
        "severity_ids": tuple(visibility.severity for visibility in diagnostics.severity_visibility),
        "missing_record_ids": missing_record_ids,
        "corrective_count": corrective_count,
    }


def validate_manifest_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    manifest_hash = hash_coordination_manifest(source)
    reference_matches = any(
        reference.manifest_reference == source.identity.manifest_id
        and reference.manifest_hash_reference == manifest_hash
        for reference in diagnostics.manifest_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_manifest_reference == source.identity.manifest_id
            and diagnostics.compatibility_manifest_reference == source.identity.manifest_id
            and diagnostics.identity.source_manifest_hash_reference == manifest_hash
            and reference_matches
        ),
        "manifest_hash_matches": diagnostics.identity.source_manifest_hash_reference == manifest_hash,
        "manifest_diagnostic_reference_matches": reference_matches,
    }


def validate_dependency_graph_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    graph_hash = hash_coordination_dependency_graph(source_graph)
    reference_matches = any(
        reference.dependency_graph_reference == source_graph.identity.graph_id
        and reference.dependency_graph_hash_reference == graph_hash
        for reference in diagnostics.dependency_graph_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_dependency_graph_reference == source_graph.identity.graph_id
            and diagnostics.compatibility_dependency_graph_reference == source_graph.identity.graph_id
            and diagnostics.identity.source_dependency_graph_hash_reference == graph_hash
            and reference_matches
        ),
        "dependency_graph_hash_matches": diagnostics.identity.source_dependency_graph_hash_reference == graph_hash,
        "dependency_graph_diagnostic_reference_matches": reference_matches,
    }


def validate_lineage_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    lineage_hash = hash_coordination_lineage_chain(source_lineage)
    reference_matches = any(
        reference.lineage_chain_reference == source_lineage.identity.chain_id
        and reference.lineage_chain_hash_reference == lineage_hash
        for reference in diagnostics.lineage_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_lineage_chain_reference == source_lineage.identity.chain_id
            and diagnostics.compatibility_lineage_chain_reference == source_lineage.identity.chain_id
            and diagnostics.identity.source_lineage_chain_hash_reference == lineage_hash
            and reference_matches
        ),
        "lineage_chain_hash_matches": diagnostics.identity.source_lineage_chain_hash_reference == lineage_hash,
        "lineage_diagnostic_reference_matches": reference_matches,
    }


def validate_sequencing_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    sequencing: CoordinationSequencingIntelligence | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    sequencing_hash = hash_coordination_sequencing_intelligence(source_sequencing)
    reference_matches = any(
        reference.sequencing_reference == source_sequencing.identity.sequencing_id
        and reference.sequencing_hash_reference == sequencing_hash
        for reference in diagnostics.sequencing_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_sequencing_reference == source_sequencing.identity.sequencing_id
            and diagnostics.compatibility_sequencing_reference == source_sequencing.identity.sequencing_id
            and diagnostics.identity.source_sequencing_hash_reference == sequencing_hash
            and reference_matches
        ),
        "sequencing_hash_matches": diagnostics.identity.source_sequencing_hash_reference == sequencing_hash,
        "sequencing_diagnostic_reference_matches": reference_matches,
    }


def validate_routing_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    routing: GovernanceRoutingVisibility | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    routing_hash = hash_governance_routing_visibility(source_routing)
    reference_matches = any(
        reference.routing_reference == source_routing.identity.routing_id
        and reference.routing_hash_reference == routing_hash
        for reference in diagnostics.routing_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_routing_reference == source_routing.identity.routing_id
            and diagnostics.compatibility_routing_reference == source_routing.identity.routing_id
            and diagnostics.identity.source_routing_hash_reference == routing_hash
            and reference_matches
        ),
        "routing_hash_matches": diagnostics.identity.source_routing_hash_reference == routing_hash,
        "routing_diagnostic_reference_matches": reference_matches,
    }


def validate_drift_diagnostics_compatibility(
    diagnostics: CoordinationDiagnosticsExplainability,
    drift: CoordinationDriftCertification | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    source_drift = drift or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    drift_hash = hash_coordination_drift_certification(source_drift)
    reference_matches = any(
        reference.drift_reference == source_drift.identity.drift_certification_id
        and reference.drift_hash_reference == drift_hash
        for reference in diagnostics.drift_diagnostic_references
    )
    return {
        "valid": (
            diagnostics.identity.source_drift_reference == source_drift.identity.drift_certification_id
            and diagnostics.compatibility_drift_reference == source_drift.identity.drift_certification_id
            and diagnostics.identity.source_drift_hash_reference == drift_hash
            and reference_matches
        ),
        "drift_hash_matches": diagnostics.identity.source_drift_hash_reference == drift_hash,
        "drift_diagnostic_reference_matches": reference_matches,
    }


def validate_coordination_diagnostics_non_execution(
    diagnostics: CoordinationDiagnosticsExplainability,
) -> dict[str, object]:
    enabled_flags = enabled_coordination_diagnostics_capability_flags(diagnostics)
    return {
        "valid": len(enabled_flags) == 0 and diagnostics.non_executable and diagnostics.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "non_executable": diagnostics.non_executable,
        "descriptive_only": diagnostics.descriptive_only,
        "remediation_disabled": not diagnostics.remediation_enabled,
        "automatic_correction_disabled": not diagnostics.automatic_correction_enabled,
        "drift_correction_disabled": not diagnostics.drift_correction_enabled,
        "drift_remediation_disabled": not diagnostics.drift_remediation_enabled,
        "routing_execution_disabled": not diagnostics.routing_execution_enabled,
        "orchestration_execution_disabled": not diagnostics.orchestration_execution_enabled,
        "refresh_execution_disabled": not diagnostics.refresh_execution_enabled,
        "sequencing_execution_disabled": not diagnostics.sequencing_execution_enabled,
        "scheduling_execution_disabled": not diagnostics.scheduling_execution_enabled,
        "dependency_resolution_disabled": not diagnostics.dependency_resolution_enabled,
        "lineage_repair_disabled": not diagnostics.lineage_repair_enabled,
        "lineage_inference_disabled": not diagnostics.lineage_inference_enabled,
        "planner_integration_disabled": not diagnostics.planner_integration_enabled,
        "production_consumption_disabled": (
            not diagnostics.production_consumption_enabled
            and not diagnostics.production_bundle_consumption_enabled
        ),
        "runtime_mutation_disabled": not diagnostics.runtime_mutation_enabled,
        "automatic_rollback_disabled": not diagnostics.automatic_rollback_enabled,
        "authorization_disabled": not diagnostics.authorization_enabled,
        "approval_disabled": not diagnostics.approval_enabled,
        "ranking_disabled": not diagnostics.ranking_enabled,
        "scoring_disabled": not diagnostics.scoring_enabled,
        "selection_disabled": not diagnostics.selection_enabled,
        "operational_execution_disabled": not diagnostics.operational_execution_enabled,
        "hidden_correction_absent": not diagnostics.hidden_correction_enabled,
        "implicit_execution_pathway_absent": not diagnostics.implicit_execution_pathway_enabled,
    }


def build_coordination_diagnostics_aggregation(
    diagnostics: CoordinationDiagnosticsExplainability | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
) -> dict[str, Any]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    source_routing = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    source_drift = drift or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    source = diagnostics or default_coordination_diagnostics_explainability(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
    )
    aggregation = validate_coordination_diagnostic_aggregation(source)
    severity = validate_diagnostic_severity_visibility(source)
    explainability = build_coordination_explainability_evidence(source)
    manifest_compatibility = validate_manifest_diagnostics_compatibility(source, source_manifest)
    graph_compatibility = validate_dependency_graph_diagnostics_compatibility(source, source_graph, source_manifest)
    lineage_compatibility = validate_lineage_diagnostics_compatibility(
        source,
        source_lineage,
        source_graph,
        source_manifest,
    )
    sequencing_compatibility = validate_sequencing_diagnostics_compatibility(
        source,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    routing_compatibility = validate_routing_diagnostics_compatibility(
        source,
        source_routing,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    drift_compatibility = validate_drift_diagnostics_compatibility(
        source,
        source_drift,
        source_routing,
        source_sequencing,
        source_lineage,
        source_graph,
        source_manifest,
    )
    non_execution = validate_coordination_diagnostics_non_execution(source)
    enabled_flags = enabled_coordination_diagnostics_capability_flags(source)
    return {
        "diagnostics_hash": hash_coordination_diagnostics_explainability(source),
        "diagnostic_record_hashes": [
            hash_cross_layer_coordination_diagnostic_record(record) for record in source.diagnostic_records
        ],
        "aggregation_visibility_hashes": {
            "unsupported": hash_state_aggregation_visibility(source.unsupported_state_aggregation),
            "prohibited": hash_state_aggregation_visibility(source.prohibited_state_aggregation),
            "blocked": hash_state_aggregation_visibility(source.blocked_state_aggregation),
            "stale": hash_state_aggregation_visibility(source.stale_state_aggregation),
            "missing": hash_state_aggregation_visibility(source.missing_state_aggregation),
            "conflicting": hash_state_aggregation_visibility(source.conflicting_state_aggregation),
        },
        "severity_visibility_hashes": [
            hash_diagnostic_severity_visibility(visibility) for visibility in source.severity_visibility
        ],
        "aggregation_validation": aggregation,
        "severity_validation": severity,
        "explainability_evidence": explainability,
        "manifest_diagnostics_compatibility_validation": manifest_compatibility,
        "dependency_graph_diagnostics_compatibility_validation": graph_compatibility,
        "lineage_diagnostics_compatibility_validation": lineage_compatibility,
        "sequencing_diagnostics_compatibility_validation": sequencing_compatibility,
        "routing_diagnostics_compatibility_validation": routing_compatibility,
        "drift_diagnostics_compatibility_validation": drift_compatibility,
        "non_execution_validation": non_execution,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "diagnostic_categories": tuple(sorted(set(record.aggregation_state for record in source.diagnostic_records))),
        "diagnostic_count": len(source.diagnostic_records),
        "fail_visible_diagnostic_count": len(aggregation["fail_visible_record_ids"]),
        "diagnostics_are_descriptive_only": all(record.descriptive_only for record in source.diagnostic_records),
    }
