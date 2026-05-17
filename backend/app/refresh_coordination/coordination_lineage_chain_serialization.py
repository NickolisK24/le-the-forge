"""Canonical serialization for v4.2 coordination lineage chain governance."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Iterable, Mapping

from .coordination_lineage_chain_models import (
    ConflictingLineageVisibility,
    CoordinationLineageChain,
    CoordinationLineageChainDiagnostic,
    CoordinationLineageChainGovernance,
    CoordinationLineageChainIdentity,
    CoordinationLineageChainRecord,
    DependencyGraphLineageChainReference,
    LineagePredecessorReference,
    LineageSourceReference,
    LineageSuccessorReference,
    ManifestLineageChainReference,
    MissingLineageVisibility,
    ProhibitedLineageMutationVisibility,
    StaleLineageVisibility,
    UnsupportedLineageTransitionVisibility,
)


CAPABILITY_FIELD_NAMES: tuple[str, ...] = (
    "execution_authorized",
    "lineage_repair_enabled",
    "lineage_inference_enabled",
    "lineage_mutation_enabled",
    "dependency_resolution_enabled",
    "orchestration_execution_enabled",
    "refresh_execution_enabled",
    "planner_integration_enabled",
    "production_consumption_enabled",
    "production_bundle_consumption_enabled",
    "runtime_mutation_enabled",
    "remediation_enabled",
    "automatic_correction_enabled",
    "automatic_rollback_enabled",
    "authorization_enabled",
    "approval_enabled",
    "ranking_enabled",
    "scoring_enabled",
    "selection_enabled",
    "operational_execution_enabled",
    "execution_enabled",
    "hidden_lineage_resolution_enabled",
    "hidden_fallback_enabled",
    "implicit_execution_pathway_enabled",
)


def sorted_entries(values: Iterable[str] | tuple[str, ...] | list[str]) -> list[str]:
    return sorted(tuple(values or ()))


def canonicalize_lineage_chain_evidence(payload: Any) -> Any:
    if is_dataclass(payload) and not isinstance(payload, type):
        return canonicalize_lineage_chain_evidence(asdict(payload))
    if isinstance(payload, Mapping):
        return {
            str(key): canonicalize_lineage_chain_evidence(value)
            for key, value in sorted(payload.items(), key=lambda item: str(item[0]))
        }
    if isinstance(payload, tuple | list):
        return [canonicalize_lineage_chain_evidence(value) for value in payload]
    return payload


def stable_serialize(payload: Any) -> str:
    return json.dumps(
        canonicalize_lineage_chain_evidence(payload),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _disable_execution_fields(data: dict[str, Any]) -> dict[str, Any]:
    for field_name in CAPABILITY_FIELD_NAMES:
        if field_name in data:
            data[field_name] = False
    return data


def export_coordination_lineage_chain_identity(
    identity: CoordinationLineageChainIdentity,
) -> dict[str, Any]:
    return _disable_execution_fields(asdict(identity))


def export_lineage_source_reference(reference: LineageSourceReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_lineage_predecessor_reference(reference: LineagePredecessorReference) -> dict[str, Any]:
    return _disable_execution_fields(asdict(reference))


def export_lineage_successor_reference(reference: LineageSuccessorReference) -> dict[str, Any]:
    return _disable_execution_fields(asdict(reference))


def export_manifest_lineage_chain_reference(reference: ManifestLineageChainReference) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    data["record_references"] = sorted_entries(data["record_references"])
    return data


def export_dependency_graph_lineage_chain_reference(
    reference: DependencyGraphLineageChainReference,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(reference))
    for field_name in ("node_references", "edge_references", "record_references"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_lineage_chain_record(record: CoordinationLineageChainRecord) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(record))
    data["evidence_references"] = sorted_entries(data["evidence_references"])
    return data


def export_stale_lineage_visibility(visibility: StaleLineageVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "stale_record_ids",
        "stale_source_reference_ids",
        "stale_predecessor_reference_ids",
        "stale_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_missing_lineage_visibility(visibility: MissingLineageVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "missing_record_ids",
        "missing_successor_reference_ids",
        "missing_reference_ids",
        "missing_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_conflicting_lineage_visibility(visibility: ConflictingLineageVisibility) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("conflicting_record_ids", "conflict_pair_visibility", "conflict_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_prohibited_lineage_mutation_visibility(
    visibility: ProhibitedLineageMutationVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in ("prohibited_record_ids", "prohibited_capabilities", "prohibited_reason_visibility"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_unsupported_lineage_transition_visibility(
    visibility: UnsupportedLineageTransitionVisibility,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(visibility))
    for field_name in (
        "unsupported_record_ids",
        "unsupported_transition_ids",
        "unknown_transition_visibility",
        "unsupported_reason_visibility",
    ):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_lineage_chain_diagnostic(
    diagnostic: CoordinationLineageChainDiagnostic,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(diagnostic))
    for field_name in ("affected_record_ids", "affected_reference_ids"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_lineage_chain_governance(
    governance: CoordinationLineageChainGovernance,
) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(governance))
    for field_name in ("governance_references", "explicit_limitations", "explicit_prohibitions"):
        data[field_name] = sorted_entries(data[field_name])
    return data


def export_coordination_lineage_chain(chain: CoordinationLineageChain) -> dict[str, Any]:
    data = _disable_execution_fields(asdict(chain))
    data["identity"] = export_coordination_lineage_chain_identity(chain.identity)
    data["source_references"] = [
        export_lineage_source_reference(reference)
        for reference in sorted(
            chain.source_references,
            key=lambda item: (item.deterministic_order, item.source_reference_id),
        )
    ]
    data["predecessor_references"] = [
        export_lineage_predecessor_reference(reference)
        for reference in sorted(
            chain.predecessor_references,
            key=lambda item: (item.deterministic_order, item.predecessor_reference_id),
        )
    ]
    data["successor_references"] = [
        export_lineage_successor_reference(reference)
        for reference in sorted(
            chain.successor_references,
            key=lambda item: (item.deterministic_order, item.successor_reference_id),
        )
    ]
    data["manifest_lineage_references"] = [
        export_manifest_lineage_chain_reference(reference)
        for reference in sorted(
            chain.manifest_lineage_references,
            key=lambda item: (item.deterministic_order, item.manifest_lineage_reference_id),
        )
    ]
    data["dependency_graph_lineage_references"] = [
        export_dependency_graph_lineage_chain_reference(reference)
        for reference in sorted(
            chain.dependency_graph_lineage_references,
            key=lambda item: (item.deterministic_order, item.dependency_graph_lineage_reference_id),
        )
    ]
    data["records"] = [
        export_coordination_lineage_chain_record(record)
        for record in sorted(chain.records, key=lambda item: (item.deterministic_order, item.record_id))
    ]
    data["stale_lineage_visibility"] = export_stale_lineage_visibility(chain.stale_lineage_visibility)
    data["missing_lineage_visibility"] = export_missing_lineage_visibility(chain.missing_lineage_visibility)
    data["conflicting_lineage_visibility"] = export_conflicting_lineage_visibility(
        chain.conflicting_lineage_visibility
    )
    data["prohibited_lineage_mutation_visibility"] = export_prohibited_lineage_mutation_visibility(
        chain.prohibited_lineage_mutation_visibility
    )
    data["unsupported_lineage_transition_visibility"] = export_unsupported_lineage_transition_visibility(
        chain.unsupported_lineage_transition_visibility
    )
    data["diagnostics"] = [
        export_coordination_lineage_chain_diagnostic(diagnostic)
        for diagnostic in sorted(chain.diagnostics, key=lambda item: (item.deterministic_order, item.diagnostic_id))
    ]
    data["governance_visibility"] = export_coordination_lineage_chain_governance(chain.governance_visibility)
    return data


def serialize_coordination_lineage_chain_identity(identity: CoordinationLineageChainIdentity) -> str:
    return stable_serialize(export_coordination_lineage_chain_identity(identity))


def serialize_coordination_lineage_chain(chain: CoordinationLineageChain) -> str:
    return stable_serialize(export_coordination_lineage_chain(chain))
