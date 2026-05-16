"""Deterministic v3.7 graph governance boundary models.

Governance records are metadata classifications only. They do not enable graph
execution, traversal, routing, scheduling, dispatch, mutation, or orchestration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphMetadataEntry, V37GraphProvenance


V3_7_GRAPH_GOVERNANCE_PHASE_ID = "v3_7_graph_governance_boundary_intelligence"
V37_DOMAIN_SUPPORTED = "supported"
V37_DOMAIN_UNSUPPORTED = "unsupported"
V37_DOMAIN_PROHIBITED = "prohibited"
V37_DOMAIN_EXPERIMENTAL = "experimental"
V37_DOMAIN_GOVERNANCE_RESTRICTED = "governance_restricted"
V37_DOMAIN_COMPATIBILITY_RESTRICTED = "compatibility_restricted"
V37_DOMAIN_CLASSIFICATIONS: tuple[str, ...] = (
    V37_DOMAIN_SUPPORTED,
    V37_DOMAIN_UNSUPPORTED,
    V37_DOMAIN_PROHIBITED,
    V37_DOMAIN_EXPERIMENTAL,
    V37_DOMAIN_GOVERNANCE_RESTRICTED,
    V37_DOMAIN_COMPATIBILITY_RESTRICTED,
)

V37_NODE_SUPPORTED = "supported"
V37_NODE_UNSUPPORTED = "unsupported"
V37_NODE_PROHIBITED = "prohibited"
V37_NODE_EXPERIMENTAL = "experimental"
V37_NODE_GOVERNANCE_RESTRICTED = "governance_restricted"
V37_NODE_COMPATIBILITY_RESTRICTED = "compatibility_restricted"
V37_NODE_CLASSIFICATIONS: tuple[str, ...] = (
    V37_NODE_SUPPORTED,
    V37_NODE_UNSUPPORTED,
    V37_NODE_PROHIBITED,
    V37_NODE_EXPERIMENTAL,
    V37_NODE_GOVERNANCE_RESTRICTED,
    V37_NODE_COMPATIBILITY_RESTRICTED,
)

V37_EDGE_ALLOWED_STRUCTURAL = "allowed_structural_relationship"
V37_EDGE_UNSUPPORTED_STRUCTURAL = "unsupported_structural_relationship"
V37_EDGE_PROHIBITED_STRUCTURAL = "prohibited_structural_relationship"
V37_EDGE_GOVERNANCE_RESTRICTED = "governance_restricted_relationship"
V37_EDGE_COMPATIBILITY_RESTRICTED = "compatibility_restricted_relationship"
V37_EDGE_CLASSIFICATIONS: tuple[str, ...] = (
    V37_EDGE_ALLOWED_STRUCTURAL,
    V37_EDGE_UNSUPPORTED_STRUCTURAL,
    V37_EDGE_PROHIBITED_STRUCTURAL,
    V37_EDGE_GOVERNANCE_RESTRICTED,
    V37_EDGE_COMPATIBILITY_RESTRICTED,
)

V37_GOVERNANCE_VISIBILITY_VISIBLE = "governance_visibility_visible"
V37_GOVERNANCE_VISIBILITY_GAP = "governance_visibility_gap"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphGovernanceDomain:
    domain_id: str
    domain_name: str
    domain_classification: str
    restriction_ids: tuple[str, ...]
    compatibility_boundary_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("restriction_ids", "compatibility_boundary_ids"):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37NodeGovernanceClassification:
    node_id: str
    node_type: str
    governance_classification: str
    governance_domain_ids: tuple[str, ...]
    restriction_ids: tuple[str, ...]
    compatibility_boundary_ids: tuple[str, ...]
    prohibited_relationship_ids: tuple[str, ...]
    unsupported_relationship_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "governance_domain_ids",
            "restriction_ids",
            "compatibility_boundary_ids",
            "prohibited_relationship_ids",
            "unsupported_relationship_ids",
            "explainability_evidence_ids",
        ):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37EdgeGovernanceClassification:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    governance_classification: str
    governance_domain_ids: tuple[str, ...]
    restriction_ids: tuple[str, ...]
    compatibility_boundary_ids: tuple[str, ...]
    prohibited_relationship_ids: tuple[str, ...]
    unsupported_relationship_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    edge_implies_execution_flow: bool = False
    traversal_execution_enabled: bool = False
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in (
            "governance_domain_ids",
            "restriction_ids",
            "compatibility_boundary_ids",
            "prohibited_relationship_ids",
            "unsupported_relationship_ids",
            "explainability_evidence_ids",
        ):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphGovernanceRule:
    rule_id: str
    rule_kind: str
    source_domain_id: str
    target_domain_id: str
    node_classification: str
    edge_classification: str
    restriction_summary: str
    relationship_visible: bool
    prohibited_relationship: bool
    unsupported_relationship: bool
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphGovernanceFinding:
    finding_id: str
    finding_kind: str
    subject_type: str
    subject_id: str
    governance_classification: str
    visibility_status: str
    reason: str
    rule_id: str
    provenance_references: tuple[str, ...]
    fail_visible: bool = True

    def __post_init__(self) -> None:
        _set_tuple_field(self, "provenance_references")


@dataclass(frozen=True)
class V37GraphGovernanceContinuityEvidence:
    continuity_id: str
    domain_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    node_classification_ids: tuple[str, ...]
    edge_classification_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    governance_lineage_references: tuple[str, ...]
    compatibility_lineage_references: tuple[str, ...]
    provenance_lineage_references: tuple[str, ...]
    explainability_lineage_references: tuple[str, ...]
    replay_lineage_references: tuple[str, ...]
    rollback_lineage_references: tuple[str, ...]
    deterministic_hash_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "domain_ids",
            "rule_ids",
            "node_classification_ids",
            "edge_classification_ids",
            "finding_ids",
            "governance_lineage_references",
            "compatibility_lineage_references",
            "provenance_lineage_references",
            "explainability_lineage_references",
            "replay_lineage_references",
            "rollback_lineage_references",
            "deterministic_hash_references",
        ):
            _set_tuple_field(self, field_name)


@dataclass(frozen=True)
class V37GraphGovernanceMap:
    graph_id: str
    governance_phase_id: str
    domains: tuple[V37GraphGovernanceDomain, ...]
    rules: tuple[V37GraphGovernanceRule, ...]
    node_classifications: tuple[V37NodeGovernanceClassification, ...]
    edge_classifications: tuple[V37EdgeGovernanceClassification, ...]
    findings: tuple[V37GraphGovernanceFinding, ...]
    continuity_evidence: tuple[V37GraphGovernanceContinuityEvidence, ...]
    governance_metadata_does_not_enable_orchestration: bool = True
    structural_governance_artifact_only: bool = True
    non_executable: bool = True
    graph_execution_enabled: bool = False
    node_execution_enabled: bool = False
    edge_traversal_execution_enabled: bool = False
    runtime_orchestration_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    optimization_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    graph_evaluation_execution_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "domains",
            "rules",
            "node_classifications",
            "edge_classifications",
            "findings",
            "continuity_evidence",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_governance_domain(domain: V37GraphGovernanceDomain) -> dict[str, Any]:
    data = asdict(domain)
    data["restriction_ids"] = sorted(data["restriction_ids"])
    data["compatibility_boundary_ids"] = sorted(data["compatibility_boundary_ids"])
    data["metadata"] = _export_metadata(domain.metadata)
    data["provenance"] = _export_provenance(domain.provenance)
    return data


def export_v3_7_node_governance_classification(
    classification: V37NodeGovernanceClassification,
) -> dict[str, Any]:
    data = asdict(classification)
    for field_name in (
        "governance_domain_ids",
        "restriction_ids",
        "compatibility_boundary_ids",
        "prohibited_relationship_ids",
        "unsupported_relationship_ids",
        "explainability_evidence_ids",
    ):
        data[field_name] = sorted(data[field_name])
    data["metadata"] = _export_metadata(classification.metadata)
    data["provenance"] = _export_provenance(classification.provenance)
    return data


def export_v3_7_edge_governance_classification(
    classification: V37EdgeGovernanceClassification,
) -> dict[str, Any]:
    data = asdict(classification)
    for field_name in (
        "governance_domain_ids",
        "restriction_ids",
        "compatibility_boundary_ids",
        "prohibited_relationship_ids",
        "unsupported_relationship_ids",
        "explainability_evidence_ids",
    ):
        data[field_name] = sorted(data[field_name])
    data["metadata"] = _export_metadata(classification.metadata)
    data["provenance"] = _export_provenance(classification.provenance)
    return data


def export_v3_7_governance_rule(rule: V37GraphGovernanceRule) -> dict[str, Any]:
    data = asdict(rule)
    data["metadata"] = _export_metadata(rule.metadata)
    data["provenance"] = _export_provenance(rule.provenance)
    return data


def export_v3_7_governance_finding(finding: V37GraphGovernanceFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["provenance_references"] = sorted(data["provenance_references"])
    return data


def export_v3_7_governance_continuity_evidence(
    evidence: V37GraphGovernanceContinuityEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "domain_ids",
        "rule_ids",
        "node_classification_ids",
        "edge_classification_ids",
        "finding_ids",
        "governance_lineage_references",
        "compatibility_lineage_references",
        "provenance_lineage_references",
        "explainability_lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "deterministic_hash_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data


def export_v3_7_governance_map(governance_map: V37GraphGovernanceMap) -> dict[str, Any]:
    return {
        "graph_id": governance_map.graph_id,
        "governance_phase_id": governance_map.governance_phase_id,
        "domains": [
            export_v3_7_governance_domain(domain)
            for domain in sorted(governance_map.domains, key=lambda item: item.domain_id)
        ],
        "rules": [
            export_v3_7_governance_rule(rule)
            for rule in sorted(governance_map.rules, key=lambda item: item.rule_id)
        ],
        "node_classifications": [
            export_v3_7_node_governance_classification(classification)
            for classification in sorted(governance_map.node_classifications, key=lambda item: item.node_id)
        ],
        "edge_classifications": [
            export_v3_7_edge_governance_classification(classification)
            for classification in sorted(governance_map.edge_classifications, key=lambda item: item.edge_id)
        ],
        "findings": [
            export_v3_7_governance_finding(finding)
            for finding in sorted(governance_map.findings, key=lambda item: item.finding_id)
        ],
        "continuity_evidence": [
            export_v3_7_governance_continuity_evidence(evidence)
            for evidence in sorted(governance_map.continuity_evidence, key=lambda item: item.continuity_id)
        ],
        "governance_metadata_does_not_enable_orchestration": (
            governance_map.governance_metadata_does_not_enable_orchestration
        ),
        "structural_governance_artifact_only": governance_map.structural_governance_artifact_only,
        "non_executable": governance_map.non_executable,
        "graph_execution_enabled": governance_map.graph_execution_enabled,
        "node_execution_enabled": governance_map.node_execution_enabled,
        "edge_traversal_execution_enabled": governance_map.edge_traversal_execution_enabled,
        "runtime_orchestration_enabled": governance_map.runtime_orchestration_enabled,
        "routing_enabled": governance_map.routing_enabled,
        "scheduling_enabled": governance_map.scheduling_enabled,
        "dispatch_enabled": governance_map.dispatch_enabled,
        "optimization_enabled": governance_map.optimization_enabled,
        "recommendation_enabled": governance_map.recommendation_enabled,
        "autonomous_orchestration_enabled": governance_map.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": governance_map.runtime_mutation_enabled,
        "graph_evaluation_execution_enabled": governance_map.graph_evaluation_execution_enabled,
    }


def export_v3_7_governance_counts(governance_map: V37GraphGovernanceMap) -> dict[str, int]:
    return {
        "domain_count": len(governance_map.domains),
        "rule_count": len(governance_map.rules),
        "node_classification_count": len(governance_map.node_classifications),
        "edge_classification_count": len(governance_map.edge_classifications),
        "finding_count": len(governance_map.findings),
        "continuity_evidence_count": len(governance_map.continuity_evidence),
    }


def serialize_v3_7_governance_map(governance_map: V37GraphGovernanceMap) -> str:
    return stable_serialize(export_v3_7_governance_map(governance_map))


def hash_v3_7_governance_map(governance_map: V37GraphGovernanceMap) -> str:
    return deterministic_hash(export_v3_7_governance_map(governance_map))


def validate_v3_7_governance_serialization_stability(
    governance_map: V37GraphGovernanceMap,
) -> dict[str, Any]:
    first = serialize_v3_7_governance_map(governance_map)
    second = serialize_v3_7_governance_map(governance_map)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_governance_map",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_governance_hash_stability(governance_map: V37GraphGovernanceMap) -> dict[str, Any]:
    first = hash_v3_7_governance_map(governance_map)
    second = hash_v3_7_governance_map(governance_map)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_governance_map",
    }


def _export_metadata(metadata: tuple[V37GraphMetadataEntry, ...]) -> list[dict[str, Any]]:
    return [
        asdict(entry)
        for entry in sorted(metadata, key=lambda item: item.metadata_key)
    ]


def _export_provenance(provenance: V37GraphProvenance) -> dict[str, Any]:
    data = asdict(provenance)
    for field_name in (
        "lineage_references",
        "replay_lineage_references",
        "rollback_lineage_references",
        "governance_references",
        "compatibility_references",
        "explainability_references",
    ):
        data[field_name] = sorted(data[field_name])
    return data
