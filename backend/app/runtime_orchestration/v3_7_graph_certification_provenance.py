"""Provenance continuity for v3.7 graph planning certification."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_certification_evidence import build_v3_7_graph_planning_continuity_certification
from .v3_7_graph_certification_models import V37GraphPlanningContinuityCertification


V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED = "v3_7_graph_certification_provenance_preserved"
V37_GRAPH_CERTIFICATION_PROVENANCE_BLOCKED = "v3_7_graph_certification_provenance_blocked"


@dataclass(frozen=True)
class V37GraphCertificationProvenanceResult:
    provenance_status: str
    provenance_record_count: int
    certification_provenance_preserved: bool
    scope_provenance_preserved: bool
    graph_provenance_preserved: bool
    governance_provenance_preserved: bool
    compatibility_provenance_preserved: bool
    evaluation_provenance_preserved: bool
    session_provenance_preserved: bool
    scenario_provenance_preserved: bool
    aggregation_provenance_preserved: bool
    integrity_provenance_preserved: bool
    replay_provenance_preserved: bool
    rollback_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    execution_boundary_provenance_preserved: bool
    deterministic_provenance_hash: str
    provenance_records: tuple[str, ...]


def audit_v3_7_graph_certification_provenance(
    certification: V37GraphPlanningContinuityCertification | None = None,
) -> V37GraphCertificationProvenanceResult:
    result = certification or build_v3_7_graph_planning_continuity_certification()
    records = collect_v3_7_graph_certification_provenance(result)
    reference_types = {reference.reference_type for reference in result.scope.references}
    checks = {
        "certification": bool(result.provenance.provenance_id),
        "scope": bool(result.scope.provenance.provenance_id),
        "graph": "graph_foundations" in reference_types,
        "governance": "governance" in reference_types,
        "compatibility": "compatibility" in reference_types,
        "evaluation": "evaluation" in reference_types,
        "session": "session" in reference_types,
        "scenario": "scenario" in reference_types,
        "aggregation": "aggregation" in reference_types,
        "integrity": "integrity" in reference_types,
        "replay": all(item.provenance_references for item in result.replay_evidence),
        "rollback": bool(result.rollback_continuity_references),
        "explainability": bool(result.explainability_reference_ids),
        "continuity": bool(result.continuity_hash_references),
        "execution_boundary": bool(result.evidence.execution_boundary_references),
    }
    status = (
        V37_GRAPH_CERTIFICATION_PROVENANCE_PRESERVED
        if all(checks.values())
        else V37_GRAPH_CERTIFICATION_PROVENANCE_BLOCKED
    )
    audit = V37GraphCertificationProvenanceResult(
        provenance_status=status,
        provenance_record_count=len(records),
        certification_provenance_preserved=checks["certification"],
        scope_provenance_preserved=checks["scope"],
        graph_provenance_preserved=checks["graph"],
        governance_provenance_preserved=checks["governance"],
        compatibility_provenance_preserved=checks["compatibility"],
        evaluation_provenance_preserved=checks["evaluation"],
        session_provenance_preserved=checks["session"],
        scenario_provenance_preserved=checks["scenario"],
        aggregation_provenance_preserved=checks["aggregation"],
        integrity_provenance_preserved=checks["integrity"],
        replay_provenance_preserved=checks["replay"],
        rollback_provenance_preserved=checks["rollback"],
        explainability_provenance_preserved=checks["explainability"],
        continuity_provenance_preserved=checks["continuity"],
        execution_boundary_provenance_preserved=checks["execution_boundary"],
        deterministic_provenance_hash="",
        provenance_records=records,
    )
    return replace(audit, deterministic_provenance_hash=hash_v3_7_graph_certification_provenance_result(audit))


def collect_v3_7_graph_certification_provenance(
    certification: V37GraphPlanningContinuityCertification,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            set(
                (
                    certification.provenance.provenance_id,
                    certification.scope.provenance.provenance_id,
                    *certification.evidence.provenance_references,
                    *certification.evidence.rollback_references,
                    *certification.evidence.explainability_references,
                    *certification.evidence.continuity_hashes,
                    *certification.evidence.execution_boundary_references,
                )
            )
        )
    )


def export_v3_7_graph_certification_provenance_result(
    result: V37GraphCertificationProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["provenance_records"] = sorted(data["provenance_records"])
    return data


def serialize_v3_7_graph_certification_provenance_result(
    result: V37GraphCertificationProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_certification_provenance_result(result))


def hash_v3_7_graph_certification_provenance_result(result: V37GraphCertificationProvenanceResult) -> str:
    data = export_v3_7_graph_certification_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)
