"""Deterministic v3.7 graph compatibility reasoning models.

Compatibility records are structural planning evidence only. They do not
authorize graph execution, traversal, routing, scheduling, dispatch, or runtime
orchestration.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable

from app.runtime_intelligence.classification_hashing import deterministic_hash, stable_serialize

from .v3_7_graph_models import V37GraphMetadataEntry, V37GraphProvenance


V3_7_GRAPH_COMPATIBILITY_PHASE_ID = "v3_7_graph_compatibility_reasoning"
V37_COMPATIBLE = "compatible"
V37_INCOMPATIBLE = "incompatible"
V37_UNSUPPORTED_COMPATIBILITY = "unsupported"
V37_PROHIBITED_COMPATIBILITY = "prohibited"
V37_GOVERNANCE_RESTRICTED_COMPATIBILITY = "governance_restricted"
V37_COMPATIBILITY_RESTRICTED = "compatibility_restricted"
V37_EXPERIMENTAL_COMPATIBILITY = "experimental"
V37_UNKNOWN_COMPATIBILITY = "unknown"
V37_COMPATIBILITY_CLASSIFICATIONS: tuple[str, ...] = (
    V37_COMPATIBLE,
    V37_INCOMPATIBLE,
    V37_UNSUPPORTED_COMPATIBILITY,
    V37_PROHIBITED_COMPATIBILITY,
    V37_GOVERNANCE_RESTRICTED_COMPATIBILITY,
    V37_COMPATIBILITY_RESTRICTED,
    V37_EXPERIMENTAL_COMPATIBILITY,
    V37_UNKNOWN_COMPATIBILITY,
)

V37_COMPATIBILITY_VISIBILITY_VISIBLE = "compatibility_visibility_visible"
V37_COMPATIBILITY_VISIBILITY_GAP = "compatibility_visibility_gap"


def _as_tuple(values: Iterable[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    return tuple(values or ())


def _set_tuple_field(source: object, field_name: str) -> None:
    object.__setattr__(source, field_name, _as_tuple(getattr(source, field_name)))


@dataclass(frozen=True)
class V37GraphCompatibilityDomain:
    domain_id: str
    domain_name: str
    compatibility_classification: str
    governance_domain_id: str
    restriction_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        _set_tuple_field(self, "restriction_ids")
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphCompatibilityRule:
    rule_id: str
    rule_kind: str
    source_domain_id: str
    target_domain_id: str
    compatibility_classification: str
    governance_rule_ids: tuple[str, ...]
    restriction_summary: str
    visible: bool
    provenance: V37GraphProvenance
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        _set_tuple_field(self, "governance_rule_ids")
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37NodeCompatibilityResult:
    relationship_id: str
    source_node_id: str
    target_node_id: str
    source_domain_id: str
    target_domain_id: str
    source_governance_classification: str
    target_governance_classification: str
    compatibility_classification: str
    rule_id: str
    governance_rule_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    node_relationship_implies_runtime_ordering: bool = False
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("governance_rule_ids", "finding_ids", "explainability_evidence_ids"):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37EdgeCompatibilityResult:
    edge_id: str
    source_node_id: str
    target_node_id: str
    relationship_type: str
    edge_governance_classification: str
    domain_compatibility_classification: str
    compatibility_classification: str
    rule_id: str
    governance_rule_ids: tuple[str, ...]
    finding_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    explainability_evidence_ids: tuple[str, ...]
    edge_compatibility_implies_traversal: bool = False
    traversal_enabled: bool = False
    metadata: tuple[V37GraphMetadataEntry, ...] = ()

    def __post_init__(self) -> None:
        for field_name in ("governance_rule_ids", "finding_ids", "explainability_evidence_ids"):
            _set_tuple_field(self, field_name)
        object.__setattr__(self, "metadata", tuple(self.metadata or ()))


@dataclass(frozen=True)
class V37GraphCompatibilityFinding:
    finding_id: str
    finding_kind: str
    subject_type: str
    subject_id: str
    compatibility_classification: str
    visibility_status: str
    reason: str
    rule_id: str
    governance_rule_ids: tuple[str, ...]
    provenance: V37GraphProvenance
    fail_visible: bool = True

    def __post_init__(self) -> None:
        _set_tuple_field(self, "governance_rule_ids")


@dataclass(frozen=True)
class V37GraphCompatibilityAggregation:
    compatible_relationship_count: int
    incompatible_relationship_count: int
    unsupported_relationship_count: int
    prohibited_relationship_count: int
    experimental_relationship_count: int
    unknown_relationship_count: int
    governance_restricted_count: int
    compatibility_restricted_count: int
    fail_visible_finding_count: int
    node_relationship_count: int
    edge_relationship_count: int


@dataclass(frozen=True)
class V37GraphCompatibilityContinuityEvidence:
    continuity_id: str
    domain_ids: tuple[str, ...]
    rule_ids: tuple[str, ...]
    node_relationship_ids: tuple[str, ...]
    edge_relationship_ids: tuple[str, ...]
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
            "node_relationship_ids",
            "edge_relationship_ids",
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
class V37GraphCompatibilityMap:
    graph_id: str
    compatibility_phase_id: str
    domains: tuple[V37GraphCompatibilityDomain, ...]
    rules: tuple[V37GraphCompatibilityRule, ...]
    node_results: tuple[V37NodeCompatibilityResult, ...]
    edge_results: tuple[V37EdgeCompatibilityResult, ...]
    findings: tuple[V37GraphCompatibilityFinding, ...]
    aggregation: V37GraphCompatibilityAggregation
    continuity_evidence: tuple[V37GraphCompatibilityContinuityEvidence, ...]
    compatibility_reasoning_is_non_executable: bool = True
    compatibility_does_not_authorize_execution: bool = True
    edge_compatibility_does_not_imply_traversal: bool = True
    node_compatibility_does_not_imply_runtime_ordering: bool = True
    structural_planning_evidence_only: bool = True
    graph_execution_enabled: bool = False
    node_execution_enabled: bool = False
    edge_traversal_execution_enabled: bool = False
    runtime_orchestration_enabled: bool = False
    routing_enabled: bool = False
    scheduling_enabled: bool = False
    dispatch_enabled: bool = False
    graph_optimization_enabled: bool = False
    recommendation_enabled: bool = False
    autonomous_orchestration_enabled: bool = False
    runtime_mutation_enabled: bool = False
    background_graph_processing_enabled: bool = False
    graph_path_selection_enabled: bool = False

    def __post_init__(self) -> None:
        for field_name in (
            "domains",
            "rules",
            "node_results",
            "edge_results",
            "findings",
            "continuity_evidence",
        ):
            object.__setattr__(self, field_name, tuple(getattr(self, field_name) or ()))


def export_v3_7_compatibility_domain(domain: V37GraphCompatibilityDomain) -> dict[str, Any]:
    data = asdict(domain)
    data["restriction_ids"] = sorted(data["restriction_ids"])
    data["metadata"] = _export_metadata(domain.metadata)
    data["provenance"] = _export_provenance(domain.provenance)
    return data


def export_v3_7_compatibility_rule(rule: V37GraphCompatibilityRule) -> dict[str, Any]:
    data = asdict(rule)
    data["governance_rule_ids"] = sorted(data["governance_rule_ids"])
    data["metadata"] = _export_metadata(rule.metadata)
    data["provenance"] = _export_provenance(rule.provenance)
    return data


def export_v3_7_node_compatibility_result(result: V37NodeCompatibilityResult) -> dict[str, Any]:
    data = asdict(result)
    for field_name in ("governance_rule_ids", "finding_ids", "explainability_evidence_ids"):
        data[field_name] = sorted(data[field_name])
    data["metadata"] = _export_metadata(result.metadata)
    data["provenance"] = _export_provenance(result.provenance)
    return data


def export_v3_7_edge_compatibility_result(result: V37EdgeCompatibilityResult) -> dict[str, Any]:
    data = asdict(result)
    for field_name in ("governance_rule_ids", "finding_ids", "explainability_evidence_ids"):
        data[field_name] = sorted(data[field_name])
    data["metadata"] = _export_metadata(result.metadata)
    data["provenance"] = _export_provenance(result.provenance)
    return data


def export_v3_7_compatibility_finding(finding: V37GraphCompatibilityFinding) -> dict[str, Any]:
    data = asdict(finding)
    data["governance_rule_ids"] = sorted(data["governance_rule_ids"])
    data["provenance"] = _export_provenance(finding.provenance)
    return data


def export_v3_7_compatibility_aggregation(
    aggregation: V37GraphCompatibilityAggregation,
) -> dict[str, Any]:
    return asdict(aggregation)


def export_v3_7_compatibility_continuity_evidence(
    evidence: V37GraphCompatibilityContinuityEvidence,
) -> dict[str, Any]:
    data = asdict(evidence)
    for field_name in (
        "domain_ids",
        "rule_ids",
        "node_relationship_ids",
        "edge_relationship_ids",
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


def export_v3_7_compatibility_map(compatibility_map: V37GraphCompatibilityMap) -> dict[str, Any]:
    return {
        "graph_id": compatibility_map.graph_id,
        "compatibility_phase_id": compatibility_map.compatibility_phase_id,
        "domains": [
            export_v3_7_compatibility_domain(domain)
            for domain in sorted(compatibility_map.domains, key=lambda item: item.domain_id)
        ],
        "rules": [
            export_v3_7_compatibility_rule(rule)
            for rule in sorted(compatibility_map.rules, key=lambda item: item.rule_id)
        ],
        "node_results": [
            export_v3_7_node_compatibility_result(result)
            for result in sorted(compatibility_map.node_results, key=lambda item: item.relationship_id)
        ],
        "edge_results": [
            export_v3_7_edge_compatibility_result(result)
            for result in sorted(compatibility_map.edge_results, key=lambda item: item.edge_id)
        ],
        "findings": [
            export_v3_7_compatibility_finding(finding)
            for finding in sorted(compatibility_map.findings, key=lambda item: item.finding_id)
        ],
        "aggregation": export_v3_7_compatibility_aggregation(compatibility_map.aggregation),
        "continuity_evidence": [
            export_v3_7_compatibility_continuity_evidence(evidence)
            for evidence in sorted(compatibility_map.continuity_evidence, key=lambda item: item.continuity_id)
        ],
        "compatibility_reasoning_is_non_executable": compatibility_map.compatibility_reasoning_is_non_executable,
        "compatibility_does_not_authorize_execution": compatibility_map.compatibility_does_not_authorize_execution,
        "edge_compatibility_does_not_imply_traversal": compatibility_map.edge_compatibility_does_not_imply_traversal,
        "node_compatibility_does_not_imply_runtime_ordering": (
            compatibility_map.node_compatibility_does_not_imply_runtime_ordering
        ),
        "structural_planning_evidence_only": compatibility_map.structural_planning_evidence_only,
        "graph_execution_enabled": compatibility_map.graph_execution_enabled,
        "node_execution_enabled": compatibility_map.node_execution_enabled,
        "edge_traversal_execution_enabled": compatibility_map.edge_traversal_execution_enabled,
        "runtime_orchestration_enabled": compatibility_map.runtime_orchestration_enabled,
        "routing_enabled": compatibility_map.routing_enabled,
        "scheduling_enabled": compatibility_map.scheduling_enabled,
        "dispatch_enabled": compatibility_map.dispatch_enabled,
        "graph_optimization_enabled": compatibility_map.graph_optimization_enabled,
        "recommendation_enabled": compatibility_map.recommendation_enabled,
        "autonomous_orchestration_enabled": compatibility_map.autonomous_orchestration_enabled,
        "runtime_mutation_enabled": compatibility_map.runtime_mutation_enabled,
        "background_graph_processing_enabled": compatibility_map.background_graph_processing_enabled,
        "graph_path_selection_enabled": compatibility_map.graph_path_selection_enabled,
    }


def export_v3_7_compatibility_counts(compatibility_map: V37GraphCompatibilityMap) -> dict[str, int]:
    return {
        "domain_count": len(compatibility_map.domains),
        "rule_count": len(compatibility_map.rules),
        "node_result_count": len(compatibility_map.node_results),
        "edge_result_count": len(compatibility_map.edge_results),
        "finding_count": len(compatibility_map.findings),
        "continuity_evidence_count": len(compatibility_map.continuity_evidence),
    }


def serialize_v3_7_compatibility_map(compatibility_map: V37GraphCompatibilityMap) -> str:
    return stable_serialize(export_v3_7_compatibility_map(compatibility_map))


def hash_v3_7_compatibility_map(compatibility_map: V37GraphCompatibilityMap) -> str:
    return deterministic_hash(export_v3_7_compatibility_map(compatibility_map))


def validate_v3_7_compatibility_serialization_stability(
    compatibility_map: V37GraphCompatibilityMap,
) -> dict[str, Any]:
    first = serialize_v3_7_compatibility_map(compatibility_map)
    second = serialize_v3_7_compatibility_map(compatibility_map)
    return {
        "stable": first == second,
        "serializer": "json_sort_keys_stable_compatibility_map",
        "first_length": len(first),
        "second_length": len(second),
    }


def validate_v3_7_compatibility_hash_stability(
    compatibility_map: V37GraphCompatibilityMap,
) -> dict[str, Any]:
    first = hash_v3_7_compatibility_map(compatibility_map)
    second = hash_v3_7_compatibility_map(compatibility_map)
    return {
        "stable": first == second,
        "first_hash": first,
        "second_hash": second,
        "hash_algorithm": "sha256_stable_json_compatibility_map",
    }


def _export_metadata(metadata: tuple[V37GraphMetadataEntry, ...]) -> list[dict[str, Any]]:
    return [asdict(entry) for entry in sorted(metadata, key=lambda item: item.metadata_key)]


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
