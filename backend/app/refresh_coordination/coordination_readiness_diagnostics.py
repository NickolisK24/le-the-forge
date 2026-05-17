"""Diagnostics for v4.2 coordination readiness certification."""

from __future__ import annotations

from typing import Any

from .coordination_continuity_hashing import hash_coordination_continuity_certification
from .coordination_continuity_models import (
    CoordinationContinuityCertification,
    default_coordination_continuity_certification,
)
from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import CoordinationDependencyGraph, default_coordination_dependency_graph
from .coordination_diagnostics_hashing import hash_coordination_diagnostics_explainability
from .coordination_diagnostics_models import (
    CoordinationDiagnosticsExplainability,
    default_coordination_diagnostics_explainability,
)
from .coordination_drift_hashing import hash_coordination_drift_certification
from .coordination_drift_models import CoordinationDriftCertification, default_coordination_drift_certification
from .coordination_lineage_chain_hashing import hash_coordination_lineage_chain
from .coordination_lineage_chain_models import CoordinationLineageChain, default_coordination_lineage_chain
from .coordination_manifest_hashing import hash_coordination_manifest
from .coordination_manifest_models import CoordinationManifest, default_coordination_manifest
from .coordination_readiness_hashing import (
    hash_coordination_readiness_certification,
    hash_coordination_readiness_diagnostic,
    hash_coordination_readiness_record,
    hash_descriptive_readiness_classification,
    hash_phase_evidence_reference,
    hash_readiness_state_visibility,
)
from .coordination_readiness_models import (
    FAIL_VISIBLE_READINESS_STATES,
    READINESS_CLASSIFICATION_DESCRIPTIVE,
    READINESS_STATE_BLOCKED,
    READINESS_STATE_CONFLICTING,
    READINESS_STATE_MISSING,
    READINESS_STATE_PROHIBITED,
    READINESS_STATE_STALE,
    READINESS_STATE_UNSUPPORTED,
    READINESS_STATES,
    CoordinationReadinessCertification,
    CoordinationReadinessRecord,
    default_coordination_readiness_certification,
)
from .coordination_readiness_serialization import serialize_coordination_readiness_certification
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import hash_governance_routing_visibility
from .governance_routing_models import GovernanceRoutingVisibility, default_governance_routing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
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
    "implicit_execution_pathway_enabled",
)


