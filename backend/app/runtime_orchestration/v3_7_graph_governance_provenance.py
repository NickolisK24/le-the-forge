"""Provenance continuity for v3.7 graph governance boundary intelligence."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_governance_models import V37GraphGovernanceMap
from .v3_7_graph_models import V37GraphProvenance


V37_GOVERNANCE_PROVENANCE_PRESERVED = "v3_7_graph_governance_provenance_preserved"
V37_GOVERNANCE_PROVENANCE_BLOCKED = "v3_7_graph_governance_provenance_blocked"


@dataclass(frozen=True)
class V37GraphGovernanceProvenanceResult:
    provenance_status: str
    domain_provenance_preserved: bool
    rule_provenance_preserved: bool
    node_classification_provenance_preserved: bool
    edge_classification_provenance_preserved: bool
    governance_continuity_preserved: bool
    compatibility_continuity_preserved: bool
    explainability_continuity_preserved: bool
    replay_continuity_preserved: bool
    rollback_continuity_preserved: bool
    missing_provenance_subjects: tuple[str, ...]
    provenance_record_count: int
    deterministic_provenance_hash: str = ""


def audit_v3_7_graph_governance_provenance(
    governance_map: V37GraphGovernanceMap,
) -> V37GraphGovernanceProvenanceResult:
    missing: list[str] = []
    domain_ok = _all_complete(
        ((domain.domain_id, domain.provenance) for domain in governance_map.domains),
        missing,
    )
    rule_ok = _all_complete(
        ((rule.rule_id, rule.provenance) for rule in governance_map.rules),
        missing,
    )
    node_ok = _all_complete(
        (
            (classification.node_id, classification.provenance)
            for classification in governance_map.node_classifications
        ),
        missing,
    )
    edge_ok = _all_complete(
        (
            (classification.edge_id, classification.provenance)
            for classification in governance_map.edge_classifications
        ),
        missing,
    )
    records = collect_v3_7_graph_governance_provenance(governance_map)
    governance_ok = all(record.governance_references for record in records)
    compatibility_ok = all(record.compatibility_references for record in records)
    explainability_ok = all(record.explainability_references for record in records)
    replay_ok = all(record.replay_lineage_references for record in records)
    rollback_ok = all(record.rollback_lineage_references for record in records)
    preserved = all(
        (
            domain_ok,
            rule_ok,
            node_ok,
            edge_ok,
            governance_ok,
            compatibility_ok,
            explainability_ok,
            replay_ok,
            rollback_ok,
        )
    )
    result = V37GraphGovernanceProvenanceResult(
        provenance_status=(
            V37_GOVERNANCE_PROVENANCE_PRESERVED
            if preserved
            else V37_GOVERNANCE_PROVENANCE_BLOCKED
        ),
        domain_provenance_preserved=domain_ok,
        rule_provenance_preserved=rule_ok,
        node_classification_provenance_preserved=node_ok,
        edge_classification_provenance_preserved=edge_ok,
        governance_continuity_preserved=governance_ok,
        compatibility_continuity_preserved=compatibility_ok,
        explainability_continuity_preserved=explainability_ok,
        replay_continuity_preserved=replay_ok,
        rollback_continuity_preserved=rollback_ok,
        missing_provenance_subjects=tuple(sorted(set(missing))),
        provenance_record_count=len(records),
    )
    return replace(
        result,
        deterministic_provenance_hash=hash_v3_7_graph_governance_provenance_result(result),
    )


def collect_v3_7_graph_governance_provenance(
    governance_map: V37GraphGovernanceMap,
) -> tuple[V37GraphProvenance, ...]:
    records: list[V37GraphProvenance] = []
    records.extend(domain.provenance for domain in governance_map.domains)
    records.extend(rule.provenance for rule in governance_map.rules)
    records.extend(classification.provenance for classification in governance_map.node_classifications)
    records.extend(classification.provenance for classification in governance_map.edge_classifications)
    return tuple(sorted(records, key=lambda item: item.provenance_id))


def export_v3_7_graph_governance_provenance_result(
    result: V37GraphGovernanceProvenanceResult,
) -> dict[str, Any]:
    data = asdict(result)
    data["missing_provenance_subjects"] = sorted(data["missing_provenance_subjects"])
    return data


def serialize_v3_7_graph_governance_provenance_result(
    result: V37GraphGovernanceProvenanceResult,
) -> str:
    return stable_serialize(export_v3_7_graph_governance_provenance_result(result))


def hash_v3_7_graph_governance_provenance_result(
    result: V37GraphGovernanceProvenanceResult,
) -> str:
    data = export_v3_7_graph_governance_provenance_result(result)
    data.pop("deterministic_provenance_hash", None)
    return deterministic_hash(data)


def _all_complete(
    records: object,
    missing: list[str],
) -> bool:
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
