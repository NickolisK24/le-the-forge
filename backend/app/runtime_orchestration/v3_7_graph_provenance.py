"""Provenance continuity auditing for v3.7 graph foundations."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphProvenance, V37OrchestrationPlanningGraph
from .v3_7_graph_serialization import export_v3_7_graph_provenance


V37_PROVENANCE_CONTINUITY_PRESERVED = "v3_7_graph_provenance_continuity_preserved"
V37_PROVENANCE_CONTINUITY_BLOCKED = "v3_7_graph_provenance_continuity_blocked"


@dataclass(frozen=True)
class V37GraphProvenanceContinuityResult:
    provenance_status: str
    graph_creation_provenance_preserved: bool
    node_provenance_preserved: bool
    edge_provenance_preserved: bool
    governance_provenance_preserved: bool
    compatibility_provenance_preserved: bool
    explainability_provenance_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_provenance(graph: V37OrchestrationPlanningGraph) -> V37GraphProvenanceContinuityResult:
    missing: list[str] = []
    graph_creation = _provenance_complete(graph.provenance)
    if not graph_creation:
        missing.append(graph.identity.graph_id)

    node_provenance = True
    for node in graph.nodes:
        if not _provenance_complete(node.provenance):
            node_provenance = False
            missing.append(node.identity.node_id)

    edge_provenance = True
    for edge in graph.edges:
        if not _provenance_complete(edge.provenance):
            edge_provenance = False
            missing.append(edge.identity.edge_id)

    governance_provenance = True
    for boundary in graph.governance_boundaries:
        if not _provenance_complete(boundary.provenance) or not boundary.provenance.governance_references:
            governance_provenance = False
            missing.append(boundary.boundary_id)

    compatibility_provenance = True
    for boundary in graph.compatibility_boundaries:
        if not _provenance_complete(boundary.provenance) or not boundary.provenance.compatibility_references:
            compatibility_provenance = False
            missing.append(boundary.boundary_id)

    explainability_provenance = True
    for evidence in graph.explainability_evidence:
        if not _provenance_complete(evidence.provenance) or not evidence.provenance.explainability_references:
            explainability_provenance = False
            missing.append(evidence.evidence_id)

    records = collect_v3_7_graph_provenance(graph)
    replay_continuity = all(record.replay_lineage_references for record in records)
    rollback_continuity = all(record.rollback_lineage_references for record in records)
    preserved = all(
        (
            graph_creation,
            node_provenance,
            edge_provenance,
            governance_provenance,
            compatibility_provenance,
            explainability_provenance,
            replay_continuity,
            rollback_continuity,
        )
    )
    result = V37GraphProvenanceContinuityResult(
        provenance_status=(
            V37_PROVENANCE_CONTINUITY_PRESERVED if preserved else V37_PROVENANCE_CONTINUITY_BLOCKED
        ),
        graph_creation_provenance_preserved=graph_creation,
        node_provenance_preserved=node_provenance,
        edge_provenance_preserved=edge_provenance,
        governance_provenance_preserved=governance_provenance,
        compatibility_provenance_preserved=compatibility_provenance,
        explainability_provenance_preserved=explainability_provenance,
        replay_continuity_preserved=replay_continuity,
        rollback_continuity_preserved=rollback_continuity,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(result, deterministic_provenance_hash=hash_v3_7_graph_provenance_result(result))


def collect_v3_7_graph_provenance(graph: V37OrchestrationPlanningGraph) -> tuple[V37GraphProvenance, ...]:
    records: list[V37GraphProvenance] = [graph.provenance]
    records.extend(node.provenance for node in graph.nodes)
    records.extend(edge.provenance for edge in graph.edges)
    records.extend(boundary.provenance for boundary in graph.governance_boundaries)
    records.extend(boundary.provenance for boundary in graph.compatibility_boundaries)
    records.extend(evidence.provenance for evidence in graph.explainability_evidence)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_provenance_continuity_result(
    result: V37GraphProvenanceContinuityResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_provenance_result(result: V37GraphProvenanceContinuityResult) -> str:
    return stable_serialize(export_v3_7_graph_provenance_continuity_result(result))


def hash_v3_7_graph_provenance_result(result: V37GraphProvenanceContinuityResult) -> str:
    data = export_v3_7_graph_provenance_continuity_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def export_v3_7_graph_provenance_records(graph: V37OrchestrationPlanningGraph) -> list[dict[str, Any]]:
    return [export_v3_7_graph_provenance(record) for record in collect_v3_7_graph_provenance(graph)]


def _provenance_complete(provenance: V37GraphProvenance) -> bool:
    return all(
        (
            provenance.provenance_id,
            provenance.source_phase_id,
            provenance.source_artifact_id,
            provenance.source_kind,
            provenance.lineage_references,
            provenance.replay_lineage_references,
            provenance.rollback_lineage_references,
        )
    )