def count_coordination_readiness_states(records: tuple[CoordinationReadinessRecord, ...]) -> dict[str, int]:
    counts = {state: 0 for state in READINESS_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.readiness_state in counts:
            counts[record.readiness_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def aggregate_readiness_state_records(
    certification: CoordinationReadinessCertification,
    readiness_state: str,
) -> tuple[str, ...]:
    return tuple(record.readiness_record_id for record in certification.readiness_records if record.readiness_state == readiness_state)


def fail_visible_coordination_readiness_record_ids(
    records: tuple[CoordinationReadinessRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        record.readiness_record_id
        for record in records
        if record.readiness_state in FAIL_VISIBLE_READINESS_STATES and record.fail_visible
    )


def coordination_readiness_capability_flags(certification: CoordinationReadinessCertification) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.blocked_readiness_visibility,
        certification.prohibited_readiness_visibility,
        certification.unsupported_readiness_visibility,
        certification.stale_readiness_visibility,
        certification.missing_readiness_visibility,
        certification.conflicting_readiness_visibility,
        certification.descriptive_readiness_classification,
        certification.governance_visibility,
        *certification.phase_evidence_references,
        *certification.manifest_readiness_references,
        *certification.dependency_graph_readiness_references,
        *certification.lineage_readiness_references,
        *certification.sequencing_readiness_references,
        *certification.routing_readiness_references,
        *certification.drift_readiness_references,
        *certification.diagnostics_explainability_readiness_references,
        *certification.continuity_readiness_references,
        *certification.readiness_records,
        *certification.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_readiness_capability_flags(
    certification: CoordinationReadinessCertification,
) -> dict[str, bool]:
    return {key: value for key, value in coordination_readiness_capability_flags(certification).items() if value}


def coordination_readiness_certifications_equal(
    left: CoordinationReadinessCertification,
    right: CoordinationReadinessCertification,
) -> bool:
    return serialize_coordination_readiness_certification(left) == serialize_coordination_readiness_certification(
        right
    )


def _corrective_enabled(item: object) -> bool:
    return any(bool(getattr(item, flag_name, False)) for flag_name in CAPABILITY_FLAG_NAMES)


def validate_coordination_readiness_visibility(
    certification: CoordinationReadinessCertification,
) -> dict[str, object]:
    blocked_ids = aggregate_readiness_state_records(certification, READINESS_STATE_BLOCKED)
    prohibited_ids = aggregate_readiness_state_records(certification, READINESS_STATE_PROHIBITED)
    unsupported_ids = aggregate_readiness_state_records(certification, READINESS_STATE_UNSUPPORTED)
    stale_ids = aggregate_readiness_state_records(certification, READINESS_STATE_STALE)
    missing_ids = aggregate_readiness_state_records(certification, READINESS_STATE_MISSING)
    conflicting_ids = aggregate_readiness_state_records(certification, READINESS_STATE_CONFLICTING)
    blocked_visible = set(blocked_ids).issubset(set(certification.blocked_readiness_visibility.readiness_record_ids))
    prohibited_visible = set(prohibited_ids).issubset(
        set(certification.prohibited_readiness_visibility.readiness_record_ids)
    )
    unsupported_visible = set(unsupported_ids).issubset(
        set(certification.unsupported_readiness_visibility.readiness_record_ids)
    )
    stale_visible = set(stale_ids).issubset(set(certification.stale_readiness_visibility.readiness_record_ids))
    missing_visible = set(missing_ids).issubset(set(certification.missing_readiness_visibility.readiness_record_ids))
    conflicting_visible = set(conflicting_ids).issubset(
        set(certification.conflicting_readiness_visibility.readiness_record_ids)
    )
    invalid_record_ids = tuple(
        record.readiness_record_id
        for record in certification.readiness_records
        if record.readiness_state not in READINESS_STATES
    )
    hidden_count = sum(
        1 for item in (*certification.readiness_records, *certification.diagnostics) if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            certification.blocked_readiness_visibility,
            certification.prohibited_readiness_visibility,
            certification.unsupported_readiness_visibility,
            certification.stale_readiness_visibility,
            certification.missing_readiness_visibility,
            certification.conflicting_readiness_visibility,
            certification.descriptive_readiness_classification,
            *certification.readiness_records,
            *certification.diagnostics,
        )
        if _corrective_enabled(item)
    )
    return {
        "valid": (
            blocked_visible
            and prohibited_visible
            and unsupported_visible
            and stale_visible
            and missing_visible
            and conflicting_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "readiness_state_counts": count_coordination_readiness_states(certification.readiness_records),
        "fail_visible_record_ids": fail_visible_coordination_readiness_record_ids(certification.readiness_records),
        "blocked_record_ids": blocked_ids,
        "prohibited_record_ids": prohibited_ids,
        "unsupported_record_ids": unsupported_ids,
        "stale_record_ids": stale_ids,
        "missing_record_ids": missing_ids,
        "conflicting_record_ids": conflicting_ids,
        "blocked_readiness_visible": blocked_visible,
        "prohibited_readiness_visible": prohibited_visible,
        "unsupported_readiness_visible": unsupported_visible,
        "stale_readiness_visible": stale_visible,
        "missing_readiness_visible": missing_visible,
        "conflicting_readiness_visible": conflicting_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in certification.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in certification.diagnostics),
    }


def validate_descriptive_readiness_classification(
    certification: CoordinationReadinessCertification,
) -> dict[str, object]:
    classification = certification.descriptive_readiness_classification
    record_ids = tuple(record.readiness_record_id for record in certification.readiness_records)
    phase_ids = tuple(reference.phase_evidence_reference_id for reference in certification.phase_evidence_references)
    return {
        "valid": (
            classification.classification == READINESS_CLASSIFICATION_DESCRIPTIVE
            and set(record_ids).issubset(set(classification.readiness_record_ids))
            and set(phase_ids).issubset(set(classification.phase_evidence_reference_ids))
            and classification.descriptive_only
            and not classification.readiness_approved
            and not classification.operational_authorized
            and not _corrective_enabled(classification)
        ),
        "classification": classification.classification,
        "readiness_approved": classification.readiness_approved,
        "operational_authorized": classification.operational_authorized,
        "record_ids_visible": set(record_ids).issubset(set(classification.readiness_record_ids)),
        "phase_evidence_visible": set(phase_ids).issubset(set(classification.phase_evidence_reference_ids)),
        "classification_reason_count": len(classification.classification_reasons),
    }


def _expected_phase_evidence(
    manifest: CoordinationManifest,
    dependency_graph: CoordinationDependencyGraph,
    lineage_chain: CoordinationLineageChain,
    sequencing: CoordinationSequencingIntelligence,
    routing: GovernanceRoutingVisibility,
    drift: CoordinationDriftCertification,
    diagnostics: CoordinationDiagnosticsExplainability,
    continuity: CoordinationContinuityCertification,
) -> dict[str, tuple[str, str]]:
    return {
        "v4_2_coordination_manifest_foundations": (
            manifest.identity.manifest_id,
            hash_coordination_manifest(manifest),
        ),
        "v4_2_coordination_dependency_graph_governance": (
            dependency_graph.identity.graph_id,
            hash_coordination_dependency_graph(dependency_graph),
        ),
        "v4_2_coordination_lineage_chain_governance": (
            lineage_chain.identity.chain_id,
            hash_coordination_lineage_chain(lineage_chain),
        ),
        "v4_2_coordination_sequencing_intelligence": (
            sequencing.identity.sequencing_id,
            hash_coordination_sequencing_intelligence(sequencing),
        ),
        "v4_2_governance_routing_visibility": (
            routing.identity.routing_id,
            hash_governance_routing_visibility(routing),
        ),
        "v4_2_coordination_drift_certification": (
            drift.identity.drift_certification_id,
            hash_coordination_drift_certification(drift),
        ),
        "v4_2_coordination_diagnostics_explainability": (
            diagnostics.identity.diagnostics_id,
            hash_coordination_diagnostics_explainability(diagnostics),
        ),
        "v4_2_coordination_continuity_certification": (
            continuity.identity.continuity_certification_id,
            hash_coordination_continuity_certification(continuity),
        ),
    }


def validate_phase_evidence_compatibility(
    certification: CoordinationReadinessCertification,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
    diagnostics: CoordinationDiagnosticsExplainability | None = None,
    continuity: CoordinationContinuityCertification | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(source_manifest, source_graph, source_lineage)
    source_routing = routing or default_governance_routing_visibility(source_manifest, source_graph, source_lineage, source_sequencing)
    source_drift = drift or default_coordination_drift_certification(source_manifest, source_graph, source_lineage, source_sequencing, source_routing)
    source_diagnostics = diagnostics or default_coordination_diagnostics_explainability(source_manifest, source_graph, source_lineage, source_sequencing, source_routing, source_drift)
    source_continuity = continuity or default_coordination_continuity_certification(source_manifest, source_graph, source_lineage, source_sequencing, source_routing, source_drift, source_diagnostics)
    expected = _expected_phase_evidence(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
        source_diagnostics,
        source_continuity,
    )
    reference_results = {}
    for reference in certification.phase_evidence_references:
        expected_reference, expected_hash = expected.get(reference.phase_id, ("", ""))
        reference_results[reference.phase_id] = {
            "reference_matches": reference.evidence_reference == expected_reference,
            "hash_matches": reference.evidence_hash_reference == expected_hash,
        }
    missing_phase_ids = tuple(phase_id for phase_id in expected if phase_id not in reference_results)
    return {
        "valid": (
            len(certification.phase_evidence_references) == 8
            and len(missing_phase_ids) == 0
            and all(item["reference_matches"] and item["hash_matches"] for item in reference_results.values())
        ),
        "phase_evidence_count": len(certification.phase_evidence_references),
        "missing_phase_ids": missing_phase_ids,
        "reference_results": reference_results,
    }


def validate_layer_readiness_compatibility(
    certification: CoordinationReadinessCertification,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
    diagnostics: CoordinationDiagnosticsExplainability | None = None,
    continuity: CoordinationContinuityCertification | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source_sequencing = sequencing or default_coordination_sequencing_intelligence(source_manifest, source_graph, source_lineage)
    source_routing = routing or default_governance_routing_visibility(source_manifest, source_graph, source_lineage, source_sequencing)
    source_drift = drift or default_coordination_drift_certification(source_manifest, source_graph, source_lineage, source_sequencing, source_routing)
    source_diagnostics = diagnostics or default_coordination_diagnostics_explainability(source_manifest, source_graph, source_lineage, source_sequencing, source_routing, source_drift)
    source_continuity = continuity or default_coordination_continuity_certification(source_manifest, source_graph, source_lineage, source_sequencing, source_routing, source_drift, source_diagnostics)
    expected = {
        "manifest": (source_manifest.identity.manifest_id, hash_coordination_manifest(source_manifest), certification.manifest_readiness_references),
        "dependency_graph": (source_graph.identity.graph_id, hash_coordination_dependency_graph(source_graph), certification.dependency_graph_readiness_references),
        "lineage": (source_lineage.identity.chain_id, hash_coordination_lineage_chain(source_lineage), certification.lineage_readiness_references),
        "sequencing": (source_sequencing.identity.sequencing_id, hash_coordination_sequencing_intelligence(source_sequencing), certification.sequencing_readiness_references),
        "routing": (source_routing.identity.routing_id, hash_governance_routing_visibility(source_routing), certification.routing_readiness_references),
        "drift": (source_drift.identity.drift_certification_id, hash_coordination_drift_certification(source_drift), certification.drift_readiness_references),
        "diagnostics_explainability": (source_diagnostics.identity.diagnostics_id, hash_coordination_diagnostics_explainability(source_diagnostics), certification.diagnostics_explainability_readiness_references),
        "continuity": (source_continuity.identity.continuity_certification_id, hash_coordination_continuity_certification(source_continuity), certification.continuity_readiness_references),
    }
    results = {}
    for layer_name, (source_reference, source_hash, references) in expected.items():
        reference = references[0]
        results[layer_name] = {
            "reference_matches": reference.source_reference == source_reference,
            "hash_matches": reference.source_hash_reference == source_hash,
            "readiness_records_visible": len(reference.readiness_record_ids) == len(certification.readiness_records),
        }
    return {
        "valid": all(
            item["reference_matches"] and item["hash_matches"] and item["readiness_records_visible"]
            for item in results.values()
        ),
        "layer_results": results,
    }


def validate_coordination_readiness_non_execution(
    certification: CoordinationReadinessCertification,
) -> dict[str, object]:
    enabled_flags = enabled_coordination_readiness_capability_flags(certification)
    return {
        "valid": len(enabled_flags) == 0 and certification.non_executable and certification.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "descriptive_only": certification.descriptive_only,
        "non_executable": certification.non_executable,
        "readiness_approval_disabled": not certification.readiness_approval_enabled,
        "operational_authorization_disabled": not certification.operational_authorization_enabled,
        "readiness_not_approved": not certification.readiness_approved,
        "operational_not_authorized": not certification.operational_authorized,
        "remediation_disabled": not certification.remediation_enabled,
        "automatic_correction_disabled": not certification.automatic_correction_enabled,
        "drift_correction_disabled": not certification.drift_correction_enabled,
        "continuity_repair_disabled": not certification.continuity_repair_enabled,
        "continuity_inference_disabled": not certification.continuity_inference_enabled,
        "routing_execution_disabled": not certification.routing_execution_enabled,
        "orchestration_execution_disabled": not certification.orchestration_execution_enabled,
        "refresh_execution_disabled": not certification.refresh_execution_enabled,
        "dependency_resolution_disabled": not certification.dependency_resolution_enabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": not certification.production_consumption_enabled,
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "authorization_disabled": not certification.authorization_enabled,
        "approval_disabled": not certification.approval_enabled,
        "implicit_execution_pathway_absent": not certification.implicit_execution_pathway_enabled,
    }


def build_coordination_readiness_diagnostics(
    certification: CoordinationReadinessCertification | None = None,
) -> dict[str, Any]:
    source = certification or default_coordination_readiness_certification()
    return {
        "readiness_hash": hash_coordination_readiness_certification(source),
        "phase_evidence_hashes": [
            hash_phase_evidence_reference(reference) for reference in source.phase_evidence_references
        ],
        "readiness_record_hashes": [
            hash_coordination_readiness_record(record) for record in source.readiness_records
        ],
        "visibility_hashes": [
            hash_readiness_state_visibility(source.blocked_readiness_visibility),
            hash_readiness_state_visibility(source.prohibited_readiness_visibility),
            hash_readiness_state_visibility(source.unsupported_readiness_visibility),
            hash_readiness_state_visibility(source.stale_readiness_visibility),
            hash_readiness_state_visibility(source.missing_readiness_visibility),
            hash_readiness_state_visibility(source.conflicting_readiness_visibility),
        ],
        "classification_hash": hash_descriptive_readiness_classification(
            source.descriptive_readiness_classification
        ),
        "diagnostic_hashes": [
            hash_coordination_readiness_diagnostic(diagnostic) for diagnostic in source.diagnostics
        ],
        "readiness_visibility_validation": validate_coordination_readiness_visibility(source),
        "readiness_classification_validation": validate_descriptive_readiness_classification(source),
        "phase_evidence_compatibility_validation": validate_phase_evidence_compatibility(source),
        "layer_readiness_compatibility_validation": validate_layer_readiness_compatibility(source),
        "non_execution_validation": validate_coordination_readiness_non_execution(source),
        "enabled_capability_count": len(enabled_coordination_readiness_capability_flags(source)),
    }
