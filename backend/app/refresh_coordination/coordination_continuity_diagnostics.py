"""Diagnostics for v4.2 coordination continuity certification."""

from __future__ import annotations

from typing import Any

from .coordination_continuity_hashing import (
    hash_continuity_state_visibility,
    hash_coordination_continuity_certification,
    hash_coordination_continuity_diagnostic,
    hash_cross_layer_continuity_summary,
    hash_cross_layer_coordination_continuity_record,
)
from .coordination_continuity_models import (
    CONTINUITY_STATE_CONFLICTING,
    CONTINUITY_STATE_CROSS_LAYER,
    CONTINUITY_STATE_MISSING,
    CONTINUITY_STATE_PROHIBITED_REPAIR,
    CONTINUITY_STATE_STALE,
    CONTINUITY_STATE_UNSUPPORTED_TRANSITION,
    CONTINUITY_STATES,
    FAIL_VISIBLE_CONTINUITY_STATES,
    CoordinationContinuityCertification,
    CrossLayerCoordinationContinuityRecord,
    default_coordination_continuity_certification,
)
from .coordination_continuity_serialization import serialize_coordination_continuity_certification
from .coordination_dependency_graph_hashing import hash_coordination_dependency_graph
from .coordination_dependency_graph_models import CoordinationDependencyGraph, default_coordination_dependency_graph
from .coordination_diagnostics_hashing import (
    hash_coordination_diagnostics_explainability,
    hash_fail_visible_explanation_summary,
)
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
from .coordination_sequencing_hashing import hash_coordination_sequencing_intelligence
from .coordination_sequencing_models import (
    CoordinationSequencingIntelligence,
    default_coordination_sequencing_intelligence,
)
from .governance_routing_hashing import hash_governance_routing_visibility
from .governance_routing_models import GovernanceRoutingVisibility, default_governance_routing_visibility


CAPABILITY_FLAG_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "continuity_repair_enabled",
    "continuity_inference_enabled",
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
    "hidden_continuity_repair_enabled",
    "implicit_execution_pathway_enabled",
)


def count_coordination_continuity_states(
    records: tuple[CrossLayerCoordinationContinuityRecord, ...],
) -> dict[str, int]:
    counts = {state: 0 for state in CONTINUITY_STATES}
    counts["invalid"] = 0
    for record in records:
        if record.continuity_state in counts:
            counts[record.continuity_state] += 1
        else:
            counts["invalid"] += 1
    return counts


def aggregate_continuity_state_records(
    certification: CoordinationContinuityCertification,
    continuity_state: str,
) -> tuple[str, ...]:
    return tuple(
        record.continuity_record_id
        for record in certification.continuity_records
        if record.continuity_state == continuity_state
    )


def fail_visible_coordination_continuity_record_ids(
    records: tuple[CrossLayerCoordinationContinuityRecord, ...],
) -> tuple[str, ...]:
    return tuple(
        record.continuity_record_id
        for record in records
        if record.continuity_state in FAIL_VISIBLE_CONTINUITY_STATES and record.fail_visible
    )


def coordination_continuity_capability_flags(
    certification: CoordinationContinuityCertification,
) -> dict[str, bool]:
    flags: dict[str, bool] = {}
    candidates: tuple[object, ...] = (
        certification,
        certification.identity,
        certification.stale_continuity_visibility,
        certification.missing_continuity_visibility,
        certification.conflicting_continuity_visibility,
        certification.prohibited_repair_visibility,
        certification.unsupported_transition_visibility,
        certification.cross_layer_continuity_summary,
        certification.governance_visibility,
        *certification.manifest_continuity_references,
        *certification.dependency_graph_continuity_references,
        *certification.lineage_continuity_references,
        *certification.sequencing_continuity_references,
        *certification.routing_continuity_references,
        *certification.drift_continuity_references,
        *certification.diagnostics_continuity_references,
        *certification.explainability_continuity_references,
        *certification.continuity_records,
        *certification.diagnostics,
    )
    for index, candidate in enumerate(candidates):
        candidate_name = candidate.__class__.__name__
        for flag_name in CAPABILITY_FLAG_NAMES:
            if hasattr(candidate, flag_name):
                flags[f"{candidate_name}.{index}.{flag_name}"] = bool(getattr(candidate, flag_name))
    return flags


