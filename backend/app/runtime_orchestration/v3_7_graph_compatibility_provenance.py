"""Provenance continuity for v3.7 graph compatibility reasoning."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_compatibility_models import V37GraphCompatibilityMap
from .v3_7_graph_models import V37GraphProvenance


V37_COMPATIBILITY_PROVENANCE_PRESERVED = "v3_7_graph_compatibility_provenance_preserved"
V37_COMPATIBILITY_PROVENANCE_BLOCKED = "v3_7_graph_compatibility_provenance_blocked"


@dataclass(frozen=True)
class V37GraphCompatibilityProvenanceResult:
    provenance_status: str
    domain_provenance_preserved: bool
    rule_provenance_preserved: bool
    node_result_provenance_preserved: bool
    edge_result_provenance_preserved: bool
    finding_provenance_preserved: bool
    governance_provenance_preserved: bool
    explainability_provenance_preserved: bool
    compatibility_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_compatibility_provenance(
    compatibility_map: V37GraphCompatibilityMap,
) -> V37GraphCompatibilityProvenanceResult:
    missing: list[str] = []
    domain_ok = _all_complete(((item.domain_id, item.provenance) for item in compatibility_map.domains), missing)
    rule_ok = _all_complete(((item.rule_id, item.provenance) for item in compatibility_map.rules), missing)
    node_ok = _all_complete(((item.relationship_id, item.provenance) for item in compatibility_map.node_results), missing)
    edge_ok = _all_complete(((item.edge_id, item.provenance) for item in compatibility_map.edge_results), missing)
    finding_ok = _all_complete(((item.finding_id, item.provenance) for item in compatibility_map.findings), missing)
    records = collect_v3_7_graph_compatibility_provenance(compatibility_map)
    governance_ok = all(record.governance_references for record in records)
    explainability_ok = all(record.explainability_references for record in records)
    replay_ok = all(record.replay_lineage_references for record in records)
    rollback_ok = all(record.rollback_lineage_references for record in records)
    continuity_ok = bool(compatibility_map.continuity_evidence) and all(
        evidence.compatibility_lineage_references
        and evidence.provenance_lineage_references
        and evidence.replay_lineage_references
        and evidence.rollback_lineage_references
        for evidence in compatibility_map.continuity_evidence
    )
    preserved = all(
        (
            domain_ok,
            rule_ok,
            node_ok,
            edge_ok,
            finding_ok,
            governance_ok,
            explainability_ok,
            continuity_ok,
            replay_ok,
            rollback_ok,
        )
    )
    result = V37GraphCompatibilityProvenanceResult(
        provenance_status=(
            V37_COMPATIBILITY_PROVENANCE_PRESERVED
            if preserved
            else V37_COMPATIBILITY_PROVENANCE_BLOCKED
        ),
        domain_provenance_preserved=domain_ok,
        rule_provenance_preserved=rule_ok,
        node_result_provenance_preserved=node_ok,
        edge_result_provenance_preserved=edge_ok,
        finding_provenance_preserved=finding_ok,
        governance_provenance_preserved=governance_ok,
        explainability_provenance_preserved=explainability_ok,
        compatibility_continuity_preserved=continuity_ok,
        replay_continuity_preserved=replay_ok,
        rollback_continuity_preserved=rollback_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_compatibility_provenance_result(result),
    )


def collect_v3_7_graph_compatibility_provenance(
    compatibility_map: V37GraphCompatibilityMap,
) -> tuple[V37GraphProvenance, ...]:
    records: list[V37GraphProvenance] = []
    records.extend(item.provenance for item in compatibility_map.domains)
    records.extend(item.provenance for item in compatibility_map.rules)
    records.extend(item.provenance for item in compatibility_map.node_results)
    records.extend(item.provenance for item in compatibility_map.edge_results)
    records.extend(item.provenance for item in compatibility_map.findings)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_compatibility_provenance_result(
    result: V37GraphCompatibilityProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_compatibility_provenance_result(
    result: V37GraphCompatibilityProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_compatibility_provenance_result(result))


def hash_v3_7_graph_compatibility_provenance_result(
    result: V37GraphCompatibilityProvenanceResult,
) -> str:
    data = export_v3_7_graph_compatibility_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _all_complete(records: object, missing: list[str]) -> bool:
    complete = True
    for subject_id, provenance in records:
        if not _provenance_complete(provenance):
            missing.append(subject_id)
            complete = False
    return complete


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
