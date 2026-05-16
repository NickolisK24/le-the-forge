"""Provenance continuity for v3.7 graph planning integrity enforcement."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_integrity_enforcement import enforce_v3_7_graph_planning_integrity
from .v3_7_graph_integrity_models import V37GraphIntegrityEnforcementResult


V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED = "v3_7_graph_integrity_provenance_preserved"
V37_GRAPH_INTEGRITY_PROVENANCE_BLOCKED = "v3_7_graph_integrity_provenance_blocked"


@dataclass(frozen=True)
class V37GraphIntegrityProvenanceResult:
    provenance_status: str
    provenance_record_count: int
    enforcement_provenance_preserved: bool
    policy_provenance_preserved: bool
    graph_provenance_preserved: bool
    governance_provenance_preserved: bool
    compatibility_provenance_preserved: bool
    evaluation_provenance_preserved: bool
    session_provenance_preserved: bool
    scenario_provenance_preserved: bool
    aggregation_provenance_preserved: bool
    replay_provenance_preserved: bool
    rollback_provenance_preserved: bool
    explainability_provenance_preserved: bool
    continuity_provenance_preserved: bool
    deterministic_provenance_hash: str
    provenance_records: tuple[str, ...]


def audit_v3_7_graph_integrity_provenance(
    result: V37GraphIntegrityEnforcementResult | None = None,
) -> V37GraphIntegrityProvenanceResult:
    enforcement = result or enforce_v3_7_graph_planning_integrity()
    records = collect_v3_7_graph_integrity_provenance(enforcement)
    source_types = set(enforcement.evidence_source_types)
    replay_ok = all(item.provenance_references for item in enforcement.replay_evidence)
    rollback_ok = bool(enforcement.rollback_continuity_references)
    explainability_ok = bool(enforcement.explainability_reference_ids)
    continuity_ok = bool(enforcement.continuity_hash_references)
    checks = {
        "enforcement": bool(enforcement.provenance.provenance_id),
        "policy": bool(enforcement.policy.provenance.provenance_id),
        "graph": "graph_foundations" in source_types,
        "governance": "governance" in source_types,
        "compatibility": "compatibility" in source_types,
        "evaluation": "evaluation" in source_types,
        "session": "session" in source_types,
        "scenario": "scenario" in source_types,
        "aggregation": "aggregation" in source_types,
        "replay": replay_ok,
        "rollback": rollback_ok,
        "explainability": explainability_ok,
        "continuity": continuity_ok,
    }
    status = (
        V37_GRAPH_INTEGRITY_PROVENANCE_PRESERVED
        if all(checks.values())
        else V37_GRAPH_INTEGRITY_PROVENANCE_BLOCKED
    )
    audit = V37GraphIntegrityProvenanceResult(
        provenance_status=status,
        provenance_record_count=len(records),
        enforcement_provenance_preserved=checks["enforcement"],
        policy_provenance_preserved=checks["policy"],
        graph_provenance_preserved=checks["graph"],
        governance_provenance_preserved=checks["governance"],
        compatibility_provenance_preserved=checks["compatibility"],
        evaluation_provenance_preserved=checks["evaluation"],
        session_provenance_preserved=checks["session"],
        scenario_provenance_preserved=checks["scenario"],
        aggregation_provenance_preserved=checks["aggregation"],
        replay_provenance_preserved=checks["replay"],
        rollback_provenance_preserved=checks["rollback"],
        explainability_provenance_preserved=checks["explainability"],
        continuity_provenance_preserved=checks["continuity"],
        deterministic_provenance_hash="",
        provenance_records=records,
    )
    return replace(audit, deterministic_provenance_hash=hash_v3_7_graph_integrity_provenance_result(audit))


def collect_v3_7_graph_integrity_provenance(
    result: V37GraphIntegrityEnforcementResult,
) -> tuple[str, ...]:
    return tuple(
        sorted(
            set(
                (
                    result.provenance.provenance_id,
                    result.policy.provenance.provenance_id,
                    *(
                        reference
                        for evidence in result.replay_evidence
                        for reference in evidence.provenance_references
                    ),
                    *result.rollback_continuity_references,
                    *result.explainability_reference_ids,
                    *result.continuity_hash_references,
                )
            )
        )
    )


def export_v3_7_graph_integrity_provenance_result(
    result: V37GraphIntegrityProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["provenance_records"] = sorted(data["provenance_records"])
    return data


def serialize_v3_7_graph_integrity_provenance_result(result: V37GraphIntegrityProvenanceResult) -> str:
    return stable_serialize(export_v3_7_graph_integrity_provenance_result(result))


def hash_v3_7_graph_integrity_provenance_result(result: V37GraphIntegrityProvenanceResult) -> str:
    data = export_v3_7_graph_integrity_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)