def enabled_coordination_continuity_capability_flags(
    certification: CoordinationContinuityCertification,
) -> dict[str, bool]:
    return {key: value for key, value in coordination_continuity_capability_flags(certification).items() if value}


def coordination_continuity_certifications_equal(
    left: CoordinationContinuityCertification,
    right: CoordinationContinuityCertification,
) -> bool:
    return serialize_coordination_continuity_certification(left) == serialize_coordination_continuity_certification(
        right
    )


def _corrective_enabled(item: object) -> bool:
    return any(bool(getattr(item, flag_name, False)) for flag_name in CAPABILITY_FLAG_NAMES)


def validate_coordination_continuity_visibility(
    certification: CoordinationContinuityCertification,
) -> dict[str, object]:
    stale_record_ids = aggregate_continuity_state_records(certification, CONTINUITY_STATE_STALE)
    missing_record_ids = aggregate_continuity_state_records(certification, CONTINUITY_STATE_MISSING)
    conflicting_record_ids = aggregate_continuity_state_records(certification, CONTINUITY_STATE_CONFLICTING)
    prohibited_record_ids = aggregate_continuity_state_records(
        certification,
        CONTINUITY_STATE_PROHIBITED_REPAIR,
    )
    unsupported_record_ids = aggregate_continuity_state_records(
        certification,
        CONTINUITY_STATE_UNSUPPORTED_TRANSITION,
    )
    stale_visible = set(stale_record_ids).issubset(
        set(certification.stale_continuity_visibility.continuity_record_ids)
    )
    missing_visible = set(missing_record_ids).issubset(
        set(certification.missing_continuity_visibility.continuity_record_ids)
    )
    conflicting_visible = set(conflicting_record_ids).issubset(
        set(certification.conflicting_continuity_visibility.continuity_record_ids)
    )
    prohibited_visible = set(prohibited_record_ids).issubset(
        set(certification.prohibited_repair_visibility.continuity_record_ids)
    )
    unsupported_visible = set(unsupported_record_ids).issubset(
        set(certification.unsupported_transition_visibility.continuity_record_ids)
    )
    invalid_record_ids = tuple(
        record.continuity_record_id
        for record in certification.continuity_records
        if record.continuity_state not in CONTINUITY_STATES
    )
    hidden_count = sum(
        1 for item in (*certification.continuity_records, *certification.diagnostics) if getattr(item, "hidden", False)
    )
    corrective_count = sum(
        1
        for item in (
            certification.stale_continuity_visibility,
            certification.missing_continuity_visibility,
            certification.conflicting_continuity_visibility,
            certification.prohibited_repair_visibility,
            certification.unsupported_transition_visibility,
            certification.cross_layer_continuity_summary,
            *certification.continuity_records,
            *certification.diagnostics,
        )
        if _corrective_enabled(item)
    )
    return {
        "valid": (
            stale_visible
            and missing_visible
            and conflicting_visible
            and prohibited_visible
            and unsupported_visible
            and len(invalid_record_ids) == 0
            and hidden_count == 0
            and corrective_count == 0
        ),
        "continuity_state_counts": count_coordination_continuity_states(certification.continuity_records),
        "fail_visible_record_ids": fail_visible_coordination_continuity_record_ids(
            certification.continuity_records
        ),
        "stale_record_ids": stale_record_ids,
        "missing_record_ids": missing_record_ids,
        "conflicting_record_ids": conflicting_record_ids,
        "prohibited_repair_record_ids": prohibited_record_ids,
        "unsupported_transition_record_ids": unsupported_record_ids,
        "stale_continuity_visible": stale_visible,
        "missing_continuity_visible": missing_visible,
        "conflicting_continuity_visible": conflicting_visible,
        "prohibited_repair_visible": prohibited_visible,
        "unsupported_transition_visible": unsupported_visible,
        "invalid_record_ids": invalid_record_ids,
        "hidden_count": hidden_count,
        "corrective_count": corrective_count,
        "diagnostics_fail_visible": all(diagnostic.fail_visible for diagnostic in certification.diagnostics),
        "diagnostics_descriptive_only": all(diagnostic.descriptive_only for diagnostic in certification.diagnostics),
    }


