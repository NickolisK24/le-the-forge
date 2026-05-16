"""Provenance continuity for v3.7 planning intelligence aggregation."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_intelligence_aggregation import build_v3_7_graph_planning_intelligence_aggregation
from .v3_7_graph_intelligence_models import V37GraphPlanningIntelligenceAggregation
from .v3_7_graph_models import V37GraphProvenance


V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED = "v3_7_graph_intelligence_provenance_preserved"
V37_GRAPH_INTELLIGENCE_PROVENANCE_BLOCKED = "v3_7_graph_intelligence_provenance_blocked"


@dataclass(frozen=True)
class V37GraphIntelligenceProvenanceResult:
    provenance_status: str
    aggregation_creation_provenance_preserved: bool
    graph_provenance_preserved: bool
    governance_provenance_preserved: bool
    compatibility_provenance_preserved: bool
    evaluation_provenance_preserved: bool
    session_provenance_preserved: bool
    scenario_provenance_preserved: bool
    replay_provenance_preserved: bool
    rollback_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_intelligence_provenance(
    aggregation: V37GraphPlanningIntelligenceAggregation | None = None,
) -> V37GraphIntelligenceProvenanceResult:
    planning_intelligence = aggregation or build_v3_7_graph_planning_intelligence_aggregation()
    missing: list[str] = []
    aggregation_ok = _provenance_complete(planning_intelligence.provenance)
    if not aggregation_ok:
        missing.append(planning_intelligence.identity.aggregation_id)
    by_type = {source.source_type: source for source in planning_intelligence.evidence_sources}
    graph_ok = _source_has_provenance(by_type, "graph_foundations", missing)
    governance_ok = _source_has_provenance(by_type, "governance", missing)
    compatibility_ok = _source_has_provenance(by_type, "compatibility", missing)
    evaluation_ok = _source_has_provenance(by_type, "evaluation", missing)
    session_ok = _source_has_provenance(by_type, "session", missing)
    scenario_ok = _source_has_provenance(by_type, "scenario", missing)
    replay_ok = all(evidence.provenance_references for evidence in planning_intelligence.replay_evidence)
    if not replay_ok:
        missing.append("intelligence_replay_evidence")
    rollback_ok = bool(planning_intelligence.rollback_continuity_references)
    if not rollback_ok:
        missing.append("intelligence_rollback_continuity")
    explainability_ok = bool(planning_intelligence.explainability_reference_ids) and all(
        source.explainability_references for source in planning_intelligence.evidence_sources
    )
    if not explainability_ok:
        missing.append("intelligence_explainability")
    continuity_ok = bool(planning_intelligence.continuity_hash_references) and all(
        source.continuity_references for source in planning_intelligence.evidence_sources
    )
    if not continuity_ok:
        missing.append("intelligence_continuity")
    preserved = all(
        (
            aggregation_ok,
            graph_ok,
            governance_ok,
            compatibility_ok,
            evaluation_ok,
            session_ok,
            scenario_ok,
            replay_ok,
            rollback_ok,
            explainability_ok,
            continuity_ok,
        )
    )
    records = collect_v3_7_graph_intelligence_provenance(planning_intelligence)
    result = V37GraphIntelligenceProvenanceResult(
        provenance_status=V37_GRAPH_INTELLIGENCE_PROVENANCE_PRESERVED if preserved else V37_GRAPH_INTELLIGENCE_PROVENANCE_BLOCKED,
        aggregation_creation_provenance_preserved=aggregation_ok,
        graph_provenance_preserved=graph_ok,
        governance_provenance_preserved=governance_ok,
        compatibility_provenance_preserved=compatibility_ok,
        evaluation_provenance_preserved=evaluation_ok,
        session_provenance_preserved=session_ok,
        scenario_provenance_preserved=scenario_ok,
        replay_provenance_preserved=replay_ok,
        rollback_provenance_preserved=rollback_ok,
        explainability_provenance_preserved=bool(explainability_ok),
        continuity_provenance_preserved=continuity_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_intelligence_provenance_result(result),
    )


def collect_v3_7_graph_intelligence_provenance(
    aggregation: V37GraphPlanningIntelligenceAggregation,
) -> tuple[V37GraphProvenance, ...]:
    return (aggregation.provenance,)


def export_v3_7_graph_intelligence_provenance_result(
    result: V37GraphIntelligenceProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_intelligence_provenance_result(
    result: V37GraphIntelligenceProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_intelligence_provenance_result(result))


def hash_v3_7_graph_intelligence_provenance_result(
    result: V37GraphIntelligenceProvenanceResult,
) -> str:
    data = export_v3_7_graph_intelligence_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _source_has_provenance(by_type: dict[str, object], source_type: str, missing: list[str]) -> bool:
    source = by_type.get(source_type)
    ok = bool(source and source.provenance_references)
    if not ok:
        missing.append(f"{source_type}_provenance")
    return ok


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
            provenance.governance_references,
            provenance.compatibility_references,
            provenance.explainability_references,
        )
    )