def validate_cross_layer_continuity_summary(
    certification: CoordinationContinuityCertification,
) -> dict[str, object]:
    cross_layer_record_ids = aggregate_continuity_state_records(certification, CONTINUITY_STATE_CROSS_LAYER)
    summary_ids = set(certification.cross_layer_continuity_summary.continuity_record_ids)
    visible = set(cross_layer_record_ids).issubset(summary_ids)
    involved_layers_visible = len(certification.cross_layer_continuity_summary.involved_layer_references) > 0
    return {
        "valid": visible
        and involved_layers_visible
        and certification.cross_layer_continuity_summary.descriptive_only
        and not _corrective_enabled(certification.cross_layer_continuity_summary),
        "cross_layer_record_ids": cross_layer_record_ids,
        "summary_record_ids": certification.cross_layer_continuity_summary.continuity_record_ids,
        "cross_layer_continuity_visible": visible,
        "involved_layers_visible": involved_layers_visible,
        "summary_line_count": len(certification.cross_layer_continuity_summary.summary_lines),
        "continuity_state_counts": certification.cross_layer_continuity_summary.continuity_state_counts,
    }


def validate_manifest_continuity_compatibility(
    certification: CoordinationContinuityCertification,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source = manifest or default_coordination_manifest()
    reference = certification.manifest_continuity_references[0]
    return {
        "valid": (
            reference.manifest_reference == source.identity.manifest_id
            and reference.manifest_hash_reference == hash_coordination_manifest(source)
            and certification.compatibility_manifest_reference == source.identity.manifest_id
        ),
        "manifest_continuity_reference_matches": reference.manifest_reference == source.identity.manifest_id,
        "manifest_hash_matches": reference.manifest_hash_reference == hash_coordination_manifest(source),
    }


def validate_dependency_graph_continuity_compatibility(
    certification: CoordinationContinuityCertification,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source = dependency_graph or default_coordination_dependency_graph(source_manifest)
    reference = certification.dependency_graph_continuity_references[0]
    return {
        "valid": (
            reference.dependency_graph_reference == source.identity.graph_id
            and reference.dependency_graph_hash_reference == hash_coordination_dependency_graph(source)
            and certification.compatibility_dependency_graph_reference == source.identity.graph_id
        ),
        "dependency_graph_continuity_reference_matches": reference.dependency_graph_reference == source.identity.graph_id,
        "dependency_graph_hash_matches": reference.dependency_graph_hash_reference
        == hash_coordination_dependency_graph(source),
    }


def validate_lineage_continuity_compatibility(
    certification: CoordinationContinuityCertification,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    reference = certification.lineage_continuity_references[0]
    return {
        "valid": (
            reference.lineage_chain_reference == source.identity.chain_id
            and reference.lineage_chain_hash_reference == hash_coordination_lineage_chain(source)
            and certification.compatibility_lineage_chain_reference == source.identity.chain_id
        ),
        "lineage_continuity_reference_matches": reference.lineage_chain_reference == source.identity.chain_id,
        "lineage_chain_hash_matches": reference.lineage_chain_hash_reference
        == hash_coordination_lineage_chain(source),
    }


def validate_sequencing_continuity_compatibility(
    certification: CoordinationContinuityCertification,
    sequencing: CoordinationSequencingIntelligence | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    manifest: CoordinationManifest | None = None,
) -> dict[str, object]:
    source_manifest = manifest or default_coordination_manifest()
    source_graph = dependency_graph or default_coordination_dependency_graph(source_manifest)
    source_lineage = lineage_chain or default_coordination_lineage_chain(source_manifest, source_graph)
    source = sequencing or default_coordination_sequencing_intelligence(
        source_manifest,
        source_graph,
        source_lineage,
    )
    reference = certification.sequencing_continuity_references[0]
    return {
        "valid": (
            reference.sequencing_reference == source.identity.sequencing_id
            and reference.sequencing_hash_reference == hash_coordination_sequencing_intelligence(source)
            and certification.compatibility_sequencing_reference == source.identity.sequencing_id
        ),
        "sequencing_continuity_reference_matches": reference.sequencing_reference == source.identity.sequencing_id,
        "sequencing_hash_matches": reference.sequencing_hash_reference
        == hash_coordination_sequencing_intelligence(source),
    }


def validate_routing_continuity_compatibility(
    certification: CoordinationContinuityCertification,
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
    source = routing or default_governance_routing_visibility(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
    )
    reference = certification.routing_continuity_references[0]
    return {
        "valid": (
            reference.routing_reference == source.identity.routing_id
            and reference.routing_hash_reference == hash_governance_routing_visibility(source)
            and certification.compatibility_routing_reference == source.identity.routing_id
        ),
        "routing_continuity_reference_matches": reference.routing_reference == source.identity.routing_id,
        "routing_hash_matches": reference.routing_hash_reference == hash_governance_routing_visibility(source),
    }


def validate_drift_continuity_compatibility(
    certification: CoordinationContinuityCertification,
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
    source = drift or default_coordination_drift_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
    )
    reference = certification.drift_continuity_references[0]
    return {
        "valid": (
            reference.drift_reference == source.identity.drift_certification_id
            and reference.drift_hash_reference == hash_coordination_drift_certification(source)
            and certification.compatibility_drift_reference == source.identity.drift_certification_id
        ),
        "drift_continuity_reference_matches": reference.drift_reference == source.identity.drift_certification_id,
        "drift_hash_matches": reference.drift_hash_reference == hash_coordination_drift_certification(source),
    }


def validate_diagnostics_explainability_continuity_compatibility(
    certification: CoordinationContinuityCertification,
    diagnostics: CoordinationDiagnosticsExplainability | None = None,
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
    source = diagnostics or default_coordination_diagnostics_explainability(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
    )
    diagnostics_reference = certification.diagnostics_continuity_references[0]
    explainability_reference = certification.explainability_continuity_references[0]
    diagnostics_hash_matches = (
        diagnostics_reference.diagnostics_hash_reference == hash_coordination_diagnostics_explainability(source)
    )
    explainability_hash_matches = (
        explainability_reference.explainability_hash_reference
        == hash_fail_visible_explanation_summary(source.fail_visible_explanation_summary)
    )
    return {
        "valid": (
            diagnostics_reference.diagnostics_reference == source.identity.diagnostics_id
            and diagnostics_hash_matches
            and explainability_reference.explainability_reference == source.identity.explainability_reference
            and explainability_hash_matches
            and certification.compatibility_diagnostics_reference == source.identity.diagnostics_id
            and certification.compatibility_explainability_reference == source.identity.explainability_reference
        ),
        "diagnostics_continuity_reference_matches": diagnostics_reference.diagnostics_reference
        == source.identity.diagnostics_id,
        "diagnostics_hash_matches": diagnostics_hash_matches,
        "explainability_continuity_reference_matches": explainability_reference.explainability_reference
        == source.identity.explainability_reference,
        "explainability_hash_matches": explainability_hash_matches,
    }


def validate_coordination_continuity_non_execution(
    certification: CoordinationContinuityCertification,
) -> dict[str, object]:
    enabled_flags = enabled_coordination_continuity_capability_flags(certification)
    return {
        "valid": len(enabled_flags) == 0 and certification.non_executable and certification.descriptive_only,
        "enabled_capability_count": len(enabled_flags),
        "enabled_capability_flags": enabled_flags,
        "descriptive_only": certification.descriptive_only,
        "non_executable": certification.non_executable,
        "continuity_repair_disabled": not certification.continuity_repair_enabled,
        "continuity_inference_disabled": not certification.continuity_inference_enabled,
        "remediation_disabled": not certification.remediation_enabled,
        "automatic_correction_disabled": not certification.automatic_correction_enabled,
        "drift_correction_disabled": not certification.drift_correction_enabled,
        "drift_remediation_disabled": not certification.drift_remediation_enabled,
        "routing_execution_disabled": not certification.routing_execution_enabled,
        "orchestration_execution_disabled": not certification.orchestration_execution_enabled,
        "refresh_execution_disabled": not certification.refresh_execution_enabled,
        "sequencing_execution_disabled": not certification.sequencing_execution_enabled,
        "scheduling_execution_disabled": not certification.scheduling_execution_enabled,
        "dependency_resolution_disabled": not certification.dependency_resolution_enabled,
        "lineage_repair_disabled": not certification.lineage_repair_enabled,
        "lineage_inference_disabled": not certification.lineage_inference_enabled,
        "planner_integration_disabled": not certification.planner_integration_enabled,
        "production_consumption_disabled": not certification.production_consumption_enabled,
        "runtime_mutation_disabled": not certification.runtime_mutation_enabled,
        "automatic_rollback_disabled": not certification.automatic_rollback_enabled,
        "authorization_disabled": not certification.authorization_enabled,
        "approval_disabled": not certification.approval_enabled,
        "ranking_disabled": not certification.ranking_enabled,
        "scoring_disabled": not certification.scoring_enabled,
        "selection_disabled": not certification.selection_enabled,
        "operational_execution_disabled": not certification.operational_execution_enabled,
        "hidden_continuity_repair_absent": not certification.hidden_continuity_repair_enabled,
        "implicit_execution_pathway_absent": not certification.implicit_execution_pathway_enabled,
    }


def build_coordination_continuity_diagnostics(
    certification: CoordinationContinuityCertification | None = None,
    manifest: CoordinationManifest | None = None,
    dependency_graph: CoordinationDependencyGraph | None = None,
    lineage_chain: CoordinationLineageChain | None = None,
    sequencing: CoordinationSequencingIntelligence | None = None,
    routing: GovernanceRoutingVisibility | None = None,
    drift: CoordinationDriftCertification | None = None,
    diagnostics: CoordinationDiagnosticsExplainability | None = None,
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
    source_diagnostics = diagnostics or default_coordination_diagnostics_explainability(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
    )
    source_certification = certification or default_coordination_continuity_certification(
        source_manifest,
        source_graph,
        source_lineage,
        source_sequencing,
        source_routing,
        source_drift,
        source_diagnostics,
    )
    return {
        "continuity_hash": hash_coordination_continuity_certification(source_certification),
        "continuity_record_hashes": [
            hash_cross_layer_coordination_continuity_record(record)
            for record in source_certification.continuity_records
        ],
        "visibility_hashes": [
            hash_continuity_state_visibility(source_certification.stale_continuity_visibility),
            hash_continuity_state_visibility(source_certification.missing_continuity_visibility),
            hash_continuity_state_visibility(source_certification.conflicting_continuity_visibility),
            hash_continuity_state_visibility(source_certification.prohibited_repair_visibility),
            hash_continuity_state_visibility(source_certification.unsupported_transition_visibility),
        ],
        "summary_hash": hash_cross_layer_continuity_summary(
            source_certification.cross_layer_continuity_summary
        ),
        "diagnostic_hashes": [
            hash_coordination_continuity_diagnostic(diagnostic)
            for diagnostic in source_certification.diagnostics
        ],
        "continuity_visibility_validation": validate_coordination_continuity_visibility(
            source_certification
        ),
        "cross_layer_summary_validation": validate_cross_layer_continuity_summary(source_certification),
        "manifest_continuity_compatibility_validation": validate_manifest_continuity_compatibility(
            source_certification,
            source_manifest,
        ),
        "dependency_graph_continuity_compatibility_validation": validate_dependency_graph_continuity_compatibility(
            source_certification,
            source_graph,
            source_manifest,
        ),
        "lineage_continuity_compatibility_validation": validate_lineage_continuity_compatibility(
            source_certification,
            source_lineage,
            source_graph,
            source_manifest,
        ),
        "sequencing_continuity_compatibility_validation": validate_sequencing_continuity_compatibility(
            source_certification,
            source_sequencing,
            source_lineage,
            source_graph,
            source_manifest,
        ),
        "routing_continuity_compatibility_validation": validate_routing_continuity_compatibility(
            source_certification,
            source_routing,
            source_sequencing,
            source_lineage,
            source_graph,
            source_manifest,
        ),
        "drift_continuity_compatibility_validation": validate_drift_continuity_compatibility(
            source_certification,
            source_drift,
            source_routing,
            source_sequencing,
            source_lineage,
            source_graph,
            source_manifest,
        ),
        "diagnostics_explainability_continuity_compatibility_validation": (
            validate_diagnostics_explainability_continuity_compatibility(
                source_certification,
                source_diagnostics,
                source_drift,
                source_routing,
                source_sequencing,
                source_lineage,
                source_graph,
                source_manifest,
            )
        ),
        "non_execution_validation": validate_coordination_continuity_non_execution(source_certification),
        "enabled_capability_count": len(enabled_coordination_continuity_capability_flags(source_certification)),
    }
